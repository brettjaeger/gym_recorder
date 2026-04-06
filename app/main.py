from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from app.claude_parser import parse_workout_image
from app.sheets_client import append_workout_to_sheet

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_workout(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported image type: {file.content_type}")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 10 MB)")

    try:
        workout = await parse_workout_image(image_bytes, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    sheet_url = await append_workout_to_sheet(workout)

    return {
        "status": "success",
        "date": workout.date,
        "workout_name": workout.workout_name,
        "exercises_parsed": len(workout.exercises),
        "cardio_parsed": len(workout.cardio),
        "sheet_url": sheet_url,
    }


# Serve PWA frontend at root — must be mounted last
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
