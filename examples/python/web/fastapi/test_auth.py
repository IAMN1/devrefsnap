import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = "testing-only-secret-key-never-use-in-production-1234567890"
from auth_app import ALGORITHM, SECRET_KEY, app, issue_token, users


def test_login_and_protected_route():
    with TestClient(app) as client:
        response = client.post("/token", data={"username": "alice", "password": "training-password-123"})
        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
        token = response.json()["access_token"]
        me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json() == {"username": "alice"}


@pytest.mark.parametrize("username,password", [
    ("alice", "wrong-password"), ("unknown", "training-password-123"),
])
def test_invalid_credentials(username, password):
    with TestClient(app) as client:
        response = client.post("/token", data={"username": username, "password": password})
        assert response.status_code == 401
        assert "access_token" not in response.json()


def test_missing_token():
    with TestClient(app) as client:
        response = client.get("/users/me")
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize("kind", ["malformed", "expired", "wrong-key", "wrong-algorithm", "no-exp", "no-sub", "unknown-user"])
def test_invalid_tokens(kind):
    claims = {"sub": "alice", "exp": datetime.now(timezone.utc) + timedelta(minutes=1)}
    key, algorithm = SECRET_KEY, ALGORITHM
    if kind == "expired":
        claims["exp"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    elif kind == "no-exp":
        del claims["exp"]
    elif kind == "no-sub":
        del claims["sub"]
    elif kind == "unknown-user":
        claims["sub"] = "unknown"
    elif kind == "wrong-key":
        key = "different-test-key-1234567890123456789012345678901234567890"
    elif kind == "wrong-algorithm":
        algorithm = "HS384"
    token = "not.a.valid-token" if kind == "malformed" else jwt.encode(claims, key, algorithm=algorithm)
    with TestClient(app) as client:
        response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"] == "Bearer"


def test_disabled_user(monkeypatch):
    monkeypatch.setitem(users["alice"], "disabled", True)
    with TestClient(app) as client:
        token = issue_token("alice")
        assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
