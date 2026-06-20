from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.case import Case, CaseCreate, CaseRead, CaseUpdate
from app.models.evidence import Evidence
from app.models.timeline import TimelineEvent
from app.models.user import User
from app.services.report import build_case_report_pdf

router = APIRouter()


def _get_case_for_user(session: Session, case_id: str, user_id: str) -> Case:
    case = session.get(Case, case_id)
    if not case or case.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.get("", response_model=list[CaseRead])
def list_cases(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> list[CaseRead]:
    cases = session.exec(select(Case).where(Case.user_id == current_user.id).order_by(Case.created_at.desc())).all()
    return [CaseRead(id=item.id, title=item.title, description=item.description, user_id=item.user_id, created_at=item.created_at) for item in cases]


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> CaseRead:
    case = Case(id=str(uuid4()), user_id=current_user.id, title=payload.title, description=payload.description)
    session.add(case)
    session.commit()
    session.refresh(case)
    return CaseRead(id=case.id, title=case.title, description=case.description, user_id=case.user_id, created_at=case.created_at)


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> CaseRead:
    case = _get_case_for_user(session, case_id, current_user.id)
    return CaseRead(id=case.id, title=case.title, description=case.description, user_id=case.user_id, created_at=case.created_at)


@router.put("/{case_id}", response_model=CaseRead)
def update_case(case_id: str, payload: CaseUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> CaseRead:
    case = _get_case_for_user(session, case_id, current_user.id)
    if payload.title is not None:
        case.title = payload.title
    if payload.description is not None:
        case.description = payload.description
    session.add(case)
    session.commit()
    session.refresh(case)
    return CaseRead(id=case.id, title=case.title, description=case.description, user_id=case.user_id, created_at=case.created_at)


@router.delete("/{case_id}")
def delete_case(case_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> dict[str, str]:
    case = _get_case_for_user(session, case_id, current_user.id)
    session.delete(case)
    session.commit()
    return {"detail": "Case deleted"}


@router.get("/{case_id}/evidence")
def list_case_evidence(case_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> list[dict]:
    _get_case_for_user(session, case_id, current_user.id)
    evidence_items = session.exec(select(Evidence).where(Evidence.case_id == case_id).order_by(Evidence.uploaded_at.desc())).all()
    return [item.model_dump() for item in evidence_items]


@router.get("/{case_id}/timeline")
def list_case_timeline(case_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> list[dict]:
    _get_case_for_user(session, case_id, current_user.id)
    timeline_rows = session.exec(select(TimelineEvent).where(TimelineEvent.case_id == case_id).order_by(TimelineEvent.event_date.nulls_last(), TimelineEvent.created_at.asc())).all()
    return [item.model_dump() for item in timeline_rows]


@router.get("/{case_id}/export")
def export_case_pdf(case_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> Response:
    case = _get_case_for_user(session, case_id, current_user.id)
    evidence_items = session.exec(select(Evidence).where(Evidence.case_id == case_id).order_by(Evidence.uploaded_at.asc())).all()
    timeline_rows = session.exec(select(TimelineEvent).where(TimelineEvent.case_id == case_id).order_by(TimelineEvent.event_date.nulls_last(), TimelineEvent.created_at.asc())).all()
    pdf_bytes = build_case_report_pdf(
        case_title=case.title,
        case_description=case.description,
        evidence_rows=[item.model_dump() for item in evidence_items],
        timeline_rows=[item.model_dump() for item in timeline_rows],
    )
    headers = {"Content-Disposition": f'attachment; filename="case-{case_id}.pdf"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
