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


def _create_workout(client, headers, ex_id) -> int:
    res = client.post(
        "/api/workouts",
        headers=headers,
        json={
            "performed_on": "2026-05-18",
            "exercises": [
                {"exercise_id": ex_id, "sets": [{"weight_kg": 60, "reps": 10}]}
            ],
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


def test_search_requires_auth(client):
    assert client.get("/api/users/search?q=a").status_code == 401


def test_follow_nonexistent_user_404(client, auth_headers):
    assert (
        client.post("/api/users/999999/follow", headers=auth_headers).status_code
        == 404
    )


def test_cannot_follow_self_422(client, auth_headers):
    me = _me(client, auth_headers)
    res = client.post(f"/api/users/{me}/follow", headers=auth_headers)
    assert res.status_code == 422


def test_follow_returns_state(client, auth_headers):
    alice = _auth(client, "alice")
    alice_id = _me(client, alice)
    res = client.post(f"/api/users/{alice_id}/follow", headers=auth_headers)
    assert res.status_code == 201
    assert res.json() == {"is_following": True, "followers_count": 1}


def test_duplicate_follow_409(client, auth_headers):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    client.post(f"/api/users/{aid}/follow", headers=auth_headers)
    assert (
        client.post(f"/api/users/{aid}/follow", headers=auth_headers).status_code
        == 409
    )


def test_unfollow_then_not_following_404(client, auth_headers):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    client.post(f"/api/users/{aid}/follow", headers=auth_headers)
    assert (
        client.delete(f"/api/users/{aid}/follow", headers=auth_headers).status_code
        == 204
    )
    assert (
        client.delete(f"/api/users/{aid}/follow", headers=auth_headers).status_code
        == 404
    )


def test_search_excludes_self_and_shows_state(client, auth_headers):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    _auth(client, "alicia")  # 部分一致でヒットする別ユーザー
    res = client.get("/api/users/search?q=alic", headers=auth_headers)
    assert res.status_code == 200
    names = {u["username"] for u in res.json()}
    assert names == {"alice", "alicia"}
    assert all(u["is_following"] is False for u in res.json())
    assert all(u["is_me"] is False for u in res.json())

    client.post(f"/api/users/{aid}/follow", headers=auth_headers)
    again = client.get("/api/users/search?q=alice", headers=auth_headers).json()
    assert again[0]["username"] == "alice"
    assert again[0]["is_following"] is True


def test_search_excludes_caller(client, auth_headers):
    # owner 自身は q=own にヒットしても結果から除外される
    res = client.get("/api/users/search?q=owner", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_profile_counts_and_flags(client, auth_headers):
    owner_id = _me(client, auth_headers)
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    client.post(f"/api/users/{aid}/follow", headers=auth_headers)

    prof = client.get(f"/api/users/{aid}", headers=auth_headers).json()
    assert prof["username"] == "alice"
    assert prof["followers_count"] == 1
    assert prof["following_count"] == 0
    assert prof["is_following"] is True
    assert prof["is_me"] is False

    own = client.get(f"/api/users/{owner_id}", headers=auth_headers).json()
    assert own["is_me"] is True
    assert own["is_following"] is False
    assert own["following_count"] == 1


def test_following_and_followers_lists(client, auth_headers):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    owner_id = _me(client, auth_headers)
    client.post(f"/api/users/{aid}/follow", headers=auth_headers)

    following = client.get(
        f"/api/users/{owner_id}/following", headers=auth_headers
    ).json()
    assert [u["username"] for u in following] == ["alice"]

    followers = client.get(
        f"/api/users/{aid}/followers", headers=auth_headers
    ).json()
    assert [u["username"] for u in followers] == ["owner"]


def test_profile_nonexistent_404(client, auth_headers):
    assert (
        client.get("/api/users/999999", headers=auth_headers).status_code == 404
    )


def test_detail_visible_only_to_owner_or_follower(
    client, auth_headers, other_headers, ex_ids
):
    alice = _auth(client, "alice")
    aid = _me(client, alice)
    wid = _create_workout(client, alice, ex_ids[0])

    # 本人は見れる
    assert (
        client.get(f"/api/workouts/{wid}", headers=alice).status_code == 200
    )
    # 未フォロワーは 403
    assert (
        client.get(f"/api/workouts/{wid}", headers=other_headers).status_code
        == 403
    )
    # フォローすると見れる
    client.post(f"/api/users/{aid}/follow", headers=auth_headers)
    assert (
        client.get(f"/api/workouts/{wid}", headers=auth_headers).status_code
        == 200
    )
    # 存在しない記録は 404
    assert (
        client.get("/api/workouts/999999", headers=auth_headers).status_code
        == 404
    )
