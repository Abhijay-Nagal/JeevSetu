import pytest

from app.services import research_submissions
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    return FakeSupabaseClient()


def test_create_submission_sets_user_id(fake_supabase):
    result = research_submissions.create_submission(
        fake_supabase,
        "user-1",
        {"title": "Unusual roosting behavior in Indian flying fox", "abstract": "Observed a colony roosting at an unusually low altitude near Pune."},
    )

    assert result["user_id"] == "user-1"
    assert result["title"] == "Unusual roosting behavior in Indian flying fox"


def test_list_my_submissions_excludes_others(fake_supabase):
    research_submissions.create_submission(fake_supabase, "user-1", {"title": "A", "abstract": "a"})
    research_submissions.create_submission(fake_supabase, "user-2", {"title": "B", "abstract": "b"})

    result = research_submissions.list_my_submissions(fake_supabase, "user-1")

    assert len(result) == 1
    assert result[0]["title"] == "A"


def test_list_my_submissions_empty_when_none_yet(fake_supabase):
    result = research_submissions.list_my_submissions(fake_supabase, "user-1")

    assert result == []
