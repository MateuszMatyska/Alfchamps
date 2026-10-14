"""OWASP Web Security Testing Guide (WSTG) full checklist seed.

Parses the bundled official WSTG testing checklist (shipped in data/), which
was downloaded at build time from the OWASP WSTG repository. All 12 categories
are included as full-report coverage. Per-category how-to hints, concrete test
examples, and deep links to the official WSTG category page are attached.
"""
import re
from pathlib import Path

from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-wstg"
MD_PATH = Path(__file__).parent / "data" / "wstg-checklist.md"
_BASE = "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/"

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

CATEGORY_EXAMPLES = {
    "INFO": "Use `whois`, DNS enumeration, and search-engine dorks (e.g. `site:target.com filetype:pdf`) to map hosts, emails, and exposed documents.",
    "CONF": "Send `OPTIONS`/`TRACE`, fetch `/server-status`, and check for exposed `.git`, backups, and default admin consoles.",
    "IDNT": "Register two accounts and probe registration/reset responses for username enumeration and weak policy.",
    "ATHN": "Try default creds (admin/admin), brute-force a small wordlist, and test MFA bypass and lockout thresholds.",
    "ATHZ": "Change object ids (IDOR: `id=100` -> `id=101`) and call admin functions as a low-privileged user.",
    "SESS": "Inspect cookie flags, replay a session after logout, and manipulate JWT `alg`/claims to escalate.",
    "INPV": "Inject `' OR '1'='1`, `<script>alert(1)</script>`, and `$(id)` payloads into parameters, headers, and JSON.",
    "ERRH": "Send malformed input and `Accept: application/xml` to trigger stack traces or verbose framework errors.",
    "CRYP": "Run `testssl.sh`, test for padding-oracle behaviour, and look for weak/short keys or ECB mode.",
    "BUSLOGIC": "Reuse a single-use coupon, submit negative quantities, and race concurrent redemption requests.",
    "CLIENT": "Test DOM XSS via `#<img src=x onerror=alert(1)>`, DOM-based redirects, and CORS misconfiguration.",
    "APIT": "Enumerate `/api/v1/`, then test object-level authz and GraphQL introspection/query abuse.",
}

CATEGORY_URLS = {
    "INFO": "01-Information_Gathering",
    "CONF": "02-Configuration_and_Deployment_Management_Testing",
    "IDNT": "03-Identity_Management_Testing",
    "ATHN": "04-Authentication_Testing",
    "ATHZ": "05-Authorization_Testing",
    "SESS": "06-Session_Management_Testing",
    "INPV": "07-Input_Validation_Testing",
    "ERRH": "08-Error_Handling",
    "CRYP": "09-Cryptography",
    "BUSLOGIC": "10-Business_Logic_Testing",
    "CLIENT": "11-Client-side_Testing",
    "APIT": "12-API_Testing",
}


def seed(db: Session) -> None:
    std, _ = ensure_standard(
        db,
        SLUG,
        "OWASP Web Security Testing Guide (WSTG)",
        "web",
        "v4.2",
        "The WSTG is a comprehensive open-source guide to testing the security of web "
        "applications and web services, organized into testing categories.",
    )
    if not MD_PATH.exists():
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
                folder = CATEGORY_URLS.get(category)
                add_item(
                    db,
                    std,
                    code=code,
                    title=title,
                    description=title,
                    how_to_test=CATEGORY_HINTS.get(category, "Apply the OWASP WSTG methodology for this test."),
                    test_examples=CATEGORY_EXAMPLES.get(category, ""),
                    reference_url=(_BASE + folder + "/") if folder else "",
                    remediation="Document the test outcome, impacted components, and recommended remediation.",
                )
    db.commit()
