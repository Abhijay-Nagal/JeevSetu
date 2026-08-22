from datetime import date

from fastapi import HTTPException, status
from supabase import Client

from app.models.schema import QuizQuery
from app.services import rag_pipeline, rewards, streaks

# Rotates through real BNHS-grounded themes so the question isn't the same
# subject every day. Picked by calendar day, not randomly, so regenerating
# (e.g. after a cache miss) for the same date is still deterministic.
TOPICS = [
    "Indian birds and their conservation",
    "endangered species of India",
    "Indian wetlands and their wildlife",
    "BNHS conservation programmes",
    "Indian mammals",
    "citizen science and wildlife monitoring",
    "vultures and raptor conservation in India",
]


def _topic_for_date(question_date: date) -> str:
    return TOPICS[question_date.toordinal() % len(TOPICS)]


def _generate_question(topic: str) -> dict:
    """Real generator -- one RAG-grounded question via the existing quiz
    pipeline. Swappable in tests via get_or_create_todays_question's
    generate_fn parameter so tests don't need a Groq key.
    """
    result = rag_pipeline.get_quiz(QuizQuery(topic=topic, num_questions=1))
    generated = result.questions[0]
    return {
        "question": generated.question,
        "options": generated.options,
        "correct_answer": generated.correct_answer,
        "explanation": generated.explanation,
        "source_reference": generated.source_reference,
    }


def get_or_create_todays_question(
    supabase: Client, today: date, generate_fn=_generate_question
) -> dict:
    existing = (
        supabase.table("daily_questions")
        .select("*")
        .eq("question_date", today.isoformat())
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]

    generated = generate_fn(_topic_for_date(today))
    result = (
        supabase.table("daily_questions")
        .insert({"question_date": today.isoformat(), **generated})
        .execute()
    )
    return result.data[0]


def has_answered_today(supabase: Client, daily_question_id: str, user_id: str) -> bool:
    result = (
        supabase.table("daily_question_attempts")
        .select("id")
        .eq("daily_question_id", daily_question_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return bool(result.data)


def submit_answer(
    supabase: Client,
    user_id: str,
    today: date,
    selected_answer: int,
    generate_fn=_generate_question,
) -> dict:
    daily_question = get_or_create_todays_question(supabase, today, generate_fn)

    if has_answered_today(supabase, daily_question["id"], user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already answered today's question"
        )

    is_correct = selected_answer == daily_question["correct_answer"]

    supabase.table("daily_question_attempts").insert(
        {
            "daily_question_id": daily_question["id"],
            "user_id": user_id,
            "selected_answer": selected_answer,
            "is_correct": is_correct,
        }
    ).execute()

    coins_awarded = 0
    if is_correct:
        coins_awarded = rewards.COINS_DAILY_QUESTION_CORRECT
        rewards.award_coins(
            supabase, user_id, coins_awarded, "daily_question_correct", daily_question["id"]
        )

    # Streak advances whether or not today's answer was correct -- showing up
    # is what keeps the streak alive, matching docs/plan.md section 5's note
    # that a wrong answer still "counts toward answered today".
    streak = streaks.update_streak(supabase, user_id, today)

    if streak["current_streak"] % streaks.FREEZE_MILESTONE_DAYS == 0:
        rewards.award_coins(
            supabase,
            user_id,
            rewards.COINS_STREAK_MILESTONE,
            "streak_milestone",
            daily_question["id"],
        )
        coins_awarded += rewards.COINS_STREAK_MILESTONE

    return {
        "is_correct": is_correct,
        "correct_answer": daily_question["correct_answer"],
        "explanation": daily_question.get("explanation"),
        "coins_awarded": coins_awarded,
        "streak": streak,
    }
