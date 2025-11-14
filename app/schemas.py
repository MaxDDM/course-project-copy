# schemas.py
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class WorkoutBase(BaseModel):
    date: date
    duration_min: int = Field(
        ..., ge=0, description="Длительность тренировки в минутах"
    )
    notes: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    id: Optional[int] = None


class WorkoutRead(WorkoutBase):
    id: int
    sets: List["SetRead"] = []

    class Config:
        from_attributes = True


class SetBase(BaseModel):
    exercise: str
    reps: int
    weight_kg: Optional[str] = None


class SetCreate(SetBase):
    id: Optional[int] = None


class SetRead(SetBase):
    id: int
    workout_id: int

    class Config:
        from_attributes = True


WorkoutRead.model_rebuild()
