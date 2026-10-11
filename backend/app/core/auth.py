"""Username + password authentication owned by this backend.

Passwords are stored as salted PBKDF2-SHA256 hashes. A successful login
returns a signed bearer token (HMAC-SHA256 over a small JSON payload) that
the frontend sends on every request.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.supabase_client import get_supabase

bearer_scheme = HTTPBearer(auto_error=False)

PBKDF2_ITERATIONS = 200_000


class CurrentUser:
    def __init__(
        self,
        id: str,
        email: str | None,
        role: str,
        name: str | None = None,
        username: str | None = None,
    ):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.username = username


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        algorithm, iterations, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
    return hmac.compare_digest(digest.hex(), expected)


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------


@lru_cache
def _signing_key() -> bytes:
    settings = get_settings()
    if settings.auth_secret:
        return settings.auth_secret.encode()

    # No secret configured: generate one once and keep it next to the data,
    # so tokens survive restarts.
    secret_file = Path(settings.data_dir) / "auth_secret"
    if secret_file.exists():
        return secret_file.read_text().strip().encode()
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    secret = secrets.token_urlsafe(48)
    secret_file.write_text(secret)
    return secret.encode()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def create_access_token(user_id: str) -> str:
    ttl = get_settings().auth_token_ttl_hours * 3600
    payload = _b64(json.dumps({"sub": user_id, "exp": int(time.time()) + ttl}).encode())
    signature = _b64(hmac.new(_signing_key(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def decode_access_token(token: str) -> str | None:
    """Returns the user id for a valid, unexpired token, else None."""
    try:
        payload, signature = token.split(".")
        expected = _b64(hmac.new(_signing_key(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        claims = json.loads(_unb64(payload))
    except (ValueError, json.JSONDecodeError):
        return None
    if claims.get("exp", 0) < time.time():
        return None
    return claims.get("sub")


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------


def load_user(supabase, user_id: str) -> CurrentUser | None:
    result = (
        supabase.table("users")
        .select("id, email, name, role, username")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    row = result.data[0]
    return CurrentUser(
        id=row["id"],
        email=row.get("email"),
        name=row.get("name"),
        role=row.get("role") or "contributor",
        username=row.get("username"),
    )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    supabase=Depends(get_supabase),
) -> CurrentUser | None:
    if credentials is None:
        return None
    user_id = decode_access_token(credentials.credentials)
    return load_user(supabase, user_id) if user_id else None


async def get_current_user(
    user: CurrentUser | None = Depends(get_optional_user),
) -> CurrentUser:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to continue",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(*allowed_roles: str):
    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

    return dependency
