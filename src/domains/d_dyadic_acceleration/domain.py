"""D_DYADIC_ACCELERATION domain metadata and registration.

Layer: 4 (Institutional - Hardware/Acceleration)
CardinalStrength: OPERATIVE
"""

from .implementation import DOMAIN_METADATA

# Domain registration hook for OE domain loader
DOMAIN = {
    "id": "D_DYADIC_ACCELERATION",
    "name": "dyadic_acceleration",
    "path": "src.domains.d_dyadic_acceleration",
    "layer": 4,
    "cardinal_strength": "OPERATIVE",
    "metadata": DOMAIN_METADATA,
    "invariants": [
        "check_denominator_is_power_of_two",
        "check_bit_shift_exactness",
        "check_requantization_no_float_contamination",
        "check_dot_product_deterministic_cross_platform",
        "check_entropy_approximation_bounded_error",
        "check_overflow_within_dynamic_range",
    ],
}
