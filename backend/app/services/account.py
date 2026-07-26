"""Account deletion — cascades a user's owned and authored rows before removing the user.

SQLModel/SQLite and the current Postgres schema don't declare ON DELETE CASCADE on
these foreign keys, so cascading has to happen explicitly here rather than relying
on the database.
"""

from __future__ import annotations

import shutil

from sqlmodel import Session, select

from app.core.config import get_settings
from app.models.case import Case
from app.models.comment import Comment
from app.models.evidence import Evidence
from app.models.timeline import TimelineEvent
from app.models.upvote import CaseUpvote
from app.models.user import User


def delete_case_contents(session: Session, case_id: str) -> None:
    for evidence in session.exec(select(Evidence).where(Evidence.case_id == case_id)).all():
        session.delete(evidence)
    for event in session.exec(select(TimelineEvent).where(TimelineEvent.case_id == case_id)).all():
        session.delete(event)
    for comment in session.exec(select(Comment).where(Comment.case_id == case_id)).all():
        session.delete(comment)
    for upvote in session.exec(select(CaseUpvote).where(CaseUpvote.case_id == case_id)).all():
        session.delete(upvote)


def delete_user_cascade(session: Session, user: User) -> None:
    """Delete a user and everything they own or authored."""
    for comment in session.exec(select(Comment).where(Comment.user_id == user.id)).all():
        session.delete(comment)
    for upvote in session.exec(select(CaseUpvote).where(CaseUpvote.user_id == user.id)).all():
        session.delete(upvote)

    owned_cases = session.exec(select(Case).where(Case.user_id == user.id)).all()
    for case in owned_cases:
        delete_case_contents(session, case.id)
        session.delete(case)

    session.delete(user)
    session.commit()

    settings = get_settings()
    shutil.rmtree(settings.uploads_dir / user.id, ignore_errors=True)
