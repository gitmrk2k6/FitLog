from datetime import date

from sqlalchemy.orm import Session

from app.core.streak import current_streak, heatmap_start, longest_streak
from app.repositories.workout_repository import WorkoutRepository
from app.schemas.dashboard import HeatmapCell, StreakOut


class StatsService:
    """F-08 ストリーク / ヒートマップ。

    集計の起点日 ref を注入可能にし（API は当日）テストを決定的にする。
    """

    def __init__(self, db: Session) -> None:
        self.repo = WorkoutRepository(db)

    def streak(self, user_id: int, ref: date | None = None) -> StreakOut:
        today = ref or date.today()
        dates = self.repo.distinct_performed_dates(user_id)
        return StreakOut(
            current=current_streak(dates, today),
            longest=longest_streak(dates),
        )

    def heatmap(
        self, user_id: int, *, months: int, ref: date | None = None
    ) -> list[HeatmapCell]:
        today = ref or date.today()
        start = heatmap_start(today, months)
        rows = self.repo.daily_volume_series(user_id, start, today)
        return [HeatmapCell(date=d, volume=v) for d, v in rows]
