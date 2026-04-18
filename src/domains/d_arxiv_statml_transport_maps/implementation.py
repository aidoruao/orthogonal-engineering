"""Implementation models for d_arxiv_statml_transport_maps."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class TransportMapClaim:
    """Structured claim parameters derived from arXiv paper 2604.07671v1 (stat.ML)."""

    source_measure_support_size: Fraction
    target_measure_support_size: Fraction
    transport_cost: Fraction
    is_uniquely_recoverable: bool
    data_point_count: Fraction


def create_nominal_claim() -> TransportMapClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return TransportMapClaim(
        source_measure_support_size=Fraction(10),
        target_measure_support_size=Fraction(10),
        transport_cost=Fraction(1, 2),
        is_uniquely_recoverable=True,
        data_point_count=Fraction(50),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_TRANSPORT_MAPS",
    "paper_id": "2604.07671v1",
    "claim_model": "TransportMapClaim",
    "check_functions": [
        "check_unique_recovery",
        "check_transport_cost_nonnegative",
        "check_support_sizes_positive",
        "check_data_sufficient",
        "check_finite_data",
    ],
}
