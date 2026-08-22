import uuid

from fastapi.testclient import TestClient

from app.core.auth import CurrentUser, get_current_user
from app.core.supabase_client import get_supabase
from app.main import app
from app.routers.community import require_staff_or_researcher
from tests.fakes import FakeSupabaseClient


def _client_as(role: str) -> tuple[TestClient, FakeSupabaseClient, str]:
    fake_supabase = FakeSupabaseClient()
    fake_supabase.set_defaults("observations", {"status": "submitted"})
    user_id = str(uuid.uuid4())
    user = CurrentUser(id=user_id, email="person@example.com", role=role)

    app.dependency_overrides[get_supabase] = lambda: fake_supabase
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[require_staff_or_researcher] = lambda: user

    return TestClient(app), fake_supabase, user_id


def teardown_function():
    app.dependency_overrides.clear()


def test_post_observations_returns_created_row():
    client, _, user_id = _client_as("contributor")

    response = client.post(
        "/observations", json={"species": "Cheetah", "description": "Near the ridge"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["species"] == "Cheetah"
    assert body["user_id"] == user_id
    assert body["status"] == "submitted"


def test_get_observations_mine_returns_only_own_rows():
    client, fake_supabase, _ = _client_as("contributor")
    fake_supabase.table("observations").insert(
        {"species": "Gaur", "user_id": str(uuid.uuid4())}
    ).execute()
    client.post("/observations", json={"species": "Cheetah"})

    response = client.get("/observations/mine")

    assert response.status_code == 200
    assert [row["species"] for row in response.json()] == ["Cheetah"]


def test_get_observations_returns_all_rows_for_staff():
    client, fake_supabase, user_id = _client_as("staff")
    fake_supabase.table("observations").insert({"species": "Gaur", "user_id": user_id}).execute()
    fake_supabase.table("observations").insert(
        {"species": "Cheetah", "user_id": str(uuid.uuid4())}
    ).execute()

    response = client.get("/observations")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_patch_observation_updates_status_and_logs_event():
    client, fake_supabase, _ = _client_as("staff")
    created = (
        fake_supabase.table("observations")
        .insert({"species": "Cheetah", "user_id": str(uuid.uuid4())})
        .execute()
        .data[0]
    )

    response = client.patch(
        f"/observations/{created['id']}",
        json={"status": "under_review", "note": "Looks promising"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "under_review"
    events = fake_supabase.table("status_events").select("*").execute().data
    assert events[0]["new_status"] == "under_review"


def test_like_and_unlike_observation():
    client, fake_supabase, _ = _client_as("staff")
    fake_supabase.set_defaults("observations", {"status": "submitted", "like_count": 0})
    created = (
        fake_supabase.table("observations")
        .insert({"species": "Cheetah", "user_id": str(uuid.uuid4())})
        .execute()
        .data[0]
    )

    like_response = client.post(f"/observations/{created['id']}/like")
    assert like_response.status_code == 200
    assert like_response.json()["like_count"] == 1

    unlike_response = client.delete(f"/observations/{created['id']}/like")
    assert unlike_response.status_code == 200
    assert unlike_response.json()["like_count"] == 0
