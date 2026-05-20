from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.social import AdviceCreate, AdviceOut
from app.services.advice_service import (
    AdviceNotFoundError,
    AdviceService,
    CannotAdviseOwnWorkoutError,
    NotAdviceOwnerError,
    WorkoutNotFoundError,
)

router = APIRouter(tags=["advices"])


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, (WorkoutNotFoundError, AdviceNotFoundError)):
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, (CannotAdviseOwnWorkoutError, NotAdviceOwnerError)):
        return HTTPException(status.HTTP_403_FORBIDDEN, detail=str(exc))
    raise exc


@router.post(
    "/workouts/{workout_id}/advices",
    response_model=AdviceOut,
    status_code=status.HTTP_201_CREATED,
    summary="アドバイスを投稿",
    description="指定ワークアウットにアドバイスコメントを投稿します。自分のワークアウットへは投稿できません（F-05）。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "自分のワークアウットへのアドバイスは不可"},
        404: {"description": "ワークアウットが見つからない"},
    },
)
def create_advice(
    workout_id: int,
    payload: AdviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AdviceService(db).create(
            current_user.id, workout_id, payload.content
        )
    except (WorkoutNotFoundError, CannotAdviseOwnWorkoutError) as exc:
        raise _handle(exc) from exc


@router.get(
    "/workouts/{workout_id}/advices",
    response_model=list[AdviceOut],
    summary="ワークアウットのアドバイス一覧取得",
    description="指定ワークアウットに投稿されたアドバイスを投稿日時昇順で返します（F-05）。",
    responses={
        401: {"description": "未認証"},
        404: {"description": "ワークアウットが見つからない"},
    },
)
def list_advices(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return AdviceService(db).list_for_workout(workout_id)
    except WorkoutNotFoundError as exc:
        raise _handle(exc) from exc


@router.delete(
    "/advices/{advice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="アドバイスを削除（投稿者のみ可）",
    description="自分が投稿したアドバイスを削除します。他ユーザーのアドバイスは削除できません（F-05）。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "他ユーザーのアドバイスへの操作は不可"},
        404: {"description": "アドバイスが見つからない"},
    },
)
def delete_advice(
    advice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        AdviceService(db).delete(current_user.id, advice_id)
    except (AdviceNotFoundError, NotAdviceOwnerError) as exc:
        raise _handle(exc) from exc
