import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import admin, auth, events, members, projects
from app.seed import seed

ALLOWED_ORIGINS = [o for o in {settings.FRONTEND_URL, os.environ.get("APP_URL", "").rstrip("/"), "http://localhost:3000"} if o]


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed()
    yield
    await engine.dispose()


app = FastAPI(title="Giguiya API", lifespan=lifespan)


@app.middleware("http")
async def origin_guard(request: Request, call_next):
    origin = request.headers.get("origin")
    if (request.method in ("POST", "PUT", "PATCH", "DELETE") and origin
            and "access_token" in request.cookies and origin not in ALLOWED_ORIGINS):
        return JSONResponse(status_code=403, content={"detail": "Origine non consentita"})
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")


@api.get("/health")
async def health():
    return {"status": "ok"}


for module in (auth, members, events, projects, admin):
    api.include_router(module.router)

app.include_router(api)
