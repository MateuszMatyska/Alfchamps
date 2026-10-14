"""OWASP API Security Top 10 2023 - curated seed."""
from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-api-top10"
_BASE = "https://owasp.org/API-Security/editions/2023/en/"

DATA = [
    (
        "API1:2023",
        "Broken Object Level Authorization",
        "APIs expose endpoints that handle object IDs, creating a wide attack surface for object-level access control issues.",
        "Manipulate object IDs in requests (path, query, payload) and attempt to access other users' objects.",
        "Authenticate as user A and replay requests with user B's object id: GET /api/orders/{id}, PATCH /api/users/{id}. Try sequential/guessable ids and confirm 403/404 is returned.",
        _BASE + "0xa1-broken-object-level-authorization/",
        "Enforce object-level authorization in every function that accesses a data source using an object ID.",
    ),
    (
        "API2:2023",
        "Broken Authentication",
        "Authentication mechanisms are often implemented incorrectly, allowing attackers to compromise tokens or assume identities.",
        "Test token generation/expiry, password reset, account lockout, and authentication flows for weaknesses.",
        "Craft a JWT with `alg:none` or a weak secret, reuse an expired/revoked token, and test unlimited login attempts. Check password-reset tokens for predictability.",
        _BASE + "0xa2-broken-authentication/",
        "Implement secure authentication with strong secrets, short-lived tokens, and proper session handling.",
    ),
    (
        "API3:2023",
        "Broken Object Property Level Authorization",
        "This combines excessive data exposure and mass assignment, focusing on object property-level authorization failures.",
        "Attempt to read sensitive properties or submit extra properties on updates (mass assignment).",
        "Inspect API responses for extra fields (password hashes, internal flags) and send extra properties on PATCH, e.g. {\"role\":\"admin\"} on a user update.",
        _BASE + "0xa3-broken-object-property-level-authorization/",
        "Explicitly define and validate the object properties that can be read or written per user.",
    ),
    (
        "API4:2023",
        "Unrestricted Resource Consumption",
        "APIs without limits on resource use can be abused for DoS and resource exhaustion.",
        "Send heavy or numerous requests to test rate limiting, payload size caps, and concurrency controls.",
        "Burst 100+ requests/second at a login or search endpoint and check for 429s. Submit a very large JSON body or request a huge `limit`/`page_size` and observe resource use.",
        _BASE + "0xa4-unrestricted-resource-consumption/",
        "Implement rate limiting, queue-based processing, payload size limits, and resource quotas.",
    ),
    (
        "API5:2023",
        "Broken Function Level Authorization",
        "Complex access control policies with different hierarchies often lead to authorization flaws.",
        "Test both low-privileged and admin functions by changing methods, paths, or roles.",
        "As a normal user, call administrative endpoints directly (GET /api/admin/users, DELETE /api/admin/user/1) and try HTTP method overrides (POST vs PUT vs DELETE).",
        _BASE + "0xa5-broken-function-level-authorization/",
        "Enforce function-level authorization on the server with a deny-by-default policy.",
    ),
    (
        "API6:2023",
        "Unrestricted Access to Sensitive Business Flows",
        "APIs exposing sensitive business flows without limits can be abused (e.g. voting, reservations).",
        "Identify sensitive business flows and test whether automated abuse or normalization is possible.",
        "Script a high-value flow (bulk coupon redemption, ticket reservation, referral bonuses) and check for anti-automation controls like CAPTCHA, device checks, or velocity limits.",
        _BASE + "0xa6-unrestricted-access-to-sensitive-business-flows/",
        "Detect and limit automated access to sensitive business flows.",
    ),
    (
        "API7:2023",
        "Server-Side Request Forgery",
        "Attackers cause the server to make requests to an unintended destination.",
        "Influence URLs/inputs used for remote fetching to reach internal services.",
        "Feed `http://169.254.169.254/latest/meta-data/iam/security-credentials/` or `http://127.0.0.1:22` into URL-based parameters and watch for internal responses or timing differences.",
        _BASE + "0xa7-server-side-request-forgery/",
        "Allow-list destinations, use network segmentation, and restrict URL schemas.",
    ),
    (
        "API8:2023",
        "Security Misconfiguration",
        "APIs and supporting systems are commonly misconfigured leading to exposure.",
        "Check for unhardened endpoints, verbose errors, missing headers, unpatched components.",
        "Trigger errors to reveal stack traces, check CORS with an arbitrary `Origin`, look for exposed `/docs`, `/metrics`, or debug endpoints, and review TLS/headers.",
        _BASE + "0xa8-security-misconfiguration/",
        "Harden configurations, automate security checks, and keep components patched.",
    ),
    (
        "API9:2023",
        "Improper Inventory Management",
        "APIs and hosts are more exposed than traditional web apps; outdated versions are a common issue.",
        "Inventory API versions, hosts, and decommissioned environments; test outdated versions.",
        "Try older versions (`/v1/` vs `/v2/`), alternate hosts (staging/api-beta), and undocumented endpoints discovered in JS bundles or Swagger. Compare auth between versions.",
        _BASE + "0xa9-improper-inventory-management/",
        "Maintain an accurate inventory, version APIs, and decommission deprecated endpoints.",
    ),
    (
        "API10:2023",
        "Unsafe Consumption of APIs",
        "Developers trust data from external APIs more than user data, lowering security standards.",
        "Test how the application processes data from third-party APIs (SSRF, injection, redirects).",
        "Point an integration at a controlled mock API that returns malicious data (redirects, injection payloads, oversized bodies) and observe how the client handles it.",
        _BASE + "0xa10-unsafe-consumption-of-apis/",
        "Validate, sanitize, and treat data from third-party APIs as untrusted.",
    ),
]


def seed(db: Session) -> None:
    std, _ = ensure_standard(
        db,
        SLUG,
        "OWASP API Security Top 10",
        "api",
        "2023",
        "The OWASP API Security Top 10 focuses on the most critical security risks to APIs.",
    )
    for code, title, desc, how, examples, url, rem in DATA:
        add_item(
            db, std,
            code=code, title=title, description=desc, how_to_test=how,
            test_examples=examples, reference_url=url, remediation=rem,
        )
    db.commit()
