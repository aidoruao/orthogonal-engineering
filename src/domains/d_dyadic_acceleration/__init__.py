"""D_DYADIC_ACCELERATION — Dyadic Rational Quantization for Fraction-Only Inference.

Layer: 4 (Institutional - Hardware/Acceleration)
CardinalStrength: OPERATIVE

Provides exact dyadic rationals (denominator = 2^k) with bit-shift arithmetic,
enabling integer-only, division-free neural network inference on OE's
Fraction-only substrate.

Based on: HAWQ-V3 (Yao et al., ICML 2021)
"""

from .implementation import (
    DyadicFraction,
    QuantizationConfig,
    RequantizationOp,
    FastDotProduct,
    EntropyFastPath,
    DOMAIN_METADATA,
)

from .invariants import (
    check_denominator_is_power_of_two,
    check_bit_shift_exactness,
    check_requantization_no_float_contamination,
    check_dot_product_deterministic_cross_platform,
    check_entropy_approximation_bounded_error,
    check_overflow_within_dynamic_range,
)

__all__ = [
    "DyadicFraction",
    "QuantizationConfig",
    "RequantizationOp",
    "FastDotProduct",
    "EntropyFastPath",
    "DOMAIN_METADATA",
    "check_denominator_is_power_of_two",
    "check_bit_shift_exactness",
    "check_requantization_no_float_contamination",
    "check_dot_product_deterministic_cross_platform",
    "check_entropy_approximation_bounded_error",
    "check_overflow_within_dynamic_range",
]
