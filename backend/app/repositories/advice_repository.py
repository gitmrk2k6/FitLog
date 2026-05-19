from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.advice import Advice
from app.models.user import User


class AdviceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, advice_id: int) -> Advice | None:
        return self.db.get(Advice, advice_id)

    def add(self, workout_id: int, user_id: int, content: str) -> Advice:
        advice = Advice(
            workout_id=workout_id, user_id=user_id, content=content
        )
        self.db.add(advice)
        self.db.commit()
        self.db.refresh(advice)
        return advice

    def delete(self, advice: Advice) -> None:
        self.db.delete(advice)
        self.db.commit()

    def list_with_username(
        self, workout_id: int
    ) -> list[tuple[Advice, str]]:
        """(Advice, 投稿者username) を created_at 昇順で返す（要件: 昇順表示）。"""
        stmt = (
            select(Advice, User.username)
            .join(User, User.id == Advice.user_id)
            .where(Advice.workout_id == workout_id)
            .order_by(Advice.created_at.asc(), Advice.id.asc())
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt)]
