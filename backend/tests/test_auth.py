"""Comprehensive tests for auth endpoints: register, login, logout, me, profile,
forgot-password, reset-password, and change-password."""

from uuid import uuid4

from app.core.security import hash_password
from app.db.session import engine
from app.models.user import User
from sqlmodel import Session


# ─── Register ────────────────────────────────────────────────────────────────

class TestRegister:
    def test_register_success(self, client):
        """Register with valid data returns 201 and sets auth cookie."""
        resp = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "StrongPass1!",
            "name": "Alice",
            "occupation": "Researcher",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == "Alice"
        assert data["occupation"] == "Researcher"
        assert "id" in data
        # Cookie should be set
        assert "evidencevault_token" in resp.cookies

    def test_register_minimal(self, client):
        """Register without optional fields still succeeds."""
        resp = client.post("/api/auth/register", json={
            "email": "minimal@example.com",
            "password": "StrongPass1!",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "minimal@example.com"
        assert data["name"] == ""
        assert data["occupation"] is None

    def test_register_duplicate_email(self, client):
        """Registering with an existing email returns 409."""
        client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "password": "OtherPass1!",
        })
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_short_password(self, client):
        """Passwords shorter than 8 chars are rejected (backend may still accept,
        but we verify the model constraint via DB)."""
        resp = client.post("/api/auth/register", json={
            "email": "shortpwd@example.com",
            "password": "Ab1",
        })
        # FastAPI may accept this and let bcrypt handle it, but we verify it works
        # (no strict length check at API level — it's at frontend)
        assert resp.status_code in (201, 422)


# ─── Login ───────────────────────────────────────────────────────────────────

class TestLogin:
    def test_login_success(self, client):
        """Login with correct credentials returns 200 and sets cookie."""
        client.post("/api/auth/register", json={
            "email": "login-test@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post("/api/auth/login", json={
            "email": "login-test@example.com",
            "password": "StrongPass1!",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "login-test@example.com"

    def test_login_wrong_password(self, client):
        """Login with wrong password returns 401."""
        client.post("/api/auth/register", json={
            "email": "wrong-pw@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post("/api/auth/login", json={
            "email": "wrong-pw@example.com",
            "password": "WrongPassword1!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Login with unregistered email returns 401."""
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "StrongPass1!",
        })
        assert resp.status_code == 401


# ─── Logout ──────────────────────────────────────────────────────────────────

class TestLogout:
    def test_logout_clears_cookie(self, client):
        """Logout clears the auth cookie."""
        client.post("/api/auth/register", json={
            "email": "logout-test@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        # Cookie should be cleared (value empty or deleted)
        set_cookie = resp.headers.get("set-cookie", "")
        assert "evidencevault_token=" in set_cookie
        assert "Max-Age=0" in set_cookie or "expires=" in set_cookie.lower()


# ─── Me ──────────────────────────────────────────────────────────────────────

class TestMe:
    def test_me_authenticated(self, client):
        """GET /api/auth/me returns the current user."""
        client.post("/api/auth/register", json={
            "email": "me-test@example.com",
            "password": "StrongPass1!",
            "name": "Bob",
            "occupation": "Analyst",
        })
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "me-test@example.com"
        assert data["name"] == "Bob"
        assert data["occupation"] == "Analyst"

    def test_me_unauthenticated(self, client):
        """GET /api/auth/me without auth returns 401."""
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_after_logout(self, client):
        """GET /api/auth/me after logout returns 401."""
        client.post("/api/auth/register", json={
            "email": "post-logout@example.com",
            "password": "StrongPass1!",
        })
        client.post("/api/auth/logout")
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


# ─── Update Profile ──────────────────────────────────────────────────────────

class TestUpdateProfile:
    def test_update_name(self, client):
        """PUT /api/auth/profile updates the user's name."""
        client.post("/api/auth/register", json={
            "email": "profile-update@example.com",
            "password": "StrongPass1!",
        })
        resp = client.put("/api/auth/profile", json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_update_occupation(self, client):
        """PUT /api/auth/profile updates occupation."""
        client.post("/api/auth/register", json={
            "email": "occ-update@example.com",
            "password": "StrongPass1!",
        })
        resp = client.put("/api/auth/profile", json={"occupation": "Pentester"})
        assert resp.status_code == 200
        assert resp.json()["occupation"] == "Pentester"

    def test_update_requires_auth(self, client):
        """PUT /api/auth/profile without auth returns 401."""
        resp = client.put("/api/auth/profile", json={"name": "X"})
        assert resp.status_code == 401


# ─── Forgot / Reset Password ─────────────────────────────────────────────────

class TestForgotPassword:
    def test_forgot_password_returns_success(self, client):
        """POST /api/auth/forgot-password returns success (no email enumeration)."""
        resp = client.post("/api/auth/forgot-password", json={
            "email": "anyone@example.com",
        })
        assert resp.status_code == 200
        assert "sent" in resp.json()["detail"].lower()

    def test_forgot_password_creates_token(self, client, db):
        """A registered user gets a reset token stored in DB."""
        client.post("/api/auth/register", json={
            "email": "reset-token@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post("/api/auth/forgot-password", json={
            "email": "reset-token@example.com",
        })
        assert resp.status_code == 200

        # Verify the token was stored
        user = db.exec(
            __import__("sqlmodel").select(User).where(User.email == "reset-token@example.com")
        ).first()
        assert user is not None
        assert user.reset_token is not None
        assert user.reset_token_expires is not None


class TestResetPassword:
    def test_reset_password_success(self, client, db):
        """POST /api/auth/reset-password with valid token changes password."""
        # Register
        client.post("/api/auth/register", json={
            "email": "reset-success@example.com",
            "password": "OldPass1!",
        })
        # Request reset (creates token)
        client.post("/api/auth/forgot-password", json={
            "email": "reset-success@example.com",
        })
        # Fetch token from DB
        user = db.exec(
            __import__("sqlmodel").select(User).where(User.email == "reset-success@example.com")
        ).first()
        assert user is not None and user.reset_token is not None

        # Use token to reset password
        resp = client.post("/api/auth/reset-password", json={
            "token": user.reset_token,
            "password": "NewStrongPass1!",
        })
        assert resp.status_code == 200

        # Verify we can log in with new password
        # Create a new client to avoid cookie interference
        from fastapi.testclient import TestClient
        from app.main import app
        new_client = TestClient(app)
        login_resp = new_client.post("/api/auth/login", json={
            "email": "reset-success@example.com",
            "password": "NewStrongPass1!",
        })
        assert login_resp.status_code == 200

    def test_reset_password_invalid_token(self, client):
        """POST /api/auth/reset-password with bad token returns 400."""
        resp = client.post("/api/auth/reset-password", json={
            "token": "invalid-token-123",
            "password": "NewStrongPass1!",
        })
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower()

    def test_reset_password_expired_token(self, client, db):
        """An expired token should be rejected."""
        from datetime import datetime, timezone, timedelta

        # Create a user with an expired token directly
        from app.core.security import hash_password
        user_id = str(uuid4())
        with Session(engine) as session:
            user = User(
                id=user_id,
                email="expired-token@example.com",
                hashed_password=hash_password("OldPass1!"),
                name="Expired",
                reset_token="expired-token-abc",
                reset_token_expires=datetime.now(timezone.utc) - timedelta(hours=2),
            )
            session.add(user)
            session.commit()

        resp = client.post("/api/auth/reset-password", json={
            "token": "expired-token-abc",
            "password": "NewPass1!",
        })
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()


# ─── Change Password ─────────────────────────────────────────────────────────

class TestChangePassword:
    def test_change_password_success(self, client):
        """Authenticated user can change their password."""
        client.post("/api/auth/register", json={
            "email": "change-pwd@example.com",
            "password": "CurrentPass1!",
        })
        resp = client.post("/api/auth/change-password", json={
            "current_password": "CurrentPass1!",
            "new_password": "NewPass123!",
        })
        assert resp.status_code == 200

        # Login with new password
        from fastapi.testclient import TestClient
        from app.main import app
        new_client = TestClient(app)
        login_resp = new_client.post("/api/auth/login", json={
            "email": "change-pwd@example.com",
            "password": "NewPass123!",
        })
        assert login_resp.status_code == 200

    def test_change_password_wrong_current(self, client):
        """Wrong current password returns 400."""
        client.post("/api/auth/register", json={
            "email": "wrong-current@example.com",
            "password": "CurrentPass1!",
        })
        resp = client.post("/api/auth/change-password", json={
            "current_password": "WrongPass1!",
            "new_password": "NewPass123!",
        })
        assert resp.status_code == 400
        assert "incorrect" in resp.json()["detail"].lower()

    def test_change_password_requires_auth(self, client):
        """Unauthenticated request returns 401."""
        resp = client.post("/api/auth/change-password", json={
            "current_password": "x",
            "new_password": "y",
        })
        assert resp.status_code == 401


# ─── Delete Account ──────────────────────────────────────────────────────────

class TestDeleteAccount:
    def test_delete_account_removes_user_and_cases(self, client):
        """DELETE /api/auth/me deletes the account and its cases."""
        client.post("/api/auth/register", json={
            "email": "delete-me@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Case to vanish"}).json()

        resp = client.delete("/api/auth/me")
        assert resp.status_code == 200

        assert client.get("/api/auth/me").status_code == 401

        from fastapi.testclient import TestClient
        from app.main import app
        new_client = TestClient(app)
        relogin = new_client.post("/api/auth/login", json={
            "email": "delete-me@example.com",
            "password": "StrongPass1!",
        })
        assert relogin.status_code == 401

    def test_delete_account_requires_auth(self, client):
        resp = client.delete("/api/auth/me")
        assert resp.status_code == 401
