"""目標達成率の純粋ロジック（F-07）。

DB 非依存の計算のみ。フロント frontend/src/lib/stats.ts の
`achievement` と同じ式・同じ期間境界に揃える（画面と数値を一致させる）。
- 週は月曜起点（stats.ts startOfWeek ＝ PostgreSQL date_trunc('week') と一致）
- rate = min(100, round(actual / target * 100))（四捨五入は half-up）
- 超過は達成扱い（achieved = actual >= target、rate は100で頭打ち表示）
"""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

WEEKLY = "weekly"
MONTHLY = "monthly"
SESSIONS = "sessions"
VOLUME = "volume"


def start_of_week(d: date) -> date:
    """その日が属する週の月曜日。"""
    return d - timedelta(days=d.weekday())


def period_start(period_type: str, ref: date) -> date:
    """ref が属する期間（週/月）の開始日。"""
    if period_type == WEEKLY:
        return start_of_week(ref)
    return ref.replace(day=1)


def next_period_start(period_type: str, start: date) -> date:
    """与えた期間開始日の次期間の開始日（end 排他境界に使う）。"""
    if period_type == WEEKLY:
        return start + timedelta(days=7)
    # 月初 + 1か月
    year = start.year + (1 if start.month == 12 else 0)
    month = 1 if start.month == 12 else start.month + 1
    return date(year, month, 1)


def prev_period_start(period_type: str, start: date) -> date:
    """与えた期間開始日の1つ前の期間の開始日。"""
    if period_type == WEEKLY:
        return start - timedelta(days=7)
    year = start.year - (1 if start.month == 1 else 0)
    month = 12 if start.month == 1 else start.month - 1
    return date(year, month, 1)


def recent_period_starts(
    period_type: str, ref: date, count: int
) -> list[date]:
    """ref が属する期間を末尾に、新しい順→古い順に count 個の期間開始日（昇順）。"""
    latest = period_start(period_type, ref)
    starts = [latest]
    for _ in range(count - 1):
        starts.append(prev_period_start(period_type, starts[-1]))
    return sorted(starts)


def achievement_rate(actual: Decimal, target: Decimal) -> int:
    """達成率(%)。target<=0 は0、上限100。half-up で丸め。"""
    if target <= 0:
        return 0
    raw = (Decimal(actual) / Decimal(target)) * 100
    pct = int(raw.quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return min(100, pct)


def is_achieved(actual: Decimal, target: Decimal) -> bool:
    """超過は達成扱い。"""
    return target > 0 and Decimal(actual) >= Decimal(target)
