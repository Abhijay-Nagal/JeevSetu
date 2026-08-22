from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase_client import get_supabase

bearer_scheme = HTTPBearer()


class CurrentUser:
    def __init__(self, id: str, email: str | None, role: str, name: str | None = None):
        self.id = id
        self.email = email
        self.name = name
        self.role = role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    """Validates the Supabase-issued JWT against Supabase Auth and loads the profile row."""
    supabase = get_supabase()
    token = credentials.credentials

    auth_response = supabase.auth.get_user(token)
    if auth_response is None or auth_response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    user = auth_response.user
    profile = (
        supabase.table("users").select("role, name").eq("id", user.id).maybe_single().execute()
    )
    role = profile.data["role"] if profile.data else "contributor"
    name = profile.data["name"] if profile.data else None

    return CurrentUser(id=user.id, email=user.email, name=name, role=role)


def require_role(*allowed_roles: str):
    async def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

    return dependency
