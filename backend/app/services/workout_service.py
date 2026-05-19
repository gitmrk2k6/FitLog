from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.workout_repository import WorkoutRepository
from app.schemas.workout import (
    WorkoutCreate,
    WorkoutDetail,
    WorkoutSetOut,
    WorkoutSummary,
    WorkoutUpdate,
)


class WorkoutNotFoundError(Exception):
    """記録が存在しない。"""


class NotWorkoutOwnerError(Exception):
    """他人の記録を操作しようとした。"""


class ExerciseNotAccessibleError(Exception):
    """指定の種目が存在しない or 参照不可。"""


class WorkoutService:
    def __init__(self, db: Session) -> None:
        self.repo = WorkoutRepository(db)
        self.exercises = ExerciseRepository(db)

    # ---- 入力の種目検証 & フラットなセット列の構築 ----
    def _build_sets(self, user_id: int, payload: WorkoutCreate) -> list[dict]:
        flat: list[dict] = []
        for block in payload.exercises:
            ex = self.exercises.get(block.exercise_id)
            if ex is None or (
                ex.created_by is not None and ex.created_by != user_id
            ):
                raise ExerciseNotAccessibleError(
                    f"種目ID {block.exercise_id} は利用できません"
                )
            # set_no は種目ブロック内で1始まり
            for i, s in enumerate(block.sets, start=1):
                flat.append(
                    {
                        "exercise_id": block.exercise_id,
                        "set_no": i,
                        "weight_kg": s.weight_kg,
                        "reps": s.reps,
                    }
                )
        return flat

    def _owned(self, workout_id: int, user_id: int) -> Workout:
        workout = self.repo.get(workout_id)
        if workout is None:
            raise WorkoutNotFoundError("記録が見つかりません")
        if workout.user_id != user_id:
            raise NotWorkoutOwnerError("この記録を操作する権限がありません")
        return workout

    # ---- F-02 作成 ----
    def create(self, user_id: int, payload: WorkoutCreate) -> WorkoutDetail:
        sets = self._build_sets(user_id, payload)
        workout = self.repo.create(
            user_id=user_id,
            performed_on=payload.performed_on,
            memo=payload.memo,
            photo_url=payload.photo_url,
            sets=sets,
        )
        return self._to_detail(workout)

    # ---- F-02 編集（全置換） ----
    def update(
        self, user_id: int, workout_id: int, payload: WorkoutUpdate
    ) -> WorkoutDetail:
        workout = self._owned(workout_id, user_id)
        sets = self._build_sets(user_id, payload)
        workout.performed_on = payload.performed_on
        workout.memo = payload.memo
        workout.photo_url = payload.photo_url
        self.repo.replace_sets(workout, sets)
        self.repo.commit_refresh(workout)
        return self._to_detail(workout)

    # ---- F-02 削除 ----
    def delete(self, user_id: int, workout_id: int) -> None:
        workout = self._owned(workout_id, user_id)
        self.repo.delete(workout)

    # ---- F-03 一覧 ----
    def list_for_user(
        self, user_id: int, *, limit: int, offset: int
    ) -> list[WorkoutSummary]:
        workouts = self.repo.list_by_user(user_id, limit=limit, offset=offset)
        ids = [w.id for w in workouts]
        set_agg = self.repo.set_aggregates(ids)
        cheers = self.repo.cheer_counts(ids)
        advices = self.repo.advice_counts(ids)
        result: list[WorkoutSummary] = []
        for w in workouts:
            ex_count, set_count, total = set_agg.get(
                w.id, (0, 0, Decimal(0))
            )
            result.append(
                WorkoutSummary(
                    id=w.id,
                    user_id=w.user_id,
                    performed_on=w.performed_on,
                    memo=w.memo,
                    photo_url=w.photo_url,
                    exercise_count=ex_count,
                    set_count=set_count,
                    total_volume=total,
                    cheers_count=cheers.get(w.id, 0),
                    advices_count=advices.get(w.id, 0),
                    created_at=w.created_at,
                )
            )
        return result

    # ---- F-03 詳細（本人のみ。他者公開は F-06 で拡張予定） ----
    def get_detail(self, user_id: int, workout_id: int) -> WorkoutDetail:
        workout = self._owned(workout_id, user_id)
        return self._to_detail(workout)

    def _to_detail(self, workout: Workout) -> WorkoutDetail:
        rows = self.repo.sets_with_exercise_name(workout.id)
        sets = [
            WorkoutSetOut(
                id=ws.id,
                exercise_id=ws.exercise_id,
                exercise_name=name,
                set_no=ws.set_no,
                weight_kg=ws.weight_kg,
                reps=ws.reps,
                is_pr=ws.is_pr,
            )
            for ws, name in rows
        ]
        total = sum((s.weight_kg * s.reps for s in sets), Decimal(0))
        ids = [workout.id]
        cheers = self.repo.cheer_counts(ids).get(workout.id, 0)
        advices = self.repo.advice_counts(ids).get(workout.id, 0)
        return WorkoutDetail(
            id=workout.id,
            user_id=workout.user_id,
            performed_on=workout.performed_on,
            memo=workout.memo,
            photo_url=workout.photo_url,
            sets=sets,
            total_volume=total,
            cheers_count=cheers,
            advices_count=advices,
            created_at=workout.created_at,
            updated_at=workout.updated_at,
        )
