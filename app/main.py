import random
import re
import time
from contextlib import contextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from .database import create_db_tables, get_db
from .models import SetORM, WorkoutORM
from .schemas import SetCreate, SetRead, WorkoutCreate, WorkoutRead

app = FastAPI(
    title="Workout log API",
    description="Простой API для логирования тренировок и подходов",
    version="0.1.0",
)

_MAX_INFLIGHT = 8
_inflight = 0


@contextmanager
def time_budget(seconds: float):
    start = time.monotonic()

    def exceeded() -> bool:
        return (time.monotonic() - start) > seconds

    yield exceeded


def retry_read(
    fn,
    *,
    attempts: int = 3,
    base_delay: float = 0.05,
    max_delay: float = 0.3,
    budget_left=lambda: False,
):
    last_exc = None
    for i in range(attempts):
        if budget_left():
            break
        try:
            return fn()
        except Exception as e:
            last_exc = e
            delay = min(max_delay, base_delay * (2**i)) * (0.7 + 0.6 * random.random())
            if not budget_left() and delay < 0.001:
                continue
            if not budget_left():
                time.sleep(delay)
    if last_exc:
        raise last_exc


SUSPECT_PATTERNS = re.compile(
    r"(--|/\*|\*/|;|\\x00|char\(|nchar\(|varchar\(|nvarchar\(|cast\(|convert\(|exec\b|execute\b|xp_|sp_|\bdrop\b|\bdelete\b|\binsert\b|\bupdate\b|\bunion\b|\bselect\b)",
    re.IGNORECASE,
)


def validate_no_sqli(value: str, field_name: str):
    if value is None:
        return
    if len(value) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field '{field_name}' is too long.",
        )
    if SUSPECT_PATTERNS.search(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field '{field_name}' contains disallowed patterns.",
        )


@app.on_event("startup")
def on_startup():
    create_db_tables()
    print("Database tables created or already exist.")


@app.get("/")
def root():
    return {"message": "Workout log API is running. Open /docs for Swagger UI."}


@app.get("/workouts", response_model=List[WorkoutRead])
def get_workouts(db: Session = Depends(get_db)):
    with time_budget(2.5) as exceeded:

        def do_query():
            return db.execute(select(WorkoutORM)).scalars().all()

        try:
            result = retry_read(
                do_query,
                attempts=3,
                base_delay=0.03,
                max_delay=0.2,
                budget_left=exceeded,
            )
        except Exception:
            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out while reading workouts.",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read workouts. Please retry.",
            )
        if exceeded():
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timed out while reading workouts.",
            )
        return result


@app.post("/workouts", response_model=WorkoutRead, status_code=status.HTTP_201_CREATED)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db)):
    global _inflight
    with time_budget(3.0) as exceeded:
        if _inflight >= _MAX_INFLIGHT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many concurrent requests. Please retry shortly.",
            )
        _inflight += 1
        try:
            validate_no_sqli(payload.notes, "notes")

            if payload.id is not None and payload.id <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workout id must be a positive integer.",
                )
            if payload.duration_min is None or payload.duration_min <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workout duration_min must be a positive integer.",
                )

            if payload.id is not None:
                existing_workout = db.get(WorkoutORM, payload.id)
                if existing_workout:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Workout with id {payload.id} already exists.",
                    )

            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out before saving workout.",
                )

            db_workout = WorkoutORM(**payload.model_dump(exclude_unset=True))
            db.add(db_workout)
            db.commit()
            db.refresh(db_workout)

            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out after saving workout.",
                )
            return WorkoutRead.model_validate(db_workout)
        finally:
            _inflight -= 1


@app.get("/workouts/{workout_id}/sets", response_model=List[SetRead])
def get_sets_for_workout(workout_id: int, db: Session = Depends(get_db)):
    if workout_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workout_id must be a positive integer.",
        )
    with time_budget(2.5) as exceeded:

        def do_read():
            workout = db.get(WorkoutORM, workout_id)
            if not workout:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workout with id {workout_id} not found.",
                )
            return workout.sets

        try:
            result = retry_read(
                do_read,
                attempts=2,
                base_delay=0.03,
                max_delay=0.15,
                budget_left=exceeded,
            )
        except HTTPException:
            # Пробрасываем заведомые клиентские ошибки
            raise
        except Exception:
            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out while reading sets.",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read sets. Please retry.",
            )
        if exceeded():
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timed out while reading sets.",
            )
        return result


@app.post(
    "/workouts/{workout_id}/sets",
    response_model=SetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_set(workout_id: int, payload: SetCreate, db: Session = Depends(get_db)):
    global _inflight
    with time_budget(3.0) as exceeded:
        if _inflight >= _MAX_INFLIGHT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many concurrent requests. Please retry shortly.",
            )
        _inflight += 1
        try:
            validate_no_sqli(payload.exercise, "exercise")
            validate_no_sqli(payload.weight_kg, "weight_kg")

            if workout_id <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="workout_id must be a positive integer.",
                )
            if payload.id is not None and payload.id <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Set id must be a positive integer.",
                )
            if payload.reps is None or payload.reps <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="reps must be a positive integer.",
                )

            exists_stmt = select(exists().where(WorkoutORM.id == workout_id))
            workout_exists = db.execute(exists_stmt).scalar()
            if not workout_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workout with id {workout_id} not found.",
                )

            if payload.id is not None:
                existing_set = db.get(SetORM, payload.id)
                if existing_set:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Set with id {payload.id} already exists.",
                    )

            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out before saving set.",
                )

            db_set = SetORM(
                **payload.model_dump(exclude_unset=True), workout_id=workout_id
            )
            db.add(db_set)
            db.commit()
            db.refresh(db_set)

            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out after saving set.",
                )
            return SetRead.model_validate(db_set)
        finally:
            _inflight -= 1


@app.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    global _inflight
    with time_budget(2.5) as exceeded:
        if workout_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="workout_id must be a positive integer.",
            )
        if _inflight >= _MAX_INFLIGHT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many concurrent requests. Please retry shortly.",
            )
        _inflight += 1
        try:
            workout = db.get(WorkoutORM, workout_id)
            if not workout:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workout with id {workout_id} not found.",
                )
            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out before deletion.",
                )
            db.delete(workout)
            db.commit()
            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out after deletion.",
                )
            return {"message": "Workout and associated sets deleted successfully."}
        finally:
            _inflight -= 1


@app.delete(
    "/workouts",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить все тренировки и подходы",
)
def delete_all_workouts(db: Session = Depends(get_db)):
    global _inflight
    with time_budget(4.0) as exceeded:
        if _inflight >= _MAX_INFLIGHT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many concurrent requests. Please retry shortly.",
            )
        _inflight += 1
        try:
            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out before deletion.",
                )
            db.query(SetORM).delete(synchronize_session=False)
            db.query(WorkoutORM).delete(synchronize_session=False)
            db.commit()
            if exceeded():
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Request timed out after deletion.",
                )
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        finally:
            _inflight -= 1
