"""ストリーク（連続記録日数）の純粋ロジック（F-08）。

DB 非依存。フロント frontend/src/lib/stats.ts の
currentStreak / longestStreak と同じ判定に揃える。
- 現在ストリーク: today に記録があれば today 起点、無ければ前日起点。
  そこから連続している日数を遡って数える（当日 or 前日まで継続なら継続中）。
- 最長ストリーク: 実施日集合の連続区間（gaps-and-islands）の最大長。
"""

from collections.abc import Iterable
from datetime import date, timedelta


def current_streak(performed_dates: Iterable[date], today: date) -> int:
    days = set(performed_dates)
    cursor = today
    if cursor not in days:
        # today に記録が無ければ前日起点（昨日まで継続なら継続中とみなす）
        cursor = today - timedelta(days=1)
        if cursor not in days:
            return 0
    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return count


def longest_streak(performed_dates: Iterable[date]) -> int:
    days = sorted(set(performed_dates))
    best = 0
    run = 0
    prev: date | None = None
    for d in days:
        if prev is not None and (d - prev).days == 1:
            run += 1
        else:
            run = 1
        best = max(best, run)
        prev = d
    return best


def heatmap_start(today: date, months: int) -> date:
    """直近 months か月のヒートマップ開始日（months-1 か月前の月初）。"""
    total = today.year * 12 + (today.month - 1) - (months - 1)
    year, month = divmod(total, 12)
    return date(year, month + 1, 1)
