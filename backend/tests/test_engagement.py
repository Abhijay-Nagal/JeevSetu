import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.local_store import LocalStore
from app.core.supabase_client import get_supabase
from app.main import app
from app.services import seed

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


@pytest.fixture
def store():
    store = LocalStore(":memory:")
    app.dependency_overrides[get_supabase] = lambda: store
    yield store
    app.dependency_overrides.clear()


@pytest.fixture
def client(store):
    return TestClient(app)


def _auth(client, username):
    token = client.post(
        "/api/auth/signup", json={"username": username, "password": "password123", "name": username}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_collecting_a_card_spends_coins_once(client):
    headers = _auth(client, "collector")

    catalog = client.get("/api/cards", headers=headers).json()
    common = next(card for card in catalog["cards"] if card["rarity"] == "Common")
    legendary = next(card for card in catalog["cards"] if card["rarity"] == "Legendary")

    bought = client.post(f"/api/cards/{common['id']}/collect", headers=headers)
    again = client.post(f"/api/cards/{common['id']}/collect", headers=headers)
    too_expensive = client.post(f"/api/cards/{legendary['id']}/collect", headers=headers)

    assert bought.status_code == 200
    assert bought.json()["coin_balance"] == catalog["coin_balance"] - common["price"]
    assert next(c for c in bought.json()["cards"] if c["id"] == common["id"])["owned"] is True
    assert again.status_code == 409
    assert too_expensive.status_code == 400
    assert client.post("/api/cards/not-a-card/collect", headers=headers).status_code == 404


def test_notifications_include_comments_and_likes_from_others(client):
    author = _auth(client, "author")
    fan = _auth(client, "fan")
    post = client.post("/api/observations", json={"species": "Sarus Crane"}, headers=author).json()

    client.post(f"/api/observations/{post['id']}/like", headers=fan)
    client.post(
        f"/api/observations/{post['id']}/comments", json={"content": "Beautiful!"}, headers=fan
    )
    client.post(f"/api/observations/{post['id']}/like", headers=author)  # own like: no notification

    types = [n["type"] for n in client.get("/api/notifications", headers=author).json()]

    assert types.count("like") == 1
    assert types.count("comment") == 1
    assert "welcome" in types


def test_feed_posts_carry_author_and_comment_count(client):
    headers = _auth(client, "poster")
    post = client.post("/api/observations", json={"species": "Kingfisher"}, headers=headers).json()
    client.post(
        f"/api/observations/{post['id']}/comments", json={"content": "Nice"}, headers=headers
    )

    feed = client.get("/api/observations", headers=headers).json()

    assert feed[0]["author_username"] == "poster"
    assert feed[0]["comment_count"] == 1


def test_empty_posts_and_blank_comments_are_rejected(client):
    headers = _auth(client, "validator")
    post = client.post("/api/observations", json={"species": "Kingfisher"}, headers=headers).json()

    assert client.post("/api/observations", json={}, headers=headers).status_code == 422
    assert (
        client.post(
            "/api/observations",
            json={"species": "x", "media_url": "javascript:alert(1)"},
            headers=headers,
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/api/observations/{post['id']}/comments", json={"content": "   "}, headers=headers
        ).status_code
        == 422
    )


def test_image_upload_validates_content(client, tmp_path):
    headers = _auth(client, "photographer")

    ok = client.post(
        "/api/uploads", files={"file": ("bird.png", PNG_BYTES, "image/png")}, headers=headers
    )
    not_image = client.post(
        "/api/uploads", files={"file": ("x.png", b"<script>", "image/png")}, headers=headers
    )
    anonymous = client.post("/api/uploads", files={"file": ("bird.png", PNG_BYTES, "image/png")})

    assert ok.status_code == 201
    assert client.get(ok.json()["url"]).content == PNG_BYTES
    assert not_image.status_code == 415
    assert anonymous.status_code == 401
    assert client.get("/api/uploads/..%2F..%2Fsecret.png").status_code == 404


def test_seeded_demo_account_can_log_in(client, store):
    settings = get_settings()
    seeded = seed.seed_if_empty(store, settings.model_copy(update={"seed_demo_data": True}))

    login = client.post(
        "/api/auth/login",
        json={"username": settings.demo_username, "password": settings.demo_password},
    )

    assert seeded is True
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert len(client.get("/api/communities").json()) == 6
    assert len(client.get("/api/communities/mine", headers=headers).json()) == 2
    assert client.get("/api/notifications", headers=headers).json()
    # Persona accounts have no password and can't be logged into.
    assert (
        client.post(
            "/api/auth/login", json={"username": "meera.kulkarni", "password": "anything"}
        ).status_code
        == 401
    )
    # Seeding is a one-off.
    assert seed.seed_if_empty(store, settings.model_copy(update={"seed_demo_data": True})) is False
