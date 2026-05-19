import pytest


@pytest.fixture
def ex_ids(common_exercises):
    return [e.id for e in common_exercises]


def _create_workout(client, headers, ex_id, performed_on="2026-05-18") -> int:
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
    return res.json()["id"]


def _advice(client, headers, wid, content):
    return client.post(
        f"/workouts/{wid}/advices", headers=headers, json={"content": content}
    )


def test_advice_requires_auth(client, auth_headers, ex_ids):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    res = client.post(f"/workouts/{wid}/advices", json={"content": "がんば"})
    assert res.status_code == 401


def test_advice_nonexistent_workout_404(client, other_headers):
    res = _advice(client, other_headers, 999999, "ナイス")
    assert res.status_code == 404


def test_cannot_advise_own_workout_403(client, auth_headers, ex_ids):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    assert _advice(client, auth_headers, wid, "自分").status_code == 403


def test_create_advice_returns_username(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    res = _advice(client, other_headers, wid, "ナイストレ！")
    assert res.status_code == 201
    body = res.json()
    assert body["content"] == "ナイストレ！"
    assert body["username"] == "intruder"
    assert body["workout_id"] == wid


@pytest.mark.parametrize("content", ["", "   "])
def test_blank_content_rejected_422(
    client, auth_headers, other_headers, ex_ids, content
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    assert _advice(client, other_headers, wid, content).status_code == 422


def test_content_length_boundary(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    assert _advice(client, other_headers, wid, "あ" * 140).status_code == 201
    assert _advice(client, other_headers, wid, "あ" * 141).status_code == 422


def test_list_ascending_by_created(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    _advice(client, other_headers, wid, "1つ目")
    _advice(client, other_headers, wid, "2つ目")
    res = client.get(f"/workouts/{wid}/advices", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert [a["content"] for a in items] == ["1つ目", "2つ目"]
    assert all(a["username"] == "intruder" for a in items)


def test_delete_own_advice_204(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    aid = _advice(client, other_headers, wid, "消す").json()["id"]
    assert (
        client.delete(f"/advices/{aid}", headers=other_headers).status_code
        == 204
    )
    assert client.get(
        f"/workouts/{wid}/advices", headers=auth_headers
    ).json() == []


def test_delete_others_advice_403(
    client, auth_headers, other_headers, ex_ids
):
    wid = _create_workout(client, auth_headers, ex_ids[0])
    aid = _advice(client, other_headers, wid, "他人のは消せない").json()["id"]
    assert (
        client.delete(f"/advices/{aid}", headers=auth_headers).status_code
        == 403
    )


def test_delete_nonexistent_advice_404(client, other_headers):
    assert (
        client.delete("/advices/999999", headers=other_headers).status_code
        == 404
    )


def test_workout_delete_cascades_advices(
    client, db_session, auth_headers, other_headers, ex_ids
):
    from app.models.advice import Advice

    wid = _create_workout(client, auth_headers, ex_ids[0])
    _advice(client, other_headers, wid, "応援")
    assert db_session.query(Advice).filter_by(workout_id=wid).count() == 1
    assert (
        client.delete(f"/workouts/{wid}", headers=auth_headers).status_code
        == 204
    )
    assert db_session.query(Advice).filter_by(workout_id=wid).count() == 0
