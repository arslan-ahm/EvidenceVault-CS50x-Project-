"""Tests for the comments API: create/list/delete on owned and public cases."""

from fastapi.testclient import TestClient

from app.main import app


class TestComments:
    def test_owner_can_comment_on_own_case(self, client):
        client.post("/api/auth/register", json={"email": "commenter@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "My case"}).json()

        resp = client.post(f"/api/cases/{case['id']}/comments", json={"body": "A note to self"})
        assert resp.status_code == 201
        assert resp.json()["body"] == "A note to self"

        listed = client.get(f"/api/cases/{case['id']}/comments")
        assert listed.status_code == 200
        assert len(listed.json()) == 1

    def test_visitor_can_comment_on_public_case_but_not_private(self, client):
        client.post("/api/auth/register", json={"email": "reporter@example.com", "password": "StrongPass1!"})
        public_case = client.post("/api/cases", json={"title": "Public case", "is_public": True}).json()
        private_case = client.post("/api/cases", json={"title": "Private case", "is_public": False}).json()

        visitor = TestClient(app)
        visitor.post("/api/auth/register", json={"email": "visitor@example.com", "password": "StrongPass1!"})

        ok = visitor.post(f"/api/cases/{public_case['id']}/comments", json={"body": "Nice find"})
        assert ok.status_code == 201

        blocked = visitor.post(f"/api/cases/{private_case['id']}/comments", json={"body": "Sneaky"})
        assert blocked.status_code == 404

    def test_comment_requires_auth(self, client):
        client.post("/api/auth/register", json={"email": "anon-owner@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Case"}).json()
        anon = TestClient(app)
        resp = anon.post(f"/api/cases/{case['id']}/comments", json={"body": "hi"})
        assert resp.status_code == 401

    def test_case_owner_can_delete_any_comment(self, client):
        client.post("/api/auth/register", json={"email": "mod-owner@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Moderated case"}).json()

        visitor = TestClient(app)
        visitor.post("/api/auth/register", json={"email": "mod-visitor@example.com", "password": "StrongPass1!"})
        comment = visitor.post(f"/api/cases/{case['id']}/comments", json={"body": "spam"}).json()

        resp = client.delete(f"/api/cases/{case['id']}/comments/{comment['id']}")
        assert resp.status_code == 200

    def test_stranger_cannot_delete_others_comment(self, client):
        client.post("/api/auth/register", json={"email": "victim@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Case"}).json()
        comment = client.post(f"/api/cases/{case['id']}/comments", json={"body": "mine"}).json()

        stranger = TestClient(app)
        stranger.post("/api/auth/register", json={"email": "stranger@example.com", "password": "StrongPass1!"})
        resp = stranger.delete(f"/api/cases/{case['id']}/comments/{comment['id']}")
        assert resp.status_code == 403
