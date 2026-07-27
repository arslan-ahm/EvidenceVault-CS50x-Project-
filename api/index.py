"""Vercel serverless entrypoint — exposes the FastAPI app from backend/app.

Vercel's Python runtime auto-detects any `app` object in `api/*.py` and
serves it as an ASGI function. This file just points at the real app so the
`backend/` package doesn't need to be restructured.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402
