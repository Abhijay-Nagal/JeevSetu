import re

from fastapi import HTTPException, status

from app.core.auth import create_access_token
from app.services import rewards

USERNAME_PATTERN = re.compile(r"^[a-z][a-z0-9_.]{2,23}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PUBLIC_FIELDS = ("id", "username", "name", "email", "role", "coin_balance", "created_at")


def normalize_username(username: str) -> str:
    return username.strip().lower()


def username_problem(username: str) -> str | None:
    """Human-readable reason a username can't be used, or None if it's valid."""
    if not USERNAME_PATTERN.match(username):
        return (
            "Usernames are 3-24 characters, start with a letter, and use only "
            "lowercase letters, numbers, '_' or '.'"
        )
    return None


def find_by_username(supabase, username: str) -> dict | None:
    result = (
        supabase.table("users")
        .select("*")
        .eq("username", normalize_username(username))
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def is_username_available(supabase, username: str) -> tuple[bool, str | None]:
    username = normalize_username(username)
    problem = username_problem(username)
    if problem:
        return False, problem
    if find_by_username(supabase, username):
        return False, "That username is already taken"
    return True, None


def public_profile(row: dict) -> dict:
    return {field: row.get(field) for field in PUBLIC_FIELDS}


def signup(supabase, username: str, name: str, email: str | None) -> dict:
    username = normalize_username(username)
    available, reason = is_username_available(supabase, username)
    if not available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=reason)
    email = (email or "").strip().lower() or None
    if email and not EMAIL_PATTERN.match(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="That email address doesn't look right"
        )

    user = (
        supabase.table("users")
        .insert(
            {
                "username": username,
                "name": name.strip() or username,
                "email": email,
                "role": "contributor",
                "coin_balance": 0,
            }
        )
        .execute()
        .data[0]
    )

    rewards.award_coins(supabase, user["id"], rewards.COINS_WELCOME_BONUS, "welcome_bonus")
    user["coin_balance"] = rewards.COINS_WELCOME_BONUS

    return {"access_token": create_access_token(user["id"]), "user": public_profile(user)}


def login(supabase, username: str) -> dict:
    user = find_by_username(supabase, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No account with that username -- check the spelling or sign up",
        )
    return {"access_token": create_access_token(user["id"]), "user": public_profile(user)}


def get_profile(supabase, user_id: str) -> dict:
    result = supabase.table("users").select("*").eq("id", user_id).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return public_profile(result.data[0])
