import logging
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlmodel import Session, select

from app.api.deps import get_current_user, get_current_user_optional
from app.core.config import get_settings
from app.db.session import get_session
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.timeline import TimelineEvent
from app.models.user import User
from app.services.access import get_visible_case_optional_user
from app.services.ocr import extract_text_from_file
from app.services.storage import cleanup_local_copy_if_remote, save_upload_file
from app.services.timeline import generate_timeline_entries
from app.utils.file_validation import guess_file_type, is_allowed_filename

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    case = session.get(Case, case_id)
    if not case or case.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not file.filename or not is_allowed_filename(file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    # save_upload_file now returns (local_path, stored_filename, public_url)
    saved_path, stored_filename, public_url = await save_upload_file(file, current_user.id, case_id)
    extracted_text = extract_text_from_file(saved_path)
    cleanup_local_copy_if_remote(saved_path, public_url)

    evidence = Evidence(
        id=str(uuid4()),
        case_id=case_id,
        user_id=current_user.id,
        file_path=str(saved_path),
        file_name=stored_filename,
        file_type=guess_file_type(file.filename, file.content_type or "application/octet-stream"),
        extracted_text=extracted_text,
        public_url=public_url,
        metadata_json={
            "original_filename": file.filename,
            "content_type": file.content_type,
            "stored_remotely": public_url is not None,
        },
    )
    session.add(evidence)
    session.commit()
    session.refresh(evidence)

    generated_entries = generate_timeline_entries(extracted_text)
    for entry in generated_entries:
        timeline_event = TimelineEvent(
            id=str(uuid4()),
            case_id=case_id,
            event_text=str(entry["event_text"]),
            event_date=entry["event_date"],
            source_evidence_id=evidence.id,
        )
        session.add(timeline_event)
    session.commit()

    return {
        "detail": "Evidence uploaded",
        "evidence": {
            "id": evidence.id,
            "case_id": evidence.case_id,
            "user_id": evidence.user_id,
            "file_path": evidence.file_path,
            "file_name": evidence.file_name,
            "file_type": evidence.file_type,
            "extracted_text": evidence.extracted_text,
            "public_url": evidence.public_url,
            "metadata_json": evidence.metadata_json,
            "uploaded_at": evidence.uploaded_at.isoformat(),
        },
        "timeline_events_created": len(generated_entries),
    }


@router.get("/{evidence_id}/download")
async def download_evidence(
    evidence_id: str,
    disposition: Literal["attachment", "inline"] = "attachment",
    session: Session = Depends(get_session),
    current_user: User | None = Depends(get_current_user_optional),
):
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
    get_visible_case_optional_user(session, evidence.case_id, current_user)

    if evidence.public_url:
        if disposition == "inline":
            cached_path = await _get_or_fetch_cached_copy(evidence)
            if cached_path is not None:
                return FileResponse(cached_path, media_type=evidence.file_type)
        # Explicit download, or the inline proxy fetch failed — fall back to MEGA's own page.
        return RedirectResponse(evidence.public_url)

    local_path = Path(evidence.file_path)
    if not local_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File no longer available")
    if disposition == "inline":
        return FileResponse(local_path, media_type=evidence.file_type, content_disposition_type="inline")
    return FileResponse(local_path, filename=evidence.file_name)


@router.delete("/{evidence_id}", status_code=status.HTTP_200_OK)
async def delete_evidence(
    evidence_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")

    case = session.get(Case, evidence.case_id)
    if not case or case.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")

    # Remove any timeline events generated from this evidence — they have no
    # standalone meaning once their source is gone.
    orphaned_events = session.exec(
        select(TimelineEvent).where(TimelineEvent.source_evidence_id == evidence_id)
    ).all()
    for event in orphaned_events:
        session.delete(event)

    session.delete(evidence)
    session.commit()

    # Best-effort storage cleanup — the DB row is already gone either way, so
    # failures here are logged rather than surfaced as a user-facing error.
    if evidence.public_url:
        try:
            from app.services.mega_storage import delete_from_mega

            await delete_from_mega(evidence.public_url)
        except Exception as exc:
            logger.warning("Failed to delete MEGA file for evidence %s: %s", evidence_id, exc)
    else:
        local_path = Path(evidence.file_path)
        try:
            local_path.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning("Failed to delete local file for evidence %s: %s", evidence_id, exc)

    # Clean up any cached inline-preview copy too.
    settings = get_settings()
    cache_path = settings.uploads_dir / "_cache" / f"{evidence_id}{Path(evidence.file_name).suffix}"
    try:
        cache_path.unlink(missing_ok=True)
    except OSError:
        pass

    return {"detail": "Evidence deleted"}


async def _get_or_fetch_cached_copy(evidence: Evidence) -> Path | None:
    """Return a local, inline-servable copy of a MEGA-hosted evidence file, downloading
    and caching it on first request. Returns None if the fetch fails (caller should
    fall back to redirecting to the MEGA share link instead)."""
    settings = get_settings()
    suffix = Path(evidence.file_name).suffix
    cache_dir = settings.uploads_dir / "_cache"
    cache_filename = f"{evidence.id}{suffix}"
    cached_path = cache_dir / cache_filename
    if cached_path.exists():
        return cached_path

    try:
        from app.services.mega_storage import download_from_mega

        return await download_from_mega(evidence.public_url, cache_dir, cache_filename)
    except Exception as exc:
        logger.warning("Inline preview proxy fetch failed for evidence %s: %s", evidence.id, exc)
        return None
