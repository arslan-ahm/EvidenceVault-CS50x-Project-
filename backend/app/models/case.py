from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


class CaseBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = None


class Case(CaseBase, table=True):
    id: str = Field(primary_key=True, index=True)
    user_id: str = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    user: "User" = Relationship(back_populates="cases")
    evidence_items: list["Evidence"] = Relationship(back_populates="case")
    timeline_events: list["TimelineEvent"] = Relationship(back_populates="case")


class CaseCreate(CaseBase):
    pass


class CaseUpdate(SQLModel):
    title: str | None = None
    description: str | None = None


class CaseRead(CaseBase):
    id: str
    user_id: str
    created_at: datetime


from app.models.evidence import Evidence  # noqa: E402
from app.models.timeline import TimelineEvent  # noqa: E402
from app.models.user import User  # noqa: E402
