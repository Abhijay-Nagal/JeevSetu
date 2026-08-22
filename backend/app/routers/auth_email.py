from fastapi import APIRouter, Depends, status
from supabase import Client

from app.core.supabase_client import get_supabase
from app.models.schema import ConfirmEmailRequest, ConfirmEmailResult, SendConfirmationRequest
from app.services import email_confirmation

# No auth dependency on either route -- the caller has no session yet at
# this point in the signup flow. The token itself is the credential.
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-confirmation", status_code=status.HTTP_202_ACCEPTED)
async def send_confirmation(
    body: SendConfirmationRequest,
    supabase: Client = Depends(get_supabase),
):
    token = email_confirmation.create_confirmation(supabase, str(body.user_id))
    email_confirmation.send_confirmation_email(body.email, body.name, token)
    return {"status": "sent"}


@router.post("/confirm-email", response_model=ConfirmEmailResult)
async def confirm_email(
    body: ConfirmEmailRequest,
    supabase: Client = Depends(get_supabase),
):
    return email_confirmation.confirm_token(supabase, body.token)
