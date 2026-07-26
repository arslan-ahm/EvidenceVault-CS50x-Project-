from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.api.deps import get_current_admin
from app.db.session import get_session
from app.models.case import Case
from app.models.comment import Comment
from app.models.organization import Organization
from app.models.user import User
from app.services.account import delete_case_contents, delete_user_cascade

router = APIRouter()


class AdminStats(BaseModel):
    total_users: int
    admin_users: int
    banned_users: int
    total_cases: int
    public_cases: int
    total_organizations: int
    total_comments: int


class AdminUserOut(BaseModel):
    id: str
    email: str
    name: str
    is_admin: bool
    is_banned: bool
    case_count: int
    created_at: str


class AdminCommentOut(BaseModel):
    id: str
    case_id: str
    case_title: str
    author_email: str
    body: str
    created_at: str


class AdminCaseOut(BaseModel):
    id: str
    title: str
    owner_email: str
    organization_name: str | None
    category: str
    severity: str
    status: str
    is_public: bool
    views_count: int
    upvotes_count: int
    created_at: str


class AdminUserUpdate(BaseModel):
    is_admin: bool | None = None
    is_banned: bool | None = None


class AdminCaseUpdate(BaseModel):
    is_public: bool | None = None
    status: str | None = None


@router.get("/stats", response_model=AdminStats)
def admin_stats(
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> AdminStats:
    return AdminStats(
        total_users=session.exec(select(func.count(User.id))).one(),
        admin_users=session.exec(select(func.count(User.id)).where(User.is_admin == True)).one(),  # noqa: E712
        banned_users=session.exec(select(func.count(User.id)).where(User.is_banned == True)).one(),  # noqa: E712
        total_cases=session.exec(select(func.count(Case.id))).one(),
        public_cases=session.exec(select(func.count(Case.id)).where(Case.is_public == True)).one(),  # noqa: E712
        total_organizations=session.exec(select(func.count(Organization.id))).one(),
        total_comments=session.exec(select(func.count(Comment.id))).one(),
    )


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> list[AdminUserOut]:
    users = session.exec(select(User).order_by(User.created_at.desc())).all()
    case_counts = dict(
        session.exec(select(Case.user_id, func.count(Case.id)).group_by(Case.user_id)).all()
    )
    return [
        AdminUserOut(
            id=u.id,
            email=u.email,
            name=u.name,
            is_admin=u.is_admin,
            is_banned=u.is_banned,
            case_count=case_counts.get(u.id, 0),
            created_at=u.created_at.isoformat(),
        )
        for u in users
    ]


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: str,
    payload: AdminUserUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> AdminUserOut:
    if user_id == admin.id and (payload.is_admin is False or payload.is_banned is True):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot modify your own admin/ban status")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if payload.is_admin is not None:
        user.is_admin = payload.is_admin
    if payload.is_banned is not None:
        user.is_banned = payload.is_banned
    session.add(user)
    session.commit()
    session.refresh(user)
    case_count = session.exec(select(func.count(Case.id)).where(Case.user_id == user.id)).one()
    return AdminUserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        is_admin=user.is_admin,
        is_banned=user.is_banned,
        case_count=case_count,
        created_at=user.created_at.isoformat(),
    )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> dict[str, str]:
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account here")
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    delete_user_cascade(session, user)
    return {"detail": "User deleted"}


@router.get("/cases", response_model=list[AdminCaseOut])
def list_all_cases(
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> list[AdminCaseOut]:
    rows = session.exec(
        select(Case, User.email, Organization.name)
        .join(User, Case.user_id == User.id)
        .join(Organization, Case.organization_id == Organization.id, isouter=True)
        .order_by(Case.created_at.desc())
    ).all()
    return [
        AdminCaseOut(
            id=case.id,
            title=case.title,
            owner_email=owner_email,
            organization_name=organization_name,
            category=case.category,
            severity=case.severity,
            status=case.status,
            is_public=case.is_public,
            views_count=case.views_count,
            upvotes_count=case.upvotes_count,
            created_at=case.created_at.isoformat(),
        )
        for case, owner_email, organization_name in rows
    ]


@router.patch("/cases/{case_id}", response_model=AdminCaseOut)
def update_case_moderation(
    case_id: str,
    payload: AdminCaseUpdate,
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> AdminCaseOut:
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if payload.is_public is not None:
        case.is_public = payload.is_public
    if payload.status is not None:
        case.status = payload.status
    session.add(case)
    session.commit()
    session.refresh(case)

    owner = session.get(User, case.user_id)
    organization_name = None
    if case.organization_id:
        organization = session.get(Organization, case.organization_id)
        organization_name = organization.name if organization else None
    return AdminCaseOut(
        id=case.id,
        title=case.title,
        owner_email=owner.email if owner else "",
        organization_name=organization_name,
        category=case.category,
        severity=case.severity,
        status=case.status,
        is_public=case.is_public,
        views_count=case.views_count,
        upvotes_count=case.upvotes_count,
        created_at=case.created_at.isoformat(),
    )


@router.delete("/cases/{case_id}")
def delete_case_admin(
    case_id: str,
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> dict[str, str]:
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    delete_case_contents(session, case.id)
    session.delete(case)
    session.commit()
    return {"detail": "Case deleted"}


@router.get("/comments", response_model=list[AdminCommentOut])
def list_all_comments(
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> list[AdminCommentOut]:
    rows = session.exec(
        select(Comment, Case.title, User.email)
        .join(Case, Comment.case_id == Case.id)
        .join(User, Comment.user_id == User.id)
        .order_by(Comment.created_at.desc())
        .limit(200)
    ).all()
    return [
        AdminCommentOut(
            id=comment.id,
            case_id=comment.case_id,
            case_title=case_title,
            author_email=author_email,
            body=comment.body,
            created_at=comment.created_at.isoformat(),
        )
        for comment, case_title, author_email in rows
    ]


@router.delete("/comments/{comment_id}")
def delete_comment_admin(
    comment_id: str,
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> dict[str, str]:
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    session.delete(comment)
    session.commit()
    return {"detail": "Comment deleted"}
