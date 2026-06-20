from fastapi import APIRouter

from app.api.routes import auth, cases, evidence, health, search

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
