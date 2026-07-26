"""Tests for the admin API: access gating, user moderation, case moderation."""

from fastapi.testclient import TestClient
from sqlmodel import select

from app.main import app
from app.models.user import User


def _promote_to_admin(db, email: str) -> None:
    user = db.exec(select(User).where(User.email == email)).first()
    user.is_admin = True
    db.add(user)
    db.commit()


class TestAdminAccessControl:
    def test_non_admin_gets_403(self, client):
        client.post("/api/auth/register", json={"email": "regular@example.com", "password": "StrongPass1!"})
        resp = client.get("/api/admin/stats")
        assert resp.status_code == 403

    def test_anonymous_gets_401(self, client):
        resp = client.get("/api/admin/stats")
        assert resp.status_code == 401

    def test_admin_can_view_stats(self, client, db):
        client.post("/api/auth/register", json={"email": "admin1@example.com", "password": "StrongPass1!"})
        _promote_to_admin(db, "admin1@example.com")
        resp = client.get("/api/admin/stats")
        assert resp.status_code == 200
        assert resp.json()["total_users"] == 1


class TestAdminUserModeration:
    def test_admin_can_ban_and_unban_a_user(self, client, db):
        client.post("/api/auth/register", json={"email": "admin2@example.com", "password": "StrongPass1!"})
        _promote_to_admin(db, "admin2@example.com")

        target = TestClient(app)
        target.post("/api/auth/register", json={"email": "target@example.com", "password": "StrongPass1!"})
        target_id = target.get("/api/auth/me").json()["id"]

        ban_resp = client.patch(f"/api/admin/users/{target_id}", json={"is_banned": True})
        assert ban_resp.status_code == 200
        assert ban_resp.json()["is_banned"] is True

        login_resp = TestClient(app).post(
            "/api/auth/login", json={"email": "target@example.com", "password": "StrongPass1!"}
        )
        assert login_resp.status_code == 403

    def test_admin_cannot_unban_or_demote_self(self, client, db):
        client.post("/api/auth/register", json={"email": "admin3@example.com", "password": "StrongPass1!"})
        _promote_to_admin(db, "admin3@example.com")
        self_id = client.get("/api/auth/me").json()["id"]

        resp = client.patch(f"/api/admin/users/{self_id}", json={"is_admin": False})
        assert resp.status_code == 400

    def test_admin_can_delete_a_user_and_their_cases(self, client, db):
        client.post("/api/auth/register", json={"email": "admin4@example.com", "password": "StrongPass1!"})
        _promote_to_admin(db, "admin4@example.com")

        target = TestClient(app)
        target.post("/api/auth/register", json={"email": "deletable@example.com", "password": "StrongPass1!"})
        target_id = target.get("/api/auth/me").json()["id"]
        target.post("/api/cases", json={"title": "Will be cascade-deleted"})

        resp = client.delete(f"/api/admin/users/{target_id}")
        assert resp.status_code == 200

        # The deleted user can no longer authenticate
        relogin = TestClient(app).post(
            "/api/auth/login", json={"email": "deletable@example.com", "password": "StrongPass1!"}
        )
        assert relogin.status_code == 401


class TestAdminCaseModeration:
    def test_admin_can_see_and_hide_any_case(self, client, db):
        client.post("/api/auth/register", json={"email": "admin5@example.com", "password": "StrongPass1!"})
        _promote_to_admin(db, "admin5@example.com")

        owner = TestClient(app)
        owner.post("/api/auth/register", json={"email": "case-owner@example.com", "password": "StrongPass1!"})
        case = owner.post("/api/cases", json={"title": "Needs moderation", "is_public": True}).json()

        listed = client.get("/api/admin/cases")
        assert listed.status_code == 200
        assert any(c["id"] == case["id"] for c in listed.json())

        hide_resp = client.patch(f"/api/admin/cases/{case['id']}", json={"is_public": False})
        assert hide_resp.status_code == 200
        assert hide_resp.json()["is_public"] is False

    def test_admin_can_delete_any_case(self, client, db):
        client.post("/api/auth/register", json={"email": "admin6@example.com", "password": "StrongPass1!"})
        _promote_to_admin(db, "admin6@example.com")

        owner = TestClient(app)
        owner.post("/api/auth/register", json={"email": "case-owner2@example.com", "password": "StrongPass1!"})
        case = owner.post("/api/cases", json={"title": "Delete me"}).json()

        resp = client.delete(f"/api/admin/cases/{case['id']}")
        assert resp.status_code == 200
        assert owner.get(f"/api/cases/{case['id']}").status_code == 404
