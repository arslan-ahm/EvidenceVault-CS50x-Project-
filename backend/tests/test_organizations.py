"""Tests for organization create (any authenticated user) and admin-only update/delete."""

from fastapi.testclient import TestClient
from sqlmodel import select

from app.main import app
from app.models.user import User


class TestOrganizations:
    def test_authenticated_user_can_create_organization(self, client):
        client.post("/api/auth/register", json={"email": "org-creator@example.com", "password": "StrongPass1!"})
        resp = client.post("/api/organizations", json={"name": "Acme Corp"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Acme Corp"
        assert data["slug"] == "acme-corp"

    def test_create_organization_requires_auth(self, client):
        resp = client.post("/api/organizations", json={"name": "No Auth Org"})
        assert resp.status_code == 401

    def test_create_organization_returns_existing_on_duplicate_name(self, client):
        client.post("/api/auth/register", json={"email": "org-dup@example.com", "password": "StrongPass1!"})
        first = client.post("/api/organizations", json={"name": "Dup Co"}).json()
        second = client.post("/api/organizations", json={"name": "Dup Co"}).json()
        assert first["id"] == second["id"]

    def test_non_admin_cannot_update_or_delete_organization(self, client):
        client.post("/api/auth/register", json={"email": "org-regular@example.com", "password": "StrongPass1!"})
        org = client.post("/api/organizations", json={"name": "Regular Co"}).json()

        update_resp = client.put(f"/api/organizations/{org['id']}", json={"name": "Hacked"})
        assert update_resp.status_code == 403

        delete_resp = client.delete(f"/api/organizations/{org['id']}")
        assert delete_resp.status_code == 403

    def test_admin_can_update_and_delete_organization(self, client, db):
        client.post("/api/auth/register", json={"email": "org-admin@example.com", "password": "StrongPass1!"})
        org = client.post("/api/organizations", json={"name": "Admin Managed Co"}).json()

        user = db.exec(select(User).where(User.email == "org-admin@example.com")).first()
        user.is_admin = True
        db.add(user)
        db.commit()

        update_resp = client.put(f"/api/organizations/{org['id']}", json={"name": "Renamed Co"})
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Renamed Co"

        delete_resp = client.delete(f"/api/organizations/{org['id']}")
        assert delete_resp.status_code == 200
