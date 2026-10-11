"""Username-only authentication owned by this backend.

Signing in needs just a unique username -- there is no password, so anyone
who knows a username can sign in as that account. A successful login
returns a signed bearer token (HMAC-SHA256 over a small JSON payload) that
the frontend sends on every request.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import IS_SERVERLESS, get_settings
from app.core.supabase_client import get_supabase

bearer_scheme = HTTPBearer(auto_error=False)

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
# Tokens
# ---------------------------------------------------------------------------


@lru_cache
def _signing_key() -> bytes:
    settings = get_settings()
    if settings.auth_secret:
        return settings.auth_secret.encode()

    # Serverless instances don't share a disk, so a per-instance generated
    # secret would reject tokens issued by another instance. Derive a stable
    # one from a server-side secret that every instance already has.
    if IS_SERVERLESS:
        for material in (settings.supabase_service_role_key, settings.groq_api_key):
            if material:
                return hmac.new(material.encode(), b"jeevsetu-auth", hashlib.sha256).digest()
        # Last resort: the project id is stable across instances but not
        # secret. With username-only login a forged token grants nothing a
        # plain login wouldn't, but set AUTH_SECRET for a proper key.
        project = os.environ.get("VERCEL_PROJECT_ID") or os.environ.get("VERCEL_GIT_REPO_ID")
        if project:
            return hashlib.sha256(f"jeevsetu-auth:{project}".encode()).digest()

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


def create_access_token(user_id: str, username: str | None = None, name: str | None = None) -> str:
    # The username and display name ride along in the (signed) token so an
    # instance that has never seen this account -- a fresh serverless
    # instance with an empty /tmp store -- can restore it instead of
    # logging the person out.
    ttl = get_settings().auth_token_ttl_hours * 3600
    claims = {"sub": user_id, "exp": int(time.time()) + ttl}
    if username:
        claims["usr"] = username
        claims["name"] = name
    payload = _b64(json.dumps(claims).encode())
    signature = _b64(hmac.new(_signing_key(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def decode_access_token(token: str) -> str | None:
    """Returns the user id for a valid, unexpired token, else None."""
    claims = decode_claims(token)
    return claims.get("sub") if claims else None


def decode_claims(token: str) -> dict | None:
    """Returns the claims of a valid, unexpired token, else None."""
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
    return claims


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
    claims = decode_claims(credentials.credentials)
    if not claims or not claims.get("sub"):
        return None
    return load_user(supabase, claims["sub"]) or _restore_user(supabase, claims)


def _restore_user(supabase, claims: dict) -> CurrentUser | None:
    """Recreates the profile row for a validly signed token whose account
    this data store has lost (serverless /tmp storage is wiped on cold
    starts). Activity history isn't recoverable, but the person stays
    signed in under the same id and username."""
    username = claims.get("usr")
    if not username:
        return None
    taken = supabase.table("users").select("id").eq("username", username).limit(1).execute()
    if taken.data:
        # Someone else registered this username on this instance meanwhile.
        return None
    supabase.table("users").insert(
        {
            "id": claims["sub"],
            "username": username,
            "name": claims.get("name") or username,
            "email": None,
            "role": "contributor",
            "coin_balance": 0,
        }
    ).execute()
    return load_user(supabase, claims["sub"])


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
