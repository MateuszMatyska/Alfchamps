"""OWASP Top 10 Web Application Security Risks 2021 - curated seed."""
from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-top10-web"

DATA = [
    (
        "A01",
        "Broken Access Control",
        "Restrictions on what authenticated users are allowed to do are often not properly enforced.",
        "Enumerate functions and objects (files, DB rows) and attempt to access resources outside the user's intended permissions.",
        "Enforce access control on the server, deny by default, apply least privilege, and fail securely.",
    ),
    (
        "A02",
        "Cryptographic Failures",
        "Failures related to cryptography, often leading to sensitive data exposure.",
        "Review all data in transit and at rest for encryption; check for weak algorithms, missing TLS, insecure key storage.",
        "Use modern strong algorithms, TLS 1.3/1.2, protect keys with proper secret management, encrypt sensitive data at rest.",
    ),
    (
        "A03",
        "Injection",
        "User-supplied data is not validated, filtered, or sanitized before being processed as part of code or a query.",
        "Feed malicious input into SQL, OS, LDAP, XPath, and other interpreters and observe result.",
        "Use parameterized queries/prepared statements, allow-list input validation, output encoding.",
    ),
    (
        "A04",
        "Insecure Design",
        "Missing or ineffective control design, often architectural, leading to flawed business logic.",
        "Threat model the application; abuse case testing for business logic, rate limiting, and workflow weakness.",
        "Adopt secure design patterns, threat modeling, and reference architectures during design phase.",
    ),
    (
        "A05",
        "Security Misconfiguration",
        "Security could be misconfigured leaving the system vulnerable.",
        "Check for default credentials, missing security headers, verbose error messages, directory listing, unnecessary features.",
        "Harden configuration, remove default accounts, set strict headers, automate configuration reviews.",
    ),
    (
        "A06",
        "Vulnerable and Outdated Components",
        "Using components (libraries, frameworks) with known vulnerabilities.",
        "Inventory all components and versions and compare against CVE databases and dependency scanners.",
        "Remove unused deps, continuously update/scan components, use software composition analysis.",
    ),
    (
        "A07",
        "Identification and Authentication Failures",
        "Failures related to the functions of authentication and session management.",
        "Test password policies, MFA, session handling, credential recovery and lockout mechanisms.",
        "Use strong auth (MFA), secure session management, rate-limiting, and NIST password guidelines.",
    ),
    (
        "A08",
        "Software and Data Integrity Failures",
        "Failures related to code and infrastructure that do not protect against integrity violations.",
        "Test for insecure deserialization, missing integrity checks on software updates, and CI/CD pipeline attacks.",
        "Verify integrity of code and data, use digital signatures, secure the CI/CD pipeline.",
    ),
    (
        "A09",
        "Security Logging and Monitoring Failures",
        "Failure to log and monitor security events, hampering detection and response.",
        "Check whether security events (auth, admin actions) are logged and monitored, and logs are protected.",
        "Log sufficient detail without sensitive data, centralize monitoring, detect anomalies and alert.",
    ),
    (
        "A10",
        "Server-Side Request Forgery (SSRF)",
        "An attacker makes the server-side application make requests to an unintended location.",
        "Test URL inputs that fetch remote resources; attempt to reach internal services, localhost, and metadata endpoints.",
        "Allow-list remote destinations, disable following redirects, restrict network access, validate URL schemas.",
    ),
]


def seed(db: Session) -> None:
    std, created = ensure_standard(
        db,
        SLUG,
        "OWASP Top 10 Web Application Security Risks",
        "web",
        "2021",
        "The OWASP Top 10 is a standard awareness document for developers and web application security.",
    )
    if not created:
        return
    for code, title, desc, how, rem in DATA:
        add_item(db, std, code=code, title=title, description=desc, how_to_test=how, remediation=rem)
    db.commit()
