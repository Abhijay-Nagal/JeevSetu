import pytest
from fastapi import HTTPException

from app.models.schema import CommunityCreate, ObservationCreate, ObservationStatusUpdate
from app.services import communities, observations, rewards
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


def test_create_observation_awards_coins_to_the_author(fake_supabase):
    observations.create_observation(fake_supabase, "user-1", ObservationCreate(species="Cheetah"))

    wallet = rewards.get_wallet(fake_supabase, "user-1")
    assert wallet["coin_balance"] == rewards.COINS_POST_CREATED


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


def test_create_observation_in_community_requires_membership(fake_supabase):
    community = communities.create_community(
        fake_supabase, "staff-user", CommunityCreate(name="Mumbai Birders")
    )

    with pytest.raises(HTTPException) as exc_info:
        observations.create_observation(
            fake_supabase,
            "outsider",
            ObservationCreate(species="Cheetah", community_slug=community["slug"]),
        )

    assert exc_info.value.status_code == 403


def test_create_observation_in_community_as_member_succeeds(fake_supabase):
    community = communities.create_community(
        fake_supabase, "creator", CommunityCreate(name="Mumbai Birders")
    )
    communities.join_community(fake_supabase, community["id"], "member-1")

    result = observations.create_observation(
        fake_supabase,
        "member-1",
        ObservationCreate(species="Cheetah", community_slug="mumbai-birders"),
    )

    assert result["community_id"] == community["id"]


def test_list_community_feed_includes_global_posts(fake_supabase):
    community = communities.create_community(
        fake_supabase, "creator", CommunityCreate(name="Mumbai Birders")
    )
    observations.create_observation(
        fake_supabase,
        "creator",
        ObservationCreate(species="In-community post", community_slug="mumbai-birders"),
    )
    observations.create_observation(
        fake_supabase, "someone-else", ObservationCreate(species="Global post")
    )

    feed = observations.list_community_feed(fake_supabase, community["id"])

    species_in_feed = {row["species"] for row in feed}
    assert species_in_feed == {"In-community post", "Global post"}
