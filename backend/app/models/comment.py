from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


class CommentBase(SQLModel):
    body: str = Field(min_length=1, max_length=5000)


class Comment(CommentBase, table=True):
    id: str = Field(primary_key=True, index=True)
    case_id: str = Field(index=True, foreign_key="case.id")
    user_id: str = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime | None = Field(default=None, nullable=True)
    is_deleted: bool = Field(default=False, nullable=False)

    case: "Case" = Relationship(back_populates="comments")
    author: "User" = Relationship()


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: str
    case_id: str
    user_id: str
    author_name: str
    created_at: datetime
    updated_at: datetime | None = None


from app.models.case import Case  # noqa: E402
from app.models.user import User  # noqa: E402
