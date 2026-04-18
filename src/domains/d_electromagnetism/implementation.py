"""Implementation models for Electromagnetism."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ElectromagnetismClaim:
    """Structured claim parameters for Electromagnetism domain invariants."""

    maxwell_consistent: bool
    gauss_law_holds: bool
    faraday_induction_valid: bool
    poynting_conserved: bool
    permittivity_ratio: Fraction


def create_nominal_claim() -> ElectromagnetismClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ElectromagnetismClaim(
        maxwell_consistent=True,
        gauss_law_holds=True,
        faraday_induction_valid=True,
        poynting_conserved=True,
        permittivity_ratio=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "ELECTROMAGNETISM",
    "claim_model": "ElectromagnetismClaim",
    "check_functions": [
        "check_maxwell_equations_consistent",
        "check_gauss_law_divergence",
        "check_faraday_induction_non_negative",
        "check_poynting_vector_conservation",
        "check_permittivity_fraction",
    ],
}
