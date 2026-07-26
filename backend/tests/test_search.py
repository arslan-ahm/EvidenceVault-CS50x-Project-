"""Tests for the search endpoint: GET /api/search?q=..."""

from io import BytesIO


class TestSearch:
    def test_search_no_results(self, client):
        """Search with no matching content returns empty list."""
        client.post("/api/auth/register", json={
            "email": "search-empty@example.com",
            "password": "StrongPass1!",
        })
        resp = client.get("/api/search?q=nonexistent")
        assert resp.status_code == 200
        assert resp.json().get("results", []) == []

    def test_search_requires_auth(self, client):
        """Search without authentication returns 401."""
        resp = client.get("/api/search?q=anything")
        assert resp.status_code == 401

    def test_search_empty_query(self, client):
        """Empty query returns 422 or empty results."""
        client.post("/api/auth/register", json={
            "email": "search-empty-q@example.com",
            "password": "StrongPass1!",
        })
        resp = client.get("/api/search?q=")
        # The router may require a minimum query length
        assert resp.status_code in (200, 400, 422)
