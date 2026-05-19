from collections.abc import Sequence
from decimal import Decimal

from datetime import date

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.advice import Advice
from app.models.cheer import Cheer
from app.models.exercise import Exercise
from app.models.workout import Workout
from app.models.workout_set import WorkoutSet


class WorkoutRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- 取得 ----
    def get(self, workout_id: int) -> Workout | None:
        return self.db.get(Workout, workout_id)

    def list_by_user(
        self, user_id: int, *, limit: int, offset: int
    ) -> list[Workout]:
        stmt = (
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.performed_on.desc(), Workout.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt))

    def list_by_users(
        self, user_ids: Sequence[int], *, limit: int, offset: int
    ) -> list[Workout]:
        """複数ユーザーの記録を実施日降順で（F-06 フォロー中フィード）。"""
        if not user_ids:
            return []
        stmt = (
            select(Workout)
            .where(Workout.user_id.in_(user_ids))
            .order_by(Workout.performed_on.desc(), Workout.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt))

    def sets_with_exercise_name(
        self, workout_id: int
    ) -> list[tuple[WorkoutSet, str]]:
        stmt = (
            select(WorkoutSet, Exercise.name)
            .join(Exercise, Exercise.id == WorkoutSet.exercise_id)
            .where(WorkoutSet.workout_id == workout_id)
            .order_by(WorkoutSet.id)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt)]

    # ---- 集計（一覧の N+1 回避用にまとめて取得） ----
    def set_aggregates(
        self, workout_ids: Sequence[int]
    ) -> dict[int, tuple[int, int, Decimal]]:
        """workout_id -> (種目数, セット数, 総ボリューム)。"""
        if not workout_ids:
            return {}
        stmt = (
            select(
                WorkoutSet.workout_id,
                func.count(func.distinct(WorkoutSet.exercise_id)),
                func.count(WorkoutSet.id),
                func.coalesce(
                    func.sum(WorkoutSet.weight_kg * WorkoutSet.reps), 0
                ),
            )
            .where(WorkoutSet.workout_id.in_(workout_ids))
            .group_by(WorkoutSet.workout_id)
        )
        return {
            wid: (ex_count, set_count, Decimal(total))
            for wid, ex_count, set_count, total in self.db.execute(stmt)
        }

    def _count_by_workout(
        self, model, workout_ids: Sequence[int]
    ) -> dict[int, int]:
        if not workout_ids:
            return {}
        stmt = (
            select(model.workout_id, func.count(model.id))
            .where(model.workout_id.in_(workout_ids))
            .group_by(model.workout_id)
        )
        return {wid: cnt for wid, cnt in self.db.execute(stmt)}

    def cheer_counts(self, workout_ids: Sequence[int]) -> dict[int, int]:
        return self._count_by_workout(Cheer, workout_ids)

    def advice_counts(self, workout_ids: Sequence[int]) -> dict[int, int]:
        return self._count_by_workout(Advice, workout_ids)

    # ---- 作成 / 更新 / 削除 ----
    def create(
        self,
        *,
        user_id: int,
        performed_on,
        memo: str | None,
        photo_url: str | None,
        sets: list[dict],
    ) -> Workout:
        workout = Workout(
            user_id=user_id,
            performed_on=performed_on,
            memo=memo,
            photo_url=photo_url,
        )
        self.db.add(workout)
        self.db.flush()  # workout.id 確定
        for s in sets:
            self.db.add(
                WorkoutSet(
                    workout_id=workout.id,
                    exercise_id=s["exercise_id"],
                    set_no=s["set_no"],
                    weight_kg=s["weight_kg"],
                    reps=s["reps"],
                    is_pr=False,  # F-09 で判定（本Increment範囲外）
                )
            )
        self.db.commit()
        self.db.refresh(workout)
        return workout

    def replace_sets(self, workout: Workout, sets: list[dict]) -> None:
        self.db.query(WorkoutSet).filter(
            WorkoutSet.workout_id == workout.id
        ).delete(synchronize_session=False)
        for s in sets:
            self.db.add(
                WorkoutSet(
                    workout_id=workout.id,
                    exercise_id=s["exercise_id"],
                    set_no=s["set_no"],
                    weight_kg=s["weight_kg"],
                    reps=s["reps"],
                    is_pr=False,
                )
            )

    def commit_refresh(self, workout: Workout) -> Workout:
        self.db.commit()
        self.db.refresh(workout)
        return workout

    def delete(self, workout: Workout) -> None:
        # 紐づくセット/ナイストレ/アドバイスは FK ON DELETE CASCADE で連動削除
        self.db.delete(workout)
        self.db.commit()

    # ---- F-08 ストリーク / ヒートマップ ----
    def distinct_performed_dates(self, user_id: int) -> list[date]:
        """ユーザーの実施日（重複なし）。ストリーク算出の入力。"""
        stmt = (
            select(Workout.performed_on)
            .where(Workout.user_id == user_id)
            .distinct()
        )
        return list(self.db.scalars(stmt))

    def daily_volume_series(
        self, user_id: int, start: date, end: date
    ) -> list[tuple[date, Decimal]]:
        """[start, end] の全日について日別総ボリューム。

        PostgreSQL generate_series で日付軸を生成し記録を LEFT JOIN するため、
        記録の無い日も volume=0 の行として欠損なく返る（GitHub風グリッド用）。
        """
        sql = text(
            """
            SELECT gs.d::date AS day,
                   COALESCE(SUM(ws.weight_kg * ws.reps), 0) AS volume
            FROM generate_series(:start, :end, interval '1 day') AS gs(d)
            LEFT JOIN workouts w
              ON w.performed_on = gs.d::date AND w.user_id = :uid
            LEFT JOIN workout_sets ws ON ws.workout_id = w.id
            GROUP BY gs.d
            ORDER BY gs.d
            """
        )
        rows = self.db.execute(
            sql, {"start": start, "end": end, "uid": user_id}
        )
        return [(r.day, Decimal(r.volume)) for r in rows]
