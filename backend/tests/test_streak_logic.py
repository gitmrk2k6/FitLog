"""F-08 ストリーク／ヒートマップ起点の純粋ロジック（DB非依存）。"""

from datetime import date

import pytest

from app.core.streak import current_streak, heatmap_start, longest_streak

D = date


def test_current_streak_from_today():
    days = [D(2026, 5, 18), D(2026, 5, 19), D(2026, 5, 20)]
    assert current_streak(days, D(2026, 5, 20)) == 3


def test_current_streak_today_missing_but_yesterday_continues():
    # today に記録が無くても前日まで継続していれば継続中
    days = [D(2026, 5, 18), D(2026, 5, 19)]
    assert current_streak(days, D(2026, 5, 20)) == 2


def test_current_streak_broken_when_yesterday_also_missing():
    days = [D(2026, 5, 18)]
    assert current_streak(days, D(2026, 5, 20)) == 0


def test_current_streak_stops_at_gap():
    days = [D(2026, 5, 15), D(2026, 5, 19), D(2026, 5, 20)]
    assert current_streak(days, D(2026, 5, 20)) == 2


def test_current_streak_empty():
    assert current_streak([], D(2026, 5, 20)) == 0


def test_longest_streak():
    assert longest_streak([]) == 0
    assert longest_streak([D(2026, 5, 1)]) == 1
    # 連続3 / 連続2 → 最大3、重複は無視
    days = [
        D(2026, 5, 1), D(2026, 5, 2), D(2026, 5, 2), D(2026, 5, 3),
        D(2026, 5, 10), D(2026, 5, 11),
    ]
    assert longest_streak(days) == 3


@pytest.mark.parametrize(
    "today,months,expected",
    [
        (D(2026, 5, 20), 5, D(2026, 1, 1)),
        (D(2026, 5, 20), 1, D(2026, 5, 1)),
        (D(2026, 2, 10), 6, D(2025, 9, 1)),  # 年跨ぎ
        (D(2026, 1, 15), 1, D(2026, 1, 1)),
    ],
)
def test_heatmap_start(today, months, expected):
    assert heatmap_start(today, months) == expected
