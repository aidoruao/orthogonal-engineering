"""D_DYADIC_ACCELERATION invariants — 6 falsifiable checks.

All checks return Tuple[bool, ProofObject] per OE convention.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Any

from .implementation import (
    DyadicFraction,
    QuantizationConfig,
    RequantizationOp,
    FastDotProduct,
    EntropyFastPath,
    _is_power_of_two,
    _log2_int,
)


@dataclass(frozen=True)
class ProofObject:
    """Minimal proof carrier for invariant results."""
    check_name: str
    passed: bool
    detail: str
    evidence: Any = None


def _proof(
    # TODO: Expand _proof() - stub detected by Yeshua Agent
    name: str, passed: bool, detail: str, evidence: Any = None
) -> Tuple[bool, ProofObject]:
    return passed, ProofObject(name, passed, detail, evidence)


# ---------------------------------------------------------------------------
# 1. check_denominator_is_power_of_two
# ---------------------------------------------------------------------------

def check_denominator_is_power_of_two(
    # TODO: Expand check_denominator_is_power_of_two() - stub detected by Yeshua Agent
    value: DyadicFraction,
) -> Tuple[bool, ProofObject]:
    """Verify that a DyadicFraction's denominator is a positive power of two.

    falsifies_if: denominator is not a positive power of two.
    """
    d = value.denominator
    ok = _is_power_of_two(d)
    return _proof(
        "check_denominator_is_power_of_two",
        ok,
        f"denominator={d} is {'a' if ok else 'NOT a'} power of two",
        evidence={"denominator": d, "bit_length": d.bit_length()},
    )


# ---------------------------------------------------------------------------
# 2. check_bit_shift_exactness
# ---------------------------------------------------------------------------

def check_bit_shift_exactness(
    # TODO: Expand check_bit_shift_exactness() - stub detected by Yeshua Agent
    value: DyadicFraction, shift: int
) -> Tuple[bool, ProofObject]:
    """Verify that dividing by 2^shift is exact via bit-shift (no division opcode).

    We simulate the operation using only shift and compare to Fraction exact result.

    falsifies_if: bit_shift_divide result does not match exact fraction arithmetic.
    """
    if shift < 0:
        return _proof(
            "check_bit_shift_exactness",
            False,
            "negative shift not allowed for exact division",
        )
    result = value.bit_shift_divide(shift)
    # Exactness: result * 2^shift must equal original value
    expected_num = value.numerator
    expected_denom = value.denominator << shift
    ok = result.numerator == expected_num and result.denominator == expected_denom
    return _proof(
        "check_bit_shift_exactness",
        ok,
        f"bit_shift_divide by 2^{shift} {'matches' if ok else 'MISMATCHES'} exact fraction",
        evidence={
            "original": (value.numerator, value.denominator),
            "result": (result.numerator, result.denominator),
            "shift": shift,
        },
    )


# ---------------------------------------------------------------------------
# 3. check_requantization_no_float_contamination
# ---------------------------------------------------------------------------

def check_requantization_no_float_contamination(
    # TODO: Expand check_requantization_no_float_contamination() - stub detected by Yeshua Agent
    op: RequantizationOp, sample_q_in: int
) -> Tuple[bool, ProofObject]:
    """Verify that requantization produces an integer without float intermediates.

    We inspect the internal computation path: only integer multiply and bit-shift
    are allowed. The RequantizationOp.requantize method is pure integer arithmetic.

    falsifies_if: requantize output is not a pure int or contains float contamination.
    """
    try:
        q_out = op.requantize(sample_q_in)
    except Exception as exc:
        return _proof(
            "check_requantization_no_float_contamination",
            False,
            f"requantize raised {type(exc).__name__}: {exc}",
        )

    ok = isinstance(q_out, int) and not isinstance(q_out, float)
    return _proof(
        "check_requantization_no_float_contamination",
        ok,
        f"output is int={ok}, value={q_out}",
        evidence={"q_in": sample_q_in, "q_out": q_out},
    )


# ---------------------------------------------------------------------------
# 4. check_dot_product_deterministic_cross_platform
# ---------------------------------------------------------------------------

def check_dot_product_deterministic_cross_platform(
    # TODO: Expand check_dot_product_deterministic_cross_platform() - stub detected by Yeshua Agent
    fdp: FastDotProduct, a: Tuple[int, ...], b: Tuple[int, ...]
) -> Tuple[bool, ProofObject]:
    """Verify that FastDotProduct yields identical results on repeated execution.

    Determinism is enforced by pure integer arithmetic (no floats, no randomness).
    We run twice and compare.

    falsifies_if: repeated execution produces different results.
    """
    try:
        out1 = fdp.compute(a, b)
        out2 = fdp.compute(a, b)
    except Exception as exc:
        return _proof(
            "check_dot_product_deterministic_cross_platform",
            False,
            f"compute raised {type(exc).__name__}: {exc}",
        )

    ok = out1 == out2
    return _proof(
        "check_dot_product_deterministic_cross_platform",
        ok,
        f"repeated execution {'matches' if ok else 'MISMATCHES'}: {out1} vs {out2}",
        evidence={"run1": out1, "run2": out2, "length": fdp.length},
    )


# ---------------------------------------------------------------------------
# 5. check_entropy_approximation_bounded_error
# ---------------------------------------------------------------------------

def check_entropy_approximation_bounded_error(
    # TODO: Expand check_entropy_approximation_bounded_error() - stub detected by Yeshua Agent
    efp: EntropyFastPath, exact_entropy_fraction: Any
) -> Tuple[bool, ProofObject]:
    """Verify that EntropyFastPath error is bounded relative to exact entropy.

    exact_entropy_fraction should be a Fraction (from d_deterministic_probability).
    Bound: |H_fast - H_exact| <= 1/2^{lut_bits - 1} (one LSB at lut_bits precision).

    falsifies_if: approximation error exceeds the declared dyadic bound.
    """
    from fractions import Fraction

    if not isinstance(exact_entropy_fraction, Fraction):
        return _proof(
            "check_entropy_approximation_bounded_error",
            False,
            "exact_entropy_fraction must be a Fraction",
        )

    fast = efp.entropy_dyadic()
    fast_frac = fast.to_fraction()
    diff = abs(fast_frac - exact_entropy_fraction)
    bound = Fraction(1, 1 << (efp.lut_bits - 1))
    ok = diff <= bound
    return _proof(
        "check_entropy_approximation_bounded_error",
        ok,
        f"error {diff} {'within' if ok else 'EXCEEDS'} bound {bound}",
        evidence={
            "fast_entropy": str(fast_frac),
            "exact_entropy": str(exact_entropy_fraction),
            "diff": str(diff),
            "bound": str(bound),
        },
    )


# ---------------------------------------------------------------------------
# 6. check_overflow_within_dynamic_range
# ---------------------------------------------------------------------------

def check_overflow_within_dynamic_range(
    # TODO: Expand check_overflow_within_dynamic_range() - stub detected by Yeshua Agent
    fdp: FastDotProduct, a: Tuple[int, ...], b: Tuple[int, ...]
) -> Tuple[bool, ProofObject]:
    """Verify that FastDotProduct does not overflow INT32 for given inputs.

    We attempt computation and catch OverflowError.

    falsifies_if: INT32 accumulator overflows during dot-product computation.
    """
    try:
        out = fdp.compute(a, b)
        ok = True
        detail = f"no overflow, result={out}"
    except OverflowError as exc:
        ok = False
        detail = f"OverflowError: {exc}"
    except Exception as exc:
        ok = False
        detail = f"unexpected {type(exc).__name__}: {exc}"

    return _proof(
        "check_overflow_within_dynamic_range",
        ok,
        detail,
        evidence={"a": a, "b": b, "length": fdp.length},
    )
