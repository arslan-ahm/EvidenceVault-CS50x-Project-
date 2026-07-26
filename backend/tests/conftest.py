import os
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["FRONTEND_ORIGIN"] = "http://localhost:5173"
os.environ["FRONTEND_RESET_URL"] = "http://localhost:5173/reset-password"
os.environ["SMTP_HOST"] = ""
# Force local-disk storage in tests — otherwise pydantic-settings falls back to
# whatever MEGA credentials are in the real .env, and the suite would upload
# real files to the developer's actual MEGA account over the network.
os.environ["MEGA_UPLOADS_EMAIL"] = ""
os.environ["MEGA_UPLOADS_PASSWORD"] = ""
# The real .env sets this true for production (HTTPS). TestClient talks to a
# fake http://testserver, so a Secure-flagged cookie would never be sent back
# on subsequent requests, breaking cookie-based auth for the whole suite.
os.environ["COOKIE_SECURE"] = "false"

from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    """Drop and recreate all tables before each test."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def client():
    """Provide a TestClient instance. Cookies persist across requests."""
    return TestClient(app)


@pytest.fixture()
def db():
    """Provide a fresh DB session for direct queries."""
    with Session(engine) as session:
        yield session


@pytest.fixture()
def user_token(client) -> str:
    """Register a test user and return the auth cookie value."""
    email = f"test-{uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/register", json={
        "email": email,
        "password": "StrongPass1!",
        "name": "Test User",
        "occupation": "Security Researcher",
    })
    assert resp.status_code == 201
    # The httponly cookie is stored in the TestClient automatically
    # Return user info for convenience
    return resp.json()


@pytest.fixture()
def auth_headers(client, user_token):
    """Extract the auth cookie as a header for manual API calls."""
    cookie_value = client.cookies.get("evidencevault_token")
    return {"Authorization": f"Bearer {cookie_value}"} if cookie_value else {}


@pytest.fixture()
def test_case(client) -> dict:
    """Register + create a case. Returns case dict."""
    client.post("/api/auth/register", json={
        "email": "case-tester@example.com",
        "password": "StrongPass1!",
    })
    resp = client.post("/api/cases", json={
        "title": "Test Investigation",
        "description": "A test case for unit tests",
        "category": "fraud",
        "severity": "high",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture()
def uploaded_file(tmp_path: Path) -> Path:
    """Create a temp evidence file with date entries for timeline extraction."""
    file_path = tmp_path / "evidence.txt"
    file_path.write_text(
        "2026-01-01 Initial contact\n2026-01-02 Follow-up message",
        encoding="utf-8",
    )
    return file_path
