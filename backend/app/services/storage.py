from __future__ import annotations

from pathlib import Path
from secrets import token_hex

from fastapi import UploadFile

from app.core.config import get_settings


def build_case_upload_dir(user_id: str, case_id: str) -> Path:
    settings = get_settings()
    directory = settings.uploads_dir / user_id / case_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory


async def save_upload_file(upload_file: UploadFile, user_id: str, case_id: str) -> tuple[Path, str]:
    directory = build_case_upload_dir(user_id, case_id)
    original_suffix = Path(upload_file.filename or "").suffix.lower()
    safe_name = f"{token_hex(16)}{original_suffix}"
    destination = directory / safe_name
    while destination.exists():
        safe_name = f"{token_hex(16)}{original_suffix}"
        destination = directory / safe_name
    content = await upload_file.read()
    destination.write_bytes(content)
    return destination, safe_name
