"""Implementation models for d_arxiv_statml_sequential_audit."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class SequentialAuditClaim:
    """Structured claim parameters derived from arXiv paper 2604.06116v1 (stat.ML)."""

    sample_size: Fraction
    population_size: Fraction
    risk_limit: Fraction
    test_statistic: Fraction
    audit_complete: bool


def create_nominal_claim() -> SequentialAuditClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return SequentialAuditClaim(
        sample_size=Fraction(100),
        population_size=Fraction(10000),
        risk_limit=Fraction(5, 100),
        test_statistic=Fraction(3, 2),
        audit_complete=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_SEQUENTIAL_AUDIT",
    "paper_id": "2604.06116v1",
    "claim_model": "SequentialAuditClaim",
    "check_functions": [
        "check_risk_limit_valid",
        "check_sample_size_valid",
        "check_test_statistic_nonnegative",
        "check_audit_completion",
        "check_population_size_positive",
    ],
}
