from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_session
from app.models.case import Case
from app.models.organization import Organization, OrganizationRead
from app.models.user import User

router = APIRouter()


def _slugify(name: str) -> str:
    return "-".join(name.strip().lower().split()) or "organization"


def _unique_slug(session: Session, name: str) -> str:
    base = _slugify(name)
    slug = base
    suffix = 1
    while session.exec(select(Organization).where(Organization.slug == slug)).first():
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: dict,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> OrganizationRead:
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization name is required")

    existing = session.exec(select(Organization).where(Organization.name == name)).first()
    if existing:
        return OrganizationRead(**existing.model_dump())

    organization = Organization(
        id=str(uuid4()),
        name=name,
        slug=_unique_slug(session, name),
        description=payload.get("description"),
        website=payload.get("website"),
        industry=payload.get("industry"),
    )
    session.add(organization)
    session.commit()
    session.refresh(organization)
    return OrganizationRead(**organization.model_dump())


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(organization_id: str, session: Session = Depends(get_session)) -> OrganizationRead:
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return OrganizationRead(**organization.model_dump())


@router.put("/{organization_id}", response_model=OrganizationRead)
def update_organization(
    organization_id: str,
    payload: dict,
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> OrganizationRead:
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    for field in ("name", "description", "website", "industry", "logo_url"):
        if field in payload and payload[field] is not None:
            setattr(organization, field, payload[field])

    session.add(organization)
    session.commit()
    session.refresh(organization)
    return OrganizationRead(**organization.model_dump())


@router.delete("/{organization_id}")
def delete_organization(
    organization_id: str,
    session: Session = Depends(get_session),
    _admin: User = Depends(get_current_admin),
) -> dict[str, str]:
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    linked_cases = session.exec(select(Case).where(Case.organization_id == organization_id)).all()
    for case in linked_cases:
        case.organization_id = None
        session.add(case)

    session.delete(organization)
    session.commit()
    return {"detail": "Organization deleted"}
