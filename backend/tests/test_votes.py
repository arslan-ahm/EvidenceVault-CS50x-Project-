"""Tests for the upvote toggle endpoint."""

from fastapi.testclient import TestClient

from app.main import app


class TestVotes:
    def test_toggle_upvote_on_public_case(self, client):
        client.post("/api/auth/register", json={"email": "vote-owner@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Votable case", "is_public": True}).json()

        voter = TestClient(app)
        voter.post("/api/auth/register", json={"email": "voter@example.com", "password": "StrongPass1!"})

        first = voter.post(f"/api/cases/{case['id']}/upvote")
        assert first.status_code == 200
        assert first.json() == {"upvoted": True, "upvotes_count": 1}

        second = voter.post(f"/api/cases/{case['id']}/upvote")
        assert second.status_code == 200
        assert second.json() == {"upvoted": False, "upvotes_count": 0}

    def test_cannot_upvote_private_case(self, client):
        client.post("/api/auth/register", json={"email": "private-owner@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Private case", "is_public": False}).json()

        voter = TestClient(app)
        voter.post("/api/auth/register", json={"email": "private-voter@example.com", "password": "StrongPass1!"})
        resp = voter.post(f"/api/cases/{case['id']}/upvote")
        assert resp.status_code == 404

    def test_upvote_requires_auth(self, client):
        client.post("/api/auth/register", json={"email": "no-auth-owner@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Case", "is_public": True}).json()
        anon = TestClient(app)
        resp = anon.post(f"/api/cases/{case['id']}/upvote")
        assert resp.status_code == 401
