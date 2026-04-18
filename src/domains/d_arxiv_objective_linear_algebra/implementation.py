"""Implementation models for d_arxiv_objective_linear_algebra."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ObjectiveLinearAlgebraClaim:
    """Structured claim parameters derived from arXiv paper 2603.19437v1 (math.CT)."""

    dimension: Fraction
    sign_consistent: bool
    exterior_power_well_defined: bool
    determinant_well_defined: bool
    orientation_invariant: bool


def create_nominal_claim() -> ObjectiveLinearAlgebraClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return ObjectiveLinearAlgebraClaim(
        dimension=Fraction(3),
        sign_consistent=True,
        exterior_power_well_defined=True,
        determinant_well_defined=True,
        orientation_invariant=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_OBJECTIVE_LINEAR_ALGEBRA",
    "paper_id": "2603.19437v1",
    "claim_model": "ObjectiveLinearAlgebraClaim",
    "check_functions": [
        "check_sign_consistency",
        "check_exterior_power",
        "check_determinant",
        "check_orientation_independence",
        "check_dimension_positive",
    ],
}
