from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.services.search import search_case_content

router = APIRouter()


@router.get("")
def search(q: str = Query(min_length=1), session: Session = Depends(get_session), current_user: User = Depends(get_current_user)) -> dict:
    results = search_case_content(session, current_user.id, q)
    return {"results": [item.model_dump() for item in results]}
