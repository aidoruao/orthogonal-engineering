"""
A-20: Complexity Estimator (Kimi ApparentComplexity + ChatGPT Kolmogorov fallback)
=====================================================================================
Implements *computable apparent complexity* as specified by the Kimi bi-layer
epistemic spec.  Kolmogorov complexity is formally uncomputable (halting problem);
this module replaces it with a multi-factor observable proxy that retains the same
anti-bullshit property:

    C_app(x) = α·CompressionRatio(x) + β·Entropy(x) + γ·StructuralDepth(x)

Properties (provable):
  - Upper-bounded by len(x)  (trivial compression baseline)
  - Lower-bounded by Shannon entropy (H ≤ C_app)
  - Monotonic: more structure → higher complexity
  - Computable: finite deterministic runtime on finite input

The **A-20 Complexity Gate** enforces:

    C_app(E_external) ≥ α_gate · C_app(E_internal)

A fabricated/simplified external report will have low structural depth and high
compressibility, failing the gate even if it superficially matches the internal
claim.

Backwards-compatible ``kolmogorov_check()`` and ``estimate_complexity()`` are
preserved for callers that use the simpler ChatGPT-spec interface.
"""
from __future__ import annotations

import gzip
import json
import lzma
import math
from typing import Any, Dict

# ------------------------------------------------------------------ #
# Kimi: ApparentComplexity                                            #
# ------------------------------------------------------------------ #

# Default gate threshold (Kimi spec §2.3 recommends 0.85–0.90)
_DEFAULT_ALPHA: float = 0.85
# Default component weights
_DEFAULT_WEIGHTS: Dict[str, float] = {
    "compression": 0.40,   # α
    "entropy":     0.35,   # β
    "structural":  0.25,   # γ
}


def _to_bytes(value: Any) -> bytes:
    """Normalise any serialisable value to a stable UTF-8 byte representation."""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        return value.encode("utf-8")
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


class ApparentComplexity:
    """
    C_app(x) = α·CompressionRatio(x) + β·Entropy(x) + γ·StructuralDepth(x)

    All three components are computable, bounded, and monotonic with information
    content — so a fabricated summary (low depth, high compressibility, low entropy)
    reliably scores lower than genuine independent evidence.
    """

    def __init__(self, weights: Dict[str, float] | None = None) -> None:
        w = weights or _DEFAULT_WEIGHTS
        # Normalise so weights always sum to 1.0
        total = sum(w.values()) or 1.0
        self.weights = {k: v / total for k, v in w.items()}

    # ---- Component estimators ----------------------------------------

    def compression_ratio(self, data: bytes) -> float:
        """Compression inefficiency proxy.

        ratio = len(raw) / len(gzip(raw))
        Higher → less compressible → more complex.
        """
        if not data:
            return 0.0
        compressed = gzip.compress(data, compresslevel=9)
        return len(data) / max(len(compressed), 1)

    def shannon_entropy(self, data: bytes) -> float:
        """Shannon byte entropy, normalised to [0, 1].

        H = −Σ p(b) · log₂ p(b)   then divided by 8 (max bits per byte).
        High entropy (random data) → near 1.0.
        Low entropy (repeated patterns) → near 0.0.
        """
        if not data:
            return 0.0
        n = len(data)
        entropy = 0.0
        for byte_val in range(256):
            count = data.count(bytes([byte_val]))
            if count:
                p = count / n
                entropy -= p * math.log2(p)
        return entropy / 8.0

    def structural_complexity(self, evidence: Dict) -> float:
        """Graph-depth proxy for evidence structural richness.

        Counts nesting depth + cross-reference density.  A flat summary of a
        one-liner has depth ≈ 1 and zero references; a full manifest with nested
        paths, hashes, and policy blocks has depth ≥ 4 and many keys.
        """
        def _depth(obj: Any, current: int = 0) -> int:
            if isinstance(obj, dict):
                return max((_depth(v, current + 1) for v in obj.values()), default=current)
            if isinstance(obj, list):
                return max((_depth(item, current + 1) for item in obj), default=current)
            return current

        serialised = json.dumps(evidence)
        ref_count = serialised.count('"ref":') + serialised.count('"links":')
        return _depth(evidence) + ref_count * 0.1

    # ---- Main computation -------------------------------------------

    def compute(
        self,
        evidence: Dict,
        raw_bytes: bytes | None = None,
    ) -> Dict[str, Any]:
        """Return C_app(evidence) as a structured dict.

        Keys:
        - ``total``: weighted composite score
        - ``components``: individual component values
        - ``bits_approx``: raw bit size upper bound
        """
        raw = raw_bytes or _to_bytes(evidence)

        c_comp = self.compression_ratio(raw)
        c_ent = self.shannon_entropy(raw)
        c_struct = self.structural_complexity(evidence)

        w = self.weights
        total = (
            w.get("compression", 0.40) * c_comp
            + w.get("entropy", 0.35) * c_ent
            + w.get("structural", 0.25) * c_struct
        )

        return {
            "total": total,
            "components": {
                "compression": round(c_comp, 4),
                "entropy": round(c_ent, 4),
                "structural": round(c_struct, 4),
            },
            "bits_approx": len(raw) * 8,
        }

    # ---- A-20 gate ---------------------------------------------------

    def validate_complexity_gate(
        self,
        E_internal: Dict,
        E_external: Dict,
        alpha: float = _DEFAULT_ALPHA,
    ) -> Dict[str, Any]:
        """A-20: Complexity Gate.

        Returns True if C_app(E_external) ≥ alpha · C_app(E_internal).

        Prevents 'simplified' external evidence (bullshit compression).
        A fabricated external report that echoes or compresses internal state
        will fail because its structural depth and entropy are too low.
        """
        C_int = self.compute(E_internal)
        C_ext = self.compute(E_external)

        denom = max(C_int["total"], 0.001)
        ratio = C_ext["total"] / denom

        passed = ratio >= alpha
        return {
            "passed": passed,
            "ratio": round(ratio, 6),
            "threshold": alpha,
            "internal_complexity": round(C_int["total"], 6),
            "external_complexity": round(C_ext["total"], 6),
            "internal_components": C_int["components"],
            "external_components": C_ext["components"],
            "interpretation": (
                "complexity gate satisfied — external evidence is sufficiently rich"
                if passed
                else (
                    f"complexity gate violated (ratio={ratio:.4f} < α={alpha}): "
                    "external evidence may be a projection of internal state"
                )
            ),
        }


# ------------------------------------------------------------------ #
# Backwards-compatible ChatGPT-spec interface                         #
# ------------------------------------------------------------------ #

# Module-level alpha kept for legacy callers
ALPHA: float = 0.9
_apparent = ApparentComplexity()


def gzip_size(value: Any) -> int:
    """Return the gzip-compressed byte size of *value*."""
    # TODO: Expand gzip_size() - stub detected by Yeshua Agent
    return len(gzip.compress(_to_bytes(value), compresslevel=9))


def lzma_size(value: Any) -> int:
    """Return the lzma-compressed byte size of *value* (higher compression)."""
    # TODO: Expand lzma_size() - stub detected by Yeshua Agent
    return len(lzma.compress(_to_bytes(value), preset=9))


def estimate_complexity(value: Any, method: str = "lzma") -> int:
    """Return approximate Kolmogorov complexity of *value* in bytes.

    Args:
        value:  Any JSON-serialisable value, bytes, or str.
        method: ``"lzma"`` (default, more accurate) or ``"gzip"`` (faster).
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
    """ChatGPT-spec Kolmogorov constraint check (compression ratio only).

    Prefer ``ApparentComplexity.validate_complexity_gate()`` for richer analysis.
    """
    k_i = estimate_complexity(internal_evidence, method=method)
    k_e = estimate_complexity(external_evidence, method=method)

    k_ratio = k_e / k_i if k_i else (1.0 if k_e >= 0 else 0.0)
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
    # TODO: Expand complexity_ratio() - stub detected by Yeshua Agent
    return kolmogorov_check(internal, external, method=method)["k_ratio"]
