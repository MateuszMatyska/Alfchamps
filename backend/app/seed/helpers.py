from sqlalchemy.orm import Session

from ..models import ChecklistItem, Standard


def _standard(db: Session, slug: str) -> Standard | None:
    return db.query(Standard).filter(Standard.slug == slug).first()


def ensure_standard(db: Session, slug: str, name: str, category: str, edition: str, description: str) -> tuple[Standard, bool]:
    std = _standard(db, slug)
    if std is not None:
        return std, False
    std = Standard(
        slug=slug,
        name=name,
        category=category,
        edition=edition,
        description=description,
    )
    db.add(std)
    db.flush()
    return std, True


def add_item(db: Session, standard: Standard, *, code: str, title: str, description: str = "",
             how_to_test: str = "", remediation: str = "", asvs_level: int | None = None) -> None:
    db.add(
        ChecklistItem(
            standard_id=standard.id,
            code=code,
            title=title,
            description=description,
            how_to_test=how_to_test,
            remediation=remediation,
            asvs_level=asvs_level,
        )
    )
