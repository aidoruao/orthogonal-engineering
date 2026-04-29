"""
Falsification test: XSS payload is neutralized before HTML output.
HTML special chars are escaped.

# @falsification_id: F_XSS_001
"""
import html
import pytest

XSS_PAYLOADS = [
    '<script>alert(1)</script>',
    '"><img src=x onerror=alert(1)>',
    "javascript:alert(1)",
    '<svg onload=alert(1)>',
]

def sanitize(s: str) -> str:
    # TODO: Expand sanitize() - stub detected by Yeshua Agent
    return html.escape(s, quote=True)

def test_xss_payloads_escaped():
    for payload in XSS_PAYLOADS:
        result = sanitize(payload)
        assert "<script" not in result.lower()
        assert "onerror" not in result.lower() or "&" in result
        assert result != payload or "<" not in payload, f"Payload not escaped: {payload!r}"
        assert "&lt;" in result or "<" not in payload, f"< not escaped in: {result!r}"
