from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.repositories.exercise_repository import ExerciseRepository


class DuplicateExerciseError(Exception):
    """同名の種目が既に存在する（共通 or 自分の追加分）。"""


class ExerciseService:
    def __init__(self, db: Session) -> None:
        self.repo = ExerciseRepository(db)

    def list_for_user(self, user_id: int) -> list[Exercise]:
        return self.repo.list_visible(user_id)

    def create_custom(
        self, *, user_id: int, name: str, category: str
    ) -> Exercise:
        if self.repo.find_by_name(name, user_id):
            raise DuplicateExerciseError(f"種目「{name}」は既に存在します")
        return self.repo.create(name=name, category=category, created_by=user_id)
