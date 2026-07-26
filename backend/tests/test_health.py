"""Tests for the /api/health endpoint."""


def test_health_check(client):
    """GET /api/health should return {'status': 'ok'}."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
