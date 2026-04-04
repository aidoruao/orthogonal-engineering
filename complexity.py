"""
A-20: Complexity Estimator
===========================
Approximates Kolmogorov complexity via compression size (gzip / lzma).

The Kolmogorov Constraint (from the bi-layer epistemic spec, §1.3):

    K(E_external) ≥ K(E_internal)

Interpretation: external evidence must not be *simpler* (more compressible)
than the internal claims it is supposed to independently verify.  If external
evidence compresses more tightly than internal evidence, it is likely either
redundant, fabricated, or a projection of internal state — none of which
constitute genuine external verification.

Both gzip and lzma are provided.  lzma is preferred for its superior
compression ratio, but gzip is available as a fast fallback.

All values are in bytes.  The complexity ratio is:

    K_ratio = compressed(E_e) / compressed(E_i)

A K_ratio below ALPHA (default 0.9) triggers a Kolmogorov violation warning.
"""
from __future__ import annotations

import gzip
import lzma
import json
from typing import Any, Dict, Union

# Minimum fraction: external compressed size / internal compressed size
# Below this threshold → violation
ALPHA: float = 0.9


def _to_bytes(value: Any) -> bytes:
    """Normalise any serialisable value to a stable byte representation."""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        return value.encode("utf-8")
    # JSON-serialise with sorted keys for determinism
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def gzip_size(value: Any) -> int:
    """Return the gzip-compressed byte size of *value*."""
    raw = _to_bytes(value)
    return len(gzip.compress(raw, compresslevel=9))


def lzma_size(value: Any) -> int:
    """Return the lzma-compressed byte size of *value* (higher compression)."""
    raw = _to_bytes(value)
    return len(lzma.compress(raw, preset=9))


def estimate_complexity(value: Any, method: str = "lzma") -> int:
    """Return approximate Kolmogorov complexity of *value* in bytes.

    Args:
        value:  Any JSON-serialisable value, bytes, or str.
        method: ``"lzma"`` (default, more accurate) or ``"gzip"`` (faster).

    Returns:
        Compressed size in bytes as complexity proxy.
    """
    if method == "gzip":
        return gzip_size(value)
    return lzma_size(value)


def kolmogorov_check(
    internal_evidence: Any,
    external_evidence: Any,
    alpha: float = ALPHA,
    method: str = "lzma",
) -> Dict[str, Any]:
    """Evaluate the Kolmogorov Constraint between internal and external evidence.

    Returns a report with fields:
    - ``k_internal``: compressed size of internal evidence
    - ``k_external``: compressed size of external evidence
    - ``k_ratio``: k_external / k_internal
    - ``alpha``: threshold used
    - ``satisfied``: True if k_ratio ≥ alpha (constraint holds)
    - ``violation``: True if constraint is violated
    - ``method``: compression method used
    """
    k_i = estimate_complexity(internal_evidence, method=method)
    k_e = estimate_complexity(external_evidence, method=method)

    # Avoid division by zero
    if k_i == 0:
        k_ratio = 1.0 if k_e >= 0 else 0.0
    else:
        k_ratio = k_e / k_i

    satisfied = k_ratio >= alpha
    return {
        "k_internal": k_i,
        "k_external": k_e,
        "k_ratio": round(k_ratio, 6),
        "alpha": alpha,
        "satisfied": satisfied,
        "violation": not satisfied,
        "method": method,
        "interpretation": (
            "external evidence is sufficiently complex (constraint satisfied)"
            if satisfied
            else (
                f"external evidence too simple (K_ratio={k_ratio:.4f} < α={alpha}): "
                "may be redundant or internally derived"
            )
        ),
    }


def complexity_ratio(internal: Any, external: Any, method: str = "lzma") -> float:
    """Convenience function: return k_external / k_internal directly."""
    result = kolmogorov_check(internal, external, method=method)
    return result["k_ratio"]
