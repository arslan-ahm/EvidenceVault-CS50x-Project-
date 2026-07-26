from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


class CaseBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = None
    organization_id: str | None = Field(default=None, foreign_key="organization.id", index=True)
    category: str = Field(default="other", index=True)
    severity: str = Field(default="medium", index=True)
    status: str = Field(default="open", index=True)
    is_public: bool = Field(default=True, index=True)


class Case(CaseBase, table=True):
    id: str = Field(primary_key=True, index=True)
    user_id: str = Field(index=True, foreign_key="user.id")
    views_count: int = Field(default=0, nullable=False)
    upvotes_count: int = Field(default=0, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    user: "User" = Relationship(back_populates="cases")
    organization: "Organization" = Relationship(back_populates="cases")
    evidence_items: list["Evidence"] = Relationship(back_populates="case")
    timeline_events: list["TimelineEvent"] = Relationship(back_populates="case")
    comments: list["Comment"] = Relationship(back_populates="case")
    upvotes: list["CaseUpvote"] = Relationship(back_populates="case")


class CaseCreate(CaseBase):
    pass


class CaseUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    organization_id: str | None = None
    category: str | None = None
    severity: str | None = None
    status: str | None = None
    is_public: bool | None = None


class CaseRead(CaseBase):
    id: str
    user_id: str
    organization_name: str | None = None
    views_count: int = 0
    upvotes_count: int = 0
    created_at: datetime


from app.models.evidence import Evidence  # noqa: E402
from app.models.timeline import TimelineEvent  # noqa: E402
from app.models.organization import Organization  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.comment import Comment  # noqa: E402
from app.models.upvote import CaseUpvote  # noqa: E402
