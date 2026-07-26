"""Tests for case CRUD endpoints: create, list, get, update, delete cases,
list evidence, list timeline, and export PDF."""


class TestCreateCase:
    def test_create_case(self, client):
        """POST /api/cases creates a case for the authenticated user."""
        client.post("/api/auth/register", json={
            "email": "create-case@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post("/api/cases", json={
            "title": "New Investigation",
            "description": "Testing case creation",
            "category": "malware",
            "severity": "critical",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "New Investigation"
        assert data["description"] == "Testing case creation"
        assert data["category"] == "malware"
        assert data["severity"] == "critical"
        assert data["status"] == "open"
        assert "id" in data
        assert "created_at" in data

    def test_create_case_minimal(self, client):
        """Create case with only required fields."""
        client.post("/api/auth/register", json={
            "email": "minimal-case@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post("/api/cases", json={"title": "Minimal Case"})
        assert resp.status_code == 201
        assert resp.json()["title"] == "Minimal Case"

    def test_create_case_requires_auth(self, client):
        """POST /api/cases without auth returns 401."""
        resp = client.post("/api/cases", json={"title": "Unauthorized"})
        assert resp.status_code == 401


class TestListCases:
    def test_list_empty(self, client):
        """User with no cases gets an empty list."""
        client.post("/api/auth/register", json={
            "email": "no-cases@example.com",
            "password": "StrongPass1!",
        })
        resp = client.get("/api/cases")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_own_cases(self, client):
        """User sees only their own cases."""
        client.post("/api/auth/register", json={
            "email": "list-cases@example.com",
            "password": "StrongPass1!",
        })
        client.post("/api/cases", json={"title": "Case A"})
        client.post("/api/cases", json={"title": "Case B"})
        resp = client.get("/api/cases")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        titles = {c["title"] for c in data}
        assert titles == {"Case A", "Case B"}

    def test_list_requires_auth(self, client):
        """GET /api/cases without auth returns 401."""
        resp = client.get("/api/cases")
        assert resp.status_code == 401


class TestGetCase:
    def test_get_case(self, client):
        """GET /api/cases/{id} returns the case."""
        client.post("/api/auth/register", json={
            "email": "get-case@example.com",
            "password": "StrongPass1!",
        })
        created = client.post("/api/cases", json={"title": "Target Case"}).json()

        resp = client.get(f"/api/cases/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Target Case"

    def test_get_case_not_found(self, client):
        """Non-existent case ID returns 404."""
        client.post("/api/auth/register", json={
            "email": "not-found@example.com",
            "password": "StrongPass1!",
        })
        resp = client.get("/api/cases/nonexistent-id")
        assert resp.status_code == 404

    def test_get_case_not_owned(self, client):
        """Case owned by another user returns 404 (scoped)."""
        # Register user A and create a case
        client.post("/api/auth/register", json={
            "email": "owner@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Owner's Case"}).json()

        # Logout (cookie cleared, need to manage via new client)
        import httpx
        from app.main import app
        from fastapi.testclient import TestClient

        # Register user B
        new_client = TestClient(app)
        new_client.post("/api/auth/register", json={
            "email": "intruder@example.com",
            "password": "StrongPass1!",
        })
        resp = new_client.get(f"/api/cases/{case['id']}")
        assert resp.status_code == 404


class TestUpdateCase:
    def test_update_case(self, client):
        """PUT /api/cases/{id} updates case fields."""
        client.post("/api/auth/register", json={
            "email": "updater@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Original"}).json()

        resp = client.put(f"/api/cases/{case['id']}", json={
            "title": "Updated",
            "description": "New description",
            "status": "resolved",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated"
        assert data["description"] == "New description"
        assert data["status"] == "resolved"

    def test_update_case_not_found(self, client):
        """Update non-existent case returns 404."""
        client.post("/api/auth/register", json={
            "email": "update-404@example.com",
            "password": "StrongPass1!",
        })
        resp = client.put("/api/cases/bad-id", json={"title": "Nope"})
        assert resp.status_code == 404

    def test_update_case_not_owned(self, client):
        """Update another user's case returns 404."""
        client.post("/api/auth/register", json={
            "email": "update-owner@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Mine"}).json()

        from fastapi.testclient import TestClient
        from app.main import app
        intruder = TestClient(app)
        intruder.post("/api/auth/register", json={
            "email": "update-intruder@example.com",
            "password": "StrongPass1!",
        })
        resp = intruder.put(f"/api/cases/{case['id']}", json={"title": "Hacked"})
        assert resp.status_code == 404

    def test_update_case_requires_auth(self, client):
        """PUT /api/cases/{id} without auth returns 401."""
        resp = client.put("/api/cases/some-id", json={"title": "X"})
        assert resp.status_code == 401


class TestDeleteCase:
    def test_delete_case(self, client):
        """DELETE /api/cases/{id} deletes the case."""
        client.post("/api/auth/register", json={
            "email": "deleter@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Delete Me"}).json()

        resp = client.delete(f"/api/cases/{case['id']}")
        assert resp.status_code == 200

        # Verify it's gone
        resp = client.get(f"/api/cases/{case['id']}")
        assert resp.status_code == 404

    def test_delete_case_not_found(self, client):
        """Delete non-existent case returns 404."""
        client.post("/api/auth/register", json={
            "email": "delete-404@example.com",
            "password": "StrongPass1!",
        })
        resp = client.delete("/api/cases/bad-id")
        assert resp.status_code == 404

    def test_delete_case_not_owned(self, client):
        """Delete another user's case returns 404."""
        client.post("/api/auth/register", json={
            "email": "delete-owner@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Hands Off"}).json()

        from fastapi.testclient import TestClient
        from app.main import app
        intruder = TestClient(app)
        intruder.post("/api/auth/register", json={
            "email": "delete-intruder@example.com",
            "password": "StrongPass1!",
        })
        resp = intruder.delete(f"/api/cases/{case['id']}")
        assert resp.status_code == 404


class TestCaseEvidence:
    def test_list_evidence_empty(self, client):
        """No evidence for a case returns empty list."""
        client.post("/api/auth/register", json={
            "email": "evidence-empty@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "No Evidence Yet"}).json()
        resp = client.get(f"/api/cases/{case['id']}/evidence")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_evidence_requires_auth(self, client):
        """Evidence endpoint requires authentication."""
        resp = client.get("/api/cases/some-id/evidence")
        assert resp.status_code == 401


class TestCaseTimeline:
    def test_list_timeline_empty(self, client):
        """No timeline events returns empty list."""
        client.post("/api/auth/register", json={
            "email": "tl-empty@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "No Timeline"}).json()
        resp = client.get(f"/api/cases/{case['id']}/timeline")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_timeline_requires_auth(self, client):
        """Timeline endpoint requires authentication."""
        resp = client.get("/api/cases/some-id/timeline")
        assert resp.status_code == 401


class TestCaseExport:
    def test_export_pdf(self, client):
        """GET /api/cases/{id}/export returns a PDF file."""
        client.post("/api/auth/register", json={
            "email": "export@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Exportable Case"}).json()

        resp = client.get(f"/api/cases/{case['id']}/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert len(resp.content) > 100  # Some PDF content exists

    def test_export_nonexistent_case(self, client):
        """Export non-existent case returns 404."""
        client.post("/api/auth/register", json={
            "email": "export-404@example.com",
            "password": "StrongPass1!",
        })
        resp = client.get("/api/cases/bad-id/export")
        assert resp.status_code == 404

    def test_export_requires_auth(self, client):
        """Export endpoint requires authentication."""
        resp = client.get("/api/cases/some-id/export")
        assert resp.status_code == 401
