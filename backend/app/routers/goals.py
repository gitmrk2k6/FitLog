from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.goal import AchievementPointOut, GoalIn, GoalOut
from app.services.goal_service import GoalNotFoundError, GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


class PeriodTypePath(str, Enum):
    weekly = "weekly"
    monthly = "monthly"


@router.get("", response_model=list[GoalOut])
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GoalService(db).list_goals(current_user.id)


@router.put("", response_model=GoalOut)
def set_goal(
    payload: GoalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GoalService(db).set_goal(current_user.id, payload)


@router.delete(
    "/{period_type}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_goal(
    period_type: PeriodTypePath,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        GoalService(db).delete_goal(current_user.id, period_type.value)
    except GoalNotFoundError as exc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get(
    "/{period_type}/trend", response_model=list[AchievementPointOut]
)
def goal_trend(
    period_type: PeriodTypePath,
    count: int = Query(8, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return GoalService(db).trend(
            current_user.id, period_type.value, count=count
        )
    except GoalNotFoundError as exc:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
