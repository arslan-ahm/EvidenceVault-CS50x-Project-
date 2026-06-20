from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_session
from app.models.user import Token, User, UserCreate, UserLogin, UserPublic

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


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, session: Session = Depends(get_session)) -> UserPublic:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(id=str(uuid4()), email=payload.email.lower(), hashed_password=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token(user.id, {"email": user.email})
    _set_auth_cookie(response, token)
    return UserPublic(id=user.id, email=user.email, created_at=user.created_at)


@router.post("/login", response_model=UserPublic)
def login(payload: UserLogin, response: Response, session: Session = Depends(get_session)) -> UserPublic:
    user = session.exec(select(User).where(User.email == payload.email.lower())).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.id, {"email": user.email})
    _set_auth_cookie(response, token)
    return UserPublic(id=user.id, email=user.email, created_at=user.created_at)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    settings = get_settings()
    response.delete_cookie(key=settings.cookie_name, path="/")
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserPublic)
def read_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic(id=current_user.id, email=current_user.email, created_at=current_user.created_at)
