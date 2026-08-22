import pytest

from app.models.schema import ObservationCreate
from app.services import likes, observations
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    client.set_defaults("observations", {"status": "submitted", "like_count": 0})
    return client


@pytest.fixture
def observation(fake_supabase):
    return observations.create_observation(
        fake_supabase, "author", ObservationCreate(species="Cheetah")
    )


def test_like_increments_count(fake_supabase, observation):
    result = likes.like_observation(fake_supabase, observation["id"], "user-1")

    assert result["like_count"] == 1
    assert result["liked_by_me"] is True


def test_liking_twice_does_not_double_count(fake_supabase, observation):
    likes.like_observation(fake_supabase, observation["id"], "user-1")
    result = likes.like_observation(fake_supabase, observation["id"], "user-1")

    assert result["like_count"] == 1


def test_unlike_decrements_count(fake_supabase, observation):
    likes.like_observation(fake_supabase, observation["id"], "user-1")

    result = likes.unlike_observation(fake_supabase, observation["id"], "user-1")

    assert result["like_count"] == 0
    assert result["liked_by_me"] is False


def test_unlike_without_liking_first_is_a_no_op(fake_supabase, observation):
    result = likes.unlike_observation(fake_supabase, observation["id"], "user-1")

    assert result["like_count"] == 0


def test_two_users_liking_counts_both(fake_supabase, observation):
    likes.like_observation(fake_supabase, observation["id"], "user-1")
    result = likes.like_observation(fake_supabase, observation["id"], "user-2")

    assert result["like_count"] == 2
