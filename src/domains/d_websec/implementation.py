"""
D_WEBSEC — Web Security domain implementation.

Invariants:
  1. Input sanitization never passes unsanitized content to output boundaries.
  2. CSP headers are deterministic and restrictive by default.
  3. CSRF validation requires session-bound exact token match.

Biblical inspiration: "Guard your heart, for everything you do flows from it."
(Proverbs 4:23)
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Dict


def html_escape(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("html_escape: text must be str")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def sanitize_payload(payload: dict[str, str]) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise TypeError("payload must be dict")
    out: dict[str, str] = {}
    for k, v in payload.items():
        out[str(k)] = html_escape(str(v))
    return out


def generate_csp_header(allow_inline_scripts: bool = False) -> str:
    script_src = "'self'"
    if allow_inline_scripts:
        script_src = "'self' 'unsafe-inline'"
    directives = [
        "default-src 'self'",
        f"script-src {script_src}",
        "object-src 'none'",
        "base-uri 'none'",
        "frame-ancestors 'none'",
    ]
    return "; ".join(directives)


def mint_csrf_token(session_id: str, secret: bytes) -> str:
    if not isinstance(secret, (bytes, bytearray)):
        raise TypeError("secret must be bytes")
    if not session_id:
        raise ValueError("session_id must not be empty")
    material = session_id.encode("utf-8")
    return hmac.new(secret, material, hashlib.sha256).hexdigest()


def validate_csrf_token(session_id: str, supplied_token: str, secret: bytes) -> bool:
    expected = mint_csrf_token(session_id, secret)
    return hmac.compare_digest(expected, supplied_token)


DOMAIN_METADATA = {
    "id": "D_WEBSEC",
    "name": "Web Security",
    "invariants": [
        "Input sanitization never passes unsanitized content to output boundaries.",
        "CSP headers are deterministic and restrictive by default.",
        "CSRF validation requires session-bound exact token match.",
    ],
    "falsification_tests": ["F_XSS_001"],
    "implementation_functions": [
        "html_escape",
        "sanitize_payload",
        "generate_csp_header",
        "mint_csrf_token",
        "validate_csrf_token",
    ],
}
