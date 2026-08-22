import uuid

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.core.supabase_client import get_supabase
from app.main import app
from tests.fakes import FakeSupabaseClient


def _client_as(user_id: str) -> tuple[TestClient, FakeSupabaseClient]:
    fake_supabase = FakeSupabaseClient()
    user = CurrentUser(id=user_id, email=f"{user_id}@example.com", role="contributor")

    app.dependency_overrides[get_supabase] = lambda: fake_supabase
    app.dependency_overrides[get_current_user] = lambda: user

    return TestClient(app), fake_supabase


def teardown_function():
    app.dependency_overrides.clear()


def test_create_and_list_communities():
    client, _ = _client_as(str(uuid.uuid4()))

    create_response = client.post(
        "/communities", json={"name": "Mumbai Birders", "description": "For birders"}
    )
    assert create_response.status_code == 201
    assert create_response.json()["slug"] == "mumbai-birders"

    list_response = client.get("/communities")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_join_then_leave():
    creator_id = str(uuid.uuid4())
    client, _ = _client_as(creator_id)
    client.post("/communities", json={"name": "Delhi Trailwalkers"})

    # Same fake DB (dependency_overrides[get_supabase] persists on `app`), switch
    # only the current-user override to simulate a second person joining.
    other_id = str(uuid.uuid4())
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        id=other_id, email="other@example.com", role="contributor"
    )

    join_response = client.post("/communities/delhi-trailwalkers/join")
    assert join_response.status_code == 201
    assert join_response.json()["user_id"] == other_id

    leave_response = client.delete("/communities/delhi-trailwalkers/leave")
    assert leave_response.status_code == 204


def test_get_unknown_community_404s():
    client, _ = _client_as(str(uuid.uuid4()))

    response = client.get("/communities/does-not-exist")

    assert response.status_code == 404
