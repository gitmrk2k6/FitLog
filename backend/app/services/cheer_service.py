from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import messages
from app.repositories.cheer_repository import CheerRepository
from app.repositories.workout_repository import WorkoutRepository
from app.schemas.social import CheerStateOut


class WorkoutNotFoundError(Exception):
    """対象記録が存在しない。"""


class CannotCheerOwnWorkoutError(Exception):
    """自分の記録にはナイストレ不可（F-04: 投稿者本人以外）。"""


class AlreadyCheeredError(Exception):
    """同一ユーザー・同一記録への重複ナイストレ。"""


class NotCheeredError(Exception):
    """未付与の記録を解除しようとした。"""


class CheerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CheerRepository(db)
        self.workouts = WorkoutRepository(db)

    def _target(self, workout_id: int, user_id: int):
        workout = self.workouts.get(workout_id)
        if workout is None:
            raise WorkoutNotFoundError(messages.WORKOUT_NOT_FOUND)
        if workout.user_id == user_id:
            raise CannotCheerOwnWorkoutError(messages.CANNOT_CHEER_OWN)
        return workout

    def add(self, user_id: int, workout_id: int) -> CheerStateOut:
        self._target(workout_id, user_id)
        if self.repo.get(workout_id, user_id) is not None:
            raise AlreadyCheeredError(messages.ALREADY_CHEERED)
        try:
            self.repo.add(workout_id, user_id)
        except IntegrityError as exc:  # 競合時の重複（UNIQUE制約）
            self.db.rollback()
            raise AlreadyCheeredError(messages.ALREADY_CHEERED) from exc
        return CheerStateOut(
            cheers_count=self.repo.count(workout_id), cheered_by_me=True
        )

    def remove(self, user_id: int, workout_id: int) -> None:
        self._target(workout_id, user_id)
        cheer = self.repo.get(workout_id, user_id)
        if cheer is None:
            raise NotCheeredError(messages.NOT_CHEERED)
        self.repo.delete(cheer)
