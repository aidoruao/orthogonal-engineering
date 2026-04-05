"""D_WEBSEC executable invariants."""

from src.domains.d_websec.implementation import (
    generate_csp_header,
    mint_csrf_token,
    sanitize_payload,
    validate_csrf_token,
)


def check_no_unsanitized_output() -> bool:
    payload = {"body": "<script>alert(1)</script>"}
    result = sanitize_payload(payload)
    assert "<script>" not in result["body"]
    assert "&lt;script&gt;" in result["body"]
    return True


def check_csp_default_is_restrictive() -> bool:
    csp = generate_csp_header()
    assert "default-src 'self'" in csp
    assert "object-src 'none'" in csp
    return True


def check_csrf_session_bound() -> bool:
    secret = b"session-secret-32-bytes-len-123456"
    token = mint_csrf_token("A", secret)
    assert validate_csrf_token("A", token, secret)
    assert not validate_csrf_token("B", token, secret)
    return True


def run_all_invariants() -> dict:
    checks = [
        check_no_unsanitized_output,
        check_csp_default_is_restrictive,
        check_csrf_session_bound,
    ]
    result = {}
    for c in checks:
        try:
            c()
            result[c.__name__] = "PASS"
        except AssertionError as e:
            result[c.__name__] = f"FAIL: {e}"
    return result
