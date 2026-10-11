"""Per-user extras: notifications and collectable cards."""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user
from app.core.supabase_client import get_supabase
from app.models.schema import CardCollection, Notification
from app.services import cards, notifications

router = APIRouter(tags=["engagement"])


@router.get("/notifications", response_model=list[Notification])
async def list_notifications(
    user: CurrentUser = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return notifications.list_notifications(supabase, user.id)


@router.get("/cards", response_model=CardCollection)
async def list_cards(
    user: CurrentUser = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return cards.list_cards(supabase, user.id)


@router.post("/cards/{card_id}/collect", response_model=CardCollection)
async def collect_card(
    card_id: str,
    user: CurrentUser = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return cards.collect_card(supabase, user.id, card_id)
