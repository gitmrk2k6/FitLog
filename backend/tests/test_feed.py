import pytest


def _auth(client, username: str) -> dict[str, str]:
    email = f"{username}@example.com"
    client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": "pass1234"},
    )
    token = client.post(
        "/api/auth/login", json={"email": email, "password": "pass1234"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _me(client, headers) -> int:
    return client.get("/api/auth/me", headers=headers).json()["id"]


@pytest.fixture
def ex_ids(common_exercises):
    return [e.id for e in common_exercises]


def _create_workout(client, headers, ex_id, performed_on) -> int:
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


def test_feed_requires_auth(client):
    assert client.get("/api/feed").status_code == 401


def test_feed_empty_when_following_nobody(client, auth_headers):
    res = client.get("/api/feed", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_feed_shows_followed_users_reverse_chronological(
    client, auth_headers, ex_ids
):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    bob = _auth(client, "bob")
    bid = _me(client, bob)

    _create_workout(client, alice, ex_ids[0], "2026-05-10")
    _create_workout(client, bob, ex_ids[1], "2026-05-18")
    # 自分の記録（フィードに出ない想定）
    _create_workout(client, auth_headers, ex_ids[0], "2026-05-19")

    client.post(f"/api/users/{aid}/follow", headers=auth_headers)
    client.post(f"/api/users/{bid}/follow", headers=auth_headers)

    items = client.get("/api/feed", headers=auth_headers).json()
    assert [i["performed_on"] for i in items] == ["2026-05-18", "2026-05-10"]
    user_ids = {i["user_id"] for i in items}
    assert user_ids == {aid, bid}
    own_id = _me(client, auth_headers)
    assert own_id not in user_ids


def test_feed_excludes_unfollowed_users(client, auth_headers, ex_ids):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    bob = _auth(client, "bob")
    _create_workout(client, alice, ex_ids[0], "2026-05-10")
    _create_workout(client, bob, ex_ids[0], "2026-05-11")

    client.post(f"/api/users/{aid}/follow", headers=auth_headers)
    items = client.get("/api/feed", headers=auth_headers).json()
    assert len(items) == 1
    assert items[0]["user_id"] == aid


def test_feed_includes_cheered_by_me_flag(client, auth_headers, ex_ids):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    wid = _create_workout(client, alice, ex_ids[0], "2026-05-10")
    client.post(f"/api/users/{aid}/follow", headers=auth_headers)
    client.post(f"/api/workouts/{wid}/cheers", headers=auth_headers)

    items = client.get("/api/feed", headers=auth_headers).json()
    assert len(items) == 1
    assert items[0]["cheers_count"] == 1
    assert items[0]["cheered_by_me"] is True
