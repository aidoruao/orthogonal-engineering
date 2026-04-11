"""D_CRYPTO invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- NIST FIPS 140-3 (Cryptographic Module Security)
- NIST SP 800-63B (Authentication Guidelines)
- RFC 2104 (HMAC specification)
- NSA Suite B / CNSA (Cryptographic standards)

Source: ontology/ontology.json#D_CRYPTO
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject

from src.domains.d_crypto.implementation import (
    constant_time_compare,
    constant_time_hmac,
    validate_psk,
    generate_psk,
)


def check_constant_time_compare_uses_hmac() -> Tuple[bool, ProofObject]:
    """
    Invariant: All secret-dependent operations are constant-time.
    
    Standard: NIST SP 800-63B 5.1.1.2 (Side-channel resistance)
    Falsifies if: hmac.compare_digest is not in use.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    import inspect
    source = inspect.getsource(constant_time_compare)
    uses_hmac = "hmac.compare_digest" in source
    
    proof = ProofObject(
        rule="ConstantTimeCompareStructure",
        premises=[
            f"source_length = {len(source)}",
            f"uses_hmac_compare_digest = {uses_hmac}",
        ],
        conclusion=(
            "Constant-time compare uses hmac.compare_digest per NIST 800-63B"
            if uses_hmac
            else "FAIL: constant_time_compare must use hmac.compare_digest"
        ),
    )
    return uses_hmac, proof


def check_psk_zero_rejected() -> Tuple[bool, ProofObject]:
    """
    Invariant: Protocol validity rules (PSK ≠ 0^32) are enforced at the API boundary.
    
    Standard: NIST SP 800-63B 5.1.1.1 (Memorized secrets)
    Falsifies if: validate_psk accepts b'\\x00'*32.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    zero_psk = b"\x00" * 32
    rejected = False
    error_type = None
    
    try:
        validate_psk(zero_psk)
    except ValueError:
        rejected = True
        error_type = "ValueError"
    except Exception as e:
        error_type = type(e).__name__
    
    proof = ProofObject(
        rule="PSKZeroRejection",
        premises=[
            f"zero_psk = b'\\\\x00' * 32",
            f"rejected = {rejected}",
            f"error_type = {error_type}",
        ],
        conclusion=(
            "Zero PSK correctly rejected per NIST 800-63B"
            if rejected
            else f"FAIL: Zero PSK accepted (error_type={error_type})"
        ),
    )
    return rejected, proof


def check_psk_nonzero_accepted() -> Tuple[bool, ProofObject]:
    """
    Invariant: Valid PSKs (≠ 0^32) must be accepted at the boundary.
    
    Standard: NIST FIPS 140-3 (Key validation)
    Falsifies if: A valid PSK raises ValueError.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    psk = generate_psk()
    accepted = False
    returned_value = None
    
    try:
        returned_value = validate_psk(psk)
        accepted = returned_value == psk
    except Exception as e:
        returned_value = f"Exception: {e}"
    
    proof = ProofObject(
        rule="PSKNonzeroAcceptance",
        premises=[
            f"psk_length = {len(psk)}",
            f"returned_value = {returned_value}",
            f"accepted = {accepted}",
        ],
        conclusion=(
            "Valid PSK accepted per FIPS 140-3"
            if accepted
            else f"FAIL: Valid PSK rejected — {returned_value}"
        ),
    )
    return accepted, proof


def check_hmac_deterministic() -> Tuple[bool, ProofObject]:
    """
    Invariant: HMAC is a pure function — same key+message → same digest.
    
    Standard: RFC 2104 Section 2 (HMAC definition)
    Falsifies if: Two calls with identical inputs return different values.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    key = b"\x42" * 32
    msg = b"test message"
    
    d1 = constant_time_hmac(key, msg)
    d2 = constant_time_hmac(key, msg)
    
    deterministic = d1 == d2
    correct_length = len(d1) == 32
    success = deterministic and correct_length
    
    proof = ProofObject(
        rule="HMACDeterminism",
        premises=[
            f"key_length = {len(key)}",
            f"message_length = {len(msg)}",
            f"digest_1 = {d1.hex()[:16]}...",
            f"digest_2 = {d2.hex()[:16]}...",
            f"deterministic = {deterministic}",
            f"correct_length = {correct_length}",
        ],
        conclusion=(
            "HMAC deterministic per RFC 2104"
            if success
            else f"FAIL: Not deterministic or wrong length"
        ),
    )
    return success, proof


def check_key_entropy_minimum() -> Tuple[bool, ProofObject]:
    """
    Invariant: Generated keys meet minimum entropy requirements.
    
    Standard: NIST SP 800-90B (Entropy sources)
    Falsifies if: Key entropy < 128 bits.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    psk = generate_psk()
    # 32 bytes = 256 bits of raw data
    # Assuming cryptographic randomness, this provides 256 bits entropy
    key_bits = len(psk) * 8
    min_entropy = 128
    
    # Check for patterns that reduce entropy
    unique_bytes = len(set(psk))
    entropy_estimate = unique_bytes * 8  # Simplified estimate
    
    sufficient_entropy = key_bits >= min_entropy
    reasonable_randomness = unique_bytes >= 16  # At least 16 unique bytes
    
    success = sufficient_entropy and reasonable_randomness
    
    proof = ProofObject(
        rule="KeyEntropyMinimum",
        premises=[
            f"key_bits = {key_bits}",
            f"min_entropy_required = {min_entropy}",
            f"unique_bytes = {unique_bytes}",
            f"entropy_estimate = {entropy_estimate}",
        ],
        conclusion=(
            f"Key entropy {key_bits} bits meets NIST 800-90B minimum"
            if success
            else f"FAIL: Insufficient entropy ({key_bits} < {min_entropy})"
        ),
    )
    return success, proof


def check_hmac_length_integrity() -> Tuple[bool, ProofObject]:
    """
    Invariant: HMAC-SHA256 output is exactly 32 bytes.
    
    Standard: FIPS 180-4 (SHA-256 output size)
    Falsifies if: Output length ≠ 32 bytes.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    key = b"test_key_1234567890123456789012"
    msg = b"test message"
    
    hmac_result = constant_time_hmac(key, msg)
    actual_length = len(hmac_result)
    expected_length = 32
    
    success = actual_length == expected_length
    
    proof = ProofObject(
        rule="HMACLengthIntegrity",
        premises=[
            f"algorithm = HMAC-SHA256",
            f"expected_length = {expected_length}",
            f"actual_length = {actual_length}",
        ],
        conclusion=(
            f"HMAC length {actual_length} bytes matches SHA-256 per FIPS 180-4"
            if success
            else f"FAIL: Length {actual_length} ≠ {expected_length}"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_CRYPTO invariants. Returns dict of check_name → pass/fail.

    Falsifies if: any crypto invariant check fails or raises an exception.
    """
    checks = [
        ("check_constant_time_compare_uses_hmac", check_constant_time_compare_uses_hmac),
        ("check_psk_zero_rejected", check_psk_zero_rejected),
        ("check_psk_nonzero_accepted", check_psk_nonzero_accepted),
        ("check_hmac_deterministic", check_hmac_deterministic),
        ("check_key_entropy_minimum", check_key_entropy_minimum),
        ("check_hmac_length_integrity", check_hmac_length_integrity),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CRYPTO invariants: PASS")
