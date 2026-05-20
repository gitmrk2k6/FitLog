import pytest


@pytest.fixture
def ex_ids(common_exercises):
    return [e.id for e in common_exercises]


def _create_workout(client, headers, ex_id, performed_on="2026-05-18") -> int:
    res = client.post(
        "/api/workouts",
        headers=headers,
        json={
            "performed_on": performed_on,
            "exercises": [
                {"exercise_id": ex_id, "sets": [{"weight_kg": 60, "reps": 10}]}
            ],
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


def test_cheer_requires_auth(client, auth_headers, ex_ids):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    assert client.post(f"/api/workouts/{wid}/cheers").status_code == 401


def test_cheer_nonexistent_workout_404(client, other_headers):
    res = client.post("/api/workouts/999999/cheers", headers=other_headers)
    assert res.status_code == 404


def test_cannot_cheer_own_workout_403(client, auth_headers, ex_ids):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    res = client.post(f"/api/workouts/{wid}/cheers", headers=auth_headers)
    assert res.status_code == 403


def test_cheer_other_workout_returns_state(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    res = client.post(f"/api/workouts/{wid}/cheers", headers=other_headers)
    assert res.status_code == 201
    assert res.json() == {"cheers_count": 1, "cheered_by_me": True}
    # 投稿者の詳細に件数が反映される（owner は付与不可なので by_me=False）
    detail = client.get(f"/api/workouts/{wid}", headers=auth_headers).json()
    assert detail["cheers_count"] == 1
    assert detail["cheered_by_me"] is False


def test_duplicate_cheer_conflict_409(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    client.post(f"/api/workouts/{wid}/cheers", headers=other_headers)
    dup = client.post(f"/api/workouts/{wid}/cheers", headers=other_headers)
    assert dup.status_code == 409


def test_uncheer_decrements_count(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    client.post(f"/api/workouts/{wid}/cheers", headers=other_headers)
    res = client.delete(f"/api/workouts/{wid}/cheers", headers=other_headers)
    assert res.status_code == 204
    detail = client.get(f"/api/workouts/{wid}", headers=auth_headers).json()
    assert detail["cheers_count"] == 0


def test_uncheer_when_not_cheered_404(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    res = client.delete(f"/api/workouts/{wid}/cheers", headers=other_headers)
    assert res.status_code == 404


def test_workout_delete_cascades_cheers(
    client, db_session, auth_headers, other_headers, ex_ids
):
    from app.models.cheer import Cheer

    wid = _create_workout(client, auth_headers, ex_ids[0])
    client.post(f"/api/workouts/{wid}/cheers", headers=other_headers)
    assert db_session.query(Cheer).filter_by(workout_id=wid).count() == 1
    assert (
        client.delete(f"/api/workouts/{wid}", headers=auth_headers).status_code
        == 204
    )
    assert db_session.query(Cheer).filter_by(workout_id=wid).count() == 0
