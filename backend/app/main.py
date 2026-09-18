from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import BASE_DIR, get_settings
from .database import Base, SessionLocal, engine, run_migrations
from .memorial import ALFRED_PHOTO_HINT, ALFRED_TAGLINE, ALFRED_TRIBUTE
from .routers import assets, checklists, projects, reports, standards
from .seed import seed_all


def _alfchamps_logo_path() -> Path:
    # Same multi-candidate resolution used by reports.py for the cover logo, so
    # this works in the container and from the repo root alike.
    for candidate in (
        BASE_DIR / "assets" / "alfchamps_logo.png",
        Path("assets", "alfchamps_logo.png"),
    ):
        if candidate.exists():
            return candidate
    return BASE_DIR / "assets" / "alfchamps_logo.png"


def _memorial_photo_path() -> Path:
    # In containers __file__ resolves differently, so accept both the repo-root
    # path and the working-directory path (like reports.py does for the logo).
    for candidate in (
        BASE_DIR / "assets" / "alfred_photo.png",
        Path("assets", "alfred_photo.png"),
    ):
        if candidate.exists():
            return candidate
    return BASE_DIR / "assets" / "alfred_photo.png"


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
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
        "has_photo": _memorial_photo_path().exists(),
    }


@app.get("/memorial/photo")
def memorial_photo():
    """Serve Alfred's photo for the memorial page (only if a real photo exists)."""
    path = _memorial_photo_path()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Alfred's photo not provided")
    return FileResponse(path, media_type="image/png")


def _alfchamps_logo_path() -> Path:
    """Resolve the Alfchamps cover/header logo (only if a real file exists).

    Mirrors the multi-candidate resolution reports.py uses, so this works in the
    container and from the repo root alike.
    """
    for candidate in (
        BASE_DIR / "assets" / "alfchamps_logo.png",
        Path("assets", "alfchamps_logo.png"),
    ):
        if candidate.exists():
            return candidate
    return BASE_DIR / "assets" / "alfchamps_logo.png"



app.include_router(standards.router)
app.include_router(projects.router)
app.include_router(checklists.router)
app.include_router(assets.router)
app.include_router(reports.router)


@app.get("/assets/alfchamps_logo.png")
def alfchamps_logo():
    """Serve the Alfchamps logo for the dashboard/report header (404 if absent)."""
    path = _alfchamps_logo_path()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Alfchamps logo not provided")
    return FileResponse(path, media_type="image/png")
