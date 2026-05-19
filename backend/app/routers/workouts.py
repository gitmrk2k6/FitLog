from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.workout import (
    WorkoutCreate,
    WorkoutDetail,
    WorkoutSummary,
    WorkoutUpdate,
)
from app.services.workout_service import (
    ExerciseNotAccessibleError,
    NotWorkoutOwnerError,
    WorkoutNotFoundError,
    WorkoutService,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, WorkoutNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, NotWorkoutOwnerError):
        return HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, ExerciseNotAccessibleError):
        return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    raise exc


@router.post(
    "", response_model=WorkoutDetail, status_code=status.HTTP_201_CREATED
)
def create_workout(
    payload: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return WorkoutService(db).create(current_user.id, payload)
    except ExerciseNotAccessibleError as exc:
        raise _handle(exc) from exc


@router.get("", response_model=list[WorkoutSummary])
def list_workouts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WorkoutService(db).list_for_user(
        current_user.id, limit=limit, offset=offset
    )


@router.get("/{workout_id}", response_model=WorkoutDetail)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return WorkoutService(db).get_detail(current_user.id, workout_id)
    except (WorkoutNotFoundError, NotWorkoutOwnerError) as exc:
        raise _handle(exc) from exc


@router.patch("/{workout_id}", response_model=WorkoutDetail)
def update_workout(
    workout_id: int,
    payload: WorkoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return WorkoutService(db).update(current_user.id, workout_id, payload)
    except (
        WorkoutNotFoundError,
        NotWorkoutOwnerError,
        ExerciseNotAccessibleError,
    ) as exc:
        raise _handle(exc) from exc


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        WorkoutService(db).delete(current_user.id, workout_id)
    except (WorkoutNotFoundError, NotWorkoutOwnerError) as exc:
        raise _handle(exc) from exc
