from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.comment import Comment, CommentCreate, CommentRead
from app.models.user import User
from app.services.access import get_visible_case

router = APIRouter()


def _to_read(comment: Comment, author_name: str) -> CommentRead:
    return CommentRead(
        id=comment.id,
        case_id=comment.case_id,
        user_id=comment.user_id,
        body=comment.body,
        author_name=author_name,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
    )


@router.get("/{case_id}/comments", response_model=list[CommentRead])
def list_comments(
    case_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[CommentRead]:
    get_visible_case(session, case_id, current_user)
    rows = session.exec(
        select(Comment, User.name)
        .join(User, Comment.user_id == User.id)
        .where(Comment.case_id == case_id)
        .where(Comment.is_deleted == False)  # noqa: E712
        .order_by(Comment.created_at.asc())
    ).all()
    return [_to_read(comment, author_name or "User") for comment, author_name in rows]


@router.post("/{case_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    case_id: str,
    payload: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    get_visible_case(session, case_id, current_user)
    comment = Comment(
        id=str(uuid4()),
        case_id=case_id,
        user_id=current_user.id,
        body=payload.body,
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return _to_read(comment, current_user.name or "User")


@router.delete("/{case_id}/comments/{comment_id}")
def delete_comment(
    case_id: str,
    comment_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    case = get_visible_case(session, case_id, current_user)
    comment = session.get(Comment, comment_id)
    if not comment or comment.case_id != case_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id and case.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this comment")
    session.delete(comment)
    session.commit()
    return {"detail": "Comment deleted"}
