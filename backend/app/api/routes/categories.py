from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.category import Category
from app.models.user import User

router = APIRouter()


class CategoryOut(BaseModel):
    id: str
    value: str
    label: str


class CategoryCreate(BaseModel):
    value: str
    label: str | None = None


@router.get("", response_model=list[CategoryOut])
def list_categories(session: Session = Depends(get_session)) -> list[CategoryOut]:
    categories = session.exec(select(Category).order_by(Category.label)).all()
    return [CategoryOut(id=c.id, value=c.value, label=c.label) for c in categories]


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    session: Session = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> CategoryOut:
    value = payload.value.strip().lower().replace(" ", "_")
    label = payload.label or payload.value.strip()

    if not value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category value cannot be empty")

    # Check case-insensitively if a category with same value already exists
    existing = session.exec(select(Category).where(Category.value == value)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{existing.label}' already covers this value",
        )

    category = Category(id=str(uuid4()), value=value, label=label)
    session.add(category)
    session.commit()
    session.refresh(category)
    return CategoryOut(id=category.id, value=category.value, label=category.label)
