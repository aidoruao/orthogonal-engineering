"""Implementation models for Topology."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class TopologyClaim:
    """Structured claim parameters for Topology domain invariants."""

    compactness_preserved: bool
    connectedness_invariant: bool
    hausdorff_separated: bool
    fundamental_group_well_defined: bool
    euler_characteristic: Fraction


def create_nominal_claim() -> TopologyClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return TopologyClaim(
        compactness_preserved=True,
        connectedness_invariant=True,
        hausdorff_separated=True,
        fundamental_group_well_defined=True,
        euler_characteristic=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "TOPOLOGY",
    "claim_model": "TopologyClaim",
    "check_functions": [
        "check_compactness_preserved",
        "check_connectedness_invariant",
        "check_hausdorff_separation",
        "check_fundamental_group_well_defined",
        "check_euler_characteristic_fraction",
    ],
}
