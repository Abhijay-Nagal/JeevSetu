from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.services import email_confirmation
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    client.table("users").insert({"id": "user-1", "email": "test@example.com"}).execute()
    return client


def test_create_confirmation_stores_a_token(fake_supabase):
    token = email_confirmation.create_confirmation(fake_supabase, "user-1")

    rows = fake_supabase.table("email_confirmations").select("*").execute().data
    assert len(rows) == 1
    assert rows[0]["token"] == token
    assert rows[0]["user_id"] == "user-1"
    assert rows[0]["confirmed_at"] is None


def test_confirm_token_marks_user_confirmed_via_admin_api(fake_supabase):
    token = email_confirmation.create_confirmation(fake_supabase, "user-1")

    result = email_confirmation.confirm_token(fake_supabase, token)

    assert result["already_confirmed"] is False
    assert "user-1" in fake_supabase.auth.admin.confirmed_user_ids


def test_confirm_token_twice_reports_already_confirmed_without_double_admin_call(fake_supabase):
    token = email_confirmation.create_confirmation(fake_supabase, "user-1")

    email_confirmation.confirm_token(fake_supabase, token)
    result = email_confirmation.confirm_token(fake_supabase, token)

    assert result["already_confirmed"] is True
    assert fake_supabase.auth.admin.confirmed_user_ids == ["user-1"]


def test_confirm_unknown_token_404s(fake_supabase):
    with pytest.raises(HTTPException) as exc_info:
        email_confirmation.confirm_token(fake_supabase, "not-a-real-token")

    assert exc_info.value.status_code == 404


def test_confirm_expired_token_is_rejected(fake_supabase):
    token = "expired-token"
    fake_supabase.table("email_confirmations").insert(
        {
            "user_id": "user-1",
            "token": token,
            "expires_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "confirmed_at": None,
        }
    ).execute()

    with pytest.raises(HTTPException) as exc_info:
        email_confirmation.confirm_token(fake_supabase, token)

    assert exc_info.value.status_code == 400
    assert "user-1" not in fake_supabase.auth.admin.confirmed_user_ids
