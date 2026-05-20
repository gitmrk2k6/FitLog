from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.social import CheerStateOut
from app.services.cheer_service import (
    AlreadyCheeredError,
    CannotCheerOwnWorkoutError,
    CheerService,
    NotCheeredError,
    WorkoutNotFoundError,
)

router = APIRouter(prefix="/workouts/{workout_id}/cheers", tags=["cheers"])


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, WorkoutNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, CannotCheerOwnWorkoutError):
        return HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, AlreadyCheeredError):
        return HTTPException(status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(exc, NotCheeredError):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    raise exc


@router.post(
    "",
    response_model=CheerStateOut,
    status_code=status.HTTP_201_CREATED,
    summary="ナイストレを付与",
    description="指定ワークアウットにナイストレ（いいね）を付与します。自分のワークアウットには付与できません（F-04）。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "自分のワークアウットへのナイストレは不可"},
        404: {"description": "ワークアウットが見つからない"},
        409: {"description": "既にナイストレ済み"},
    },
)
def add_cheer(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return CheerService(db).add(current_user.id, workout_id)
    except (
        WorkoutNotFoundError,
        CannotCheerOwnWorkoutError,
        AlreadyCheeredError,
    ) as exc:
        raise _handle(exc) from exc


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ナイストレを解除",
    description="指定ワークアウットに付与済みのナイストレを解除します（F-04）。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "自分のワークアウットへの操作は不可"},
        404: {"description": "ワークアウットが見つからない、またはナイストレしていない"},
    },
)
def remove_cheer(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        CheerService(db).remove(current_user.id, workout_id)
    except (
        WorkoutNotFoundError,
        CannotCheerOwnWorkoutError,
        NotCheeredError,
    ) as exc:
        raise _handle(exc) from exc
