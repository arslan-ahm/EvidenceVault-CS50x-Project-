from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", Path(".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "EvidenceVault AI"
    api_v1_prefix: str = "/api"

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/evidencevault"

    # Local JWT (app-level)
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Cookie auth
    cookie_name: str = "evidencevault_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    # Frontend
    frontend_origin: str = "http://localhost:5173"

    # Uploads
    uploads_dir: Path = Path("uploads")
    max_upload_mb: int = 25

    # Supabase integration (optional)
    supabase_url: Optional[str] = None
    supabase_publishable_key: Optional[str] = None
    supabase_secret_key: Optional[str] = None
    supabase_jwks_url: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite"):
        return database_url
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    return database_url
