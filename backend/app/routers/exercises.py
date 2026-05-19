from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.exercise import ExerciseCreate, ExerciseOut
from app.services.exercise_service import DuplicateExerciseError, ExerciseService

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseOut])
def list_exercises(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ExerciseService(db).list_for_user(current_user.id)


@router.post(
    "", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED
)
def create_exercise(
    payload: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ExerciseService(db).create_custom(
            user_id=current_user.id,
            name=payload.name,
            category=payload.category,
        )
    except DuplicateExerciseError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
