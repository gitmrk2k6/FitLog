from sqlalchemy.orm import Session

from app.core import messages
from app.repositories.advice_repository import AdviceRepository
from app.repositories.workout_repository import WorkoutRepository
from app.schemas.social import AdviceOut


class WorkoutNotFoundError(Exception):
    """対象記録が存在しない。"""


class CannotAdviseOwnWorkoutError(Exception):
    """自分の記録にはアドバイス不可（F-05: 他ユーザーの記録に）。"""


class AdviceNotFoundError(Exception):
    """対象アドバイスが存在しない。"""


class NotAdviceOwnerError(Exception):
    """他人のアドバイスを削除しようとした。"""


class AdviceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AdviceRepository(db)
        self.workouts = WorkoutRepository(db)

    def create(
        self, user_id: int, workout_id: int, content: str
    ) -> AdviceOut:
        workout = self.workouts.get(workout_id)
        if workout is None:
            raise WorkoutNotFoundError(messages.WORKOUT_NOT_FOUND)
        if workout.user_id == user_id:
            raise CannotAdviseOwnWorkoutError(messages.CANNOT_ADVISE_OWN)
        advice = self.repo.add(workout_id, user_id, content)
        # username を含めて返すため一覧経由で整形
        return self._find_out(workout_id, advice.id)

    def list_for_workout(self, workout_id: int) -> list[AdviceOut]:
        workout = self.workouts.get(workout_id)
        if workout is None:
            raise WorkoutNotFoundError(messages.WORKOUT_NOT_FOUND)
        return [
            AdviceOut(
                id=a.id,
                workout_id=a.workout_id,
                user_id=a.user_id,
                username=username,
                content=a.content,
                created_at=a.created_at,
            )
            for a, username in self.repo.list_with_username(workout_id)
        ]

    def delete(self, user_id: int, advice_id: int) -> None:
        advice = self.repo.get(advice_id)
        if advice is None:
            raise AdviceNotFoundError(messages.ADVICE_NOT_FOUND)
        if advice.user_id != user_id:
            raise NotAdviceOwnerError(messages.NOT_ADVICE_OWNER)
        self.repo.delete(advice)

    def _find_out(self, workout_id: int, advice_id: int) -> AdviceOut:
        for out in self.list_for_workout(workout_id):
            if out.id == advice_id:
                return out
        raise AdviceNotFoundError(messages.ADVICE_NOT_FOUND)
