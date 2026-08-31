import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from reportlab.lib.utils import ImageReader as RLImageReader
from sqlalchemy.orm import Session

from ..config import get_settings
from ..database import get_db
from ..models import ProjectItem, Screenshot

settings = get_settings()
router = APIRouter(prefix="/projects/{project_id}/items/{item_id}/screenshots", tags=["assets"])


def _get_item(db: Session, project_id: int, item_id: int) -> ProjectItem:
    item = db.query(ProjectItem).filter(ProjectItem.id == item_id, ProjectItem.project_id == project_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Project item not found")
    return item


def _save_image(file: UploadFile) -> Path:
    original = file.filename or "image"
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type not allowed: .{ext}")
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    dest = settings.upload_dir / stored_name
    size = 0
    with dest.open("wb") as out:
        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.upload_max_size_mb * 1024 * 1024:
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large")
            out.write(chunk)
    try:
        RLImageReader(str(dest)).getSize()
    except (OSError, ValueError):
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")
    return dest


@router.post("")
def upload_screenshot(
    project_id: int,
    item_id: int,
    file: UploadFile = File(...),
    alt_text: str = Form(""),
    db: Session = Depends(get_db),
):
    _get_item(db, project_id, item_id)
    dest = _save_image(file)
    row = Screenshot(project_item_id=item_id, file_path=str(dest), alt_text=alt_text)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "alt_text": row.alt_text, "filename": dest.name}


@router.get("/{screenshot_id}/file")
def serve_screenshot(project_id: int, item_id: int, screenshot_id: int, db: Session = Depends(get_db)):
    _get_item(db, project_id, item_id)
    shot = db.get(Screenshot, screenshot_id)
    if shot is None or shot.project_item_id != item_id:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    path = Path(shot.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")
    return FileResponse(path, media_type="image/png")
