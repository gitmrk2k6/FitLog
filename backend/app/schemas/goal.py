from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PeriodType = Literal["weekly", "monthly"]
Metric = Literal["sessions", "volume"]


class GoalIn(BaseModel):
    """目標設定入力。period_type/metric は固定語彙、target_value は正の数。"""

    period_type: PeriodType
    metric: Metric
    target_value: Decimal = Field(gt=0)


class GoalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    period_type: PeriodType
    metric: Metric
    target_value: Decimal
    start_on: date


class AchievementOut(BaseModel):
    """現在期間（今週/今月）の達成状況。"""

    period_type: PeriodType
    metric: Metric
    target_value: Decimal
    actual: Decimal
    rate: int  # 0..100（超過は100頭打ち）
    achieved: bool  # 超過は達成扱い
    period_start: date
    period_end: date  # 排他境界（次期間の開始日）


class AchievementPointOut(BaseModel):
    """達成率推移グラフの1点（期間バケット）。"""

    period_start: date
    actual: Decimal
    target_value: Decimal
    rate: int
    achieved: bool
