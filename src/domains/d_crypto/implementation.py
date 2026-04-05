"""
D_CRYPTO — Cryptography domain implementation.

Invariants (from ontology/ontology.json#D_CRYPTO):
  1. All secret-dependent operations are constant-time.
  2. Protocol validity rules (e.g., PSK ≠ 0^32) are enforced at the API boundary.
  3. No secret material is stored in plain-text logs or error messages.

Biblical inspiration: "Be wise as serpents and innocent as doves." (Matthew 10:16)
Constant-time operations are the serpent-wisdom of cryptography — subtle, precise,
leaving no timing oracle for an adversary to exploit.

Falsification IDs: F_CRYPTO_001, F_CRYPTO_002, F_CRYPTO_003
"""

import hashlib
import hmac
import os
import secrets


# ---------------------------------------------------------------------------
# Constant-time comparison (F_CRYPTO_001)
# ---------------------------------------------------------------------------

def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Compare two byte strings in constant time.

    Invariant: Execution time is independent of the content of `a` and `b`.
    Falsification: If timing differs based on byte values, F_CRYPTO_001 is violated.
    Implementation: Delegates to hmac.compare_digest which is guaranteed constant-time
    by CPython's implementation using a secret-independent bitwise XOR accumulator.
    """
    if not isinstance(a, (bytes, bytearray)) or not isinstance(b, (bytes, bytearray)):
        raise TypeError("constant_time_compare requires bytes arguments")
    return hmac.compare_digest(a, b)


def constant_time_hmac(key: bytes, message: bytes) -> bytes:
    """
    Compute HMAC-SHA256 of message under key.

    The HMAC construction is inherently constant-time over the secret key
    because it processes key bytes uniformly through the inner hash.

    Invariant: All secret-dependent operations are constant-time.
    Falsification: If any branch in this function depends on key content, F_CRYPTO_001 fails.
    """
    if not isinstance(key, (bytes, bytearray)):
        raise TypeError("key must be bytes")
    if not isinstance(message, (bytes, bytearray)):
        raise TypeError("message must be bytes")
    return hmac.new(key, message, hashlib.sha256).digest()


# ---------------------------------------------------------------------------
# PSK validity enforcement (F_CRYPTO_002)
# ---------------------------------------------------------------------------

_ZERO_PSK = b"\x00" * 32


def validate_psk(psk: bytes) -> bytes:
    """
    Enforce PSK ≠ 0^32 at the API boundary.

    Invariant: Protocol validity rules are enforced at the API boundary.
    Falsification: If a zero PSK is accepted without error, F_CRYPTO_002 is violated.

    Uses constant_time_compare to avoid leaking information about the PSK value
    while still enforcing the non-zero requirement.
    """
    if len(psk) != 32:
        raise ValueError(f"PSK must be exactly 32 bytes, got {len(psk)}")
    if constant_time_compare(psk, _ZERO_PSK):
        raise ValueError("PSK must not be the all-zero key (0^32)")
    return psk


def generate_psk() -> bytes:
    """Generate a cryptographically random 32-byte PSK (never all-zero by design).
    Raises RuntimeError if RNG fails to produce a non-zero key in 1000 attempts."""
    for _ in range(1000):
        key = secrets.token_bytes(32)
        if not constant_time_compare(key, _ZERO_PSK):
            return key
    raise RuntimeError(
        "generate_psk: RNG produced 1000 consecutive all-zero keys — "
        "system random source appears compromised."
    )


# ---------------------------------------------------------------------------
# Secret-safe error messages (F_CRYPTO_003)
# ---------------------------------------------------------------------------

class CryptoError(Exception):
    """
    Invariant: No secret material appears in error messages or logs.
    Falsification: If the exception message contains key material, F_CRYPTO_003 fails.
    """

    def __init__(self, message: str, *, secret_involved: bool = False):
        if secret_involved:
            import re
            # Redact any hex sequences (8+ hex chars) that might be key material
            message = re.sub(r"[0-9A-Fa-f]{8,}", "<redacted>", message)
            # Redact base64-like sequences (12+ chars from base64 alphabet)
            message = re.sub(r"[A-Za-z0-9+/]{12,}={0,2}", "<redacted>", message)
        super().__init__(message)


# ---------------------------------------------------------------------------
# Domain depth score (used by depth_measurement.py)
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "id": "D_CRYPTO",
    "name": "Cryptography",
    "invariants": [
        "All secret-dependent operations are constant-time.",
        "Protocol validity rules (e.g., PSK ≠ 0^32) are enforced at the API boundary.",
        "No secret material is stored in plain-text logs or error messages.",
    ],
    "falsification_tests": ["F_CRYPTO_001", "F_CRYPTO_002", "F_CRYPTO_003"],
    "implementation_functions": [
        "constant_time_compare",
        "constant_time_hmac",
        "validate_psk",
        "generate_psk",
    ],
    "uses_hmac_compare_digest": True,
}
