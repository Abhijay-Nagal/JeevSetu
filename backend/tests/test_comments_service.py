import pytest
from fastapi import HTTPException

from app.models.schema import ObservationCreate
from app.services import comments, observations
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    client.set_defaults("observations", {"status": "submitted", "like_count": 0})
    client.table("users").insert({"id": "author", "name": "Asha", "coin_balance": 0}).execute()
    client.table("users").insert({"id": "commenter", "name": "Rahul", "coin_balance": 0}).execute()
    return client


@pytest.fixture
def observation(fake_supabase):
    return observations.create_observation(
        fake_supabase, "author", ObservationCreate(species="Cheetah")
    )


def test_create_comment_attaches_commenter_name(fake_supabase, observation):
    comment = comments.create_comment(fake_supabase, observation["id"], "commenter", "Seen this near the ridge too!")

    assert comment["content"] == "Seen this near the ridge too!"
    assert comment["user_name"] == "Rahul"


def test_list_comments_returns_in_chronological_order(fake_supabase, observation):
    comments.create_comment(fake_supabase, observation["id"], "commenter", "First comment")
    comments.create_comment(fake_supabase, observation["id"], "author", "Second comment")

    result = comments.list_comments(fake_supabase, observation["id"])

    assert [c["content"] for c in result] == ["First comment", "Second comment"]
    assert result[1]["user_name"] == "Asha"


def test_list_comments_empty_when_none_yet(fake_supabase, observation):
    result = comments.list_comments(fake_supabase, observation["id"])

    assert result == []


def test_create_comment_on_missing_post_404s(fake_supabase):
    with pytest.raises(HTTPException) as exc_info:
        comments.create_comment(fake_supabase, "does-not-exist", "commenter", "Hello")

    assert exc_info.value.status_code == 404
