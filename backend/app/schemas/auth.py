import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.core.messages import WEAK_PASSWORD

_HAS_LETTER = re.compile(r"[A-Za-z]")
_HAS_DIGIT = re.compile(r"\d")


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

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
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    profile_image_url: str | None = None
    bio: str | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
