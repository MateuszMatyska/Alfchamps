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
        "Try IDOR by changing an object id: GET /api/users/123 -> GET /api/users/124. Force-browse to /admin while logged in as a normal user. Replay a request with the role parameter flipped (role=user -> role=admin).",
        "https://owasp.org/Top10/A01_2021-Broken_Access_Control/",
        "Enforce access control on the server, deny by default, apply least privilege, and fail securely.",
    ),
    (
        "A02",
        "Cryptographic Failures",
        "Failures related to cryptography, often leading to sensitive data exposure.",
        "Review all data in transit and at rest for encryption; check for weak algorithms, missing TLS, insecure key storage.",
        "Run `testssl.sh https://target` and look for TLS 1.0/1.1, RC4, or NULL ciphers. Inspect cookies for missing Secure/HttpOnly. Check response bodies and URLs for cleartext secrets, SSNs, or tokens.",
        "https://owasp.org/Top10/A02_2021-Cryptographic_Failures/",
        "Use modern strong algorithms, TLS 1.3/1.2, protect keys with proper secret management, encrypt sensitive data at rest.",
    ),
    (
        "A03",
        "Injection",
        "User-supplied data is not validated, filtered, or sanitized before being processed as part of code or a query.",
        "Feed malicious input into SQL, OS, LDAP, XPath, and other interpreters and observe result.",
        "Send `' OR '1'='1` in a login form; try `1; SELECT pg_sleep(5)--` and watch for a delay. Use `$(id)` / `; whoami` for command injection and `<script>alert(1)</script>` for reflected XSS.",
        "https://owasp.org/Top10/A03_2021-Injection/",
        "Use parameterized queries/prepared statements, allow-list input validation, output encoding.",
    ),
    (
        "A04",
        "Insecure Design",
        "Missing or ineffective control design, often architectural, leading to flawed business logic.",
        "Threat model the application; abuse case testing for business logic, rate limiting, and workflow weakness.",
        "Walk a checkout/reset flow out of order, reuse a single-use coupon, submit negative quantities, or skip a payment step. Confirm anti-automation controls exist on sensitive endpoints.",
        "https://owasp.org/Top10/A04_2021-Insecure_Design/",
        "Adopt secure design patterns, threat modeling, and reference architectures during design phase.",
    ),
    (
        "A05",
        "Security Misconfiguration",
        "Security could be misconfigured leaving the system vulnerable.",
        "Check for default credentials, missing security headers, verbose error messages, directory listing, unnecessary features.",
        "Request a non-existent path and look for stack traces. Send `OPTIONS`/`TRACE`. Fetch `/server-status`, `/.git/config`, `/swagger-ui.html`. Verify CSP, HSTS, X-Frame-Options headers are present.",
        "https://owasp.org/Top10/A05_2021-Security_Misconfiguration/",
        "Harden configuration, remove default accounts, set strict headers, automate configuration reviews.",
    ),
    (
        "A06",
        "Vulnerable and Outdated Components",
        "Using components (libraries, frameworks) with known vulnerabilities.",
        "Inventory all components and versions and compare against CVE databases and dependency scanners.",
        "Fingerprint the stack (Wappalyzer / response headers), then map versions to CVEs. Run `npm audit`, `pip-audit`, or OWASP Dependency-Check against the manifest if available.",
        "https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/",
        "Remove unused deps, continuously update/scan components, use software composition analysis.",
    ),
    (
        "A07",
        "Identification and Authentication Failures",
        "Failures related to the functions of authentication and session management.",
        "Test password policies, MFA, session handling, credential recovery and lockout mechanisms.",
        "Attempt credential stuffing with a small wordlist, check for username enumeration via login/reset messages, verify the session id rotates after login, and test whether logout invalidates the token.",
        "https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/",
        "Use strong auth (MFA), secure session management, rate-limiting, and NIST password guidelines.",
    ),
    (
        "A08",
        "Software and Data Integrity Failures",
        "Failures related to code and infrastructure that do not protect against integrity violations.",
        "Test for insecure deserialization, missing integrity checks on software updates, and CI/CD pipeline attacks.",
        "Look for auto-update mechanisms without signature checks, unsigned JWTs (`alg:none`), or serialized objects in cookies/params. Try tampering with a signed value and confirm rejection.",
        "https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/",
        "Verify integrity of code and data, use digital signatures, secure the CI/CD pipeline.",
    ),
    (
        "A09",
        "Security Logging and Monitoring Failures",
        "Failure to log and monitor security events, hampering detection and response.",
        "Check whether security events (auth, admin actions) are logged and monitored, and logs are protected.",
        "Trigger failed logins and admin actions, then confirm they are recorded without secrets/PII. Verify logs cannot be spoofed or read by unauthenticated users.",
        "https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/",
        "Log sufficient detail without sensitive data, centralize monitoring, detect anomalies and alert.",
    ),
    (
        "A10",
        "Server-Side Request Forgery (SSRF)",
        "An attacker makes the server-side application make requests to an unintended location.",
        "Test URL inputs that fetch remote resources; attempt to reach internal services, localhost, and metadata endpoints.",
        "Submit URLs such as `http://127.0.0.1:80`, `http://169.254.169.254/latest/meta-data/`, or `http://[::1]` into any fetch/webhook/import field and observe the response or timing.",
        "https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/",
        "Allow-list remote destinations, disable following redirects, restrict network access, validate URL schemas.",
    ),
]


def seed(db: Session) -> None:
    std, _ = ensure_standard(
        db,
        SLUG,
        "OWASP Top 10 Web Application Security Risks",
        "web",
        "2021",
        "The OWASP Top 10 is a standard awareness document for developers and web application security.",
    )
    for code, title, desc, how, examples, url, rem in DATA:
        add_item(
            db, std,
            code=code, title=title, description=desc, how_to_test=how,
            test_examples=examples, reference_url=url, remediation=rem,
        )
    db.commit()
