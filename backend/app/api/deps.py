from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlmodel import Session

from app.core.config import get_settings
from app.core.security import decode_token, decode_supabase_token
from app.db.session import get_session
from app.models.user import User


def get_current_user(
    session: Session = Depends(get_session),
    token_cookie: str | None = Cookie(default=None, alias=get_settings().cookie_name),
    authorization: str | None = Header(default=None),
) -> User:
    settings = get_settings()

    token = token_cookie
    if not token and authorization:
        if authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = None
    # Try local HS256 app token first
    try:
        payload = decode_token(token)
    except Exception:
        # If Supabase JWKS is configured, try verifying as a Supabase token
        if settings.supabase_jwks_url:
            try:
                payload = decode_supabase_token(token)
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = session.get(User, user_id)
    # If a Supabase token was used and the user does not exist locally, create a placeholder user
    if not user and settings.supabase_jwks_url and payload.get("email"):
        new_user = User(id=user_id, email=payload.get("email"), hashed_password="")
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        user = new_user

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def get_current_user_optional(
    session: Session = Depends(get_session),
    token_cookie: str | None = Cookie(default=None, alias=get_settings().cookie_name),
    authorization: str | None = Header(default=None),
) -> User | None:
    """Like get_current_user, but returns None instead of raising when unauthenticated
    or the token is invalid — for endpoints that serve both public and private content."""
    if not token_cookie and not authorization:
        return None
    try:
        return get_current_user(session=session, token_cookie=token_cookie, authorization=authorization)
    except HTTPException:
        return None
