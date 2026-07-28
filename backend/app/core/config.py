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
    app_name: str = "EvidenceVault"
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
    # This backend's own publicly reachable base URL (used to build absolute links,
    # e.g. locally-stored avatar images, when MEGA isn't configured).
    public_api_base_url: str = "http://localhost:8000/api"

    # Uploads (local fallback when MEGA not configured)
    uploads_dir: Path = Path("uploads")
    max_upload_mb: int = 25

    # SMTP (email) — leave smtp_host empty to disable outgoing email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = "noreply@evidencevault.app"

    # Frontend URLs for emails
    frontend_reset_url: str = "http://localhost:5173/reset-password"

    # Supabase integration (optional)
    supabase_url: Optional[str] = None
    supabase_publishable_key: Optional[str] = None
    supabase_secret_key: Optional[str] = None
    supabase_jwks_url: Optional[str] = None

    # ── MEGA (evidence/avatar storage) ────────────────────────────────────────
    # When both are set, uploads go to this MEGA account instead of local disk.
    mega_uploads_email: Optional[str] = None
    mega_uploads_password: Optional[str] = None

    # ── Cloudflare Turnstile (CAPTCHA) ────────────────────────────────────────
    # When set, the register and login endpoints verify the Turnstile token.
    cloudflare_turnstile_secret: Optional[str] = None

    @property
    def mega_enabled(self) -> bool:
        return bool(self.mega_uploads_email and self.mega_uploads_password)

    @property
    def turnstile_enabled(self) -> bool:
        return bool(self.cloudflare_turnstile_secret)


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
