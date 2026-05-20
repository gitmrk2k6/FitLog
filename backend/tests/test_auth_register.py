from app.core import messages

VALID = {
    "username": "taro",
    "email": "taro@example.com",
    "password": "pass1234",
}


def test_register_success(client):
    res = client.post("/api/auth/register", json=VALID)
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "taro"
    assert body["email"] == "taro@example.com"
    assert "id" in body
    # パスワード（ハッシュ含む）が漏れていないこと
    assert "password" not in body
    assert "password_digest" not in body


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json=VALID)
    res = client.post(
        "/api/auth/register",
        json={**VALID, "username": "another"},
    )
    assert res.status_code == 409
    assert res.json()["detail"] == messages.EMAIL_ALREADY_REGISTERED


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json=VALID)
    res = client.post(
        "/api/auth/register",
        json={**VALID, "email": "other@example.com"},
    )
    assert res.status_code == 409
    assert res.json()["detail"] == messages.USERNAME_ALREADY_TAKEN


def test_register_weak_password_too_short(client):
    res = client.post(
        "/api/auth/register",
        json={**VALID, "password": "ab12"},
    )
    assert res.status_code == 422
    assert messages.WEAK_PASSWORD in res.text


def test_register_weak_password_letters_only(client):
    res = client.post(
        "/api/auth/register",
        json={**VALID, "password": "abcdefgh"},
    )
    assert res.status_code == 422
    assert messages.WEAK_PASSWORD in res.text


def test_register_weak_password_digits_only(client):
    res = client.post(
        "/api/auth/register",
        json={**VALID, "password": "12345678"},
    )
    assert res.status_code == 422
    assert messages.WEAK_PASSWORD in res.text
