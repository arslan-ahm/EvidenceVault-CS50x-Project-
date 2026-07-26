"""Shared visibility rules for content that can be either private (owner-only)
or public (visible to any authenticated user), e.g. cases with comments/votes."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.case import Case
from app.models.user import User


def get_visible_case(session: Session, case_id: str, user: User) -> Case:
    """Return the case if the user owns it or it is public; otherwise 404."""
    case = session.get(Case, case_id)
    if not case or (case.user_id != user.id and not case.is_public):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


def get_visible_case_optional_user(session: Session, case_id: str, user: User | None) -> Case:
    """Like get_visible_case, but allows anonymous access to public cases."""
    case = session.get(Case, case_id)
    is_owner = bool(user) and case is not None and case.user_id == user.id
    if not case or (not is_owner and not case.is_public):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case
