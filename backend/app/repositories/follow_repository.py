from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.follow import Follow
from app.models.user import User


class FollowRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, follower_id: int, following_id: int) -> Follow | None:
        stmt = select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id,
        )
        return self.db.scalars(stmt).first()

    def add(self, follower_id: int, following_id: int) -> Follow:
        follow = Follow(follower_id=follower_id, following_id=following_id)
        self.db.add(follow)
        self.db.commit()
        self.db.refresh(follow)
        return follow

    def delete(self, follow: Follow) -> None:
        self.db.delete(follow)
        self.db.commit()

    def following_count(self, user_id: int) -> int:
        stmt = select(func.count(Follow.id)).where(
            Follow.follower_id == user_id
        )
        return self.db.scalar(stmt) or 0

    def followers_count(self, user_id: int) -> int:
        stmt = select(func.count(Follow.id)).where(
            Follow.following_id == user_id
        )
        return self.db.scalar(stmt) or 0

    def following_user_ids(self, user_id: int) -> list[int]:
        """user_id がフォローしている following_id の一覧（フィード/状態判定用）。"""
        stmt = select(Follow.following_id).where(
            Follow.follower_id == user_id
        )
        return list(self.db.scalars(stmt))

    def following_subset(
        self, follower_id: int, candidate_ids: Sequence[int]
    ) -> set[int]:
        """candidate_ids のうち follower_id がフォロー済みの集合（N+1回避）。"""
        if not candidate_ids:
            return set()
        stmt = select(Follow.following_id).where(
            Follow.follower_id == follower_id,
            Follow.following_id.in_(candidate_ids),
        )
        return set(self.db.scalars(stmt))

    def list_following(self, user_id: int) -> list[User]:
        """user_id がフォローしているユーザー（新しい順）。"""
        stmt = (
            select(User)
            .join(Follow, Follow.following_id == User.id)
            .where(Follow.follower_id == user_id)
            .order_by(Follow.created_at.desc(), Follow.id.desc())
        )
        return list(self.db.scalars(stmt))

    def list_followers(self, user_id: int) -> list[User]:
        """user_id をフォローしているユーザー（新しい順）。"""
        stmt = (
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.following_id == user_id)
            .order_by(Follow.created_at.desc(), Follow.id.desc())
        )
        return list(self.db.scalars(stmt))
