import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

# Serverless hosts (Vercel sets VERCEL=1) only allow writes under /tmp, and
# that storage is per-instance and wiped on cold starts.
IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
DEFAULT_DATA_DIR = "/tmp/jeevsetu" if IS_SERVERLESS else str(BACKEND_DIR / ".data")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "local" (default) keeps everything in a SQLite file under DATA_DIR, so
    # the app runs with no external services. "supabase" uses the hosted
    # Postgres project below instead (apply supabase/migrations first).
    data_backend: str = "local"
    data_dir: str = DEFAULT_DATA_DIR

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    groq_api_key: str = ""

    # Signs login tokens. Leave empty locally and one is generated and kept in
    # DATA_DIR; set it explicitly anywhere with more than one server process.
    auth_secret: str = ""
    auth_token_ttl_hours: int = 24 * 7

    # Seeds communities, posts and the demo account into an empty local store.
    seed_demo_data: bool = True
    demo_username: str = "demo_explorer"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_email: str = ""
    app_password: str = ""
    smtp_from_name: str = "JeevSetu"
    frontend_url: str = "http://localhost:5173"

    # Security
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    rate_limit_per_minute: int = 120

    @property
    def uses_supabase(self) -> bool:
        return self.data_backend.lower() == "supabase"


@lru_cache
def get_settings() -> Settings:
    return Settings()
