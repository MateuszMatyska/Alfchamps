"""OWASP Mobile Application Security Verification Standard (MASVS) 2.x - curated seed."""
from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-masvs"

DATA = [
    (
        "MSTG-STORAGE-1", "Platform Data Storage", "Verifies that sensitive data is securely stored on the device.",
        "Inspect for sensitive data in local storage, log files, backups, and derived data.",
        "Use platform secure storage (Keychain/Keystore) and avoid logging sensitive data.", 0,
    ),
    (
        "MSTG-STORAGE-2", "Cache and Clipboard", "Checks for sensitive data leakage through caches and the clipboard.",
        "Review caching of user input and test copy/paste behaviour for sensitive fields.",
        "Disable caching/clipboard for sensitive fields where inappropriate.", 0,
    ),
    (
        "MSTG-CRYPTO-1", "Use of Strong Cryptography", "Ensures the app uses strong, approved cryptographic algorithms.",
        "Review crypto implementation for hard-coded keys, weak algorithms, custom crypto.",
        "Use platform-provided strong crypto and secure key handling.", 0,
    ),
    (
        "MSTG-AUTH-1", "Secure Authentication", "Verifies authentication mechanisms follow best practices.",
        "Test local vs remote authentication, session handling, and auth bypass.",
        "Prefer remote authentication; implement robust session management.", 0,
    ),
    (
        "MSTG-AUTH-2", "Session Handling", "Validates that sessions are managed securely.",
        "Review tokens, expiry, revocation, and handling of session in storage.",
        "Use short-lived, revocable tokens stored securely.", 0,
    ),
    (
        "MSTG-NETWORK-1", "Network Communication Security", "Ensures all network traffic is encrypted and authenticated.",
        "Intercept traffic (e.g. MITM proxy) to verify TLS everywhere and correct validation.",
        "Enforce TLS with certificate pinning where appropriate; validate certificates.", 0,
    ),
    (
        "MSTG-PLATFORM-1", "App Permissions", "Verifies the app only requests necessary permissions.",
        "Review requested permissions against app functionality.",
        "Request only required permissions, handle denial gracefully.", 0,
    ),
    (
        "MSTG-PLATFORM-2", "Exported Components", "Checks for insecure exported components/activities.",
        "Review AndroidManifest/iOS configuration for exported or open components.",
        "Protect exported components with permissions and validate intents.", 0,
    ),
    (
        "MSTG-RESILIENCE-1", "Reverse Engineering Resistance", "Assesses resilience against tampering and reverse engineering.",
        "Check for debugger detection, integrity checks, and obfuscation.",
        "Implement integrity checks, anti-debugging, and code obfuscation for high-risk apps.", 0,
    ),
    (
        "MSTG-CODE-1", "Input Validation & Sanitization", "Ensures the app validates and sanitizes inputs.",
        "Fuzz inputs (webviews, IPC, deep links, user forms) for injection.",
        "Apply allow-list validation and output encoding throughout.", 0,
    ),
    (
        "MSTG-DATA-1", "Data Protection in Transit", "Ensures sensitive data is protected during transmission.",
        "Test for plaintext data flows between app and backend.",
        "Encrypt all sensitive data in transit with TLS.", 0,
    ),
]


def seed(db: Session) -> None:
    std, created = ensure_standard(
        db,
        SLUG,
        "OWASP Mobile Application Security Verification Standard",
        "mobile",
        "2.x",
        "MASVS establishes security requirements for designing, developing, and testing mobile apps.",
    )
    if not created:
        return
    for code, title, desc, how, rem, _lvl in DATA:
        add_item(db, std, code=code, title=title, description=desc, how_to_test=how, remediation=rem)
    db.commit()
