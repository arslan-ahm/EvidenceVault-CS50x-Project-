from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_session
from app.models.user import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    User,
    UserCreate,
    UserLogin,
    UserPublic,
    UserUpdate,
)
from app.services.account import delete_user_cascade
from app.services.email import (
    send_change_password_notification,
    send_password_reset_email,
    send_welcome_email,
)
from app.services.storage import save_avatar_file
from app.services.turnstile import verify_turnstile_token

router = APIRouter()


def _set_auth_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


class UserCreateWithCaptcha(UserCreate):
    """Extended registration payload that includes an optional Turnstile token."""
    cf_turnstile_response: str | None = None


class UserLoginWithCaptcha(UserLogin):
    """Extended login payload that includes an optional Turnstile token."""
    cf_turnstile_response: str | None = None


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreateWithCaptcha,
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
) -> UserPublic:
    # Verify Turnstile CAPTCHA (no-op when secret not configured)
    client_ip = request.client.host if request.client else None
    verify_turnstile_token(payload.cf_turnstile_response, client_ip)

    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        id=str(uuid4()),
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        name=payload.name or "",
        occupation=payload.occupation,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token(user.id, {"email": user.email})
    _set_auth_cookie(response, token)
    # Send welcome email in the background (best-effort)
    if user.name:
        send_welcome_email(user.email, user.name)
    return UserPublic(
        id=user.id,
        email=user.email,
        name=user.name,
        occupation=user.occupation,
        profile_image_url=user.profile_image_url,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


@router.post("/login", response_model=UserPublic)
def login(
    payload: UserLoginWithCaptcha,
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
) -> UserPublic:
    # Verify Turnstile CAPTCHA (no-op when secret not configured)
    client_ip = request.client.host if request.client else None
    verify_turnstile_token(payload.cf_turnstile_response, client_ip)

    user = session.exec(select(User).where(User.email == payload.email.lower())).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    token = create_access_token(user.id, {"email": user.email})
    _set_auth_cookie(response, token)
    return UserPublic(
        id=user.id,
        email=user.email,
        name=user.name,
        occupation=user.occupation,
        profile_image_url=user.profile_image_url,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    settings = get_settings()
    response.delete_cookie(key=settings.cookie_name, path="/")
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserPublic)
def read_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        occupation=current_user.occupation,
        profile_image_url=current_user.profile_image_url,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
    )


@router.put("/profile", response_model=UserPublic)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserPublic:
    if payload.name is not None:
        current_user.name = payload.name
    if payload.occupation is not None:
        current_user.occupation = payload.occupation
    if payload.profile_image_url is not None:
        current_user.profile_image_url = payload.profile_image_url
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        occupation=current_user.occupation,
        profile_image_url=current_user.profile_image_url,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
    )


@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    user = session.exec(select(User).where(User.email == payload.email.lower())).first()
    # Always return success to avoid email enumeration
    if not user:
        return {"detail": "If that email exists, a reset link has been sent."}

    from uuid import uuid4

    token = str(uuid4()) + str(uuid4()).replace("-", "")
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc).replace(hour=datetime.now(timezone.utc).hour + 1)
    session.add(user)
    session.commit()

    send_password_reset_email(user.email, token)
    return {"detail": "If that email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(
    payload: ResetPasswordRequest,
    session: Session = Depends(get_session),
) -> dict[str, str]:
    user = session.exec(select(User).where(User.reset_token == payload.token)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    if user.reset_token_expires and user.reset_token_expires < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired")

    user.hashed_password = hash_password(payload.password)
    user.reset_token = None
    user.reset_token_expires = None
    session.add(user)
    session.commit()

    return {"detail": "Password reset successful. You can now log in."}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    current_user.hashed_password = hash_password(payload.new_password)
    session.add(current_user)
    session.commit()

    send_change_password_notification(current_user.email)
    return {"detail": "Password changed successfully."}


@router.post("/profile-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")
    url = await save_avatar_file(file, current_user.id)
    return {"url": url}


@router.get("/profile-image/{user_id}/{filename}")
def get_profile_image(user_id: str, filename: str) -> FileResponse:
    settings = get_settings()
    path = settings.uploads_dir / "avatars" / user_id / filename
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return FileResponse(path)


@router.delete("/me")
def delete_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    delete_user_cascade(session, current_user)
    settings = get_settings()
    response.delete_cookie(key=settings.cookie_name, path="/")
    return {"detail": "Account deleted"}
