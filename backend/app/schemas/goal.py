from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PeriodType = Literal["weekly", "monthly"]
Metric = Literal["sessions", "volume"]


class GoalIn(BaseModel):
    """目標設定入力。period_type/metric は固定語彙、target_value は正の数。"""

    period_type: PeriodType = Field(description="期間種別（weekly / monthly）", examples=["weekly"])
    metric: Metric = Field(description="計測指標（sessions=回数 / volume=総ボリュームkg）", examples=["sessions"])
    target_value: Decimal = Field(gt=0, description="目標値（0より大きい数値）", examples=[3])


class GoalOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "period_type": "weekly",
                "metric": "sessions",
                "target_value": "3",
                "start_on": "2026-05-18",
            }
        },
    )

    id: int = Field(description="目標ID")
    period_type: PeriodType = Field(description="期間種別")
    metric: Metric = Field(description="計測指標")
    target_value: Decimal = Field(description="目標値")
    start_on: date = Field(description="目標開始日")


class AchievementOut(BaseModel):
    """現在期間（今週/今月）の達成状況。"""

    period_type: PeriodType = Field(description="期間種別")
    metric: Metric = Field(description="計測指標")
    target_value: Decimal = Field(description="目標値")
    actual: Decimal = Field(description="現在の実績値")
    rate: int = Field(description="達成率（0〜100、超過は100に頭打ち）")
    achieved: bool = Field(description="達成済みか（超過も達成扱い）")
    period_start: date = Field(description="期間開始日（含む）")
    period_end: date = Field(description="期間終了日（排他、次期間の開始日）")


class AchievementPointOut(BaseModel):
    """達成率推移グラフの1点（期間バケット）。"""

    period_start: date = Field(description="期間開始日")
    actual: Decimal = Field(description="実績値")
    target_value: Decimal = Field(description="目標値")
    rate: int = Field(description="達成率（0〜100）")
    achieved: bool = Field(description="達成済みか")
