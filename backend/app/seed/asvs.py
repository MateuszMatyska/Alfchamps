"""OWASP ASVS 4.0.3 full requirements seed.

Parses the bundled official ASVS 4.0.3 CSV (shipped in data/), which was
downloaded at build time from the OWASP repository. Each requirement carries
its ASVS security level (L1/L2/L3) so the wizard can filter which items are
included. Rows marked [DELETED] are skipped.

Each requirement links to the official ASVS 4.0.3 chapter markdown on GitHub
(anchored to its section) and carries a chapter-level testing example.
"""
import csv
import re
from pathlib import Path

from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-asvs"
CSV_PATH = Path(__file__).parent / "data" / "asvs-4.0.3.csv"
GH_BASE = "https://github.com/OWASP/ASVS/blob/v4.0.3/4.0/en/"

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

CHAPTER_EXAMPLES = {
    "V1": "Review the threat model and secure-SDLC evidence; map each documented control to its enforcement point in code/CI.",
    "V2": "Attempt credential stuffing and username enumeration; verify MFA, lockout, and password-reset tokens.",
    "V3": "Inspect Set-Cookie flags (Secure/HttpOnly/SameSite), confirm the session id rotates on login, and that logout revokes it.",
    "V4": "Change object ids (IDOR), replay requests as another role, and force-browse to admin functions.",
    "V5": "Submit SQLi/NoSQL/XSS/command payloads to every parameter and confirm they are rejected or safely encoded.",
    "V6": "Check for TLS 1.0/1.1, MD5/SHA1, ECB mode, hard-coded keys, and predictable random values.",
    "V7": "Trigger 500s and auth failures; verify no stack traces/PII leak and that security events are logged.",
    "V8": "Look for tokens/PII in URLs, browser cache, autocomplete, and API responses; verify server-side caching doesn't leak.",
    "V9": "Run testssl.sh and inspect certificate validation; verify HSTS and that no cleartext channel is used.",
    "V10": "Review dependencies and build pipeline for integrity checks; test that unsigned/unexpected code cannot execute.",
    "V11": "Walk business flows out of order, reuse one-time values, and check for anti-automation limits.",
    "V12": "Upload unexpected file types, test path traversal, and provide internal URLs to any fetch/import feature (SSRF).",
    "V13": "Test REST/GraphQL endpoints for object/function-level authz, filtering, and injection via structured queries.",
    "V14": "Verify security headers, disabled debug endpoints, dependency hygiene, and hardened defaults.",
}

CHAPTER_FILE = {
    "V1": "0x10-V1-Architecture.md",
    "V2": "0x11-V2-Authentication.md",
    "V3": "0x12-V3-Session-management.md",
    "V4": "0x12-V4-Access-Control.md",
    "V5": "0x13-V5-Validation-Sanitization-Encoding.md",
    "V6": "0x14-V6-Cryptography.md",
    "V7": "0x15-V7-Error-Logging.md",
    "V8": "0x16-V8-Data-Protection.md",
    "V9": "0x17-V9-Communications.md",
    "V10": "0x18-V10-Malicious.md",
    "V11": "0x19-V11-BusLogic.md",
    "V12": "0x20-V12-Files-Resources.md",
    "V13": "0x21-V13-API.md",
    "V14": "0x22-V14-Config.md",
}


def _anchor(text: str) -> str:
    """Approximate GitHub heading anchor: lowercase, punctuation stripped."""
    slug = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    return re.sub(r"[\s-]+", "-", slug).strip("-")


def _reference_url(chapter: str, section_id: str, section_name: str) -> str:
    chapter_file = CHAPTER_FILE.get(chapter)
    if not chapter_file:
        return ""
    url = GH_BASE + chapter_file
    if section_id and section_name:
        url += "#" + _anchor(f"{section_id} {section_name}")
    return url


def seed(db: Session) -> None:
    std, _ = ensure_standard(
        db,
        SLUG,
        "OWASP Application Security Verification Standard (ASVS)",
        "web",
        "4.0.3",
        "ASVS defines a classification of security requirements and verification levels "
        "for web applications, from Level 1 (automated/opportunistic) to Level 3 (high-value/high-risk).",
    )
    if not CSV_PATH.exists():
        return

    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            req_id = (row.get("req_id") or "").strip()
            desc = (row.get("req_description") or "").strip()
            chapter = (row.get("chapter_id") or "").strip()
            section_id = (row.get("section_id") or "").strip()
            section_name = (row.get("section_name") or "").strip()
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
                test_examples=CHAPTER_EXAMPLES.get(chapter, ""),
                reference_url=_reference_url(chapter, section_id, section_name),
                asvs_level=min(levels) if levels else None,
            )
    db.commit()
