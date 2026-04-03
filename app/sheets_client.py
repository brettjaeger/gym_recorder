import asyncio
import json
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from app.models import WorkoutRecord

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME = "Workouts"


def _get_service():
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def _append_sync(workout: WorkoutRecord) -> str:
    spreadsheet_id = os.environ["GOOGLE_SHEET_ID"]
    service = _get_service()

    muscle_str = ", ".join(workout.muscle_groups)
    base = [
        workout.date,
        workout.workout_name,
        muscle_str,
        workout.water_oz if workout.water_oz is not None else "",
        workout.sleep_hours if workout.sleep_hours is not None else "",
        workout.bodyweight_lbs if workout.bodyweight_lbs is not None else "",
        workout.duration_minutes if workout.duration_minutes is not None else "",
        workout.rating_percent if workout.rating_percent is not None else "",
        workout.notes or "",
    ]

    rows = []

    for exercise in workout.exercises:
        for s in exercise.sets:
            rows.append(base + [
                exercise.name,
                s.set_number,
                s.weight_lbs if s.weight_lbs is not None else "",
                s.reps if s.reps is not None else "",
                exercise.notes or "",
                "", "", "", "",
            ])

    for cardio in workout.cardio:
        rows.append(base + [
            "", "", "", "", "",
            cardio.name,
            cardio.duration_minutes if cardio.duration_minutes is not None else "",
            cardio.distance_miles if cardio.distance_miles is not None else "",
            cardio.calories if cardio.calories is not None else "",
        ])

    # Write at least one summary row if no exercises or cardio
    if not rows:
        rows.append(base + ["", "", "", "", "", "", "", "", ""])

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{SHEET_NAME}!A:R",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()

    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"


async def append_workout_to_sheet(workout: WorkoutRecord) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _append_sync, workout)
