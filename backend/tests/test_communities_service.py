import pytest
from fastapi import HTTPException

from app.models.schema import CommunityCreate
from app.services import communities, rewards
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    return FakeSupabaseClient()


def test_create_community_makes_creator_a_member(fake_supabase):
    result = communities.create_community(
        fake_supabase, "user-1", CommunityCreate(name="Mumbai Birders")
    )

    assert result["slug"] == "mumbai-birders"
    assert communities.is_member(fake_supabase, result["id"], "user-1")


def test_create_community_dedupes_slug_collision(fake_supabase):
    communities.create_community(fake_supabase, "user-1", CommunityCreate(name="Mumbai Birders"))
    second = communities.create_community(
        fake_supabase, "user-2", CommunityCreate(name="Mumbai Birders")
    )

    assert second["slug"] != "mumbai-birders"
    assert second["slug"].startswith("mumbai-birders-")


def test_join_community_is_idempotent(fake_supabase):
    community = communities.create_community(
        fake_supabase, "user-1", CommunityCreate(name="Delhi Trailwalkers")
    )

    first_join = communities.join_community(fake_supabase, community["id"], "user-2")
    second_join = communities.join_community(fake_supabase, community["id"], "user-2")

    assert first_join["user_id"] == second_join["user_id"] == "user-2"
    members = (
        fake_supabase.table("community_members")
        .select("*")
        .eq("community_id", community["id"])
        .execute()
        .data
    )
    assert len(members) == 2  # creator + user-2, not user-2 twice


def test_leave_community_removes_membership(fake_supabase):
    community = communities.create_community(
        fake_supabase, "user-1", CommunityCreate(name="Nagpur Naturalists")
    )
    communities.join_community(fake_supabase, community["id"], "user-2")

    communities.leave_community(fake_supabase, community["id"], "user-2")

    assert not communities.is_member(fake_supabase, community["id"], "user-2")


def test_leave_community_blocks_creator(fake_supabase):
    community = communities.create_community(
        fake_supabase, "user-1", CommunityCreate(name="Nagpur Naturalists")
    )

    with pytest.raises(HTTPException) as exc_info:
        communities.leave_community(fake_supabase, community["id"], "user-1")

    assert exc_info.value.status_code == 400


def test_get_community_by_slug_404s_when_missing(fake_supabase):
    with pytest.raises(HTTPException) as exc_info:
        communities.get_community_by_slug(fake_supabase, "does-not-exist")

    assert exc_info.value.status_code == 404


def test_list_my_communities_only_returns_joined(fake_supabase):
    mumbai = communities.create_community(
        fake_supabase, "user-1", CommunityCreate(name="Mumbai Birders")
    )
    communities.create_community(
        fake_supabase, "user-2", CommunityCreate(name="Delhi Trailwalkers")
    )
    communities.join_community(fake_supabase, mumbai["id"], "user-3")

    result = communities.list_my_communities(fake_supabase, "user-3")

    assert [community["slug"] for community in result] == ["mumbai-birders"]


def test_list_my_communities_empty_when_no_memberships(fake_supabase):
    communities.create_community(fake_supabase, "user-1", CommunityCreate(name="Mumbai Birders"))

    result = communities.list_my_communities(fake_supabase, "user-3")

    assert result == []


def test_create_community_awards_coins_to_the_creator(fake_supabase):
    communities.create_community(fake_supabase, "user-1", CommunityCreate(name="Mumbai Birders"))

    wallet = rewards.get_wallet(fake_supabase, "user-1")
    assert wallet["coin_balance"] == rewards.COINS_COMMUNITY_CREATED


def test_join_community_awards_coins_once_not_on_repeat_join(fake_supabase):
    community = communities.create_community(
        fake_supabase, "user-1", CommunityCreate(name="Delhi Trailwalkers")
    )

    communities.join_community(fake_supabase, community["id"], "user-2")
    communities.join_community(fake_supabase, community["id"], "user-2")

    wallet = rewards.get_wallet(fake_supabase, "user-2")
    assert wallet["coin_balance"] == rewards.COINS_COMMUNITY_JOINED
