from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBrief(BaseModel):
    """検索結果・フォロー中/フォロワー一覧の1要素。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    profile_image_url: str | None = None
    bio: str | None = None
    is_following: bool  # viewer がこのユーザーをフォロー済みか
    is_me: bool  # viewer 自身か


class ProfileOut(BaseModel):
    """SC-10 プロフィール: ユーザー情報 + フォロー関係の集計。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    profile_image_url: str | None = None
    bio: str | None = None
    created_at: datetime
    following_count: int
    followers_count: int
    is_following: bool
    is_me: bool


class FollowStateOut(BaseModel):
    """フォロー/解除後の最新状態（対象ユーザー視点）。"""

    is_following: bool
    followers_count: int
