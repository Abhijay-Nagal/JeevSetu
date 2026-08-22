import pytest
from fastapi import HTTPException

from app.models.schema import ObservationCreate, ObservationStatusUpdate
from app.services import observations
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    client.set_defaults("observations", {"status": "submitted"})
    return client


def test_create_observation_sets_user_id(fake_supabase):
    body = ObservationCreate(species="Cheetah", description="Seen near the ridge")

    result = observations.create_observation(fake_supabase, "user-1", body)

    assert result["user_id"] == "user-1"
    assert result["species"] == "Cheetah"
    assert result["status"] == "submitted"


def test_list_own_observations_excludes_others(fake_supabase):
    observations.create_observation(fake_supabase, "user-1", ObservationCreate(species="Cheetah"))
    observations.create_observation(fake_supabase, "user-2", ObservationCreate(species="Gaur"))

    result = observations.list_own_observations(fake_supabase, "user-1")

    assert len(result) == 1
    assert result[0]["species"] == "Cheetah"


def test_list_all_observations_returns_every_row(fake_supabase):
    observations.create_observation(fake_supabase, "user-1", ObservationCreate(species="Cheetah"))
    observations.create_observation(fake_supabase, "user-2", ObservationCreate(species="Gaur"))

    result = observations.list_all_observations(fake_supabase)

    assert len(result) == 2


def test_update_observation_status_writes_status_event(fake_supabase):
    created = observations.create_observation(
        fake_supabase, "user-1", ObservationCreate(species="Cheetah")
    )

    updated = observations.update_observation_status(
        fake_supabase,
        created["id"],
        ObservationStatusUpdate(status="under_review", note="Looks promising"),
    )

    assert updated["status"] == "under_review"
    events = fake_supabase.table("status_events").select("*").execute().data
    assert len(events) == 1
    assert events[0]["old_status"] == "submitted"
    assert events[0]["new_status"] == "under_review"
    assert events[0]["note"] == "Looks promising"


def test_update_observation_status_missing_observation_raises_404(fake_supabase):
    with pytest.raises(HTTPException) as exc_info:
        observations.update_observation_status(
            fake_supabase, "does-not-exist", ObservationStatusUpdate(status="under_review")
        )

    assert exc_info.value.status_code == 404
