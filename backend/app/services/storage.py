"""Storage service — routes evidence uploads through MEGA or local disk.

When MEGA_UPLOADS_EMAIL / MEGA_UPLOADS_PASSWORD are set, files are uploaded to
MEGA and a shareable link is returned. Otherwise files are saved to the local
`uploads/` directory, preserving the original behaviour.
"""

from __future__ import annotations

import logging
from pathlib import Path
from secrets import token_hex

from fastapi import UploadFile

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# ── Local disk helpers ─────────────────────────────────────────────────────────

def build_case_upload_dir(user_id: str, case_id: str) -> Path:
    settings = get_settings()
    directory = settings.uploads_dir / user_id / case_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _local_safe_name(original_filename: str) -> str:
    suffix = Path(original_filename).suffix.lower()
    return f"{token_hex(16)}{suffix}"


async def _save_local(upload_file: UploadFile, user_id: str, case_id: str, content: bytes) -> tuple[Path, str]:
    """Write bytes to local disk and return (path, filename)."""
    directory = build_case_upload_dir(user_id, case_id)
    safe_name = _local_safe_name(upload_file.filename or "file")
    destination = directory / safe_name
    while destination.exists():
        safe_name = _local_safe_name(upload_file.filename or "file")
        destination = directory / safe_name
    destination.write_bytes(content)
    return destination, safe_name


# ── Public API ─────────────────────────────────────────────────────────────────

async def save_upload_file(
    upload_file: UploadFile,
    user_id: str,
    case_id: str,
) -> tuple[Path, str, str | None]:
    """Save an uploaded file and return (local_path, stored_filename, public_url).

    - ``local_path`` — always a valid local Path (used for OCR processing).
      When MEGA is active this is a *temporary* local copy in the uploads directory.
    - ``stored_filename`` — the basename without path.
    - ``public_url`` — ``None`` when using local storage; a MEGA link otherwise.
    """
    settings = get_settings()
    content = await upload_file.read()

    local_path, stored_filename = await _save_local(upload_file, user_id, case_id, content)

    public_url: str | None = None

    if settings.mega_enabled:
        try:
            from app.services.mega_storage import build_mega_evidence_filename, upload_to_mega
            remote_filename = build_mega_evidence_filename(user_id, case_id, upload_file.filename or stored_filename)
            public_url = await upload_to_mega(local_path, remote_filename)
            logger.info("Uploaded %s to MEGA as %s", stored_filename, remote_filename)
        except Exception as exc:
            logger.warning("MEGA upload failed, falling back to local storage: %s", exc)
            public_url = None

    return local_path, stored_filename, public_url


def cleanup_local_copy_if_remote(local_path: Path, public_url: str | None) -> None:
    """Remove the temporary local copy once it has been durably stored remotely.

    Only called after OCR has already read the local file — remotely-backed
    evidence would otherwise be stored twice (locally and remotely) forever.
    """
    if public_url is None:
        return
    try:
        local_path.unlink(missing_ok=True)
    except OSError:
        logger.warning("Failed to remove local temp copy %s", local_path)


# ── Avatar images ──────────────────────────────────────────────────────────────

def build_avatar_dir(user_id: str) -> Path:
    settings = get_settings()
    directory = settings.uploads_dir / "avatars" / user_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory


async def save_avatar_file(upload_file: UploadFile, user_id: str) -> str:
    """Save a profile image locally and return a servable URL.

    Avatars are always kept on local disk, never uploaded to MEGA: MEGA's
    shareable links (``mega.co.nz/#!id!key``) are web-viewer links that require
    client-side JS to decrypt — they cannot be used as an ``<img src>`` value,
    unlike R2/S3-style URLs that serve raw bytes directly. Evidence downloads
    are a good fit for MEGA (the browser fully navigates through the link);
    inline avatar images are not.
    """
    settings = get_settings()
    content = await upload_file.read()

    directory = build_avatar_dir(user_id)
    safe_name = _local_safe_name(upload_file.filename or "avatar")
    destination = directory / safe_name
    while destination.exists():
        safe_name = _local_safe_name(upload_file.filename or "avatar")
        destination = directory / safe_name
    destination.write_bytes(content)

    return f"{settings.public_api_base_url.rstrip('/')}/auth/profile-image/{user_id}/{safe_name}"
