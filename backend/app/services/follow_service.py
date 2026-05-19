from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import messages
from app.models.user import User
from app.repositories.follow_repository import FollowRepository
from app.repositories.user_repository import UserRepository
from app.schemas.follow import FollowStateOut, ProfileOut, UserBrief


class UserNotFoundError(Exception):
    """対象ユーザーが存在しない。"""


class CannotFollowSelfError(Exception):
    """自分自身をフォローしようとした（DB CHECK no_self_follow）。"""


class AlreadyFollowingError(Exception):
    """重複フォロー（UNIQUE uq_follows_pair）。"""


class NotFollowingError(Exception):
    """フォローしていない相手を解除しようとした。"""


class FollowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FollowRepository(db)
        self.users = UserRepository(db)

    def _require_user(self, user_id: int) -> User:
        user = self.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(messages.USER_NOT_FOUND)
        return user

    def _brief(
        self, user: User, viewer_id: int, following_ids: set[int]
    ) -> UserBrief:
        return UserBrief(
            id=user.id,
            username=user.username,
            profile_image_url=user.profile_image_url,
            bio=user.bio,
            is_following=user.id in following_ids,
            is_me=user.id == viewer_id,
        )

    # ---- フォロー ----
    def follow(self, follower_id: int, following_id: int) -> FollowStateOut:
        if follower_id == following_id:
            raise CannotFollowSelfError(messages.CANNOT_FOLLOW_SELF)
        self._require_user(following_id)
        if self.repo.get(follower_id, following_id) is not None:
            raise AlreadyFollowingError(messages.ALREADY_FOLLOWING)
        try:
            self.repo.add(follower_id, following_id)
        except IntegrityError as exc:  # 競合時の重複（UNIQUE制約）
            self.db.rollback()
            raise AlreadyFollowingError(messages.ALREADY_FOLLOWING) from exc
        return FollowStateOut(
            is_following=True,
            followers_count=self.repo.followers_count(following_id),
        )

    def unfollow(self, follower_id: int, following_id: int) -> None:
        self._require_user(following_id)
        follow = self.repo.get(follower_id, following_id)
        if follow is None:
            raise NotFollowingError(messages.NOT_FOLLOWING)
        self.repo.delete(follow)

    # ---- 検索 / プロフィール / 一覧 ----
    def search(self, viewer_id: int, query: str) -> list[UserBrief]:
        users = self.users.search_by_username(query, exclude_id=viewer_id)
        following = self.repo.following_subset(
            viewer_id, [u.id for u in users]
        )
        return [self._brief(u, viewer_id, following) for u in users]

    def profile(self, viewer_id: int, user_id: int) -> ProfileOut:
        user = self._require_user(user_id)
        is_following = (
            viewer_id != user_id
            and self.repo.get(viewer_id, user_id) is not None
        )
        return ProfileOut(
            id=user.id,
            username=user.username,
            profile_image_url=user.profile_image_url,
            bio=user.bio,
            created_at=user.created_at,
            following_count=self.repo.following_count(user_id),
            followers_count=self.repo.followers_count(user_id),
            is_following=is_following,
            is_me=viewer_id == user_id,
        )

    def list_following(
        self, viewer_id: int, user_id: int
    ) -> list[UserBrief]:
        self._require_user(user_id)
        users = self.repo.list_following(user_id)
        following = self.repo.following_subset(
            viewer_id, [u.id for u in users]
        )
        return [self._brief(u, viewer_id, following) for u in users]

    def list_followers(
        self, viewer_id: int, user_id: int
    ) -> list[UserBrief]:
        self._require_user(user_id)
        users = self.repo.list_followers(user_id)
        following = self.repo.following_subset(
            viewer_id, [u.id for u in users]
        )
        return [self._brief(u, viewer_id, following) for u in users]
