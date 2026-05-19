from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.dashboard import HeatmapCell, PersonalRecordOut, StreakOut
from app.schemas.goal import AchievementOut
from app.services.goal_service import GoalService
from app.services.personal_record_service import PersonalRecordService
from app.services.stats_service import StatsService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/personal-records", response_model=list[PersonalRecordOut])
def personal_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = PersonalRecordService(db).list_for_user(current_user.id)
    return [
        PersonalRecordOut(
            exercise_id=pr.exercise_id,
            exercise_name=name,
            max_weight_kg=pr.max_weight_kg,
            max_weight_reps=pr.max_weight_reps,
            max_weight_on=pr.max_weight_on,
            best_volume=pr.best_volume,
            best_volume_on=pr.best_volume_on,
            best_est_1rm=pr.best_est_1rm,
            best_1rm_weight_kg=pr.best_1rm_weight_kg,
            best_1rm_reps=pr.best_1rm_reps,
            best_1rm_on=pr.best_1rm_on,
        )
        for pr, name in rows
    ]


@router.get("/achievements", response_model=list[AchievementOut])
def achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """現在期間（今週/今月）の目標達成率（F-07）。"""
    return GoalService(db).current_achievements(current_user.id)


@router.get("/streak", response_model=StreakOut)
def streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """連続記録日数（現在・最長）（F-08）。"""
    return StatsService(db).streak(current_user.id)


@router.get("/heatmap", response_model=list[HeatmapCell])
def heatmap(
    months: int = Query(5, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """直近Nか月の日別ボリューム（記録なし日も0で出力）（F-08）。"""
    return StatsService(db).heatmap(current_user.id, months=months)
