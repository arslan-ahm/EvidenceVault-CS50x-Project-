from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.rate_limit import InMemoryRateLimiter, RateLimitConfig
from app.db.init_db import init_db


settings = get_settings()
rate_limiter = InMemoryRateLimiter(RateLimitConfig(max_requests=120, window_seconds=60))


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def basic_rate_limit(request: Request, call_next):
    client_host = request.client.host if request.client else "anonymous"
    key = f"{client_host}:{request.url.path}"
    if request.url.path.startswith("/api") and not rate_limiter.allow(key):
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    return await call_next(request)


app.include_router(api_router, prefix=settings.api_v1_prefix)
