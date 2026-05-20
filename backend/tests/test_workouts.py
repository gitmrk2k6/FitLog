import pytest


@pytest.fixture
def ex_ids(common_exercises):
    return [e.id for e in common_exercises]


def _payload(ex_id, performed_on="2026-05-18"):
    return {
        "performed_on": performed_on,
        "memo": "調子良かった",
        "exercises": [
            {
                "exercise_id": ex_id,
                "sets": [
                    {"weight_kg": 60, "reps": 10},
                    {"weight_kg": 70, "reps": 8},
                ],
            }
        ],
    }


def test_create_requires_auth(client, ex_ids):
    assert client.post("/api/workouts", json=_payload(ex_ids[0])).status_code == 401


def test_create_workout(client, auth_headers, ex_ids):
    res = client.post("/api/workouts", headers=auth_headers, json=_payload(ex_ids[0]))
    assert res.status_code == 201
    body = res.json()
    assert body["performed_on"] == "2026-05-18"
    assert len(body["sets"]) == 2
    assert [s["set_no"] for s in body["sets"]] == [1, 2]
    assert body["sets"][0]["exercise_name"] == "ベンチプレス"
    # 総ボリューム = 60*10 + 70*8 = 1160
    assert float(body["total_volume"]) == 1160.0
    assert body["sets"][0]["is_pr"] is False  # F-09 は範囲外


def test_create_rejects_unknown_exercise(client, auth_headers):
    res = client.post(
        "/api/workouts",
        headers=auth_headers,
        json={
            "performed_on": "2026-05-18",
            "exercises": [{"exercise_id": 99999, "sets": [{"weight_kg": 50, "reps": 5}]}],
        },
    )
    assert res.status_code == 422


def test_create_rejects_empty_exercises(client, auth_headers):
    res = client.post(
        "/api/workouts",
        headers=auth_headers,
        json={"performed_on": "2026-05-18", "exercises": []},
    )
    assert res.status_code == 422


def test_list_reverse_chronological_with_aggregates(client, auth_headers, ex_ids):
    client.post("/api/workouts", headers=auth_headers, json=_payload(ex_ids[0], "2026-05-10"))
    client.post("/api/workouts", headers=auth_headers, json=_payload(ex_ids[1], "2026-05-18"))
    res = client.get("/api/workouts", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2
    assert items[0]["performed_on"] == "2026-05-18"  # 降順
    assert items[1]["performed_on"] == "2026-05-10"
    assert items[0]["exercise_count"] == 1
    assert items[0]["set_count"] == 2
    assert float(items[0]["total_volume"]) == 1160.0
    assert items[0]["cheers_count"] == 0
    assert items[0]["advices_count"] == 0


def test_list_only_own_records(client, auth_headers, other_headers, ex_ids):
    client.post("/api/workouts", headers=auth_headers, json=_payload(ex_ids[0]))
    res = client.get("/api/workouts", headers=other_headers)
    assert res.json() == []


def test_get_detail(client, auth_headers, ex_ids):
    wid = client.post(
        "/api/workouts", headers=auth_headers, json=_payload(ex_ids[0])
    ).json()["id"]
    res = client.get(f"/api/workouts/{wid}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["id"] == wid
    assert len(res.json()["sets"]) == 2


def test_get_detail_not_found(client, auth_headers):
    assert client.get("/api/workouts/99999", headers=auth_headers).status_code == 404


def test_get_detail_forbidden_for_others(
    client, auth_headers, other_headers, ex_ids
):
    wid = client.post(
        "/api/workouts", headers=auth_headers, json=_payload(ex_ids[0])
    ).json()["id"]
    assert client.get(f"/api/workouts/{wid}", headers=other_headers).status_code == 403


def test_update_workout(client, auth_headers, ex_ids):
    wid = client.post(
        "/api/workouts", headers=auth_headers, json=_payload(ex_ids[0])
    ).json()["id"]
    res = client.patch(
        f"/api/workouts/{wid}",
        headers=auth_headers,
        json={
            "performed_on": "2026-05-19",
            "memo": "更新後",
            "exercises": [
                {"exercise_id": ex_ids[1], "sets": [{"weight_kg": 100, "reps": 5}]}
            ],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["performed_on"] == "2026-05-19"
    assert body["memo"] == "更新後"
    assert len(body["sets"]) == 1
    assert float(body["total_volume"]) == 500.0


def test_update_forbidden_for_others(
    client, auth_headers, other_headers, ex_ids
):
    wid = client.post(
        "/api/workouts", headers=auth_headers, json=_payload(ex_ids[0])
    ).json()["id"]
    res = client.patch(
        f"/api/workouts/{wid}", headers=other_headers, json=_payload(ex_ids[0])
    )
    assert res.status_code == 403


def test_delete_workout(client, auth_headers, ex_ids):
    wid = client.post(
        "/api/workouts", headers=auth_headers, json=_payload(ex_ids[0])
    ).json()["id"]
    assert client.delete(f"/api/workouts/{wid}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/workouts/{wid}", headers=auth_headers).status_code == 404


def test_delete_forbidden_for_others(
    client, auth_headers, other_headers, ex_ids
):
    wid = client.post(
        "/api/workouts", headers=auth_headers, json=_payload(ex_ids[0])
    ).json()["id"]
    assert (
        client.delete(f"/api/workouts/{wid}", headers=other_headers).status_code == 403
    )
