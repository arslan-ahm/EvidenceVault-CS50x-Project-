import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["FRONTEND_ORIGIN"] = "http://localhost:5173"

from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def uploaded_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "evidence.txt"
    file_path.write_text("2026-01-01 Initial contact\n2026-01-02 Follow-up message", encoding="utf-8")
    return file_path
