from datetime import date
from decimal import Decimal

from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session
from sqlalchemy.types import Date

from app.models.goal import Goal
from app.models.workout import Workout
from app.models.workout_set import WorkoutSet


class GoalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- 目標 CRUD ----
    def get(self, user_id: int, period_type: str) -> Goal | None:
        stmt = select(Goal).where(
            Goal.user_id == user_id, Goal.period_type == period_type
        )
        return self.db.scalars(stmt).first()

    def list_by_user(self, user_id: int) -> list[Goal]:
        stmt = (
            select(Goal)
            .where(Goal.user_id == user_id)
            .order_by(Goal.period_type.asc())
        )
        return list(self.db.scalars(stmt))

    def add(
        self,
        *,
        user_id: int,
        period_type: str,
        metric: str,
        target_value: Decimal,
        start_on: date,
    ) -> Goal:
        goal = Goal(
            user_id=user_id,
            period_type=period_type,
            metric=metric,
            target_value=target_value,
            start_on=start_on,
        )
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update(
        self, goal: Goal, *, metric: str, target_value: Decimal
    ) -> Goal:
        goal.metric = metric
        goal.target_value = target_value
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: Goal) -> None:
        self.db.delete(goal)
        self.db.commit()

    # ---- 実績集計（PostgreSQL date_trunc で期間バケット化） ----
    def actuals_by_bucket(
        self,
        *,
        user_id: int,
        period_type: str,
        metric: str,
        start: date,
        end_exclusive: date,
    ) -> dict[date, Decimal]:
        """期間バケット開始日 -> 実績。記録の無いバケットは含まれない。

        - sessions: バケット内の実施日数（COUNT DISTINCT performed_on）
        - volume:   バケット内の総ボリューム（SUM weight_kg * reps）
        """
        # date_trunc('week'|'month', performed_on)::date がバケット開始日
        unit = "week" if period_type == "weekly" else "month"
        bucket = cast(
            func.date_trunc(unit, Workout.performed_on), Date
        ).label("bucket")
        in_window = (
            Workout.user_id == user_id,
            Workout.performed_on >= start,
            Workout.performed_on < end_exclusive,
        )
        if metric == "sessions":
            stmt = (
                select(
                    bucket,
                    func.count(func.distinct(Workout.performed_on)),
                )
                .where(*in_window)
                .group_by(bucket)
            )
        else:  # volume
            stmt = (
                select(
                    bucket,
                    func.coalesce(
                        func.sum(WorkoutSet.weight_kg * WorkoutSet.reps), 0
                    ),
                )
                .join(WorkoutSet, WorkoutSet.workout_id == Workout.id)
                .where(*in_window)
                .group_by(bucket)
            )
        return {b: Decimal(v) for b, v in self.db.execute(stmt)}
