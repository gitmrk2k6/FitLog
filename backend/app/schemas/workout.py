from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---- 入力（種目グルーピング、docs: 1記録 = 実施日 + 種目×セット） ----
class SetInput(BaseModel):
    weight_kg: Decimal = Field(ge=0, description="重量（kg、0以上）", examples=[60.0])
    reps: int = Field(ge=1, description="レップ数（1以上）", examples=[10])


class ExerciseBlockInput(BaseModel):
    exercise_id: int = Field(description="種目ID")
    sets: list[SetInput] = Field(description="セット一覧（1セット以上必要）")

    @field_validator("sets")
    @classmethod
    def _at_least_one_set(cls, v: list[SetInput]) -> list[SetInput]:
        if len(v) < 1:
            raise ValueError("セットは1件以上必要です")
        return v


class WorkoutCreate(BaseModel):
    performed_on: date = Field(description="実施日（YYYY-MM-DD）", examples=["2026-05-18"])
    exercises: list[ExerciseBlockInput] = Field(description="種目×セット一覧（1件以上必要）")
    memo: str | None = Field(default=None, max_length=280, description="メモ（最大280文字）", examples=["調子良かった"])
    photo_url: str | None = Field(default=None, max_length=1000, description="写真URL（photos エンドポイントで設定）")

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

    id: int = Field(description="セットID")
    exercise_id: int = Field(description="種目ID")
    exercise_name: str = Field(description="種目名")
    set_no: int = Field(description="セット番号（種目内の連番）")
    weight_kg: Decimal = Field(description="重量（kg）")
    reps: int = Field(description="レップ数")
    is_pr: bool = Field(description="このセットで自己ベストを更新したか")


class WorkoutSummary(BaseModel):
    """一覧用（F-03 一覧表示）。"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 10,
                "user_id": 1,
                "performed_on": "2026-05-18",
                "memo": "調子良かった",
                "photo_url": None,
                "exercise_count": 3,
                "set_count": 9,
                "total_volume": "4500.00",
                "cheers_count": 2,
                "advices_count": 1,
                "cheered_by_me": False,
                "created_at": "2026-05-18T10:00:00",
            }
        }
    )

    id: int = Field(description="ワークアウトID")
    user_id: int = Field(description="記録したユーザーID")
    performed_on: date = Field(description="実施日")
    memo: str | None = Field(description="メモ")
    photo_url: str | None = Field(description="写真URL")
    exercise_count: int = Field(description="種目数")
    set_count: int = Field(description="総セット数")
    total_volume: Decimal = Field(description="総ボリューム（kg × reps の合計）")
    cheers_count: int = Field(description="ナイストレ数")
    advices_count: int = Field(description="アドバイス数")
    cheered_by_me: bool = Field(default=False, description="ログインユーザーがナイストレ済みか（F-04）")
    created_at: datetime = Field(description="作成日時（UTC）")


class PrUpdateOut(BaseModel):
    """F-09: この保存で更新された自己ベスト指標。"""

    exercise_id: int = Field(description="自己ベストが更新された種目ID")
    metrics: list[str] = Field(description="更新された指標（max_weight / best_volume / best_est_1rm）")


class WorkoutDetail(BaseModel):
    """詳細用（F-03 詳細表示）。sets はフラット、種目別はクライアントで集約。"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 10,
                "user_id": 1,
                "performed_on": "2026-05-18",
                "memo": "調子良かった",
                "photo_url": None,
                "sets": [
                    {"id": 1, "exercise_id": 1, "exercise_name": "ベンチプレス", "set_no": 1, "weight_kg": "60.0", "reps": 10, "is_pr": False}
                ],
                "total_volume": "600.00",
                "cheers_count": 0,
                "advices_count": 0,
                "cheered_by_me": False,
                "pr_updates": [],
                "created_at": "2026-05-18T10:00:00",
                "updated_at": "2026-05-18T10:00:00",
            }
        }
    )

    id: int = Field(description="ワークアウトID")
    user_id: int = Field(description="記録したユーザーID")
    performed_on: date = Field(description="実施日")
    memo: str | None = Field(description="メモ")
    photo_url: str | None = Field(description="写真URL")
    sets: list[WorkoutSetOut] = Field(description="全セット一覧（フラット）")
    total_volume: Decimal = Field(description="総ボリューム（kg × reps の合計）")
    cheers_count: int = Field(description="ナイストレ数")
    advices_count: int = Field(description="アドバイス数")
    cheered_by_me: bool = Field(default=False, description="ログインユーザーがナイストレ済みか（F-04）")
    pr_updates: list[PrUpdateOut] = Field(default=[], description="この保存で更新された自己ベスト一覧（F-09）")
    created_at: datetime = Field(description="作成日時（UTC）")
    updated_at: datetime = Field(description="最終更新日時（UTC）")
