import asyncio
import base64
import json
import os

import anthropic

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


def _call_claude(image_bytes: bytes, mime_type: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": "Extract the workout data from this image."},
                ],
            }
        ],
    )
    return next(block.text for block in response.content if block.type == "text").strip()


async def parse_workout_image(image_bytes: bytes, mime_type: str) -> WorkoutRecord:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set. Check your .env file.")
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, _call_claude, image_bytes, mime_type, api_key)

    # Strip accidental markdown fences
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\nRaw response: {raw[:500]}")

    return WorkoutRecord(**data)
