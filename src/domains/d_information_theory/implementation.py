"""Implementation models for Information Theory."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class InformationTheoryClaim:
    """Structured claim parameters for Information Theory domain invariants."""

    entropy_non_negative: bool
    mutual_information_symmetric: bool
    channel_capacity_achievable: bool
    kl_divergence_non_negative: bool
    code_rate: Fraction


def create_nominal_claim() -> InformationTheoryClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return InformationTheoryClaim(
        entropy_non_negative=True,
        mutual_information_symmetric=True,
        channel_capacity_achievable=True,
        kl_divergence_non_negative=True,
        code_rate=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "INFORMATION_THEORY",
    "claim_model": "InformationTheoryClaim",
    "check_functions": [
        "check_entropy_non_negative",
        "check_mutual_information_symmetric",
        "check_channel_capacity_achievable",
        "check_kullback_leibler_non_negative",
        "check_code_rate_fraction",
    ],
}
