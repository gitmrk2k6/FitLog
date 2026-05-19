from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import get_settings

VALID = {
    "username": "kenta",
    "email": "kenta@example.com",
    "password": "pwd12345",
}


def _token(client) -> str:
    client.post("/auth/register", json=VALID)
    res = client.post(
        "/auth/login",
        json={"email": VALID["email"], "password": VALID["password"]},
    )
    return res.json()["access_token"]


def test_me_without_token(client):
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_me_with_garbage_token(client):
    res = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401


def test_me_with_expired_token(client):
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expired = jwt.encode(
        {
            "sub": "1",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
            "type": "access",
        },
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401


def test_me_with_valid_token(client):
    token = _token(client)
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == VALID["email"]
