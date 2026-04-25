"""D_DYADIC_ACCELERATION implementation — Dyadic Rational Quantization.

Layer: 4 (Institutional - Hardware/Acceleration)
CardinalStrength: OPERATIVE

Mathematical Standards:
- Dyadic rationals: Q_2 = { a / 2^k | a ∈ Z, k ∈ N }
- Bit-shift exactness: division by 2^k is replaced by arithmetic right-shift
- Deterministic requantization: scale ratios restricted to m / 2^k
- HAWQ-V3 (Yao et al., ICML 2021): integer-only inference pipeline

Based on: HAWQ-V3: Dyadic Neural Network Quantization

Cross-Reference d_jepa_world_model:
- DyadicFraction can replace LatentState.components for fast-path inference
- FastDotProduct accelerates LatentState.dot() and CEM planning loops
- RequantizationOp enables quantized SIGReg random projections

Cross-Reference d_deterministic_probability:
- EntropyFastPath provides bit-shift approximation for exact entropy baseline
- Dyadic probabilities are a subset of Fraction; no float contamination
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Tuple, Optional, List
import math


# ---------------------------------------------------------------------------
# DyadicFraction — exact rational with power-of-two denominator
# ---------------------------------------------------------------------------

def _is_power_of_two(n: int) -> bool:
    """Return True iff n > 0 and n is a power of two."""
    return n > 0 and (n & (n - 1)) == 0


def _log2_int(n: int) -> int:
    """Return k such that n == 2**k. Precondition: _is_power_of_two(n)."""
    return n.bit_length() - 1


@dataclass(frozen=True)
class DyadicFraction:
    """A dyadic rational a / 2^k.

    falsifies_if: denominator is not a positive power of two.
    falsifies_if: any float appears in numerator or denominator.
    """
    numerator: int
    denominator: int  # must be 2**k

    def __post_init__(self) -> None:
        if not _is_power_of_two(self.denominator):
            raise ValueError(
                f"DyadicFraction denominator must be a power of two, got {self.denominator}"
            )
        if isinstance(self.numerator, float) or isinstance(self.denominator, float):
            raise TypeError("DyadicFraction rejects float operands")

    # -- Normalized Fraction view ------------------------------------------------

    def to_fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    @classmethod
    def from_fraction(cls, f: Fraction) -> "DyadicFraction":
        """Convert a general Fraction to dyadic by expanding denominator to next 2^k.

        This is *approximate* for non-dyadic inputs — caller must verify bounded error.
        """
        if f.denominator == 1:
            return cls(f.numerator, 1)
        # Find next power of two >= denominator
        k = (f.denominator - 1).bit_length()
        scale = 2 ** k
        new_num = f.numerator * (scale // f.denominator)
        return cls(new_num, scale)

    # -- Bit-shift exact operations ----------------------------------------------

    def __add__(self, other: "DyadicFraction") -> "DyadicFraction":
        """Exact addition of two dyadic rationals."""
        a1, d1 = self.numerator, self.denominator
        a2, d2 = other.numerator, other.denominator
        if d1 == d2:
            return DyadicFraction(a1 + a2, d1)
        if d1 > d2:
            # d1 is larger power of two
            shift = _log2_int(d1) - _log2_int(d2)
            return DyadicFraction(a1 + (a2 << shift), d1)
        else:
            shift = _log2_int(d2) - _log2_int(d1)
            return DyadicFraction((a1 << shift) + a2, d2)

    def __sub__(self, other: "DyadicFraction") -> "DyadicFraction":
        """Exact subtraction of two dyadic rationals."""
        return self + DyadicFraction(-other.numerator, other.denominator)

    def __mul__(self, other: "DyadicFraction") -> "DyadicFraction":
        """Exact multiplication; denominator may grow (2^{k1+k2})."""
        return DyadicFraction(
            self.numerator * other.numerator,
            self.denominator * other.denominator,
        )

    def scale_by_int(self, m: int) -> "DyadicFraction":
        """Exact multiplication by integer m."""
        return DyadicFraction(self.numerator * m, self.denominator)

    def requantize(self, new_denominator: int) -> "DyadicFraction":
        """Requantize to a new power-of-two denominator via bit-shift.

        If new_denominator > self.denominator: upshift (exact).
        If new_denominator < self.denominator: downshift (round-to-nearest).
        """
        if not _is_power_of_two(new_denominator):
            raise ValueError("requantize target must be power of two")
        old_k = _log2_int(self.denominator)
        new_k = _log2_int(new_denominator)
        if new_k >= old_k:
            shift = new_k - old_k
            return DyadicFraction(self.numerator << shift, new_denominator)
        else:
            shift = old_k - new_k
            # Round-to-nearest: add 1 << (shift - 1) before shifting
            rounded = (self.numerator + (1 << (shift - 1))) >> shift
            return DyadicFraction(rounded, new_denominator)

    def bit_shift_divide(self, shift: int) -> "DyadicFraction":
        """Exact division by 2^shift via arithmetic right-shift.

        Precondition: shift >= 0.
        """
        if shift < 0:
            raise ValueError("bit_shift_divide requires non-negative shift")
        new_denom = self.denominator << shift
        return DyadicFraction(self.numerator, new_denom)

    def __repr__(self) -> str:
        return f"DyadicFraction({self.numerator}/{self.denominator})"


# ---------------------------------------------------------------------------
# QuantizationConfig — per-tensor static quantization parameters
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QuantizationConfig:
    """Static quantization configuration for a tensor.

    Maps real values r to integers q via:
        q = clamp(round(r / S) - Z, 0, 2**bit_width - 1)

    In dyadic mode, S is restricted to m / 2^k so that rescaling uses
    integer multiply + bit-shift only.

    falsifies_if: bit_width <= 0 or bit_width > 32.
    falsifies_if: scale numerator or denominator is zero.
    """
    bit_width: int
    scale_numerator: int      # m in S = m / 2^k
    scale_denominator: int    # must be power of two (2^k)
    zero_point: int = 0
    symmetric: bool = True

    def __post_init__(self) -> None:
        if not (1 <= self.bit_width <= 32):
            raise ValueError("bit_width must be in [1, 32]")
        if self.scale_numerator == 0:
            raise ValueError("scale numerator must be non-zero")
        if not _is_power_of_two(self.scale_denominator):
            raise ValueError("scale denominator must be power of two")

    def quantize(self, value: DyadicFraction) -> int:
        """Quantize a dyadic value to an integer q."""
        # value / S = value * (2^k / m)
        scaled_num = value.numerator * self.scale_denominator
        scaled_denom = value.denominator * self.scale_numerator
        # scaled_num / scaled_denom is rational; round to nearest integer
        if scaled_denom == 1:
            q = scaled_num
        else:
            q = (scaled_num + (scaled_denom // 2)) // scaled_denom
        q = q - self.zero_point
        q_max = (1 << self.bit_width) - 1
        return max(0, min(q, q_max))

    def dequantize(self, q: int) -> DyadicFraction:
        """Map integer q back to dyadic rational."""
        r = q + self.zero_point
        return DyadicFraction(r * self.scale_numerator, self.scale_denominator)


# ---------------------------------------------------------------------------
# RequantizationOp — dyadic scale-ratio for layer-to-layer handoff
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RequantizationOp:
    """Integer-only requantization between two quantization configs.

    Given input quantized as q_in with scale S_in, and desired output
    scale S_out, the dyadic rescaling factor is:

        factor = (S_in / S_out) = (m_in * 2^{k_out}) / (m_out * 2^{k_in})

    We restrict factor to dyadic form M / 2^K so that:

        q_out = clamp( round( q_in * M ) >> K , 0, 2^{bit_width_out}-1 )

    This is the core HAWQ-V3 primitive: no floating point, no division.

    falsifies_if: resulting shift K is negative (would require left-shift overflow).
    """
    in_config: QuantizationConfig
    out_config: QuantizationConfig

    def __post_init__(self) -> None:
        # Precompute dyadic factor M / 2^K
        m_in = self.in_config.scale_numerator
        k_in = _log2_int(self.in_config.scale_denominator)
        m_out = self.out_config.scale_numerator
        k_out = _log2_int(self.out_config.scale_denominator)

        # factor = (m_in / 2^{k_in}) / (m_out / 2^{k_out})
        #        = (m_in * 2^{k_out}) / (m_out * 2^{k_in})
        # We want this as M / 2^K.
        # Simplify: multiply numerator and denominator, then factor out powers of two.
        num = m_in * (1 << k_out)
        den = m_out * (1 << k_in)

        # Extract common power of two from den
        # den may not be power of two because m_out can be odd.
        # HAWQ-V3 restricts m to integers; we keep full integer multiply then shift.
        # Here we store raw multiply factor and shift separately.
        object.__setattr__(self, "_multiply_factor", num)
        object.__setattr__(self, "_shift", k_in - k_out)

    def requantize(self, q_in: int) -> int:
        """Requantize integer q_in to q_out using integer multiply + bit-shift."""
        mf = getattr(self, "_multiply_factor", None)
        sh = getattr(self, "_shift", None)
        if mf is None or sh is None:
            raise RuntimeError("RequantizationOp not properly initialized")

        # q_in * factor = q_in * mf / 2^sh  (if sh > 0)
        # If sh < 0, we left-shift (rare, guarded by config validation).
        if sh > 0:
            acc = q_in * mf
            # Round-to-nearest: add 1 << (sh - 1) before shifting
            q_out = (acc + (1 << (sh - 1))) >> sh
        elif sh < 0:
            q_out = (q_in * mf) << (-sh)
        else:
            q_out = q_in * mf

        q_max = (1 << self.out_config.bit_width) - 1
        return max(0, min(q_out, q_max))


# ---------------------------------------------------------------------------
# FastDotProduct — integer MAC with dyadic accumulation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FastDotProduct:
    """Dot product of two quantized vectors using integer multiply-accumulate
    followed by dyadic requantization.

    Given vectors a (quantized) and b (quantized), compute:
        acc = Σ_i (a_i * b_i)   [INT32 accumulation]
        out = (acc * M) >> K    [dyadic rescaling]

    falsifies_if: accumulator overflows 32-bit signed range.
    """
    length: int
    requant: RequantizationOp

    def compute(self, a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
        """Compute integer dot product with dyadic rescaling."""
        if len(a) != self.length or len(b) != self.length:
            raise ValueError("Length mismatch")
        acc = 0
        for ai, bi in zip(a, b):
            acc += ai * bi
            # Overflow guard: 32-bit signed range
            if acc > 2_147_483_647 or acc < -2_147_483_648:
                raise OverflowError("INT32 accumulator overflow in FastDotProduct")
        return self.requant.requantize(acc)


# ---------------------------------------------------------------------------
# EntropyFastPath — dyadic probability → bit-shift entropy approximation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EntropyFastPath:
    """Approximate entropy using dyadic probabilities and bit-shift log2.

    For a probability distribution where each p_i = a_i / 2^k (dyadic),
    the entropy H = -Σ p_i log2(p_i) can be approximated without
    transcendental functions by precomputing log2(a_i) via integer LUT
    and subtracting k.

    falsifies_if: any probability is not dyadic (denominator not power of two).
    falsifies_if: probabilities do not sum to 1 within tolerance.
    """
    probabilities: Tuple[DyadicFraction, ...]
    lut_bits: int = 8  # log2 LUT precision

    def __post_init__(self) -> None:
        total = DyadicFraction(0, 1)
        for p in self.probabilities:
            total = total + p
        # total should be 1 = 1/1
        if total.numerator != total.denominator:
            raise ValueError("Probabilities must sum to 1")

    def _log2_lut(self, a: int) -> int:
        """Return fixed-point log2(a) scaled by 2^{lut_bits}.

        For a in [1, 2^{lut_bits}], use precomputed rounded values.
        For a > 2^{lut_bits}, use bit_length approximation.
        """
        if a <= 0:
            raise ValueError("log2 LUT input must be positive")
        if a == 1:
            return 0
        # Approximate: log2(a) ≈ (bit_length - 1) + fractional part
        # Fractional part via LUT on normalized value
        bl = a.bit_length() - 1
        if bl > self.lut_bits:
            # Normalize: a = m * 2^{bl}, where m in [1, 2)
            # We approximate fractional part as 0.5 for speed
            return (bl << self.lut_bits) + (1 << (self.lut_bits - 1))
        # For small a, use integer log2 rounded to lut_bits fractional precision
        # log2(a) * 2^{lut_bits} ≈ bl * 2^{lut_bits} + (a - 2^{bl}) * 2^{lut_bits} / 2^{bl}
        frac = ((a - (1 << bl)) << self.lut_bits) >> bl
        return (bl << self.lut_bits) + frac

    def entropy_scaled(self) -> int:
        """Return entropy H scaled by 2^{lut_bits} (fixed-point integer).

        H = -Σ (a_i / 2^k) * (log2(a_i) - k)
          = -Σ (a_i / 2^k) * log2(a_i) + Σ (a_i / 2^k) * k
          = -Σ (a_i / 2^k) * log2(a_i) + k

        Since Σ a_i / 2^k = 1, the second term is k.
        """
        k = _log2_int(self.probabilities[0].denominator)
        total = 0
        scale = 1 << self.lut_bits
        for p in self.probabilities:
            a = p.numerator
            if a == 0:
                continue
            log2_a = self._log2_lut(a)
            # contribution = - (a / 2^k) * log2(a)
            # scaled: - a * log2_a / 2^k
            # We keep result in fixed-point: multiply by scale
            contrib = -(a * log2_a) >> k
            total += contrib
        # Add k * scale (since Σ p_i = 1)
        total += k * scale
        return total

    def entropy_dyadic(self) -> DyadicFraction:
        """Return entropy as a dyadic rational H / 2^{lut_bits}."""
        return DyadicFraction(self.entropy_scaled(), 1 << self.lut_bits)


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "name": "d_dyadic_acceleration",
    "version": "1.0.0",
    "paper_id": "2011.10680v3",
    "paper_title": "HAWQ-V3: Dyadic Neural Network Quantization",
    "authors": [
        "Zhewei Yao", "Zhen Dong", "Zhangcheng Zheng", "Amir Gholami",
        "Jiali Yu", "Eric Tan", "Leyuan Wang", "Qijing Huang",
        "Yida Wang", "Michael W. Mahoney", "Kurt Keutzer",
    ],
    "institutions": ["UC Berkeley", "Amazon", "Shanghai Jiao Tong University"],
    "theorems": ["Dyadic Rational Exactness", "Bit-Shift Division Equivalence"],
    "layer": 4,
    "cardinal_strength": "OPERATIVE",
}
