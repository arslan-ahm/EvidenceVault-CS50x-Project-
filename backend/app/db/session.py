from collections.abc import Generator

from sqlalchemy import create_engine
from sqlmodel import Session

from app.core.config import get_settings, normalize_database_url


settings = get_settings()
database_url = normalize_database_url(settings.database_url)
engine_kwargs: dict[str, object] = {"pool_pre_ping": True}
if database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_kwargs)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
