"""
D_CRYPTO invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ontology/ontology.json#D_CRYPTO
"""

import hmac
import hashlib

from src.domains.d_crypto.implementation import (
    constant_time_compare,
    constant_time_hmac,
    validate_psk,
    generate_psk,
)


def check_constant_time_compare_uses_hmac() -> bool:
    """
    Invariant: All secret-dependent operations are constant-time.
    Falsification: If hmac.compare_digest is not in use, the structural guarantee is absent.

    Checks that our constant_time_compare delegates to hmac.compare_digest.
    """
    import inspect
    source = inspect.getsource(constant_time_compare)
    assert "hmac.compare_digest" in source, (
        "constant_time_compare must use hmac.compare_digest — F_CRYPTO_001 structural check"
    )
    return True


def check_psk_zero_rejected() -> bool:
    """
    Invariant: Protocol validity rules (PSK ≠ 0^32) are enforced at the API boundary.
    Falsification: If validate_psk accepts b'\\x00'*32, the invariant is violated.
    """
    import sys
    zero_psk = b"\x00" * 32
    try:
        validate_psk(zero_psk)
        raise AssertionError("validate_psk accepted zero PSK — F_CRYPTO_002 VIOLATED")
    except ValueError:
        pass  # expected: zero PSK must be rejected
    return True


def check_psk_nonzero_accepted() -> bool:
    """
    Invariant: Valid PSKs (≠ 0^32) must be accepted at the boundary.
    Falsification: If a valid PSK raises ValueError, implementation is over-restrictive.
    """
    psk = generate_psk()
    result = validate_psk(psk)
    assert result == psk, "validate_psk must return the validated PSK"
    return True


def check_hmac_deterministic() -> bool:
    """
    Invariant: HMAC is a pure function — same key+message → same digest.
    Falsification: Two calls with identical inputs return different values.
    """
    key = b"\x42" * 32
    msg = b"test message"
    d1 = constant_time_hmac(key, msg)
    d2 = constant_time_hmac(key, msg)
    assert d1 == d2, f"HMAC not deterministic: {d1.hex()} != {d2.hex()}"
    assert len(d1) == 32, f"HMAC-SHA256 must be 32 bytes, got {len(d1)}"
    return True


def run_all_invariants() -> dict:
    """Run all D_CRYPTO invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_constant_time_compare_uses_hmac,
        check_psk_zero_rejected,
        check_psk_nonzero_accepted,
        check_hmac_deterministic,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CRYPTO invariants: PASS")
