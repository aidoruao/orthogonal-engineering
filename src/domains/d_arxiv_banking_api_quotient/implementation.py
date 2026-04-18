"""Implementation models for d_arxiv_banking_api_quotient."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class BankingAPIQuotientClaim:
    """Structured claim parameters derived from arXiv paper 2604.08833v1 (math.CT)."""

    api_count: Fraction
    morphism_count: Fraction
    quotient_exists: bool
    is_universal: bool
    preserves_financial_invariants: bool


def create_nominal_claim() -> BankingAPIQuotientClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return BankingAPIQuotientClaim(
        api_count=Fraction(5),
        morphism_count=Fraction(10),
        quotient_exists=True,
        is_universal=True,
        preserves_financial_invariants=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_BANKING_API_QUOTIENT",
    "paper_id": "2604.08833v1",
    "claim_model": "BankingAPIQuotientClaim",
    "check_functions": [
        "check_quotient_existence",
        "check_universality",
        "check_financial_invariants_preserved",
        "check_api_count_positive",
        "check_morphism_count_positive",
    ],
}
