from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


@lru_cache
def get_supabase():
    """The data client every service talks to.

    Either the hosted Supabase project (service-role client, bypasses RLS --
    backend only) or the bundled SQLite store, which implements the same
    query-builder API. Chosen by DATA_BACKEND.
    """
    settings = get_settings()
    if settings.uses_supabase:
        from supabase import create_client

        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RuntimeError(
                "DATA_BACKEND=supabase needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
            )
        return create_client(settings.supabase_url, settings.supabase_service_role_key)

    from app.core.local_store import LocalStore

    return LocalStore(Path(settings.data_dir) / "jeevsetu.db")
