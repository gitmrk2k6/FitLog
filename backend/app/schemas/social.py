from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---- F-04 ナイストレ ----
class CheerStateOut(BaseModel):
    """付与/解除後の最新状態（件数 + 自分が付与済みか）。"""

    cheers_count: int
    cheered_by_me: bool


# ---- F-05 アドバイス ----
class AdviceCreate(BaseModel):
    """投稿入力。本文は必須・最大140文字（DBは LENGTH>=1 のみ、上限はここで担保）。"""

    content: str = Field(min_length=1, max_length=140)

    @field_validator("content")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("本文を入力してください")
        return s


class AdviceOut(BaseModel):
    """一覧/詳細用。投稿者名・本文・日時を含む（要件: 昇順表示）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_id: int
    user_id: int
    username: str
    content: str
    created_at: datetime
