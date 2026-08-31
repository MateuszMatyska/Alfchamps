from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, SessionLocal, engine
from .memorial import ALFRED_PHOTO_HINT, ALFRED_TAGLINE, ALFRED_TRIBUTE
from .routers import assets, checklists, projects, reports, standards
from .seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_all(db)
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; connect-src 'self'"
    )
    return response


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/api")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "local_only": True,
        "message": "Alfchamps is a local-only reporting tool. Run it on localhost only.",
        "endpoints": {
            "standards": "/standards",
            "projects": "/projects",
            "report_pdf": "/projects/{id}/report/pdf",
            "memorial": "/memorial",
            "docs": "/docs",
        },
    }


@app.get("/memorial")
def memorial():
    """Standalone Alfred tribute, shown on the dedicated memorial page."""
    return {
        "tagline": ALFRED_TAGLINE,
        "text": ALFRED_TRIBUTE,
        "photo_hint": ALFRED_PHOTO_HINT,
    }


app.include_router(standards.router)
app.include_router(projects.router)
app.include_router(checklists.router)
app.include_router(assets.router)
app.include_router(reports.router)
