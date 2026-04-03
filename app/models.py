from pydantic import BaseModel
from typing import Optional


class SetRecord(BaseModel):
    set_number: int
    weight_lbs: Optional[float] = None
    reps: Optional[int] = None


class ExerciseRecord(BaseModel):
    name: str
    sets: list[SetRecord]
    notes: Optional[str] = None


class CardioRecord(BaseModel):
    name: str
    duration_minutes: Optional[float] = None
    distance_miles: Optional[float] = None
    calories: Optional[int] = None


class WorkoutRecord(BaseModel):
    date: str
    workout_name: str
    muscle_groups: list[str]
    water_oz: Optional[float] = None
    sleep_hours: Optional[float] = None
    bodyweight_lbs: Optional[float] = None
    duration_minutes: Optional[int] = None
    exercises: list[ExerciseRecord]
    cardio: list[CardioRecord]
    notes: Optional[str] = None
    rating_percent: Optional[int] = None
