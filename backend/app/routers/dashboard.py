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


@router.get(
    "/personal-records",
    response_model=list[PersonalRecordOut],
    summary="種目別の自己ベスト一覧取得",
    description="ログインユーザーの種目別自己ベスト（最大重量・ベストボリューム・推定1RM）を返します（F-09）。",
    responses={
        401: {"description": "未認証"},
    },
)
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


@router.get(
    "/achievements",
    response_model=list[AchievementOut],
    summary="現在期間の目標達成率取得",
    description="今週・今月の目標達成率（実績値・達成率・達成済みフラグ）を返します（F-07）。",
    responses={
        401: {"description": "未認証"},
    },
)
def achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return GoalService(db).current_achievements(current_user.id)


@router.get(
    "/streak",
    response_model=StreakOut,
    summary="連続記録日数（現在・最長）取得",
    description="ログインユーザーの現在の連続記録日数と過去最長の連続記録日数を返します（F-08）。",
    responses={
        401: {"description": "未認証"},
    },
)
def streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return StatsService(db).streak(current_user.id)


@router.get(
    "/heatmap",
    response_model=list[HeatmapCell],
    summary="日別ボリュームヒートマップデータ取得",
    description="直近Nか月（デフォルト5）の日別ボリュームを返します。記録なし日も volume=0 で含まれます（F-08）。",
    responses={
        401: {"description": "未認証"},
    },
)
def heatmap(
    months: int = Query(5, ge=1, le=12, description="取得する月数（1〜12、デフォルト5）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return StatsService(db).heatmap(current_user.id, months=months)
