from datetime import date, timedelta

import pytest

from app.core.streak import heatmap_start
from app.services.stats_service import StatsService


@pytest.fixture
def ex_ids(common_exercises):
    return [e.id for e in common_exercises]


def _me(client, headers) -> int:
    return client.get("/auth/me", headers=headers).json()["id"]


def _create_workout(client, headers, ex_id, performed_on: str):
    res = client.post(
        "/workouts",
        headers=headers,
        json={
            "performed_on": performed_on,
            "exercises": [
                {"exercise_id": ex_id, "sets": [{"weight_kg": 60, "reps": 10}]}
            ],
        },
    )
    assert res.status_code == 201


# ---- API スモーク（認証・形） ----
def test_stats_require_auth(client):
    assert client.get("/dashboard/streak").status_code == 401
    assert client.get("/dashboard/heatmap").status_code == 401


def test_heatmap_months_out_of_range_422(client, auth_headers):
    assert client.get(
        "/dashboard/heatmap?months=0", headers=auth_headers
    ).status_code == 422
    assert client.get(
        "/dashboard/heatmap?months=13", headers=auth_headers
    ).status_code == 422


def test_streak_endpoint_shape(client, auth_headers):
    body = client.get("/dashboard/streak", headers=auth_headers).json()
    assert body == {"current": 0, "longest": 0}


# ---- サービス層（ref 注入で決定的） ----
def test_streak_current_and_longest(
    client, db_session, auth_headers, ex_ids
):
    uid = _me(client, auth_headers)
    ref = date(2026, 5, 20)
    # 当日含む連続3日 + 過去に連続2日（最長は3）
    for d in (ref, ref - timedelta(days=1), ref - timedelta(days=2)):
        _create_workout(client, auth_headers, ex_ids[0], d.isoformat())
    for d in (ref - timedelta(days=10), ref - timedelta(days=9)):
        _create_workout(client, auth_headers, ex_ids[0], d.isoformat())

    s = StatsService(db_session).streak(uid, ref=ref)
    assert s.current == 3
    assert s.longest == 3


def test_streak_continues_when_today_empty(
    client, db_session, auth_headers, ex_ids
):
    uid = _me(client, auth_headers)
    ref = date(2026, 5, 20)
    # today は記録なし、前日まで連続2日 → current=2
    _create_workout(
        client, auth_headers, ex_ids[0],
        (ref - timedelta(days=1)).isoformat()
    )
    _create_workout(
        client, auth_headers, ex_ids[0],
        (ref - timedelta(days=2)).isoformat()
    )
    s = StatsService(db_session).streak(uid, ref=ref)
    assert s.current == 2
    assert s.longest == 2


def test_heatmap_fills_missing_days_with_zero(
    client, db_session, auth_headers, ex_ids
):
    uid = _me(client, auth_headers)
    ref = date(2026, 5, 20)
    # 60kg*10 = 600 を ref に記録
    _create_workout(client, auth_headers, ex_ids[0], ref.isoformat())

    cells = StatsService(db_session).heatmap(uid, months=2, ref=ref)
    start = heatmap_start(ref, 2)  # 2026-04-01
    expected_len = (ref - start).days + 1
    assert len(cells) == expected_len
    assert cells[0].date == start
    assert cells[-1].date == ref
    # 記録日は volume>0、それ以外は 0（欠損日も行として存在）
    by_date = {c.date: c.volume for c in cells}
    assert by_date[ref] == 600
    assert by_date[start] == 0
    assert all(c.volume == 0 for c in cells if c.date != ref)
