"""OWASP API Security Top 10 2023 - curated seed."""
from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-api-top10"

DATA = [
    (
        "API1:2023",
        "Broken Object Level Authorization",
        "APIs expose endpoints that handle object IDs, creating a wide attack surface for object-level access control issues.",
        "Manipulate object IDs in requests (path, query, payload) and attempt to access other users' objects.",
        "Enforce object-level authorization in every function that accesses a data source using an object ID.",
    ),
    (
        "API2:2023",
        "Broken Authentication",
        "Authentication mechanisms are often implemented incorrectly, allowing attackers to compromise tokens or assume identities.",
        "Test token generation/expiry, password reset, account lockout, and authentication flows for weaknesses.",
        "Implement secure authentication with strong secrets, short-lived tokens, and proper session handling.",
    ),
    (
        "API3:2023",
        "Broken Object Property Level Authorization",
        "This combines excessive data exposure and mass assignment, focusing on object property-level authorization failures.",
        "Attempt to read sensitive properties or submit extra properties on updates (mass assignment).",
        "Explicitly define and validate the object properties that can be read or written per user.",
    ),
    (
        "API4:2023",
        "Unrestricted Resource Consumption",
        "APIs without limits on resource use can be abused for DoS and resource exhaustion.",
        "Send heavy or numerous requests to test rate limiting, payload size caps, and concurrency controls.",
        "Implement rate limiting, queue-based processing, payload size limits, and resource quotas.",
    ),
    (
        "API5:2023",
        "Broken Function Level Authorization",
        "Complex access control policies with different hierarchies often lead to authorization flaws.",
        "Test both low-privileged and admin functions by changing methods, paths, or roles.",
        "Enforce function-level authorization on the server with a deny-by-default policy.",
    ),
    (
        "API6:2023",
        "Unrestricted Access to Sensitive Business Flows",
        "APIs exposing sensitive business flows without limits can be abused (e.g. voting, reservations).",
        "Identify sensitive business flows and test whether automated abuse or normalization is possible.",
        "Detect and limit automated access to sensitive business flows.",
    ),
    (
        "API7:2023",
        "Server-Side Request Forgery",
        "Attackers cause the server to make requests to an unintended destination.",
        "Influence URLs/inputs used for remote fetching to reach internal services.",
        "Allow-list destinations, use network segmentation, and restrict URL schemas.",
    ),
    (
        "API8:2023",
        "Security Misconfiguration",
        "APIs and supporting systems are commonly misconfigured leading to exposure.",
        "Check for unhardened endpoints, verbose errors, missing headers, unpatched components.",
        "Harden configurations, automate security checks, and keep components patched.",
    ),
    (
        "API9:2023",
        "Improper Inventory Management",
        "APIs and hosts are more exposed than traditional web apps; outdated versions are a common issue.",
        "Inventory API versions, hosts, and decommissioned environments; test outdated versions.",
        "Maintain an accurate inventory, version APIs, and decommission deprecated endpoints.",
    ),
    (
        "API10:2023",
        "Unsafe Consumption of APIs",
        "Developers trust data from external APIs more than user data, lowering security standards.",
        "Test how the application processes data from third-party APIs (SSRF, injection, redirects).",
        "Validate, sanitize, and treat data from third-party APIs as untrusted.",
    ),
]


def seed(db: Session) -> None:
    std, created = ensure_standard(
        db,
        SLUG,
        "OWASP API Security Top 10",
        "api",
        "2023",
        "The OWASP API Security Top 10 focuses on the most critical security risks to APIs.",
    )
    if not created:
        return
    for code, title, desc, how, rem in DATA:
        add_item(db, std, code=code, title=title, description=desc, how_to_test=how, remediation=rem)
    db.commit()
