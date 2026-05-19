from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise


class ExerciseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_visible(self, user_id: int) -> list[Exercise]:
        """共通マスタ（created_by IS NULL）+ 自分が追加した種目。"""
        stmt = (
            select(Exercise)
            .where(or_(Exercise.created_by.is_(None), Exercise.created_by == user_id))
            .order_by(Exercise.id)
        )
        return list(self.db.scalars(stmt))

    def get(self, exercise_id: int) -> Exercise | None:
        return self.db.get(Exercise, exercise_id)

    def find_by_name(self, name: str, user_id: int) -> Exercise | None:
        stmt = select(Exercise).where(
            Exercise.name == name,
            or_(Exercise.created_by.is_(None), Exercise.created_by == user_id),
        )
        return self.db.scalars(stmt).first()

    def create(self, *, name: str, category: str, created_by: int) -> Exercise:
        ex = Exercise(name=name, category=category, created_by=created_by)
        self.db.add(ex)
        self.db.commit()
        self.db.refresh(ex)
        return ex
