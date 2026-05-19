"""F-07 目標達成率の純粋ロジック（DB非依存）。"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.core.goals import (
    achievement_rate,
    is_achieved,
    next_period_start,
    period_start,
    prev_period_start,
    recent_period_starts,
    start_of_week,
)


def test_start_of_week_is_monday():
    for offset in range(0, 14):
        d = date(2026, 5, 4) + timedelta(days=offset)
        s = start_of_week(d)
        assert s.weekday() == 0  # 月曜
        assert 0 <= (d - s).days <= 6
        assert s <= d


def test_start_of_week_sunday_maps_back_to_monday():
    sunday = date(2026, 5, 17)  # 日曜
    assert sunday.weekday() == 6
    assert start_of_week(sunday) == date(2026, 5, 11)  # 同週の月曜


def test_period_start_monthly_is_first_day():
    assert period_start("monthly", date(2026, 5, 19)) == date(2026, 5, 1)
    assert period_start("weekly", date(2026, 5, 19)) == start_of_week(
        date(2026, 5, 19)
    )


def test_next_period_start():
    assert next_period_start("weekly", date(2026, 5, 11)) == date(2026, 5, 18)
    assert next_period_start("monthly", date(2026, 5, 1)) == date(2026, 6, 1)
    # 年跨ぎ
    assert next_period_start("monthly", date(2026, 12, 1)) == date(
        2027, 1, 1
    )


def test_prev_period_start():
    assert prev_period_start("weekly", date(2026, 5, 18)) == date(2026, 5, 11)
    assert prev_period_start("monthly", date(2026, 1, 1)) == date(
        2025, 12, 1
    )


def test_recent_period_starts_ascending_and_consecutive():
    starts = recent_period_starts("weekly", date(2026, 5, 19), 4)
    assert len(starts) == 4
    assert starts == sorted(starts)
    assert starts[-1] == period_start("weekly", date(2026, 5, 19))
    for a, b in zip(starts, starts[1:]):
        assert (b - a).days == 7

    months = recent_period_starts("monthly", date(2026, 2, 10), 3)
    assert months == [date(2025, 12, 1), date(2026, 1, 1), date(2026, 2, 1)]


@pytest.mark.parametrize(
    "actual,target,expected",
    [
        (0, 100, 0),
        (50, 100, 50),
        (100, 100, 100),
        (150, 100, 100),  # 超過は100頭打ち
        (1, 3, 33),  # 33.33 → 33
        (2, 3, 67),  # 66.67 → 67（half-up）
        (5, 0, 0),  # target<=0
    ],
)
def test_achievement_rate(actual, target, expected):
    assert (
        achievement_rate(Decimal(actual), Decimal(target)) == expected
    )


@pytest.mark.parametrize(
    "actual,target,expected",
    [
        (3, 3, True),  # ちょうど達成
        (4, 3, True),  # 超過は達成扱い
        (2, 3, False),
        (1, 0, False),  # target<=0
    ],
)
def test_is_achieved(actual, target, expected):
    assert is_achieved(Decimal(actual), Decimal(target)) is expected
