import pytest
from fastapi.testclient import TestClient

from app.core.auth import create_access_token, decode_access_token
from app.core.local_store import LocalStore
from app.core.supabase_client import get_supabase
from app.main import app


@pytest.fixture
def store():
    store = LocalStore(":memory:")
    app.dependency_overrides[get_supabase] = lambda: store
    yield store
    app.dependency_overrides.clear()


@pytest.fixture
def client(store):
    return TestClient(app)


def _signup(client, username="asha_k", **extra):
    return client.post(
        "/api/auth/signup",
        json={"username": username, "name": "Asha K", **extra},
    )


def test_token_roundtrip_and_tamper_detection():
    token = create_access_token("user-1")

    assert decode_access_token(token) == "user-1"
    assert decode_access_token(token[:-2] + "xx") is None
    assert decode_access_token("garbage") is None


def test_signup_returns_token_profile_and_welcome_bonus(client):
    response = _signup(client)

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["user"]["username"] == "asha_k"
    assert body["user"]["coin_balance"] == 50


def test_signup_normalises_and_rejects_duplicate_usernames(client):
    assert _signup(client, username="Asha_K").status_code == 201

    duplicate = _signup(client, username="asha_k")

    assert duplicate.status_code == 409
    assert "taken" in duplicate.json()["detail"]


@pytest.mark.parametrize("username", ["ab", "1starts_with_digit", "has space", "bad!char"])
def test_signup_rejects_invalid_usernames(client, username):
    assert _signup(client, username=username).status_code in (409, 422)


def test_login_with_username_only(client):
    _signup(client)

    ok = client.post("/api/auth/login", json={"username": "ASHA_K"})
    unknown = client.post("/api/auth/login", json={"username": "nobody"})

    assert ok.status_code == 200
    assert ok.json()["access_token"]
    assert ok.json()["user"]["username"] == "asha_k"
    assert unknown.status_code == 401


def test_me_requires_a_valid_token(client):
    token = _signup(client).json()["access_token"]

    assert client.get("/api/auth/me").status_code == 401
    assert (
        client.get("/api/auth/me", headers={"Authorization": "Bearer nonsense"}).status_code == 401
    )
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "asha_k"


def test_username_availability(client):
    _signup(client)

    taken = client.get("/api/auth/username-available", params={"username": "asha_k"}).json()
    free = client.get("/api/auth/username-available", params={"username": "new_birder"}).json()
    invalid = client.get("/api/auth/username-available", params={"username": "x"}).json()

    assert taken["available"] is False
    assert free["available"] is True
    assert invalid["available"] is False and invalid["reason"]


def test_protected_routes_reject_anonymous_requests(client):
    assert client.get("/api/rewards/wallet").status_code == 401
    assert client.post("/api/observations", json={"species": "Tiger"}).status_code == 401
