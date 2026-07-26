from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True, nullable=False)


class User(UserBase, table=True):
    id: str = Field(primary_key=True, index=True)
    hashed_password: str
    name: str = Field(default="", nullable=False)
    occupation: str | None = Field(default=None, nullable=True)
    profile_image_url: str | None = Field(default=None, nullable=True)
    reset_token: str | None = Field(default=None, nullable=True)
    reset_token_expires: datetime | None = Field(default=None, nullable=True)
    is_admin: bool = Field(default=False, nullable=False)
    is_banned: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    cases: list["Case"] = Relationship(back_populates="user")


class UserPublic(SQLModel):
    id: str
    email: str
    name: str = ""
    occupation: str | None = None
    profile_image_url: str | None = None
    is_admin: bool = False
    created_at: datetime


class UserCreate(SQLModel):
    email: str
    password: str
    name: str = ""
    occupation: str | None = None


class UserUpdate(SQLModel):
    name: str | None = None
    occupation: str | None = None
    profile_image_url: str | None = None


class UserLogin(SQLModel):
    email: str
    password: str


class ForgotPasswordRequest(SQLModel):
    email: str


class ResetPasswordRequest(SQLModel):
    token: str
    password: str


class ChangePasswordRequest(SQLModel):
    current_password: str
    new_password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: Optional[str] = None


from app.models.case import Case  # noqa: E402
