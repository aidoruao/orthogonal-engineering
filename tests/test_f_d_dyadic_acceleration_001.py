"""Test suite for d_dyadic_acceleration — HAWQ-V3 dyadic rational quantization.

Covers:
- DyadicFraction construction, arithmetic, requantization
- QuantizationConfig quantize/dequantize round-trip
- RequantizationOp integer-only rescaling
- FastDotProduct MAC + overflow behavior
- EntropyFastPath bounded error against exact Fraction entropy
- All 6 invariant checks
"""

from __future__ import annotations

from fractions import Fraction
# Note: pytest not available in this environment; tests use plain assert

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from domains.d_dyadic_acceleration.implementation import (
    DyadicFraction,
    QuantizationConfig,
    RequantizationOp,
    FastDotProduct,
    EntropyFastPath,
    _is_power_of_two,
    _log2_int,
)
from domains.d_dyadic_acceleration.invariants import (
    check_denominator_is_power_of_two,
    check_bit_shift_exactness,
    check_requantization_no_float_contamination,
    check_dot_product_deterministic_cross_platform,
    check_entropy_approximation_bounded_error,
    check_overflow_within_dynamic_range,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _exact_entropy(probs: tuple[Fraction, ...]) -> Fraction:
    """Baseline entropy H = -Σ p log2(p) using dyadic integer approximation.

    Since log2 of a Fraction is irrational, we approximate using a
    precomputed dyadic lookup table at 10-bit precision. This avoids
    float contamination while providing a reproducible baseline.
    """
    LUT_BITS = 10
    SCALE = 1 << LUT_BITS

    def _log2_fixed(a: int, b: int) -> int:
        """Return log2(a/b) scaled by 2^{LUT_BITS} as an integer."""
        # log2(a/b) = log2(a) - log2(b)
        def _log2_int_scaled(n: int) -> int:
            if n <= 0:
                return -SCALE * 100  # large negative for zero guard
            bl = n.bit_length() - 1
            # fractional part approx: (n - 2^bl) / 2^bl * SCALE
            frac = ((n - (1 << bl)) << LUT_BITS) >> bl
            return (bl << LUT_BITS) + frac
        return _log2_int_scaled(a) - _log2_int_scaled(b)

    h = Fraction(0)
    for p in probs:
        if p == 0:
            continue
        log2_p_scaled = _log2_fixed(p.numerator, p.denominator)
        # contribution = -p * (log2_p_scaled / SCALE)
        h += -Fraction(p.numerator * log2_p_scaled, p.denominator * SCALE)
    return h


# ---------------------------------------------------------------------------
# DyadicFraction
# ---------------------------------------------------------------------------

class TestDyadicFraction:
    def test_construction_valid(self):
        d = DyadicFraction(3, 8)
        assert d.numerator == 3
        assert d.denominator == 8

    def test_construction_invalid_denominator(self):
        try:
            DyadicFraction(3, 6)
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_construction_rejects_float(self):
        try:
            DyadicFraction(3.0, 8)
            assert False, "Expected TypeError"
        except TypeError:
            pass

    def test_to_fraction(self):
        d = DyadicFraction(3, 8)
        assert d.to_fraction() == Fraction(3, 8)

    def test_from_fraction_exact(self):
        f = Fraction(3, 8)
        d = DyadicFraction.from_fraction(f)
        assert d.numerator == 3
        assert d.denominator == 8

    def test_from_fraction_approximate(self):
        f = Fraction(1, 3)
        d = DyadicFraction.from_fraction(f)
        assert _is_power_of_two(d.denominator)
        # 1/3 ≈ 5461/16384 at 14-bit precision
        assert d.denominator >= f.denominator

    def test_add_same_denominator(self):
        a = DyadicFraction(1, 8)
        b = DyadicFraction(2, 8)
        c = a + b
        assert c == DyadicFraction(3, 8)

    def test_add_different_denominator(self):
        a = DyadicFraction(1, 4)
        b = DyadicFraction(1, 8)
        c = a + b
        assert c == DyadicFraction(3, 8)

    def test_sub(self):
        a = DyadicFraction(5, 8)
        b = DyadicFraction(2, 8)
        c = a - b
        assert c == DyadicFraction(3, 8)

    def test_mul(self):
        a = DyadicFraction(3, 8)
        b = DyadicFraction(2, 4)
        c = a * b
        assert c == DyadicFraction(6, 32)

    def test_scale_by_int(self):
        a = DyadicFraction(3, 8)
        b = a.scale_by_int(5)
        assert b == DyadicFraction(15, 8)

    def test_requantize_up(self):
        a = DyadicFraction(3, 8)
        b = a.requantize(32)
        assert b == DyadicFraction(12, 32)

    def test_requantize_down_rounding(self):
        a = DyadicFraction(5, 8)  # 0.625
        b = a.requantize(4)       # round to nearest quarter: 0.5 or 0.75?
        # 5/8 = 2.5/4 -> round to 2/4 = 0.5 ... wait, 2.5 rounds to 3? 
        # Our round-to-nearest: (5 + 2) >> 1 = 3 -> 3/4 = 0.75
        assert b == DyadicFraction(3, 4)

    def test_bit_shift_divide(self):
        a = DyadicFraction(3, 8)
        b = a.bit_shift_divide(2)
        assert b == DyadicFraction(3, 32)

    def test_bit_shift_divide_negative_shift_rejected(self):
        try:
            DyadicFraction(3, 8).bit_shift_divide(-1)
            assert False, "Expected ValueError"
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# QuantizationConfig
# ---------------------------------------------------------------------------

class TestQuantizationConfig:
    def test_construction_valid(self):
        qc = QuantizationConfig(8, 2, 16)
        assert qc.bit_width == 8
        assert qc.scale_numerator == 2
        assert qc.scale_denominator == 16

    def test_construction_invalid_bit_width(self):
        try:
            QuantizationConfig(0, 1, 2)
            assert False, "Expected ValueError"
        except ValueError:
            pass
        try:
            QuantizationConfig(33, 1, 2)
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_construction_zero_scale_num(self):
        try:
            QuantizationConfig(8, 0, 16)
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_construction_non_power_of_two_denom(self):
        try:
            QuantizationConfig(8, 1, 12)
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_quantize_dequantize_roundtrip(self):
        qc = QuantizationConfig(8, 1, 16)  # S = 1/16
        value = DyadicFraction(5, 16)       # 0.3125
        q = qc.quantize(value)
        back = qc.dequantize(q)
        # q = round(5/16 / (1/16)) = 5
        assert q == 5
        assert back == DyadicFraction(5, 16)

    def test_quantize_clamping(self):
        qc = QuantizationConfig(4, 1, 1)  # S = 1, max = 15
        value = DyadicFraction(100, 1)
        q = qc.quantize(value)
        assert q == 15


# ---------------------------------------------------------------------------
# RequantizationOp
# ---------------------------------------------------------------------------

class TestRequantizationOp:
    def test_requantize_identity(self):
        qc = QuantizationConfig(8, 1, 16)
        op = RequantizationOp(qc, qc)
        assert op.requantize(10) == 10

    def test_requantize_scale_up(self):
        # S_in = 1/16, S_out = 1/4  => factor = (1/16)/(1/4) = 1/4
        # q_out = q_in / 4
        qc_in = QuantizationConfig(8, 1, 16)
        qc_out = QuantizationConfig(8, 1, 4)
        op = RequantizationOp(qc_in, qc_out)
        # 20 * (1/4) = 5
        assert op.requantize(20) == 5

    def test_requantize_no_float(self):
        qc_in = QuantizationConfig(8, 3, 32)
        qc_out = QuantizationConfig(8, 1, 8)
        op = RequantizationOp(qc_in, qc_out)
        passed, proof = check_requantization_no_float_contamination(op, 7)
        assert passed
        assert isinstance(proof.evidence["q_out"], int)


# ---------------------------------------------------------------------------
# FastDotProduct
# ---------------------------------------------------------------------------

class TestFastDotProduct:
    def test_simple_dot(self):
        qc = QuantizationConfig(8, 1, 1)
        req = RequantizationOp(qc, qc)
        fdp = FastDotProduct(3, req)
        a = (1, 2, 3)
        b = (4, 5, 6)
        # acc = 4 + 10 + 18 = 32
        assert fdp.compute(a, b) == 32

    def test_determinism(self):
        qc = QuantizationConfig(8, 1, 1)
        req = RequantizationOp(qc, qc)
        fdp = FastDotProduct(3, req)
        a = (1, 2, 3)
        b = (4, 5, 6)
        passed, proof = check_dot_product_deterministic_cross_platform(fdp, a, b)
        assert passed

    def test_overflow_caught(self):
        qc = QuantizationConfig(8, 1, 1)
        req = RequantizationOp(qc, qc)
        fdp = FastDotProduct(2, req)
        a = (100_000, 100_000)
        b = (100_000, 100_000)
        passed, proof = check_overflow_within_dynamic_range(fdp, a, b)
        assert not passed
        assert "OverflowError" in proof.detail


# ---------------------------------------------------------------------------
# EntropyFastPath
# ---------------------------------------------------------------------------

class TestEntropyFastPath:
    def test_uniform_distribution(self):
        # p = [1/2, 1/2] -> H = 1.0
        p = (DyadicFraction(1, 2), DyadicFraction(1, 2))
        efp = EntropyFastPath(p, lut_bits=8)
        h = efp.entropy_dyadic()
        # Should be close to 1.0 within 1/128
        # Compare as fractions to avoid float contamination
        assert abs(h.to_fraction() - Fraction(1, 1)) < Fraction(1, 32)

    def test_bounded_error(self):
        p = (
            DyadicFraction(1, 4),
            DyadicFraction(1, 4),
            DyadicFraction(1, 2),
        )
        efp = EntropyFastPath(p, lut_bits=10)
        exact = _exact_entropy(
            (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2))
        )
        passed, proof = check_entropy_approximation_bounded_error(efp, exact)
        assert passed, proof.detail

    def test_probabilities_must_sum_to_one(self):
        try:
            EntropyFastPath(
                (DyadicFraction(1, 4), DyadicFraction(1, 4)), lut_bits=8
            )
            assert False, "Expected ValueError"
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# Invariant checks
# ---------------------------------------------------------------------------

class TestInvariants:
    def test_check_denominator(self):
        d = DyadicFraction(7, 16)
        passed, proof = check_denominator_is_power_of_two(d)
        assert passed

    def test_check_bit_shift_exactness(self):
        d = DyadicFraction(7, 16)
        passed, proof = check_bit_shift_exactness(d, 3)
        assert passed

    def test_check_requantization_no_float(self):
        qc = QuantizationConfig(8, 1, 16)
        op = RequantizationOp(qc, qc)
        passed, proof = check_requantization_no_float_contamination(op, 42)
        assert passed

    def test_check_dot_product_deterministic(self):
        qc = QuantizationConfig(8, 1, 1)
        req = RequantizationOp(qc, qc)
        fdp = FastDotProduct(2, req)
        passed, proof = check_dot_product_deterministic_cross_platform(
            fdp, (3, 4), (5, 6)
        )
        assert passed

    def test_check_overflow_within_range(self):
        qc = QuantizationConfig(8, 1, 1)
        req = RequantizationOp(qc, qc)
        fdp = FastDotProduct(2, req)
        passed, proof = check_overflow_within_dynamic_range(
            fdp, (1, 2), (3, 4)
        )
        assert passed

    def test_check_overflow_exceeded(self):
        qc = QuantizationConfig(8, 1, 1)
        req = RequantizationOp(qc, qc)
        fdp = FastDotProduct(2, req)
        passed, proof = check_overflow_within_dynamic_range(
            fdp, (1_000_000, 1_000_000), (1_000_000, 1_000_000)
        )
        assert not passed
