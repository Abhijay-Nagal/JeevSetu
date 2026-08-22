import pytest

from app.services import rewards
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    client.table("users").insert({"id": "user-1", "coin_balance": 0}).execute()
    return client


def test_award_coins_updates_balance_and_writes_ledger_entry(fake_supabase):
    rewards.award_coins(fake_supabase, "user-1", 10, "daily_question_correct")

    wallet = rewards.get_wallet(fake_supabase, "user-1")

    assert wallet["coin_balance"] == 10
    assert len(wallet["recent_transactions"]) == 1
    assert wallet["recent_transactions"][0]["amount"] == 10
    assert wallet["recent_transactions"][0]["reason"] == "daily_question_correct"


def test_award_coins_accumulates_across_multiple_awards(fake_supabase):
    rewards.award_coins(fake_supabase, "user-1", 10, "daily_question_correct")
    rewards.award_coins(fake_supabase, "user-1", 5, "post_created")

    wallet = rewards.get_wallet(fake_supabase, "user-1")

    assert wallet["coin_balance"] == 15
    assert len(wallet["recent_transactions"]) == 2


def test_get_wallet_for_user_with_no_transactions_yet(fake_supabase):
    wallet = rewards.get_wallet(fake_supabase, "user-1")

    assert wallet["coin_balance"] == 0
    assert wallet["recent_transactions"] == []
