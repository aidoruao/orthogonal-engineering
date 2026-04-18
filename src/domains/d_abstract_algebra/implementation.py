"""Implementation models for Abstract Algebra."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class AbstractAlgebraClaim:
    """Structured claim parameters for Abstract Algebra domain invariants."""

    group_axioms_satisfied: bool
    ring_distributive: bool
    field_has_inverses: bool
    homomorphism_preserves: bool
    element_order: Fraction


def create_nominal_claim() -> AbstractAlgebraClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return AbstractAlgebraClaim(
        group_axioms_satisfied=True,
        ring_distributive=True,
        field_has_inverses=True,
        homomorphism_preserves=True,
        element_order=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "ABSTRACT_ALGEBRA",
    "claim_model": "AbstractAlgebraClaim",
    "check_functions": [
        "check_group_axioms_satisfied",
        "check_ring_distributivity",
        "check_field_multiplicative_inverse",
        "check_homomorphism_preserves_operation",
        "check_order_of_element_fraction",
    ],
}
