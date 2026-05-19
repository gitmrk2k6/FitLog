from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.pr import PrMetrics, SetRow
from app.models.exercise import Exercise
from app.models.personal_record import PersonalRecord
from app.models.workout import Workout
from app.models.workout_set import WorkoutSet


class PersonalRecordRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def user_set_rows(
        self,
        user_id: int,
        exercise_id: int,
        *,
        exclude_workout_id: int | None = None,
    ) -> list[SetRow]:
        """ある種目について、そのユーザーの全セット（重量>0）を返す。

        exclude_workout_id を指定すると「今回を除く過去最高」を求められる。
        """
        stmt = (
            select(
                WorkoutSet.id,
                WorkoutSet.exercise_id,
                Workout.id,
                Workout.performed_on,
                WorkoutSet.weight_kg,
                WorkoutSet.reps,
            )
            .join(Workout, Workout.id == WorkoutSet.workout_id)
            .where(
                Workout.user_id == user_id,
                WorkoutSet.exercise_id == exercise_id,
                WorkoutSet.weight_kg > 0,
            )
        )
        if exclude_workout_id is not None:
            stmt = stmt.where(Workout.id != exclude_workout_id)
        return [
            SetRow(
                set_id=r[0],
                exercise_id=r[1],
                workout_id=r[2],
                performed_on=r[3],
                weight_kg=r[4],
                reps=r[5],
            )
            for r in self.db.execute(stmt)
        ]

    def workout_set_brief(
        self, workout_id: int
    ) -> list[tuple[int, int, Decimal]]:
        """指定記録のセット (set_id, exercise_id, weight_kg)。"""
        stmt = select(
            WorkoutSet.id, WorkoutSet.exercise_id, WorkoutSet.weight_kg
        ).where(WorkoutSet.workout_id == workout_id)
        return [(r[0], r[1], r[2]) for r in self.db.execute(stmt)]

    def exercise_ids_in_workout(self, workout_id: int) -> list[int]:
        stmt = (
            select(WorkoutSet.exercise_id)
            .where(WorkoutSet.workout_id == workout_id)
            .distinct()
        )
        return [r[0] for r in self.db.execute(stmt)]

    def get(self, user_id: int, exercise_id: int) -> PersonalRecord | None:
        stmt = select(PersonalRecord).where(
            PersonalRecord.user_id == user_id,
            PersonalRecord.exercise_id == exercise_id,
        )
        return self.db.scalars(stmt).first()

    def upsert(
        self, user_id: int, exercise_id: int, m: PrMetrics
    ) -> PersonalRecord:
        row = self.get(user_id, exercise_id)
        if row is None:
            row = PersonalRecord(user_id=user_id, exercise_id=exercise_id)
            self.db.add(row)
        row.max_weight_kg = m.max_weight_kg
        row.max_weight_reps = m.max_weight_reps
        row.max_weight_set_id = m.max_weight_set_id
        row.max_weight_on = m.max_weight_on
        row.best_volume = m.best_volume
        row.best_volume_workout_id = m.best_volume_workout_id
        row.best_volume_on = m.best_volume_on
        row.best_est_1rm = m.best_est_1rm
        row.best_1rm_weight_kg = m.best_1rm_weight_kg
        row.best_1rm_reps = m.best_1rm_reps
        row.best_1rm_set_id = m.best_1rm_set_id
        row.best_1rm_on = m.best_1rm_on
        return row

    def delete_for(self, user_id: int, exercise_id: int) -> None:
        row = self.get(user_id, exercise_id)
        if row is not None:
            self.db.delete(row)

    def list_for_user(
        self, user_id: int
    ) -> list[tuple[PersonalRecord, str]]:
        stmt = (
            select(PersonalRecord, Exercise.name)
            .join(Exercise, Exercise.id == PersonalRecord.exercise_id)
            .where(PersonalRecord.user_id == user_id)
            .order_by(Exercise.id)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt)]

    def mark_sets_pr(self, set_ids: Sequence[int]) -> None:
        if not set_ids:
            return
        self.db.query(WorkoutSet).filter(
            WorkoutSet.id.in_(set_ids)
        ).update({WorkoutSet.is_pr: True}, synchronize_session=False)
