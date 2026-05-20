import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.messages import WEAK_PASSWORD

_HAS_LETTER = re.compile(r"[A-Za-z]")
_HAS_DIGIT = re.compile(r"\d")


class RegisterRequest(BaseModel):
    username: str = Field(description="ユーザー名（1〜50文字）", examples=["alice"])
    email: EmailStr = Field(description="メールアドレス", examples=["alice@example.com"])
    password: str = Field(description="パスワード（8文字以上、英字+数字を含む）", examples=["pass1234"])

    @field_validator("username")
    @classmethod
    def _username_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 50):
            raise ValueError("ユーザー名は1〜50文字で入力してください")
        return v

    @field_validator("password")
    @classmethod
    def _password_strength(cls, v: str) -> str:
        # 8文字以上 かつ 英字+数字を両方含む（functional-requirements.md F-01）
        if len(v) < 8 or not _HAS_LETTER.search(v) or not _HAS_DIGIT.search(v):
            raise ValueError(WEAK_PASSWORD)
        return v


class LoginRequest(BaseModel):
    email: EmailStr = Field(description="登録済みメールアドレス", examples=["alice@example.com"])
    password: str = Field(description="パスワード", examples=["pass1234"])


class UserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "alice",
                "email": "alice@example.com",
                "profile_image_url": None,
                "bio": "筋トレ好き",
                "created_at": "2026-01-01T00:00:00",
            }
        },
    )

    id: int = Field(description="ユーザーID")
    username: str = Field(description="ユーザー名")
    email: EmailStr = Field(description="メールアドレス")
    profile_image_url: str | None = Field(default=None, description="プロフィール画像URL")
    bio: str | None = Field(default=None, description="自己紹介文")
    created_at: datetime = Field(description="アカウント作成日時（UTC）")


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT アクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ（常に bearer）")
