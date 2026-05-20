from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBrief(BaseModel):
    """検索結果・フォロー中/フォロワー一覧の1要素。"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "username": "bob",
                "profile_image_url": None,
                "bio": "毎日ランニング",
                "is_following": True,
                "is_me": False,
            }
        },
    )

    id: int = Field(description="ユーザーID")
    username: str = Field(description="ユーザー名")
    profile_image_url: str | None = Field(default=None, description="プロフィール画像URL")
    bio: str | None = Field(default=None, description="自己紹介文")
    is_following: bool = Field(description="閲覧ユーザーがこのユーザーをフォロー済みか")
    is_me: bool = Field(description="閲覧ユーザー自身か")


class ProfileOut(BaseModel):
    """SC-10 プロフィール: ユーザー情報 + フォロー関係の集計。"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "username": "bob",
                "profile_image_url": None,
                "bio": "毎日ランニング",
                "created_at": "2026-01-01T00:00:00",
                "following_count": 10,
                "followers_count": 5,
                "is_following": True,
                "is_me": False,
            }
        },
    )

    id: int = Field(description="ユーザーID")
    username: str = Field(description="ユーザー名")
    profile_image_url: str | None = Field(default=None, description="プロフィール画像URL")
    bio: str | None = Field(default=None, description="自己紹介文")
    created_at: datetime = Field(description="アカウント作成日時（UTC）")
    following_count: int = Field(description="フォロー中のユーザー数")
    followers_count: int = Field(description="フォロワー数")
    is_following: bool = Field(description="閲覧ユーザーがこのユーザーをフォロー済みか")
    is_me: bool = Field(description="閲覧ユーザー自身か")


class FollowStateOut(BaseModel):
    """フォロー/解除後の最新状態（対象ユーザー視点）。"""

    is_following: bool = Field(description="フォロー中か")
    followers_count: int = Field(description="対象ユーザーのフォロワー数（操作後の最新値）")
