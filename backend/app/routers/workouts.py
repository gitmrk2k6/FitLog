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
    "",
    response_model=WorkoutDetail,
    status_code=status.HTTP_201_CREATED,
    summary="ワークアウット記録を作成",
    description="実施日・種目×セット構成・メモを指定してワークアウット記録を新規作成します。自己ベスト（PR）が更新された場合は `pr_updates` に指標が返ります（F-09）。",
    responses={
        401: {"description": "未認証"},
        422: {"description": "指定した種目IDにアクセス権限がない"},
    },
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


@router.get(
    "",
    response_model=list[WorkoutSummary],
    summary="自分のワークアウット一覧取得",
    description="ログインユーザー自身のワークアウット記録を実施日降順で返します（F-03）。`limit` / `offset` でページネーション可能です。",
    responses={
        401: {"description": "未認証"},
    },
)
def list_workouts(
    limit: int = Query(20, ge=1, le=100, description="取得件数上限（1〜100、デフォルト20）"),
    offset: int = Query(0, ge=0, description="取得オフセット（デフォルト0）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WorkoutService(db).list_for_user(
        current_user.id, limit=limit, offset=offset
    )


@router.get(
    "/{workout_id}",
    response_model=WorkoutDetail,
    summary="ワークアウット詳細取得",
    description="指定した ID のワークアウット記録の詳細（全セット・ボリューム・ナイストレ数・アドバイス数）を返します。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "他ユーザーのワークアウットへのアクセス"},
        404: {"description": "ワークアウットが見つからない"},
    },
)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return WorkoutService(db).get_detail(current_user.id, workout_id)
    except (WorkoutNotFoundError, NotWorkoutOwnerError) as exc:
        raise _handle(exc) from exc


@router.patch(
    "/{workout_id}",
    response_model=WorkoutDetail,
    summary="ワークアウット記録を更新（全置換）",
    description="実施日・種目構成・メモ・写真URLをまとめて差し替えます。部分更新は非対応です。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "他ユーザーのワークアウットへの操作"},
        404: {"description": "ワークアウットが見つからない"},
        422: {"description": "指定した種目IDにアクセス権限がない"},
    },
)
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


@router.delete(
    "/{workout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ワークアウット記録を削除",
    description="指定した ID のワークアウット記録（関連セット・写真含む）を完全に削除します。",
    responses={
        401: {"description": "未認証"},
        403: {"description": "他ユーザーのワークアウットへの操作"},
        404: {"description": "ワークアウットが見つからない"},
    },
)
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        WorkoutService(db).delete(current_user.id, workout_id)
    except (WorkoutNotFoundError, NotWorkoutOwnerError) as exc:
        raise _handle(exc) from exc
