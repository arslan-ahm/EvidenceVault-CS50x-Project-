from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.case import Case
from app.models.upvote import CaseUpvote
from app.models.user import User

router = APIRouter()


@router.post("/{case_id}/upvote")
def toggle_upvote(
    case_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    case = session.get(Case, case_id)
    if not case or not case.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    existing = session.exec(
        select(CaseUpvote).where(CaseUpvote.case_id == case_id).where(CaseUpvote.user_id == current_user.id)
    ).first()

    if existing:
        session.delete(existing)
        case.upvotes_count = max(0, case.upvotes_count - 1)
        upvoted = False
    else:
        session.add(CaseUpvote(id=str(uuid4()), case_id=case_id, user_id=current_user.id))
        case.upvotes_count += 1
        upvoted = True

    session.add(case)
    session.commit()
    return {"upvoted": upvoted, "upvotes_count": case.upvotes_count}


@router.get("/{case_id}/upvote/status")
def upvote_status(
    case_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    existing = session.exec(
        select(CaseUpvote).where(CaseUpvote.case_id == case_id).where(CaseUpvote.user_id == current_user.id)
    ).first()
    return {"upvoted": existing is not None}
