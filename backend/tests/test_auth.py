from app.core.security import verify_password
from app.models.user import User
from tests.factories import auth_headers, create_user


def test_signup_success_hashes_password(client, db_session):
    resp = client.post(
        "/api/auth/signup",
        json={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert "password" not in body
    assert "password_hash" not in body

    user = db_session.query(User).filter_by(email="alice@example.com").one()
    assert user.password_hash != "password123"
    assert verify_password("password123", user.password_hash)


def test_signup_duplicate_email_conflict(client, db_session):
    create_user(db_session, email="bob@example.com", password="password123")
    resp = client.post(
        "/api/auth/signup",
        json={"name": "Bob Two", "email": "bob@example.com", "password": "password123"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CONFLICT"


def test_signup_invalid_email_rejected(client):
    resp = client.post(
        "/api/auth/signup",
        json={"name": "Bad", "email": "not-an-email", "password": "password123"},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


def test_signup_short_password_rejected(client):
    resp = client.post(
        "/api/auth/signup",
        json={"name": "Short", "email": "short@example.com", "password": "short"},
    )
    assert resp.status_code == 422


def test_login_success_returns_usable_token(client, db_session):
    create_user(db_session, email="carol@example.com", password="password123")
    resp = client.post("/api/auth/login", json={"email": "carol@example.com", "password": "password123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me_resp = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "carol@example.com"


def test_login_wrong_password_unauthorized(client, db_session):
    create_user(db_session, email="dave@example.com", password="password123")
    resp = client.post("/api/auth/login", json={"email": "dave@example.com", "password": "wrongpass"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_nonexistent_email_unauthorized(client):
    resp = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "password123"})
    assert resp.status_code == 401


def test_me_without_token_unauthorized(client):
    resp = client.get("/api/me")
    assert resp.status_code == 401


def test_me_with_valid_token(client, db_session):
    user = create_user(db_session, email="erin@example.com")
    resp = client.get("/api/me", headers=auth_headers(user))
    assert resp.status_code == 200
    assert resp.json()["email"] == "erin@example.com"


def test_me_with_malformed_token_unauthorized(client):
    resp = client.get("/api/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
