from pathlib import Path


def test_upload_evidence_generates_timeline(client, monkeypatch, tmp_path: Path):
    client.post("/api/auth/register", json={"email": "upload@example.com", "password": "Password123!"})
    case_response = client.post("/api/cases", json={"title": "Upload case", "description": "Testing upload flow"})
    case_id = case_response.json()["id"]

    file_path = tmp_path / "sample.txt"
    file_path.write_text("2026-01-01 First event\n2026-01-03 Second event", encoding="utf-8")

    from app.api.routes import evidence as evidence_route

    async def fake_save_upload_file(upload_file, user_id: str, case_id: str):
        destination = tmp_path / f"{user_id}-{case_id}.txt"
        destination.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        return destination, destination.name

    monkeypatch.setattr(evidence_route, "save_upload_file", fake_save_upload_file)
    monkeypatch.setattr(evidence_route, "extract_text_from_file", lambda saved_path: file_path.read_text(encoding="utf-8"))

    with file_path.open("rb") as handle:
        response = client.post(
            "/api/evidence/upload",
            data={"case_id": case_id},
            files={"file": ("sample.txt", handle, "text/plain")},
        )

    assert response.status_code == 201
    assert response.json()["timeline_events_created"] == 2

    timeline_response = client.get(f"/api/cases/{case_id}/timeline")
    assert timeline_response.status_code == 200
    assert len(timeline_response.json()) == 2
