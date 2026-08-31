from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ChecklistItem, Standard
from ..schemas import StandardOut

router = APIRouter(prefix="/standards", tags=["standards"])


@router.get("", response_model=list[StandardOut])
def list_standards(db: Session = Depends(get_db)):
    return db.query(Standard).order_by(Standard.id).all()


@router.get("/{slug}/count")
def standard_item_count(slug: str, db: Session = Depends(get_db)):
    std = db.query(Standard).filter(Standard.slug == slug).first()
    if std is None:
        return {"slug": slug, "count": 0}
    count = db.query(ChecklistItem).filter(ChecklistItem.standard_id == std.id).count()
    return {"slug": slug, "count": count}
