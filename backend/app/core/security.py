from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any
import json
import urllib.request

import bcrypt
from jose import jwt, jwk
from jose.utils import base64url_decode

from app.core.config import get_settings


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": now,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode a locally-signed HS256 token created by this app."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


@lru_cache(maxsize=1)
def _fetch_jwks(jwks_url: str) -> dict[str, Any]:
    with urllib.request.urlopen(jwks_url) as resp:
        return json.load(resp)


def decode_supabase_token(token: str) -> dict[str, Any]:
    """
    Verify a Supabase/Auth (RS256) JWT using the JWKS endpoint and return claims.

    This function performs signature verification against the JWKS and basic
    expiry checking, then returns the token claims. It raises on invalid
    signature or expired tokens.
    """
    settings = get_settings()
    if not settings.supabase_jwks_url:
        raise RuntimeError("Supabase JWKS URL not configured")

    jwks = _fetch_jwks(settings.supabase_jwks_url)
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    key_dict = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key_dict:
        raise RuntimeError("Unable to find matching JWKS key")

    public_key = jwk.construct(key_dict)
    signing_input, encoded_sig = token.rsplit(".", 1)
    decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))
    if not public_key.verify(signing_input.encode("utf-8"), decoded_sig):
        raise RuntimeError("Invalid token signature")

    claims = jwt.get_unverified_claims(token)
    exp = claims.get("exp")
    now_ts = datetime.now(timezone.utc).timestamp()
    if exp and now_ts > exp:
        raise RuntimeError("Token is expired")
    return claims
