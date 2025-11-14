from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class WorkoutORM(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    duration_min = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)

    sets = relationship(
        "SetORM", back_populates="workout", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Workout(id={self.id}, date={self.date}, duration_min={self.duration_min})>"


class SetORM(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise = Column(String, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(String, nullable=True)

    workout = relationship("WorkoutORM", back_populates="sets")

    def __repr__(self):
        return (
            f"<Set(id={self.id}, workout_id={self.workout_id}, "
            f"exercise='{self.exercise}', reps={self.reps})>"
        )
