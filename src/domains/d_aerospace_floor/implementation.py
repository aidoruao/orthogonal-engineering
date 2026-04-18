"""Implementation models for Aerospace Floor meta-standard domain."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class AerospaceFloorClaim:
    """Structured claim parameters for aerospace floor invariants."""

    do178c_determinism_verified: bool
    mcdc_coverage_achieved: bool
    misra_recursion_bounded: bool
    milstd882e_mishap_probability_assessed: bool
    independence_review_conducted: bool
    iec61508_sil4_verified: bool
    nasa_npr7150_class_a_compliant: bool
    af_compliance_scanned: bool


def create_nominal_claim() -> AerospaceFloorClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return AerospaceFloorClaim(
        do178c_determinism_verified=True,
        mcdc_coverage_achieved=True,
        misra_recursion_bounded=True,
        milstd882e_mishap_probability_assessed=True,
        independence_review_conducted=True,
        iec61508_sil4_verified=True,
        nasa_npr7150_class_a_compliant=True,
        af_compliance_scanned=True,
    )


DOMAIN_METADATA = {
    "id": "D_AEROSPACE_FLOOR",
    "claim_model": "AerospaceFloorClaim",
    "check_functions": [
        "check_do178c_determinism",
        "check_mcdc_coverage",
        "check_misra_recursion_bounded",
        "check_milstd882e_mishap_probability",
        "check_independence_review",
        "check_iec61508_sil4",
        "check_nasa_npr7150_class_a",
        "check_af_compliance_scanned",
    ],
}
