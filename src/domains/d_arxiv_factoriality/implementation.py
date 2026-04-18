"""Implementation models for d_arxiv_factoriality."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class FactorialityClaim:
    """Structured claim parameters derived from arXiv paper 2604.05238v1 (cs.LO)."""

    ring_element_count: Fraction
    prime_generator_count: Fraction
    is_ufd: bool
    is_noetherian: bool
    localization_is_ufd: bool


def create_nominal_claim() -> FactorialityClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return FactorialityClaim(
        ring_element_count=Fraction(100),
        prime_generator_count=Fraction(3),
        is_ufd=True,
        is_noetherian=True,
        localization_is_ufd=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_FACTORIALITY",
    "paper_id": "2604.05238v1",
    "claim_model": "FactorialityClaim",
    "check_functions": [
        "check_ufd_property",
        "check_noetherian_property",
        "check_localization_ufd",
        "check_prime_generators_positive",
        "check_nagata_criterion",
    ],
}
