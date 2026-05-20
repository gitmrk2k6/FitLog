from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.workout import WorkoutSummary
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get(
    "",
    response_model=list[WorkoutSummary],
    summary="フォロー中ユーザーのワークアウットフィード取得",
    description="フォロー中のユーザーが投稿したワークアウットを実施日降順で返します。`limit` / `offset` でページネーション可能です（F-06）。",
    responses={
        401: {"description": "未認証"},
    },
)
def get_feed(
    limit: int = Query(20, ge=1, le=100, description="取得件数上限（1〜100、デフォルト20）"),
    offset: int = Query(0, ge=0, description="取得オフセット（デフォルト0）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return WorkoutService(db).feed(
        current_user.id, limit=limit, offset=offset
    )
