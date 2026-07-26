from datetime import datetime, timezone

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


class EvidenceBase(SQLModel):
    file_path: str
    file_name: str
    file_type: str
    extracted_text: str | None = None
    # When stored in MEGA, this holds the shareable link; None for local storage
    public_url: str | None = Field(default=None, nullable=True)
    metadata_json: dict = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))


class Evidence(EvidenceBase, table=True):
    id: str = Field(primary_key=True, index=True)
    case_id: str = Field(index=True, foreign_key="case.id")
    user_id: str = Field(index=True, foreign_key="user.id")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    case: "Case" = Relationship(back_populates="evidence_items")


class EvidenceRead(EvidenceBase):
    id: str
    case_id: str
    user_id: str
    uploaded_at: datetime


from app.models.case import Case  # noqa: E402
