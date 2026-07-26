"""CaseUpvote — records which users have upvoted which cases.

Used to enforce one-vote-per-user and to toggle votes.
"""

from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


class CaseUpvote(SQLModel, table=True):
    __tablename__ = "caseupvote"

    id: str = Field(primary_key=True, index=True)
    case_id: str = Field(index=True, foreign_key="case.id")
    user_id: str = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    case: "Case" = Relationship(back_populates="upvotes")


from app.models.case import Case  # noqa: E402
