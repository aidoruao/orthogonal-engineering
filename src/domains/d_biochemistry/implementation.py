"""Implementation models for Biochemistry."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class BiochemistryClaim:
    """Structured claim parameters for Biochemistry domain invariants."""

    michaelis_menten_valid: bool
    atp_hydrolysis_exergonic: bool
    folding_entropy_valid: bool
    replication_fidelity_high: bool
    equilibrium_concentration: Fraction


def create_nominal_claim() -> BiochemistryClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return BiochemistryClaim(
        michaelis_menten_valid=True,
        atp_hydrolysis_exergonic=True,
        folding_entropy_valid=True,
        replication_fidelity_high=True,
        equilibrium_concentration=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "BIOCHEMISTRY",
    "claim_model": "BiochemistryClaim",
    "check_functions": [
        "check_enzyme_kinetics_michaelis",
        "check_atp_hydrolysis_exergonic",
        "check_protein_folding_entropy",
        "check_dna_replication_fidelity",
        "check_concentration_equilibrium_fraction",
    ],
}
