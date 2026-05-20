from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExerciseCreate(BaseModel):
    name: str = Field(description="種目名（1〜100文字）", examples=["ベンチプレス"])
    category: str = Field(description="カテゴリ（例: chest, back, legs, shoulders, arms, core）", examples=["chest"])

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 100):
            raise ValueError("種目名は1〜100文字で入力してください")
        return v

    @field_validator("category")
    @classmethod
    def _category_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 30):
            raise ValueError("カテゴリは1〜30文字で入力してください")
        return v


class ExerciseOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "ベンチプレス",
                "category": "chest",
                "created_by": None,
                "created_at": "2026-01-01T00:00:00",
            }
        },
    )

    id: int = Field(description="種目ID")
    name: str = Field(description="種目名")
    category: str = Field(description="カテゴリ")
    created_by: int | None = Field(default=None, description="作成ユーザーID（共通種目は null）")
    created_at: datetime = Field(description="作成日時（UTC）")
