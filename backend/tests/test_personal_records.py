import pytest


@pytest.fixture
def ex(common_exercises):
    # 0: ベンチプレス(chest), 1: スクワット(legs), 2: ランニング(cardio)
    return [e.id for e in common_exercises]


def _wk(ex_id, sets, on="2026-05-10"):
    return {
        "performed_on": on,
        "exercises": [{"exercise_id": ex_id, "sets": sets}],
    }


def _create(client, h, *args, **kw):
    return client.post("/workouts", headers=h, json=_wk(*args, **kw))


def test_first_workout_sets_all_three_prs(client, auth_headers, ex):
    res = _create(client, auth_headers, ex[0], [{"weight_kg": 60, "reps": 10}])
    body = res.json()
    assert len(body["pr_updates"]) == 1
    u = body["pr_updates"][0]
    assert u["exercise_id"] == ex[0]
    assert set(u["metrics"]) == {"max_weight", "best_volume", "best_est_1rm"}
    assert body["sets"][0]["is_pr"] is True


def test_heavier_only_updates_max_weight(client, auth_headers, ex):
    _create(client, auth_headers, ex[0], [{"weight_kg": 60, "reps": 10}], "2026-05-10")
    # 重量↑だが 1set でボリューム(80<600)・1RMは(96>80)…1RMも上がるので
    # ボリュームだけ更新されない構成にする: 80kg×1 → vol80, 1rm≈82.7>80
    res = _create(
        client, auth_headers, ex[0], [{"weight_kg": 80, "reps": 1}], "2026-05-12"
    )
    metrics = res.json()["pr_updates"][0]["metrics"]
    assert "max_weight" in metrics
    assert "best_volume" not in metrics


def test_no_improvement_returns_empty_pr(client, auth_headers, ex):
    _create(client, auth_headers, ex[0], [{"weight_kg": 100, "reps": 10}], "2026-05-10")
    res = _create(
        client, auth_headers, ex[0], [{"weight_kg": 50, "reps": 5}], "2026-05-12"
    )
    body = res.json()
    assert body["pr_updates"] == []
    assert body["sets"][0]["is_pr"] is False


def test_zero_weight_excluded_from_pr(client, auth_headers, ex):
    # ランニング(重量0) は対象外
    res = _create(client, auth_headers, ex[2], [{"weight_kg": 0, "reps": 30}])
    assert res.json()["pr_updates"] == []


def test_dashboard_personal_records(client, auth_headers, ex):
    _create(client, auth_headers, ex[0], [{"weight_kg": 70, "reps": 6}])
    res = client.get("/dashboard/personal-records", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    pr = data[0]
    assert pr["exercise_id"] == ex[0]
    assert float(pr["max_weight_kg"]) == 70.0
    assert pr["max_weight_reps"] == 6
    # 推定1RM = 70×(1+6/30)=84.0
    assert float(pr["best_est_1rm"]) == 84.0


def test_dashboard_requires_auth(client):
    assert client.get("/dashboard/personal-records").status_code == 401


def test_delete_recomputes_pr(client, auth_headers, ex):
    w1 = _create(
        client, auth_headers, ex[0], [{"weight_kg": 60, "reps": 10}], "2026-05-10"
    ).json()["id"]
    _create(
        client, auth_headers, ex[0], [{"weight_kg": 100, "reps": 5}], "2026-05-12"
    )
    # 100kg の記録を削除 → 最大重量は 60 に戻るはず
    assert client.delete(f"/workouts/{w1}", headers=auth_headers).status_code == 204
    # w1(60kg) を消したので残るのは 100kg。max は 100
    pr = client.get("/dashboard/personal-records", headers=auth_headers).json()[0]
    assert float(pr["max_weight_kg"]) == 100.0


def test_delete_last_workout_clears_pr(client, auth_headers, ex):
    wid = _create(
        client, auth_headers, ex[0], [{"weight_kg": 60, "reps": 10}]
    ).json()["id"]
    client.delete(f"/workouts/{wid}", headers=auth_headers)
    assert client.get("/dashboard/personal-records", headers=auth_headers).json() == []


def test_edit_removing_exercise_recomputes(client, auth_headers, ex):
    wid = _create(
        client, auth_headers, ex[0], [{"weight_kg": 80, "reps": 5}]
    ).json()["id"]
    # 種目をスクワットに差し替え → ベンチのPRは消える
    client.patch(
        f"/workouts/{wid}",
        headers=auth_headers,
        json=_wk(ex[1], [{"weight_kg": 90, "reps": 5}]),
    )
    prs = client.get("/dashboard/personal-records", headers=auth_headers).json()
    ex_ids = {p["exercise_id"] for p in prs}
    assert ex[0] not in ex_ids
    assert ex[1] in ex_ids
