from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.workout import WorkoutSummary
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=list[WorkoutSummary])
def get_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """フォロー中ユーザーの記録を実施日降順で集約（F-06）。"""
    return WorkoutService(db).feed(
        current_user.id, limit=limit, offset=offset
    )
