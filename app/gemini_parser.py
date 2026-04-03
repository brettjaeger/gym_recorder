import asyncio
import json
import os

from google import genai

from app.models import WorkoutRecord

SYSTEM_PROMPT = """
You are a precise data extraction assistant. You will receive a photo of a handwritten gym notebook page.
Extract all information and return ONLY valid JSON matching this exact schema. Do not include markdown,
code fences, or any explanation — raw JSON only.

Schema:
{
  "date": "YYYY-MM-DD",
  "workout_name": "string (e.g. 'Push Day A')",
  "muscle_groups": ["string", ...],
  "water_oz": number or null,
  "sleep_hours": number or null,
  "bodyweight_lbs": number or null,
  "duration_minutes": integer or null,
  "exercises": [
    {
      "name": "string",
      "sets": [
        { "set_number": 1, "weight_lbs": number or null, "reps": integer or null }
      ],
      "notes": "string or null"
    }
  ],
  "cardio": [
    {
      "name": "string",
      "duration_minutes": number or null,
      "distance_miles": number or null,
      "calories": integer or null
    }
  ],
  "notes": "string or null",
  "rating_percent": integer or null
}

Rules:
- Dates: if the year is absent, assume the most recent plausible year
- Weight values: always convert to lbs (if kg is written, multiply by 2.205)
- Sets written as "55 lbs x 15" -> weight_lbs: 55, reps: 15
- If a set has only reps (bodyweight), weight_lbs is null
- Compound sets mentioned in notes: record exercises separately, add a notes field to each
- If a field is illegible or absent, use null — never guess
- rating_percent: if written as a fraction (e.g. "8/10"), convert to percent (80)
- Return an empty list [] for exercises or cardio if none are present
"""


def _call_gemini(image_bytes: bytes, mime_type: str, api_key: str) -> str:
    client = genai.Client(api_key=api_key)
    image_part = genai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[SYSTEM_PROMPT, image_part],
    )
    return response.text.strip()


async def parse_workout_image(image_bytes: bytes, mime_type: str) -> WorkoutRecord:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Check your .env file.")
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, _call_gemini, image_bytes, mime_type, api_key)

    # Strip accidental markdown fences if Gemini ignores the instruction
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\nRaw response: {raw[:500]}")

    return WorkoutRecord(**data)
