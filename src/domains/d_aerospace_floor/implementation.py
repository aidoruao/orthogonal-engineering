"""Implementation models for Aerospace Floor meta-standard domain.

All compliance scores are represented as :class:`fractions.Fraction` to
preserve byte-exact cross-platform arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

MIN_DETERMINISM_SCORE: Fraction = Fraction(3, 4)
MIN_MCDC_COVERAGE: Fraction = Fraction(1, 1)
MAX_RECURSION_DEPTH: int = 10
MAX_MISHAP_PROBABILITY: Fraction = Fraction(1, 100)
MIN_INDEPENDENCE_REVIEW_SCORE: Fraction = Fraction(1, 2)
MIN_SIL_LEVEL: int = 4
MIN_NASA_COMPLIANCE: Fraction = Fraction(3, 4)
MIN_AF_SCAN_COVERAGE: Fraction = Fraction(1, 1)


@dataclass(frozen=True)
class AerospaceFloorClaim:
    """Structured claim parameters for aerospace floor invariants.

    Fields store quantitative scores rather than boolean flags so that
    invariant checks perform real Fraction computation.
    """

    determinism_score: Fraction = Fraction(1, 1)
    mcdc_coverage_fraction: Fraction = Fraction(1, 1)
    recursion_depth_bound: int = 10
    mishap_probability: Fraction = Fraction(1, 1000)
    independence_review_score: Fraction = Fraction(1, 1)
    sil_integrity_level: int = 4
    nasa_compliance_score: Fraction = Fraction(1, 1)
    af_scan_coverage: Fraction = Fraction(1, 1)


def create_nominal_claim() -> AerospaceFloorClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return AerospaceFloorClaim()


DOMAIN_METADATA = {
    "id": "D_AEROSPACE_FLOOR",
    "claim_model": "AerospaceFloorClaim",
    "check_functions": [
        "check_determinism_score",
        "check_mcdc_coverage_fraction",
        "check_recursion_depth_bound",
        "check_mishap_probability_risk",
        "check_independence_review_score",
        "check_sil_integrity_level",
        "check_nasa_compliance_score",
        "check_af_scan_coverage",
    ],
}
