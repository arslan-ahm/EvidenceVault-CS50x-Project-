from __future__ import annotations

from sqlmodel import Session, func, or_, select

from app.models.case import Case
from app.models.evidence import Evidence
from app.schemas.search import SearchResult


def search_case_content(session: Session, user_id: str, query: str) -> list[SearchResult]:
    pattern = f"%{query.lower()}%"
    cases = session.exec(
        select(Case)
        .where(Case.user_id == user_id)
        .where(or_(func.lower(Case.title).like(pattern), func.lower(Case.description).like(pattern)))
    ).all()
    results: list[SearchResult] = [
        SearchResult(case_id=case.id, case_title=case.title, evidence_id=None, snippet=case.description or case.title)
        for case in cases
    ]
    evidence_rows = session.exec(
        select(Evidence, Case)
        .join(Case, Evidence.case_id == Case.id)
        .where(Case.user_id == user_id)
        .where(
            or_(
                func.lower(Evidence.extracted_text).like(pattern),
                func.lower(Evidence.file_name).like(pattern),
                func.lower(Case.title).like(pattern),
            )
        )
    ).all()
    for evidence, case in evidence_rows:
        snippet = (evidence.extracted_text or evidence.file_name)[:200]
        results.append(SearchResult(case_id=case.id, case_title=case.title, evidence_id=evidence.id, snippet=snippet))
    return results
