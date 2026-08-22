from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_supabase() -> Client:
    """Service-role client. Bypasses RLS — backend use only, never exposed to the frontend."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
