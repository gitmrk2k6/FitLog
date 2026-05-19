from datetime import date, timedelta

import pytest

from app.core.goals import start_of_week
from app.schemas.goal import GoalIn
from app.services.goal_service import GoalNotFoundError, GoalService


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
    return res.json()


# ---- CRUD（API・決定的） ----
def test_goals_requires_auth(client):
    assert client.get("/goals").status_code == 401
    assert client.get("/dashboard/achievements").status_code == 401


def test_goal_upsert_keeps_one_per_period(client, auth_headers):
    assert client.get("/goals", headers=auth_headers).json() == []

    r1 = client.put(
        "/goals",
        headers=auth_headers,
        json={"period_type": "weekly", "metric": "sessions",
              "target_value": 3},
    )
    assert r1.status_code == 200
    assert r1.json()["target_value"] == "3"
    assert r1.json()["start_on"] == date.today().isoformat()

    # 同一 period_type は upsert（件数は増えず内容更新）
    r2 = client.put(
        "/goals",
        headers=auth_headers,
        json={"period_type": "weekly", "metric": "volume",
              "target_value": 5000},
    )
    assert r2.status_code == 200
    goals = client.get("/goals", headers=auth_headers).json()
    assert len(goals) == 1
    assert goals[0]["metric"] == "volume"
    assert goals[0]["target_value"] == "5000"


def test_goal_list_sorted_by_period_type(client, auth_headers):
    client.put("/goals", headers=auth_headers,
               json={"period_type": "weekly", "metric": "sessions",
                     "target_value": 3})
    client.put("/goals", headers=auth_headers,
               json={"period_type": "monthly", "metric": "volume",
                     "target_value": 20000})
    goals = client.get("/goals", headers=auth_headers).json()
    assert [g["period_type"] for g in goals] == ["monthly", "weekly"]


@pytest.mark.parametrize(
    "body",
    [
        {"period_type": "weekly", "metric": "sessions", "target_value": 0},
        {"period_type": "weekly", "metric": "sessions", "target_value": -1},
        {"period_type": "daily", "metric": "sessions", "target_value": 3},
        {"period_type": "weekly", "metric": "steps", "target_value": 3},
    ],
)
def test_goal_validation_422(client, auth_headers, body):
    assert client.put(
        "/goals", headers=auth_headers, json=body
    ).status_code == 422


def test_goal_delete(client, auth_headers):
    client.put("/goals", headers=auth_headers,
               json={"period_type": "weekly", "metric": "sessions",
                     "target_value": 3})
    assert client.delete(
        "/goals/weekly", headers=auth_headers
    ).status_code == 204
    assert client.get("/goals", headers=auth_headers).json() == []
    # 未設定の削除は 404
    assert client.delete(
        "/goals/weekly", headers=auth_headers
    ).status_code == 404


def test_trend_without_goal_404(client, auth_headers):
    assert client.get(
        "/goals/weekly/trend", headers=auth_headers
    ).status_code == 404


# ---- 達成率（サービス層・ref 注入で決定的） ----
def test_current_achievement_sessions(
    client, db_session, auth_headers, ex_ids
):
    uid = _me(client, auth_headers)
    ref = date(2026, 5, 20)
    wk = start_of_week(ref)
    _create_workout(client, auth_headers, ex_ids[0], wk.isoformat())
    _create_workout(
        client, auth_headers, ex_ids[1],
        (wk + timedelta(days=2)).isoformat()
    )
    # 別週の記録（当期に含まれない）
    _create_workout(
        client, auth_headers, ex_ids[0],
        (wk - timedelta(days=3)).isoformat()
    )
    client.put("/goals", headers=auth_headers,
               json={"period_type": "weekly", "metric": "sessions",
                     "target_value": 3})

    ach = GoalService(db_session).current_achievements(uid, ref=ref)
    assert len(ach) == 1
    a = ach[0]
    assert a.actual == 2  # 当期の実施日数（別週は除外）
    assert a.target_value == 3
    assert a.rate == 67  # 2/3 → 66.7 → 67
    assert a.achieved is False
    assert a.period_start == wk


def test_current_achievement_volume_over_target(
    client, db_session, auth_headers, ex_ids
):
    uid = _me(client, auth_headers)
    ref = date(2026, 5, 20)
    wk = start_of_week(ref)
    # 60kg*10 = 600/記録、2記録 = 1200
    _create_workout(client, auth_headers, ex_ids[0], wk.isoformat())
    _create_workout(
        client, auth_headers, ex_ids[0],
        (wk + timedelta(days=1)).isoformat()
    )
    client.put("/goals", headers=auth_headers,
               json={"period_type": "weekly", "metric": "volume",
                     "target_value": 1000})

    a = GoalService(db_session).current_achievements(uid, ref=ref)[0]
    assert a.actual == 1200
    assert a.rate == 100  # 超過は100頭打ち
    assert a.achieved is True


def test_trend_buckets_fill_gaps(
    client, db_session, auth_headers, ex_ids
):
    uid = _me(client, auth_headers)
    ref = date(2026, 5, 20)
    wk = start_of_week(ref)
    # 当週のみ実施（過去週は記録なし＝0で埋まる）
    _create_workout(client, auth_headers, ex_ids[0], wk.isoformat())
    client.put("/goals", headers=auth_headers,
               json={"period_type": "weekly", "metric": "sessions",
                     "target_value": 2})

    pts = GoalService(db_session).trend(
        uid, "weekly", count=4, ref=ref
    )
    assert len(pts) == 4
    assert [p.period_start for p in pts] == sorted(
        p.period_start for p in pts
    )
    assert pts[-1].period_start == wk
    assert pts[-1].actual == 1
    assert pts[-1].rate == 50  # 1/2
    assert all(p.actual == 0 and p.rate == 0 for p in pts[:-1])


def test_trend_missing_goal_raises(db_session, client, auth_headers):
    uid = _me(client, auth_headers)
    with pytest.raises(GoalNotFoundError):
        GoalService(db_session).trend(uid, "monthly", count=3)
