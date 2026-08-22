from datetime import date, timedelta

import pytest

from app.services import streaks
from tests.fakes import FakeSupabaseClient


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    return FakeSupabaseClient()


DAY1 = date(2026, 1, 1)


def test_first_ever_answer_starts_streak_at_one(fake_supabase):
    result = streaks.update_streak(fake_supabase, "user-1", DAY1)

    assert result["current_streak"] == 1
    assert result["longest_streak"] == 1
    assert result["freezes_available"] == 0


def test_answering_on_consecutive_days_increments_streak(fake_supabase):
    streaks.update_streak(fake_supabase, "user-1", DAY1)
    result = streaks.update_streak(fake_supabase, "user-1", DAY1 + timedelta(days=1))

    assert result["current_streak"] == 2


def test_answering_same_day_twice_is_a_no_op(fake_supabase):
    streaks.update_streak(fake_supabase, "user-1", DAY1)
    result = streaks.update_streak(fake_supabase, "user-1", DAY1)

    assert result["current_streak"] == 1


def test_missing_a_day_with_no_freeze_resets_streak(fake_supabase):
    streaks.update_streak(fake_supabase, "user-1", DAY1)
    result = streaks.update_streak(fake_supabase, "user-1", DAY1 + timedelta(days=3))

    assert result["current_streak"] == 1


def test_missing_a_day_with_a_freeze_available_bridges_the_gap(fake_supabase):
    fake_supabase.table("user_streaks").insert(
        {
            "user_id": "user-1",
            "current_streak": 5,
            "longest_streak": 5,
            "last_answered_date": DAY1.isoformat(),
            "freezes_available": 1,
            "freezes_used_total": 0,
        }
    ).execute()

    result = streaks.update_streak(fake_supabase, "user-1", DAY1 + timedelta(days=3))

    assert result["current_streak"] == 6
    assert result["freezes_available"] == 0


def test_reaching_a_seven_day_milestone_earns_a_freeze(fake_supabase):
    current = DAY1
    for _ in range(7):
        result = streaks.update_streak(fake_supabase, "user-1", current)
        current += timedelta(days=1)

    assert result["current_streak"] == 7
    assert result["freezes_available"] == 1


def test_banked_freezes_are_capped(fake_supabase):
    fake_supabase.table("user_streaks").insert(
        {
            "user_id": "user-1",
            "current_streak": 13,
            "longest_streak": 13,
            "last_answered_date": DAY1.isoformat(),
            "freezes_available": 3,
            "freezes_used_total": 0,
        }
    ).execute()

    # day 14 hits another 7-day milestone -- freeze count should stay capped at 3
    result = streaks.update_streak(fake_supabase, "user-1", DAY1 + timedelta(days=1))

    assert result["current_streak"] == 14
    assert result["freezes_available"] == 3


def test_longest_streak_tracks_the_high_water_mark(fake_supabase):
    current = DAY1
    for _ in range(3):
        streaks.update_streak(fake_supabase, "user-1", current)
        current += timedelta(days=1)

    # miss a day with no freeze -- streak resets, but longest_streak should stick
    result = streaks.update_streak(fake_supabase, "user-1", current + timedelta(days=2))

    assert result["current_streak"] == 1
    assert result["longest_streak"] == 3
