from datetime import date

from fastapi import APIRouter, Depends
from supabase import Client

from app.core.auth import CurrentUser, get_current_user
from app.core.supabase_client import get_supabase
from app.models.schema import (
    DailyQuestionAnswer,
    DailyQuestionPublic,
    DailyQuestionResult,
    WalletSummary,
)
from app.services import daily_question, rewards, streaks

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.get("/wallet", response_model=WalletSummary)
async def get_wallet(
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return rewards.get_wallet(supabase, user.id)


@router.get("/daily-question", response_model=DailyQuestionPublic)
async def get_daily_question(
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    today = date.today()
    question = daily_question.get_or_create_todays_question(supabase, today)
    already_answered = daily_question.has_answered_today(supabase, question["id"], user.id)

    return {
        "id": question["id"],
        "question": question["question"],
        "options": question["options"],
        "already_answered": already_answered,
        "streak": streaks.get_streak(supabase, user.id),
    }


@router.post("/daily-question/answer", response_model=DailyQuestionResult)
async def answer_daily_question(
    body: DailyQuestionAnswer,
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return daily_question.submit_answer(supabase, user.id, date.today(), body.selected_answer)
