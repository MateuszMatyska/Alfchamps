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
             how_to_test: str = "", test_examples: str = "", reference_url: str = "",
             remediation: str = "", asvs_level: int | None = None) -> None:
    """Idempotent upsert of a seeded checklist item (keyed on standard + code).

    Seeded items are read-only reference data, so on every startup we refresh
    their content. This also backfills fields (examples, doc links) onto items
    that were inserted by an older version of the app.
    """
    existing = (
        db.query(ChecklistItem)
        .filter(ChecklistItem.standard_id == standard.id, ChecklistItem.code == code)
        .first()
    )
    if existing is not None:
        existing.title = title
        existing.description = description
        existing.how_to_test = how_to_test
        existing.test_examples = test_examples
        existing.reference_url = reference_url
        existing.remediation = remediation
        existing.asvs_level = asvs_level
        return
    db.add(
        ChecklistItem(
            standard_id=standard.id,
            code=code,
            title=title,
            description=description,
            how_to_test=how_to_test,
            test_examples=test_examples,
            reference_url=reference_url,
            remediation=remediation,
            asvs_level=asvs_level,
        )
    )
