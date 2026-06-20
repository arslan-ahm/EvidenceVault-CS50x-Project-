from sqlmodel import SQLModel


class SearchResult(SQLModel):
    case_id: str
    case_title: str
    evidence_id: str | None = None
    snippet: str
