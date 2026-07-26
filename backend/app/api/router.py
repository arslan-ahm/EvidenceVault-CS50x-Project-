from fastapi import APIRouter

from app.api.routes import (
    admin,
    auth,
    cases,
    categories,
    comments,
    evidence,
    health,
    organizations,
    public,
    search,
    votes,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(comments.router, prefix="/cases", tags=["comments"])
api_router.include_router(votes.router, prefix="/cases", tags=["votes"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
