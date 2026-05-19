from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ExerciseCreate(BaseModel):
    name: str
    category: str

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    created_by: int | None = None
    created_at: datetime
