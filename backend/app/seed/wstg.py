"""OWASP Web Security Testing Guide (WSTG) full checklist seed.

Parses the bundled official WSTG testing checklist (shipped in data/), which
was downloaded at build time from the OWASP WSTG repository. All 12 categories
are included as full-report coverage. A concise how-to-test hint is derived from
the category.
"""
import re
from pathlib import Path

from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-wstg"
MD_PATH = Path(__file__).parent / "data" / "wstg-checklist.md"

CATEGORY_HINTS = {
    "INFO": "Gather data about the target (reconnaissance, fingerprinting, entry points).",
    "CONF": "Inspect the target's network, platform, HTTP methods, headers, and deployment configuration.",
    "IDNT": "Test user identity lifecycle: registration, provisioning, roles, and enumeration.",
    "ATHN": "Test authentication: credential transport, defaults, lockout, bypass, and MFA.",
    "ATHZ": "Test authorization: traversal, schema bypass, privilege escalation, and IDOR.",
    "SESS": "Test session management: tokens, cookies, fixation, CSRF, timeout, and JWT.",
    "INPV": "Inject payloads into all inputs (XSS, SQL, XML, command, template, SSRF, and more).",
    "ERRH": "Trigger errors and check for verbose or stack-trace disclosure.",
    "CRYP": "Verify TLS strength, padding oracles, and encryption of sensitive traffic/data.",
    "BUSLOGIC": "Abuse business logic: data validation, forging, timing, workflows, and file uploads.",
    "CLIENT": "Test client-side: DOM XSS, JS, HTML/CSS injection, CORS, WebSockets, storage, clickjacking.",
    "APIT": "Test API endpoints: reconnaissance, object-level authorization, and GraphQL.",
}


def seed(db: Session) -> None:
    std, created = ensure_standard(
        db,
        SLUG,
        "OWASP Web Security Testing Guide (WSTG)",
        "web",
        "v4.2",
        "The WSTG is a comprehensive open-source guide to testing the security of web "
        "applications and web services, organized into testing categories.",
    )
    if not created or not MD_PATH.exists():
        return

    category = None
    with MD_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            header = re.search(r"\*\*(WSTG-[A-Z]+)\*\*", line)
            if header:
                category = header.group(1).split("-", 1)[1]
                continue
            m = re.match(r"^\|\s*(WSTG-[A-Z]+-\d+)\s*\|\s*([^|]+?)\s*\|", line)
            if m and category:
                code = m.group(1).strip()
                title = m.group(2).strip()
                if title.lower() in {"test id", "test name"} or code.endswith("000"):
                    continue
                add_item(
                    db,
                    std,
                    code=code,
                    title=title,
                    description=title,
                    how_to_test=CATEGORY_HINTS.get(category, "Apply the OWASP WSTG methodology for this test."),
                    remediation="Document the test outcome, impacted components, and recommended remediation.",
                )
    db.commit()
