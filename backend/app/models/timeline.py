from datetime import date, datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


class TimelineEventBase(SQLModel):
    event_text: str
    event_date: date | None = None
    source_evidence_id: str | None = Field(default=None, foreign_key="evidence.id")


class TimelineEvent(TimelineEventBase, table=True):
    id: str = Field(primary_key=True, index=True)
    case_id: str = Field(index=True, foreign_key="case.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    case: "Case" = Relationship(back_populates="timeline_events")


class TimelineEventRead(TimelineEventBase):
    id: str
    case_id: str
    created_at: datetime


from app.models.case import Case  # noqa: E402
