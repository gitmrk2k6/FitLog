from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---- 入力（種目グルーピング、docs: 1記録 = 実施日 + 種目×セット） ----
class SetInput(BaseModel):
    weight_kg: Decimal = Field(ge=0)
    reps: int = Field(ge=1)


class ExerciseBlockInput(BaseModel):
    exercise_id: int
    sets: list[SetInput]

    @field_validator("sets")
    @classmethod
    def _at_least_one_set(cls, v: list[SetInput]) -> list[SetInput]:
        if len(v) < 1:
            raise ValueError("セットは1件以上必要です")
        return v


class WorkoutCreate(BaseModel):
    performed_on: date
    exercises: list[ExerciseBlockInput]
    memo: str | None = Field(default=None, max_length=280)
    photo_url: str | None = Field(default=None, max_length=1000)

    @field_validator("exercises")
    @classmethod
    def _at_least_one_exercise(
        cls, v: list[ExerciseBlockInput]
    ) -> list[ExerciseBlockInput]:
        if len(v) < 1:
            raise ValueError("種目は1件以上必要です")
        return v


class WorkoutUpdate(WorkoutCreate):
    """編集は全置換（実施日・種目構成・メモ・写真をまとめて差し替え）。"""


# ---- 応答 ----
class WorkoutSetOut(BaseModel):
    """フロント Workout.sets に対応するフラット表現。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    exercise_name: str
    set_no: int
    weight_kg: Decimal
    reps: int
    is_pr: bool


class WorkoutSummary(BaseModel):
    """一覧用（F-03 一覧表示）。"""

    id: int
    user_id: int
    performed_on: date
    memo: str | None
    photo_url: str | None
    exercise_count: int
    set_count: int
    total_volume: Decimal
    cheers_count: int
    advices_count: int
    created_at: datetime


class WorkoutDetail(BaseModel):
    """詳細用（F-03 詳細表示）。sets はフラット、種目別はクライアントで集約。"""

    id: int
    user_id: int
    performed_on: date
    memo: str | None
    photo_url: str | None
    sets: list[WorkoutSetOut]
    total_volume: Decimal
    cheers_count: int
    advices_count: int
    created_at: datetime
    updated_at: datetime
