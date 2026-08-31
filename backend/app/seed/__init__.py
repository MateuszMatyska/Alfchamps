"""Idempotent seed loader for OWASP checklist content.

Ships official ASVS 4.0.3 requirements (parsed from the bundled OWASP CSV) and
WSTG tests (parsed from the official checklist) plus curated seeds for other
standards. Seeding is skipped when the standard already exists.
"""
from sqlalchemy.orm import Session

from . import api_top10, asvs, genai, masvs, top10_web, wstg

SEEDERS = [
    top10_web.seed,
    api_top10.seed,
    asvs.seed,
    wstg.seed,
    masvs.seed,
    genai.seed,
]


def seed_all(db: Session) -> None:
    for seeder in SEEDERS:
        seeder(db)
