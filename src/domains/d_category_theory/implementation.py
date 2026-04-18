"""Implementation models for Category Theory."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CategoryTheoryClaim:
    """Structured claim parameters for Category Theory domain invariants."""

    composition_associative: bool
    identity_exists: bool
    functor_preserves_identity: bool
    naturality_square_commutes: bool
    hom_set_size: Fraction


def create_nominal_claim() -> CategoryTheoryClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return CategoryTheoryClaim(
        composition_associative=True,
        identity_exists=True,
        functor_preserves_identity=True,
        naturality_square_commutes=True,
        hom_set_size=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "CATEGORY_THEORY",
    "claim_model": "CategoryTheoryClaim",
    "check_functions": [
        "check_composition_associative",
        "check_identity_morphism_exists",
        "check_functor_preserves_identity",
        "check_natural_transformation_commutes",
        "check_hom_set_size_fraction",
    ],
}
