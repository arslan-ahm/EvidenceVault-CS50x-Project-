from collections.abc import Generator

from sqlalchemy import create_engine
from sqlmodel import Session

from app.core.config import get_settings, normalize_database_url


settings = get_settings()
database_url = normalize_database_url(settings.database_url)
engine_kwargs: dict[str, object] = {"pool_pre_ping": True}
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Supabase's connection string (port 6543) routes through Supavisor in
    # transaction-pooling mode, which doesn't preserve server-side prepared
    # statements across pooled connections. psycopg3 prepares statements
    # automatically after a few uses, which then fail with
    # "prepared statement ... does not exist" on the next pooled connection.
    # Disabling it keeps every query unnamed/unprepared, which pgbouncer-style
    # poolers require.
    engine_kwargs["connect_args"] = {"prepare_threshold": None}

engine = create_engine(database_url, **engine_kwargs)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
