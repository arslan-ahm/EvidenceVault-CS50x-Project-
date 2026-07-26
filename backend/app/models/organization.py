from datetime import datetime, timezone

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


class OrganizationBase(SQLModel):
    name: str = Field(index=True)
    slug: str = Field(index=True, unique=True)
    description: str | None = None
    website: str | None = None
    industry: str | None = None
    logo_url: str | None = None
    social_links_json: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))


class Organization(OrganizationBase, table=True):
    id: str = Field(primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    cases: list["Case"] = Relationship(back_populates="organization")


class OrganizationRead(OrganizationBase):
    id: str
    created_at: datetime


from app.models.case import Case  # noqa: E402