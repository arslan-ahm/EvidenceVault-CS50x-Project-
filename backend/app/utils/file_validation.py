from pathlib import Path

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf", ".tif", ".tiff", ".txt", ".docx"}
ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "image/tiff",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def is_allowed_filename(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def guess_file_type(filename: str, content_type: str) -> str:
    suffix = Path(filename).suffix.lower()
    if content_type in ALLOWED_MIME_TYPES:
        return content_type
    return suffix.lstrip(".") or "unknown"
