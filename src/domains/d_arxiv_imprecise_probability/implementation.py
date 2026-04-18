"""Implementation models for d_arxiv_imprecise_probability."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ImpreciseProbabilityClaim:
    """Structured claim parameters derived from arXiv paper 2604.09272v1 (cs.LO)."""

    lower_probability: Fraction
    upper_probability: Fraction
    credal_set_size: Fraction
    domain_element_count: Fraction
    is_scott_continuous: bool


def create_nominal_claim() -> ImpreciseProbabilityClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ImpreciseProbabilityClaim(
        lower_probability=Fraction(1, 4),
        upper_probability=Fraction(3, 4),
        credal_set_size=Fraction(5),
        domain_element_count=Fraction(10),
        is_scott_continuous=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_IMPRECISE_PROBABILITY",
    "paper_id": "2604.09272v1",
    "claim_model": "ImpreciseProbabilityClaim",
    "check_functions": [
        "check_credal_interval_validity",
        "check_credal_set_nonempty",
        "check_scott_continuity",
        "check_domain_theoretic_bound",
        "check_vacuous_coherence",
    ],
}
