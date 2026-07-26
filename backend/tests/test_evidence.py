"""Tests for evidence upload endpoint: /api/evidence/upload."""

from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


class TestEvidenceUpload:
    def test_upload_txt(self, client, uploaded_file):
        """Upload a .txt evidence file attaches to case and returns metadata."""
        client.post("/api/auth/register", json={
            "email": "upload-txt@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Upload Target"}).json()

        with open(uploaded_file, "rb") as f:
            resp = client.post(
                "/api/evidence/upload",
                data={"case_id": case["id"]},
                files={"file": ("report.txt", f, "text/plain")},
            )
        assert resp.status_code == 201
        data = resp.json()
        ev = data["evidence"]
        # file_name is stored as a randomized token, so just check it ends with .txt
        assert ev["file_name"].endswith(".txt")
        assert ev["metadata_json"]["original_filename"] == "report.txt"
        assert ev["metadata_json"]["content_type"] == "text/plain"
        assert ev["case_id"] == case["id"]
        assert "id" in ev

    def test_upload_pdf(self, client):
        """Upload a minimal valid PDF."""
        client.post("/api/auth/register", json={
            "email": "upload-pdf@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "PDF Case"}).json()

        # Minimal valid PDF (just enough header + EOF marker)
        minimal_pdf = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<>>\nstartxref\n0\n%%EOF"

        resp = client.post(
            "/api/evidence/upload",
            data={"case_id": case["id"]},
            files={"file": ("doc.pdf", BytesIO(minimal_pdf), "application/pdf")},
        )
        assert resp.status_code == 201
        ev = resp.json()["evidence"]
        assert ev["file_name"].endswith(".pdf")
        assert ev["metadata_json"]["original_filename"] == "doc.pdf"

    def test_upload_image(self, client):
        """Upload a .png image file (1x1 px minimal PNG)."""
        client.post("/api/auth/register", json={
            "email": "upload-img@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Image Case"}).json()

        # Minimal 1x1 red PNG (valid PNG header + IDAT + IEND)
        minimal_png = (
            b"\x89PNG\r\n\x1a\n"  # signature
            b"\x00\x00\x00\x0dIHDR"  # IHDR chunk
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"  # 1x1, 8-bit RGB
            b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\x0f\x00\x00\x00\x00\xff\xff\x03\x00\x00\x04\x00\x01\x0c\x0c\x0c"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"  # IEND
        )

        resp = client.post(
            "/api/evidence/upload",
            data={"case_id": case["id"]},
            files={"file": ("screenshot.png", BytesIO(minimal_png), "image/png")},
        )
        assert resp.status_code == 201
        ev = resp.json()["evidence"]
        assert ev["file_name"].endswith(".png")
        assert ev["metadata_json"]["original_filename"] == "screenshot.png"

    def test_upload_no_case_id(self, client):
        """Upload without case_id returns 422 or 400."""
        client.post("/api/auth/register", json={
            "email": "no-caseid@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post(
            "/api/evidence/upload",
            files={"file": ("test.txt", BytesIO(b"hello"), "text/plain")},
        )
        assert resp.status_code in (400, 422)

    def test_upload_invalid_case_id(self, client):
        """Upload to non-existent case returns 404."""
        client.post("/api/auth/register", json={
            "email": "bad-case@example.com",
            "password": "StrongPass1!",
        })
        resp = client.post(
            "/api/evidence/upload",
            data={"case_id": "nonexistent"},
            files={"file": ("test.txt", BytesIO(b"hello"), "text/plain")},
        )
        assert resp.status_code == 404

    def test_upload_not_owned_case(self, client):
        """Upload to another user's case returns 404."""
        # Register user A and create a case
        client.post("/api/auth/register", json={
            "email": "evidence-owner@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Owner Case"}).json()

        # Register user B and try to upload to A's case
        from fastapi.testclient import TestClient
        from app.main import app
        intruder = TestClient(app)
        intruder.post("/api/auth/register", json={
            "email": "evidence-intruder@example.com",
            "password": "StrongPass1!",
        })
        resp = intruder.post(
            "/api/evidence/upload",
            data={"case_id": case["id"]},
            files={"file": ("hack.txt", BytesIO(b"pwned"), "text/plain")},
        )
        assert resp.status_code == 404

    def test_upload_empty_file(self, client):
        """Uploading an empty file may succeed or fail gracefully."""
        client.post("/api/auth/register", json={
            "email": "empty-file@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Empty Upload"}).json()

        resp = client.post(
            "/api/evidence/upload",
            data={"case_id": case["id"]},
            files={"file": ("empty.txt", BytesIO(b""), "text/plain")},
        )
        # Depending on validation, could be 201 or 422
        assert resp.status_code in (201, 400, 422)

    def test_upload_requires_auth(self, client):
        """Upload without authentication returns 401."""
        resp = client.post(
            "/api/evidence/upload",
            data={"case_id": "x"},
            files={"file": ("x.txt", BytesIO(b"x"), "text/plain")},
        )
        assert resp.status_code == 401

    def test_upload_generates_timeline(self, client, uploaded_file):
        """Uploading a .txt with date lines creates timeline entries."""
        client.post("/api/auth/register", json={
            "email": "timeline-gen@example.com",
            "password": "StrongPass1!",
        })
        case = client.post("/api/cases", json={"title": "Timeline Gen"}).json()

        with open(uploaded_file, "rb") as f:
            client.post(
                "/api/evidence/upload",
                data={"case_id": case["id"]},
                files={"file": ("dates.txt", f, "text/plain")},
            )

        # Check timeline was generated
        tl = client.get(f"/api/cases/{case['id']}/timeline")
        assert tl.status_code == 200
        events = tl.json()
        assert len(events) >= 2
        dates = {e["event_date"] for e in events}
        assert "2026-01-01" in dates
        assert "2026-01-02" in dates


class TestEvidenceStorageFallback:
    def test_upload_uses_local_storage_when_mega_not_configured(self, client, uploaded_file):
        """Regression guard: tests must never silently upload to a real MEGA account.

        conftest.py forces MEGA_UPLOADS_EMAIL/PASSWORD empty; this asserts that
        actually took effect (public_url stays None, i.e. the local-disk path).
        """
        client.post("/api/auth/register", json={"email": "storage-fallback@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Fallback Case"}).json()
        with open(uploaded_file, "rb") as f:
            resp = client.post(
                "/api/evidence/upload",
                data={"case_id": case["id"]},
                files={"file": ("report.txt", f, "text/plain")},
            )
        ev = resp.json()["evidence"]
        assert ev["public_url"] is None
        assert ev["metadata_json"]["stored_remotely"] is False


class TestEvidenceDownload:
    def test_owner_can_download_own_evidence(self, client, uploaded_file):
        client.post("/api/auth/register", json={"email": "dl-owner@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Downloadable"}).json()
        with open(uploaded_file, "rb") as f:
            upload = client.post(
                "/api/evidence/upload",
                data={"case_id": case["id"]},
                files={"file": ("report.txt", f, "text/plain")},
            ).json()

        resp = client.get(f"/api/evidence/{upload['evidence']['id']}/download")
        assert resp.status_code == 200
        assert resp.content

    def test_stranger_cannot_download_private_case_evidence(self, client, uploaded_file):
        client.post("/api/auth/register", json={"email": "dl-private@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Private", "is_public": False}).json()
        with open(uploaded_file, "rb") as f:
            upload = client.post(
                "/api/evidence/upload",
                data={"case_id": case["id"]},
                files={"file": ("report.txt", f, "text/plain")},
            ).json()

        stranger = TestClient(app)
        stranger.post("/api/auth/register", json={"email": "dl-stranger@example.com", "password": "StrongPass1!"})
        resp = stranger.get(f"/api/evidence/{upload['evidence']['id']}/download")
        assert resp.status_code == 404

    def test_download_nonexistent_evidence_returns_404(self, client):
        resp = client.get("/api/evidence/nonexistent/download")
        assert resp.status_code == 404

    def test_anonymous_can_download_public_case_evidence(self, client, uploaded_file):
        client.post("/api/auth/register", json={"email": "dl-public@example.com", "password": "StrongPass1!"})
        case = client.post("/api/cases", json={"title": "Public", "is_public": True}).json()
        with open(uploaded_file, "rb") as f:
            upload = client.post(
                "/api/evidence/upload",
                data={"case_id": case["id"]},
                files={"file": ("report.txt", f, "text/plain")},
            ).json()

        anon = TestClient(app)
        resp = anon.get(f"/api/evidence/{upload['evidence']['id']}/download")
        assert resp.status_code == 200
