from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import messages
from app.core.goals import (
    achievement_rate,
    is_achieved,
    next_period_start,
    period_start,
    recent_period_starts,
)
from app.models.goal import Goal
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import (
    AchievementOut,
    AchievementPointOut,
    GoalIn,
    GoalOut,
)


class GoalNotFoundError(Exception):
    """対象 period_type の目標が未設定。"""


class GoalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = GoalRepository(db)

    # ---- 目標設定（同一 period_type は1件＝upsert） ----
    def set_goal(self, user_id: int, payload: GoalIn) -> GoalOut:
        existing = self.repo.get(user_id, payload.period_type)
        if existing is not None:
            goal = self.repo.update(
                existing,
                metric=payload.metric,
                target_value=payload.target_value,
            )
            return GoalOut.model_validate(goal)
        try:
            goal = self.repo.add(
                user_id=user_id,
                period_type=payload.period_type,
                metric=payload.metric,
                target_value=payload.target_value,
                start_on=date.today(),
            )
        except IntegrityError as exc:  # 競合: 同時設定で UNIQUE 衝突
            self.db.rollback()
            current = self.repo.get(user_id, payload.period_type)
            if current is None:
                raise exc
            goal = self.repo.update(
                current,
                metric=payload.metric,
                target_value=payload.target_value,
            )
        return GoalOut.model_validate(goal)

    def list_goals(self, user_id: int) -> list[GoalOut]:
        return [
            GoalOut.model_validate(g) for g in self.repo.list_by_user(user_id)
        ]

    def delete_goal(self, user_id: int, period_type: str) -> None:
        goal = self.repo.get(user_id, period_type)
        if goal is None:
            raise GoalNotFoundError(messages.GOAL_NOT_FOUND)
        self.repo.delete(goal)

    # ---- 現在期間（今週/今月）の達成率 ----
    def current_achievements(
        self, user_id: int, ref: date | None = None
    ) -> list[AchievementOut]:
        ref = ref or date.today()
        out: list[AchievementOut] = []
        for g in self.repo.list_by_user(user_id):
            start = period_start(g.period_type, ref)
            end = next_period_start(g.period_type, start)
            actuals = self.repo.actuals_by_bucket(
                user_id=user_id,
                period_type=g.period_type,
                metric=g.metric,
                start=start,
                end_exclusive=end,
            )
            actual = actuals.get(start, Decimal(0))
            out.append(
                AchievementOut(
                    period_type=g.period_type,
                    metric=g.metric,
                    target_value=g.target_value,
                    actual=actual,
                    rate=achievement_rate(actual, g.target_value),
                    achieved=is_achieved(actual, g.target_value),
                    period_start=start,
                    period_end=end,
                )
            )
        return out

    # ---- 達成率の推移（週次/月次グラフ） ----
    def trend(
        self,
        user_id: int,
        period_type: str,
        *,
        count: int,
        ref: date | None = None,
    ) -> list[AchievementPointOut]:
        ref = ref or date.today()
        goal: Goal | None = self.repo.get(user_id, period_type)
        if goal is None:
            raise GoalNotFoundError(messages.GOAL_NOT_FOUND)
        starts = recent_period_starts(period_type, ref, count)
        window_end = next_period_start(period_type, starts[-1])
        actuals = self.repo.actuals_by_bucket(
            user_id=user_id,
            period_type=period_type,
            metric=goal.metric,
            start=starts[0],
            end_exclusive=window_end,
        )
        points: list[AchievementPointOut] = []
        for s in starts:
            actual = actuals.get(s, Decimal(0))
            points.append(
                AchievementPointOut(
                    period_start=s,
                    actual=actual,
                    target_value=goal.target_value,
                    rate=achievement_rate(actual, goal.target_value),
                    achieved=is_achieved(actual, goal.target_value),
                )
            )
        return points
