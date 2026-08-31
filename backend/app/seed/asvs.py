"""OWASP ASVS 4.0.3 full requirements seed.

Parses the bundled official ASVS 4.0.3 CSV (shipped in data/), which was
downloaded at build time from the OWASP repository. Each requirement carries
its ASVS security level (L1/L2/L3) so the wizard can filter which items are
included. Rows marked [DELETED] are skipped.
"""
import csv
from pathlib import Path

from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-asvs"
CSV_PATH = Path(__file__).parent / "data" / "asvs-4.0.3.csv"

CHAPTER_HINTS = {
    "V1": "Architecture: review design docs, threat models, and enforcement points for these architectural controls.",
    "V2": "Authentication: exercise login, password policies, credential storage, recovery, and MFA flows.",
    "V3": "Session management: capture and manipulate session tokens, cookies, revocation and logout.",
    "V4": "Access control: test object references, CSRF, least privilege and admin interfaces.",
    "V5": "Validation/sanitization/encoding: fuzz inputs and inject payloads to verify output encoding and injection resistance.",
    "V6": "Cryptography: review algorithms, random values, secrets management and at-rest encryption.",
    "V7": "Error handling and logging: induce errors and verify logs capture security events without leaking secrets.",
    "V8": "Data protection: test for sensitive data in URLs, caches, backups, and unintended disclosure.",
    "V9": "Communications: verify TLS strength, certificate validation, and client/server communication security.",
    "V10": "Malicious code: review for backdoors, tampering, and code/data integrity controls.",
    "V11": "Business logic: abuse-case test workflows, timing, and sequencing weaknesses.",
    "V12": "Files and resources: test upload/download, execution, storage, and SSRF protections.",
    "V13": "API/web service: test REST/SOAP/GraphQL endpoints for structured query and auth weaknesses.",
    "V14": "Configuration: verify build/deploy, dependency hygiene, headers, and request validation.",
}


def seed(db: Session) -> None:
    std, created = ensure_standard(
        db,
        SLUG,
        "OWASP Application Security Verification Standard (ASVS)",
        "web",
        "4.0.3",
        "ASVS defines a classification of security requirements and verification levels "
        "for web applications, from Level 1 (automated/opportunistic) to Level 3 (high-value/high-risk).",
    )
    if not created:
        return

    if not CSV_PATH.exists():
        return

    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            req_id = (row.get("req_id") or "").strip()
            desc = (row.get("req_description") or "").strip()
            chapter = (row.get("chapter_id") or "").strip()
            if not req_id or not desc:
                continue
            if "[DELETED" in desc.upper():
                continue

            levels = []
            if (row.get("level1") or "").strip():
                levels.append(1)
            if (row.get("level2") or "").strip():
                levels.append(2)
            if (row.get("level3") or "").strip():
                levels.append(3)

            add_item(
                db,
                std,
                code=req_id,
                title=desc,
                description=desc,
                how_to_test=CHAPTER_HINTS.get(chapter, "Verify this requirement is met and document evidence."),
                asvs_level=min(levels) if levels else None,
            )
    db.commit()
