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


@router.get(
    "",
    response_model=list[GoalOut],
    summary="目標一覧取得（週次・月次）",
    description="ログインユーザーが設定した週次・月次の目標一覧を返します（F-07）。",
    responses={
        401: {"description": "未認証"},
    },
)
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GoalService(db).list_goals(current_user.id)


@router.put(
    "",
    response_model=GoalOut,
    summary="目標を設定（upsert）",
    description="期間種別・指標・目標値で目標を設定します。既存の目標がある場合は上書き（upsert）します（F-07）。",
    responses={
        401: {"description": "未認証"},
    },
)
def set_goal(
    payload: GoalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GoalService(db).set_goal(current_user.id, payload)


@router.delete(
    "/{period_type}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="目標を削除",
    description="指定した期間種別（weekly / monthly）の目標を削除します（F-07）。",
    responses={
        401: {"description": "未認証"},
        404: {"description": "指定した期間の目標が設定されていない"},
    },
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
    "/{period_type}/trend",
    response_model=list[AchievementPointOut],
    summary="目標達成率の推移データ取得",
    description="指定した期間種別の過去N期間分（デフォルト8）の達成率推移を返します。グラフ表示に使用します（F-07）。",
    responses={
        401: {"description": "未認証"},
        404: {"description": "指定した期間の目標が設定されていない"},
    },
)
def goal_trend(
    period_type: PeriodTypePath,
    count: int = Query(8, ge=1, le=24, description="取得する期間数（1〜24、デフォルト8）"),
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
