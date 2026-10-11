from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.auth import CurrentUser, get_current_user
from app.core.security import limiter
from app.core.supabase_client import get_supabase
from app.models.schema import (
    AuthResponse,
    ConfirmEmailRequest,
    ConfirmEmailResult,
    LoginRequest,
    SignupRequest,
    UsernameAvailability,
    UserProfile,
)
from app.services import accounts, email_confirmation

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def signup(request: Request, body: SignupRequest, supabase=Depends(get_supabase)):
    result = accounts.signup(supabase, body.username, body.password, body.name, body.email)
    # Confirmation email is a bonus, not a gate: login works with the
    # username straight away, and an unconfigured SMTP server shouldn't
    # stop anyone signing up.
    if result["user"]["email"] and email_confirmation.smtp_configured():
        try:
            token = email_confirmation.create_confirmation(supabase, result["user"]["id"])
            email_confirmation.send_confirmation_email(
                result["user"]["email"], result["user"]["name"], token
            )
        except Exception:  # noqa: BLE001 -- best effort, logged by the mailer
            pass
    return result


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, supabase=Depends(get_supabase)):
    return accounts.login(supabase, body.username, body.password)


@router.get("/me", response_model=UserProfile)
async def me(user: CurrentUser = Depends(get_current_user), supabase=Depends(get_supabase)):
    return accounts.get_profile(supabase, user.id)


@router.get("/username-available", response_model=UsernameAvailability)
@limiter.limit("60/minute")
async def username_available(request: Request, username: str, supabase=Depends(get_supabase)):
    available, reason = accounts.is_username_available(supabase, username)
    return {
        "username": accounts.normalize_username(username),
        "available": available,
        "reason": reason,
    }


@router.post("/send-confirmation", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/minute")
async def send_confirmation(
    request: Request,
    user: CurrentUser = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    # Only ever mails the signed-in user's own address -- the old version
    # accepted any user_id/email pair from an anonymous caller.
    if not user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Add an email address first"
        )
    token = email_confirmation.create_confirmation(supabase, user.id)
    email_confirmation.send_confirmation_email(user.email, user.name or user.username, token)
    return {"status": "sent"}


@router.post("/confirm-email", response_model=ConfirmEmailResult)
async def confirm_email(body: ConfirmEmailRequest, supabase=Depends(get_supabase)):
    return email_confirmation.confirm_token(supabase, body.token)
