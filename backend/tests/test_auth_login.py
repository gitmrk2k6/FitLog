from app.core import messages
from app.core.security import decode_access_token

VALID = {
    "username": "hanako",
    "email": "hanako@example.com",
    "password": "secret123",
}


def _register(client):
    res = client.post("/api/auth/register", json=VALID)
    assert res.status_code == 201
    return res.json()


def test_login_success_returns_valid_jwt(client):
    user = _register(client)
    res = client.post(
        "/api/auth/login",
        json={"email": VALID["email"], "password": VALID["password"]},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert decode_access_token(body["access_token"]) == user["id"]


def test_login_wrong_password(client):
    _register(client)
    res = client.post(
        "/api/auth/login",
        json={"email": VALID["email"], "password": "wrongpass1"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == messages.INVALID_CREDENTIALS


def test_login_nonexistent_email(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "whatever1"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == messages.INVALID_CREDENTIALS
