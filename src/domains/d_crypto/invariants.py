"""D_CRYPTO invariants — Yeshua Standard. 0 floats.

Standards:
- NIST FIPS 186-5 — Digital Signature Standard
- NIST SP 800-131A — Cryptographic Algorithm Transitions
- RFC 8446 — TLS 1.3
- FIPS 140-3 — Security Requirements for Cryptographic Modules
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import (
    constant_time_compare, validate_psk, generate_psk, CryptoError
)


def check_constant_time_compare_equal(a: bytes, b: bytes) -> Tuple[bool, ProofObject]:
    """constant_time_compare(a, a) must return True.

    Standard: NIST SP 800-131A — constant-time comparison requirement
    falsifies_if: constant_time_compare(a, a) returns False.
    """
    result = constant_time_compare(a, a)
    ok = result is True
    premises = [f"a_len={len(a)}", f"result={result}"]
    return ok, ProofObject(
        rule="ConstantTimeCompareEqual",
        premises=premises,
        conclusion="PASS: constant_time_compare reflexive" if ok else "VIOLATION: constant_time_compare(a,a) != True",
    )


def check_constant_time_compare_unequal(a: bytes, b: bytes) -> Tuple[bool, ProofObject]:
    """constant_time_compare(a, b) must return False when a != b.

    Standard: NIST FIPS 186-5 — authentication correctness
    falsifies_if: constant_time_compare(a, b) returns True when a != b.
    """
    if a == b:
        ok = True
        premises = ["a==b, cannot test inequality"]
    else:
        result = constant_time_compare(a, b)
        ok = result is False
        premises = [f"a_len={len(a)}", f"b_len={len(b)}", f"result={result}"]
    return ok, ProofObject(
        rule="ConstantTimeCompareUnequal",
        premises=premises,
        conclusion="PASS: unequal values correctly rejected" if ok else "VIOLATION: constant_time_compare accepted unequal values",
    )


def check_validate_psk_rejects_zero_key(zero_psk: bytes) -> Tuple[bool, ProofObject]:
    """validate_psk must raise ValueError for all-zero PSK.

    Standard: RFC 8446 §4.2.11 — PSK non-zero requirement
    falsifies_if: validate_psk(zero_psk) does not raise ValueError.
    """
    raised = False
    try:
        validate_psk(zero_psk)
    except ValueError:
        raised = True
    ok = raised
    premises = [f"psk_len={len(zero_psk)}", f"all_zeros={zero_psk == bytes(32)}"]
    return ok, ProofObject(
        rule="ValidatePSKRejectsZeroKey",
        premises=premises,
        conclusion="PASS: zero PSK rejected" if ok else "VIOLATION: zero PSK accepted",
    )


def check_generate_psk_nonzero() -> Tuple[bool, ProofObject]:
    """Generated PSK must be non-zero.

    Standard: NIST SP 800-131A — random key generation
    falsifies_if: generate_psk() returns all-zero bytes.
    """
    psk = generate_psk()
    ok = psk != bytes(32) and len(psk) == 32
    premises = [f"psk_len={len(psk)}", f"is_nonzero={psk != bytes(32)}"]
    return ok, ProofObject(
        rule="GeneratePSKNonZero",
        premises=premises,
        conclusion="PASS: PSK is non-zero 32 bytes" if ok else "VIOLATION: generated PSK is zero or wrong length",
    )


def check_crypto_error_no_secret_in_msg() -> Tuple[bool, ProofObject]:
    """CryptoError message must not contain raw secret material.

    Standard: NIST SP 800-131A §3.1 — no plaintext secrets in logs
    falsifies_if: CryptoError leaks secret content in str(exception).
    """
    try:
        validate_psk(bytes(32))
        ok = False
        msg = ""
    except (ValueError, CryptoError) as e:
        msg = str(e)
        # Must not contain actual PSK bytes
        ok = b"\x00" * 5 not in msg.encode()
    premises = [f"error_message_safe={ok}"]
    return ok, ProofObject(
        rule="CryptoErrorNoSecretInMsg",
        premises=premises,
        conclusion="PASS: error message safe" if ok else "VIOLATION: secret content in error message",
    )


def check_validate_psk_accepts_valid() -> Tuple[bool, ProofObject]:
    """validate_psk must accept a valid non-zero 32-byte PSK.

    Standard: FIPS 140-3 — key acceptance requirement
    falsifies_if: validate_psk raises for a valid PSK.
    """
    import os
    psk = os.urandom(32)
    # Ensure non-zero
    psk = bytes([0x01] + list(psk[1:]))
    try:
        result = validate_psk(psk)
        ok = result == psk
    except Exception:
        ok = False
    premises = [f"psk_is_valid_nonzero=True"]
    return ok, ProofObject(
        rule="ValidatePSKAcceptsValid",
        premises=premises,
        conclusion="PASS: valid PSK accepted" if ok else "VIOLATION: valid PSK rejected",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    a = b"hello_world_1234"
    b_val = b"different_bytes_"
    zero_psk = bytes(32)
    results = {}
    for fn, args in [
        (check_constant_time_compare_equal, (a, a)),
        (check_constant_time_compare_unequal, (a, b_val)),
        (check_validate_psk_rejects_zero_key, (zero_psk,)),
        (check_generate_psk_nonzero, ()),
        (check_crypto_error_no_secret_in_msg, ()),
        (check_validate_psk_accepts_valid, ()),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
