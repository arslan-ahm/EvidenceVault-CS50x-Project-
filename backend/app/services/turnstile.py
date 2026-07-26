"""Cloudflare Turnstile server-side verification service.

Usage in route handlers:
    from app.services.turnstile import verify_turnstile_token
    ...
    if settings.turnstile_enabled:
        await verify_turnstile_token(token)   # raises HTTPException on failure

The verification endpoint is:
    https://challenges.cloudflare.com/turnstile/v0/siteverify

Reference: https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
"""

from __future__ import annotations

import logging
import urllib.parse
import urllib.request

import json

from fastapi import HTTPException, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile_token(token: str | None, remote_ip: str | None = None) -> bool:
    """Verify a Turnstile challenge token with Cloudflare's API.

    Returns True on success.  Raises HTTPException 422 on failure.
    If Turnstile is not configured (secret not set), skips verification and returns True.

    Args:
        token: The ``cf-turnstile-response`` value sent from the frontend widget.
        remote_ip: Optional client IP to include in the verification request.
    """
    settings = get_settings()

    if not settings.turnstile_enabled:
        return True  # gracefully skip when not configured

    if not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CAPTCHA token is required",
        )

    data: dict = {
        "secret": settings.cloudflare_turnstile_secret,
        "response": token,
    }
    if remote_ip:
        data["remoteip"] = remote_ip

    encoded = urllib.parse.urlencode(data).encode("utf-8")

    try:
        req = urllib.request.Request(
            TURNSTILE_VERIFY_URL,
            data=encoded,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.warning("Turnstile verification request failed: %s", exc)
        # On network failure, fail open (don't block users if Cloudflare is down)
        return True

    if not result.get("success"):
        error_codes = result.get("error-codes", [])
        logger.info("Turnstile verification failed: %s", error_codes)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CAPTCHA verification failed. Please try again.",
        )

    return True
