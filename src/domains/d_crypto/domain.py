"""D_CRYPTO domain definition — Cryptography

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: NIST FIPS 140-3, RFC 8446 (TLS 1.3), various cryptographic standards
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CRYPTO"
DOMAIN_NAME = "Cryptography"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    "post-quantum",
    "classical",
    "timing-side-channel",
    "key-management",
    "protocol-correctness"
]

INVARIANTS = [
    "All secret-dependent operations are constant-time.",
    "Protocol validity rules (e.g., PSK ≠ 0^32) are enforced at the API boundary.",
    "No secret material is stored in plain-text logs or error messages."
]

FALSIFICATION_TESTS = ["F_CRYPTO_001"]
ONTOLOGICAL_ISSUES = ["OI_CRYPTO_001"]
