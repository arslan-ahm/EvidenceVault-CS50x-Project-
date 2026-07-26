from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import case as sql_case
from sqlmodel import Session, func, or_, select

from app.db.session import get_session
from app.models.case import Case
from app.models.comment import Comment, CommentRead
from app.models.evidence import Evidence
from app.models.organization import Organization
from app.models.timeline import TimelineEvent
from app.models.user import User

router = APIRouter()


class PublicStats(BaseModel):
    total_reports: int
    total_organizations: int
    resolved_reports: int
    pending_reports: int
    active_researchers: int
    total_evidence_items: int


class PublicReportSummary(BaseModel):
    id: str
    title: str
    description: str | None
    organization_name: str | None
    category: str
    severity: str
    status: str
    views_count: int
    upvotes_count: int
    created_at: datetime


class PublicOrganizationSummary(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    website: str | None
    industry: str | None
    total_reports: int
    resolved_reports: int
    open_reports: int


class PublicReportDetail(BaseModel):
    report: PublicReportSummary
    evidence: list[dict[str, Any]]
    timeline: list[dict[str, Any]]


def _case_summary(case: Case, organization_name: str | None) -> PublicReportSummary:
    return PublicReportSummary(
        id=case.id,
        title=case.title,
        description=case.description,
        organization_name=organization_name,
        category=case.category,
        severity=case.severity,
        status=case.status,
        views_count=case.views_count,
        upvotes_count=case.upvotes_count,
        created_at=case.created_at,
    )


@router.get("/stats", response_model=PublicStats)
def public_stats(session: Session = Depends(get_session)) -> PublicStats:
    total_reports = session.exec(select(func.count(Case.id)).where(Case.is_public == True)).one()
    total_organizations = session.exec(select(func.count(Organization.id))).one()
    resolved_reports = session.exec(
        select(func.count(Case.id)).where(Case.is_public == True).where(Case.status == "resolved")
    ).one()
    pending_reports = session.exec(
        select(func.count(Case.id)).where(Case.is_public == True).where(Case.status != "resolved")
    ).one()
    active_researchers = session.exec(
        select(func.count(func.distinct(Case.user_id))).where(Case.is_public == True)
    ).one()
    total_evidence_items = session.exec(
        select(func.count(Evidence.id)).join(Case, Evidence.case_id == Case.id).where(Case.is_public == True)
    ).one()
    return PublicStats(
        total_reports=total_reports,
        total_organizations=total_organizations,
        resolved_reports=resolved_reports,
        pending_reports=pending_reports,
        active_researchers=active_researchers,
        total_evidence_items=total_evidence_items,
    )


@router.get("/reports", response_model=list[PublicReportSummary])
def public_reports(
    q: str | None = Query(default=None, min_length=1),
    category: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    organization: str | None = None,
    sort: str = Query(default="recent"),
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[PublicReportSummary]:
    statement = select(Case, Organization.name).join(Organization, Case.organization_id == Organization.id, isouter=True).where(
        Case.is_public == True
    )
    if q:
        pattern = f"%{q.lower()}%"
        statement = statement.where(
            or_(
                func.lower(Case.title).like(pattern),
                func.lower(Case.description).like(pattern),
                func.lower(Case.category).like(pattern),
                func.lower(Organization.name).like(pattern),
            )
        )
    if category:
        statement = statement.where(Case.category == category)
    if severity:
        statement = statement.where(Case.severity == severity)
    if status:
        statement = statement.where(Case.status == status)
    if organization:
        statement = statement.where(func.lower(Organization.slug) == organization.lower())

    if sort == "trending":
        statement = statement.order_by(Case.upvotes_count.desc(), Case.views_count.desc(), Case.created_at.desc())
    elif sort == "popular":
        statement = statement.order_by(Case.views_count.desc(), Case.created_at.desc())
    else:
        statement = statement.order_by(Case.created_at.desc())

    rows = session.exec(statement.offset(offset).limit(limit)).all()
    return [_case_summary(case, organization_name).model_dump() for case, organization_name in rows]


@router.get("/reports/{report_id}", response_model=PublicReportDetail)
def public_report_detail(report_id: str, session: Session = Depends(get_session)) -> PublicReportDetail:
    row = session.exec(
        select(Case, Organization.name)
        .join(Organization, Case.organization_id == Organization.id, isouter=True)
        .where(Case.id == report_id)
        .where(Case.is_public == True)
    ).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    case, organization_name = row
    evidence_items = session.exec(select(Evidence).where(Evidence.case_id == case.id).order_by(Evidence.uploaded_at.asc())).all()
    timeline_rows = session.exec(select(TimelineEvent).where(TimelineEvent.case_id == case.id).order_by(TimelineEvent.created_at.asc())).all()
    return PublicReportDetail(
        report=_case_summary(case, organization_name),
        evidence=[item.model_dump() for item in evidence_items],
        timeline=[item.model_dump() for item in timeline_rows],
    )


@router.post("/reports/{report_id}/view")
def track_report_view(report_id: str, session: Session = Depends(get_session)) -> dict[str, int]:
    """Increment the view counter for a public report.

    This is a simple counter (not deduplicated per visitor) — good enough for
    a rough "how much attention did this get" signal without adding session
    tracking infrastructure.
    """
    case = session.get(Case, report_id)
    if not case or not case.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    case.views_count += 1
    session.add(case)
    session.commit()
    return {"views_count": case.views_count}


@router.get("/reports/{report_id}/comments", response_model=list[CommentRead])
def public_report_comments(report_id: str, session: Session = Depends(get_session)) -> list[CommentRead]:
    case = session.get(Case, report_id)
    if not case or not case.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    rows = session.exec(
        select(Comment, User.name)
        .join(User, Comment.user_id == User.id)
        .where(Comment.case_id == report_id)
        .where(Comment.is_deleted == False)  # noqa: E712
        .order_by(Comment.created_at.asc())
    ).all()
    return [
        CommentRead(
            id=comment.id,
            case_id=comment.case_id,
            user_id=comment.user_id,
            body=comment.body,
            author_name=author_name or "User",
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
        for comment, author_name in rows
    ]


@router.get("/organizations", response_model=list[PublicOrganizationSummary])
def public_organizations(
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[PublicOrganizationSummary]:
    organizations = session.exec(select(Organization)).all()
    stats_rows = session.exec(
        select(
            Case.organization_id,
            func.count(Case.id),
            func.sum(sql_case((Case.status == "resolved", 1), else_=0)),
            func.sum(sql_case((Case.status != "resolved", 1), else_=0)),
        )
        .where(Case.is_public == True)
        .group_by(Case.organization_id)
    ).all()
    stats_by_org = {
        organization_id: {
            "total_reports": total_reports or 0,
            "resolved_reports": resolved_reports or 0,
            "open_reports": open_reports or 0,
        }
        for organization_id, total_reports, resolved_reports, open_reports in stats_rows
    }
    ordered_organizations = sorted(
        organizations,
        key=lambda organization: (-stats_by_org.get(organization.id, {}).get("total_reports", 0), organization.name.lower()),
    )
    page = ordered_organizations[offset : offset + limit]
    return [
        PublicOrganizationSummary(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            description=organization.description,
            website=organization.website,
            industry=organization.industry,
            total_reports=stats_by_org.get(organization.id, {}).get("total_reports", 0),
            resolved_reports=stats_by_org.get(organization.id, {}).get("resolved_reports", 0),
            open_reports=stats_by_org.get(organization.id, {}).get("open_reports", 0),
        )
        for organization in page
    ]