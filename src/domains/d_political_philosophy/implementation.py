"""Implementation models for Political Philosophy."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class PoliticalPhilosophyClaim:
    """Structured claim parameters for Political Philosophy domain invariants."""

    social_contract_consensual: bool
    rights_non_derogable: bool
    distributive_justice_symmetric: bool
    sovereignty_indivisible: bool
    legitimacy_score: Fraction


def create_nominal_claim() -> PoliticalPhilosophyClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return PoliticalPhilosophyClaim(
        social_contract_consensual=True,
        rights_non_derogable=True,
        distributive_justice_symmetric=True,
        sovereignty_indivisible=True,
        legitimacy_score=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "POLITICAL_PHILOSOPHY",
    "claim_model": "PoliticalPhilosophyClaim",
    "check_functions": [
        "check_social_contract_consensual",
        "check_rights_non_derogable",
        "check_distributive_justice_symmetric",
        "check_sovereignty_indivisible",
        "check_legitimacy_score_fraction",
    ],
}
