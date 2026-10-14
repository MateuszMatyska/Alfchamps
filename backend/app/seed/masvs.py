"""OWASP Mobile Application Security Verification Standard (MASVS) 2.x - curated seed."""
from sqlalchemy.orm import Session

from .helpers import add_item, ensure_standard

SLUG = "owasp-masvs"
_BASE = "https://mas.owasp.org/MASVS/"

DATA = [
    (
        "MSTG-STORAGE-1", "Platform Data Storage", "Verifies that sensitive data is securely stored on the device.",
        "Inspect for sensitive data in local storage, log files, backups, and derived data.",
        "Pull the app sandbox (adb backup / idevicebackup2), grep for tokens and PII, and check SharedPreferences/NSUserDefaults and the Keychain/Keystore.",
        _BASE + "05-MASVS-STORAGE/",
        "Use platform secure storage (Keychain/Keystore) and avoid logging sensitive data.", 0,
    ),
    (
        "MSTG-STORAGE-2", "Cache and Clipboard", "Checks for sensitive data leakage through caches and the clipboard.",
        "Review caching of user input and test copy/paste behaviour for sensitive fields.",
        "Copy a sensitive field and inspect the clipboard with a helper app; check screenshots/app-switcher previews and keyboard cache for secrets.",
        _BASE + "05-MASVS-STORAGE/",
        "Disable caching/clipboard for sensitive fields where inappropriate.", 0,
    ),
    (
        "MSTG-CRYPTO-1", "Use of Strong Cryptography", "Ensures the app uses strong, approved cryptographic algorithms.",
        "Review crypto implementation for hard-coded keys, weak algorithms, custom crypto.",
        "Static-analyse the binary for hard-coded keys/IVs, ECB mode, MD5/SHA1, or `Random` instead of a CSPRNG. Check key material is not derived insecurely.",
        _BASE + "06-MASVS-CRYPTO/",
        "Use platform-provided strong crypto and secure key handling.", 0,
    ),
    (
        "MSTG-AUTH-1", "Secure Authentication", "Verifies authentication mechanisms follow best practices.",
        "Test local vs remote authentication, session handling, and auth bypass.",
        "Attempt biometric/PIN bypass on a rooted/jailbroken device, test whether auth state is checked server-side, and try to skip the login screen via deep links.",
        _BASE + "07-MASVS-AUTH/",
        "Prefer remote authentication; implement robust session management.", 0,
    ),
    (
        "MSTG-AUTH-2", "Session Handling", "Validates that sessions are managed securely.",
        "Review tokens, expiry, revocation, and handling of session in storage.",
        "Inspect tokens for expiry/length/entropy, verify server-side revocation on logout, and confirm tokens are not stored in plaintext or reused across sessions.",
        _BASE + "07-MASVS-AUTH/",
        "Use short-lived, revocable tokens stored securely.", 0,
    ),
    (
        "MSTG-NETWORK-1", "Network Communication Security", "Ensures all network traffic is encrypted and authenticated.",
        "Intercept traffic (e.g. MITM proxy) to verify TLS everywhere and correct validation.",
        "Proxy traffic (Burp/mitmproxy) with a custom CA and look for cleartext HTTP, ignored certificate errors, or missing pinning. Try downgrade/redirect attempts.",
        _BASE + "08-MASVS-NETWORK/",
        "Enforce TLS with certificate pinning where appropriate; validate certificates.", 0,
    ),
    (
        "MSTG-PLATFORM-1", "App Permissions", "Verifies the app only requests necessary permissions.",
        "Review requested permissions against app functionality.",
        "List the manifest/Info.plist permissions and compare to actual feature use; flag dangerous permissions not justified by functionality.",
        _BASE + "09-MASVS-PLATFORM/",
        "Request only required permissions, handle denial gracefully.", 0,
    ),
    (
        "MSTG-PLATFORM-2", "Exported Components", "Checks for insecure exported components/activities.",
        "Review AndroidManifest/iOS configuration for exported or open components.",
        "Enumerate exported activities/services/providers, then invoke them with `adb shell am start` or a malicious app and test for missing permission checks or intent validation.",
        _BASE + "09-MASVS-PLATFORM/",
        "Protect exported components with permissions and validate intents.", 0,
    ),
    (
        "MSTG-RESILIENCE-1", "Reverse Engineering Resistance", "Assesses resilience against tampering and reverse engineering.",
        "Check for debugger detection, integrity checks, and obfuscation.",
        "Attach a debugger, repackage the APK with a modified payload, and run on a rooted device to see whether tamper/root/debug detection triggers.",
        _BASE + "10-MASVS-RESILIENCE/",
        "Implement integrity checks, anti-debugging, and code obfuscation for high-risk apps.", 0,
    ),
    (
        "MSTG-CODE-1", "Input Validation & Sanitization", "Ensures the app validates and sanitizes inputs.",
        "Fuzz inputs (webviews, IPC, deep links, user forms) for injection.",
        "Send crafted deep links, intents, or WebView payloads (`javascript:`, `file://`) and check for injection or unauthorized actions.",
        _BASE + "11-MASVS-CODE/",
        "Apply allow-list validation and output encoding throughout.", 0,
    ),
    (
        "MSTG-DATA-1", "Data Protection in Transit", "Ensures sensitive data is protected during transmission.",
        "Test for plaintext data flows between app and backend.",
        "Capture traffic and look for sensitive fields sent over cleartext or unprotected channels; verify credentials never travel without TLS.",
        _BASE + "08-MASVS-NETWORK/",
        "Encrypt all sensitive data in transit with TLS.", 0,
    ),
]


def seed(db: Session) -> None:
    std, _ = ensure_standard(
        db,
        SLUG,
        "OWASP Mobile Application Security Verification Standard",
        "mobile",
        "2.x",
        "MASVS establishes security requirements for designing, developing, and testing mobile apps.",
    )
    for code, title, desc, how, examples, url, rem, _lvl in DATA:
        add_item(
            db, std,
            code=code, title=title, description=desc, how_to_test=how,
            test_examples=examples, reference_url=url, remediation=rem,
        )
    db.commit()
