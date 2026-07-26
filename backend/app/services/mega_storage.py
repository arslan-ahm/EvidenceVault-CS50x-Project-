"""MEGA storage service (via the unofficial `mega.py` package).

When MEGA_UPLOADS_EMAIL / MEGA_UPLOADS_PASSWORD are configured, evidence files
are uploaded to the account's MEGA drive and a shareable link is returned.
Otherwise the storage layer falls back to local disk. Avatars are always kept
local (see storage.save_avatar_file for why).

Compatibility note: `mega.py` pins `tenacity<6.0.0`, and tenacity 5.x imports
`asyncio.coroutine` at module load time — removed in Python 3.11+. Forcing a
newer tenacity in pyproject.toml makes pip's resolver backtrack to an older
mega.py release that depends on the unmaintained `pycrypto` package (which
fails to build here). Instead we let `mega.py` install with its natural,
cleanly-resolvable dependencies and patch the missing attribute ourselves —
the async retry path this shim stands in for is never exercised by mega.py's
own (synchronous) usage of tenacity.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path
from secrets import token_hex

import anyio

if not hasattr(asyncio, "coroutine"):
    asyncio.coroutine = lambda func: func  # type: ignore[attr-defined]

logger = logging.getLogger(__name__)

_client = None
_client_lock = threading.Lock()


def _get_client():
    global _client
    if _client is not None:
        return _client
    with _client_lock:
        if _client is None:
            from app.core.config import get_settings
            from mega import Mega

            settings = get_settings()
            mega = Mega()
            _client = mega.login(settings.mega_uploads_email, settings.mega_uploads_password)
    return _client


def _upload_sync(local_path: Path, remote_filename: str) -> str:
    client = _get_client()
    try:
        uploaded = client.upload(str(local_path), dest_filename=remote_filename)
        return client.get_upload_link(uploaded)
    except Exception:
        # A stale/broken session shouldn't wedge every future upload.
        global _client
        _client = None
        raise


def _delete_sync(url: str) -> bool:
    try:
        client = _get_client()
        client.destroy_url(url)
        return True
    except Exception as exc:
        logger.warning("MEGA delete failed for %s: %s", url, exc)
        return False


def _download_sync(url: str, dest_dir: Path, dest_filename: str) -> Path:
    client = _get_client()
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        result_path = client.download_url(url, dest_path=str(dest_dir), dest_filename=dest_filename)
        return Path(result_path)
    except Exception:
        global _client
        _client = None
        raise


async def upload_to_mega(local_path: Path, remote_filename: str) -> str:
    """Upload a local file to MEGA and return a shareable link."""
    return await anyio.to_thread.run_sync(_upload_sync, local_path, remote_filename)


async def download_from_mega(url: str, dest_dir: Path, dest_filename: str) -> Path:
    """Download a MEGA-hosted file (by public share link) to a local path for inline preview.

    Used to proxy evidence stored on MEGA so it can be embedded (<img>/<iframe>) the same way
    as locally-stored evidence — MEGA share links themselves cannot be used as an embed src.
    """
    return await anyio.to_thread.run_sync(_download_sync, url, dest_dir, dest_filename)


async def delete_from_mega(url: str) -> bool:
    """Delete a file from MEGA by its public share link. Returns True on success."""
    return await anyio.to_thread.run_sync(_delete_sync, url)


def build_mega_evidence_filename(user_id: str, case_id: str, filename: str) -> str:
    """Build a collision-safe filename that encodes user/case (MEGA has no key/prefix concept)."""
    suffix = Path(filename).suffix.lower()
    return f"evidence_{user_id}_{case_id}_{token_hex(8)}{suffix}"
