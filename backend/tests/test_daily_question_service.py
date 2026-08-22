from datetime import date

import pytest
from fastapi import HTTPException

from app.services import daily_question
from tests.fakes import FakeSupabaseClient

DAY1 = date(2026, 1, 1)


@pytest.fixture
def fake_supabase() -> FakeSupabaseClient:
    client = FakeSupabaseClient()
    client.table("users").insert({"id": "user-1", "coin_balance": 0}).execute()
    return client


def fake_generator(_topic: str) -> dict:
    return {
        "question": "Which bird is BNHS's flagship conservation species?",
        "options": ["Great Indian Bustard", "Peacock", "Sparrow", "Crow"],
        "correct_answer": 0,
        "explanation": "The Great Indian Bustard is critically endangered and a BNHS priority.",
        "source_reference": "BNHS GIB Conservation Programme",
    }


def test_get_or_create_generates_once_and_caches(fake_supabase):
    first = daily_question.get_or_create_todays_question(fake_supabase, DAY1, fake_generator)
    second = daily_question.get_or_create_todays_question(fake_supabase, DAY1, fake_generator)

    assert first["id"] == second["id"]
    assert len(fake_supabase.table("daily_questions").select("*").execute().data) == 1


def test_submit_correct_answer_awards_coins_and_advances_streak(fake_supabase):
    result = daily_question.submit_answer(fake_supabase, "user-1", DAY1, 0, fake_generator)

    assert result["is_correct"] is True
    assert result["coins_awarded"] == 10
    assert result["streak"]["current_streak"] == 1


def test_submit_wrong_answer_awards_no_coins_but_still_advances_streak(fake_supabase):
    result = daily_question.submit_answer(fake_supabase, "user-1", DAY1, 2, fake_generator)

    assert result["is_correct"] is False
    assert result["coins_awarded"] == 0
    assert result["streak"]["current_streak"] == 1


def test_submit_answer_twice_same_day_is_rejected(fake_supabase):
    daily_question.submit_answer(fake_supabase, "user-1", DAY1, 0, fake_generator)

    with pytest.raises(HTTPException) as exc_info:
        daily_question.submit_answer(fake_supabase, "user-1", DAY1, 0, fake_generator)

    assert exc_info.value.status_code == 400


def test_seven_day_streak_pays_milestone_bonus_on_top_of_daily_coins(fake_supabase):
    current = DAY1
    result = None
    for _ in range(7):
        # Fresh daily question each day -- use a per-day topic key so the
        # unique(question_date) constraint doesn't collide.
        result = daily_question.submit_answer(fake_supabase, "user-1", current, 0, fake_generator)
        current = date.fromordinal(current.toordinal() + 1)

    assert result["streak"]["current_streak"] == 7
    assert result["coins_awarded"] == 10 + 20  # daily correct + streak milestone
