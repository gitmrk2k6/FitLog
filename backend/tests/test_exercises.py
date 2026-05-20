def test_list_requires_auth(client):
    assert client.get("/api/exercises").status_code == 401


def test_list_returns_common_exercises(client, auth_headers, common_exercises):
    res = client.get("/api/exercises", headers=auth_headers)
    assert res.status_code == 200
    names = {e["name"] for e in res.json()}
    assert {"ベンチプレス", "スクワット", "ランニング"} <= names


def test_create_custom_exercise(client, auth_headers):
    res = client.post(
        "/api/exercises",
        headers=auth_headers,
        json={"name": "アームカール", "category": "arms"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "アームカール"
    assert body["created_by"] is not None


def test_create_duplicate_exercise(client, auth_headers, common_exercises):
    res = client.post(
        "/api/exercises",
        headers=auth_headers,
        json={"name": "ベンチプレス", "category": "chest"},
    )
    assert res.status_code == 409


def test_other_user_cannot_see_my_custom_exercise(
    client, auth_headers, other_headers
):
    client.post(
        "/api/exercises",
        headers=auth_headers,
        json={"name": "オリジナル種目", "category": "etc"},
    )
    res = client.get("/api/exercises", headers=other_headers)
    assert "オリジナル種目" not in {e["name"] for e in res.json()}
