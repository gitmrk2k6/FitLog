from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """users テーブルへの純粋なデータアクセス層。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def create(self, *, username: str, email: str, password_digest: str) -> User:
        user = User(
            username=username, email=email, password_digest=password_digest
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
