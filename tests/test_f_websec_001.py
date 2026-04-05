"""F_WEBSEC_001 — sanitization and CSRF boundary checks."""

from src.domains.d_websec.implementation import (
    generate_csp_header,
    html_escape,
    mint_csrf_token,
    sanitize_payload,
    validate_csrf_token,
)


def test_websec_sanitization_and_csrf_boundary():
    raw = "<script>alert('x')</script>"
    escaped = html_escape(raw)
    assert "<" not in escaped
    assert ">" not in escaped
    assert "&lt;script&gt;" in escaped

    payload = {"a": raw, "b": "safe"}
    sanitized = sanitize_payload(payload)
    assert sanitized["a"] == escaped
    assert sanitized["b"] == "safe"
    assert sanitized != payload

    csp = generate_csp_header()
    assert "default-src 'self'" in csp
    assert "object-src 'none'" in csp

    secret = b"secret-secret-secret-secret-1234"
    token = mint_csrf_token("s1", secret)
    assert validate_csrf_token("s1", token, secret)
    assert not validate_csrf_token("s2", token, secret)
