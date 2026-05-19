from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class StreakOut(BaseModel):
    """F-08 ストリーク（現在の連続記録日数・最長）。"""

    current: int
    longest: int


class HeatmapCell(BaseModel):
    """F-08 ヒートマップの1日。記録なし日も volume=0 で出力。"""

    date: date
    volume: Decimal


class PersonalRecordOut(BaseModel):
    """種目別の自己ベスト（F-09 ダッシュボード併記表示）。"""

    exercise_id: int
    exercise_name: str
    # ① 最大重量
    max_weight_kg: Decimal | None
    max_weight_reps: int | None
    max_weight_on: date | None
    # ② ベストボリューム
    best_volume: Decimal | None
    best_volume_on: date | None
    # ③ 推定1RMベスト
    best_est_1rm: Decimal | None
    best_1rm_weight_kg: Decimal | None
    best_1rm_reps: int | None
    best_1rm_on: date | None
