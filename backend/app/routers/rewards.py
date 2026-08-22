from fastapi import APIRouter, Depends
from supabase import Client

from app.core.auth import CurrentUser, get_current_user
from app.core.supabase_client import get_supabase
from app.models.schema import WalletSummary
from app.services import rewards

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.get("/wallet", response_model=WalletSummary)
async def get_wallet(
    user: CurrentUser = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
):
    return rewards.get_wallet(supabase, user.id)
