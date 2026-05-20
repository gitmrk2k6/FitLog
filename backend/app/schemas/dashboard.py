from datetime import date as _date
from decimal import Decimal

from pydantic import BaseModel, Field


class StreakOut(BaseModel):
    """F-08 ストリーク（現在の連続記録日数・最長）。"""

    current: int = Field(description="現在の連続記録日数")
    longest: int = Field(description="過去最長の連続記録日数")


class HeatmapCell(BaseModel):
    """F-08 ヒートマップの1日。記録なし日も volume=0 で出力。"""

    date: _date = Field(description="日付（YYYY-MM-DD）")
    volume: Decimal = Field(description="その日の総ボリューム（kg × reps の合計、記録なし=0）")


class PersonalRecordOut(BaseModel):
    """種目別の自己ベスト（F-09 ダッシュボード併記表示）。"""

    exercise_id: int = Field(description="種目ID")
    exercise_name: str = Field(description="種目名")
    # ① 最大重量
    max_weight_kg: Decimal | None = Field(description="最大重量（kg）")
    max_weight_reps: int | None = Field(description="最大重量時のレップ数")
    max_weight_on: _date | None = Field(description="最大重量を達成した日")
    # ② ベストボリューム
    best_volume: Decimal | None = Field(description="1日の最大総ボリューム（kg × reps）")
    best_volume_on: _date | None = Field(description="ベストボリュームを達成した日")
    # ③ 推定1RMベスト
    best_est_1rm: Decimal | None = Field(description="推定1RM最大値（kg）")
    best_1rm_weight_kg: Decimal | None = Field(description="推定1RM算出時の重量（kg）")
    best_1rm_reps: int | None = Field(description="推定1RM算出時のレップ数")
    best_1rm_on: _date | None = Field(description="推定1RMベストを達成した日")
