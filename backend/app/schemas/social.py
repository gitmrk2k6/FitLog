from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---- F-04 ナイストレ ----
class CheerStateOut(BaseModel):
    """付与/解除後の最新状態（件数 + 自分が付与済みか）。"""

    cheers_count: int = Field(description="現在のナイストレ総数")
    cheered_by_me: bool = Field(description="ログインユーザーが付与済みか")


# ---- F-05 アドバイス ----
class AdviceCreate(BaseModel):
    """投稿入力。本文は必須・最大140文字（DBは LENGTH>=1 のみ、上限はここで担保）。"""

    content: str = Field(
        min_length=1,
        max_length=140,
        description="アドバイス本文（1〜140文字）",
        examples=["フォームが綺麗でした！"],
    )

    @field_validator("content")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("本文を入力してください")
        return s


class AdviceOut(BaseModel):
    """一覧/詳細用。投稿者名・本文・日時を含む（要件: 昇順表示）。"""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "workout_id": 10,
                "user_id": 2,
                "username": "bob",
                "content": "フォームが綺麗でした！",
                "created_at": "2026-05-18T12:00:00",
            }
        },
    )

    id: int = Field(description="アドバイスID")
    workout_id: int = Field(description="対象ワークアウトID")
    user_id: int = Field(description="投稿者ユーザーID")
    username: str = Field(description="投稿者ユーザー名")
    content: str = Field(description="アドバイス本文")
    created_at: datetime = Field(description="投稿日時（UTC）")
