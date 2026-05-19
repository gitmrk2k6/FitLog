from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.cheer import Cheer


class CheerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, workout_id: int, user_id: int) -> Cheer | None:
        stmt = select(Cheer).where(
            Cheer.workout_id == workout_id, Cheer.user_id == user_id
        )
        return self.db.scalars(stmt).first()

    def add(self, workout_id: int, user_id: int) -> Cheer:
        cheer = Cheer(workout_id=workout_id, user_id=user_id)
        self.db.add(cheer)
        self.db.commit()
        self.db.refresh(cheer)
        return cheer

    def delete(self, cheer: Cheer) -> None:
        self.db.delete(cheer)
        self.db.commit()

    def count(self, workout_id: int) -> int:
        stmt = select(func.count(Cheer.id)).where(
            Cheer.workout_id == workout_id
        )
        return self.db.scalar(stmt) or 0

    def cheered_workout_ids(
        self, user_id: int, workout_ids: Sequence[int]
    ) -> set[int]:
        """viewer が付与済みの workout_id 集合（一覧の N+1 回避用）。"""
        if not workout_ids:
            return set()
        stmt = select(Cheer.workout_id).where(
            Cheer.user_id == user_id, Cheer.workout_id.in_(workout_ids)
        )
        return set(self.db.scalars(stmt))
