"""Implementation models for Neuroscience."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class NeuroscienceClaim:
    """Structured claim parameters for Neuroscience domain invariants."""

    action_potential_all_or_none: bool
    neurotransmitter_release_valid: bool
    myelination_increases_speed: bool
    refractory_period_bounded: bool
    synaptic_weight: Fraction


def create_nominal_claim() -> NeuroscienceClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return NeuroscienceClaim(
        action_potential_all_or_none=True,
        neurotransmitter_release_valid=True,
        myelination_increases_speed=True,
        refractory_period_bounded=True,
        synaptic_weight=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "NEUROSCIENCE",
    "claim_model": "NeuroscienceClaim",
    "check_functions": [
        "check_action_potential_all_or_none",
        "check_synapse_neurotransmitter_release",
        "check_myelination_conduction_speed",
        "check_refractory_period_bounded",
        "check_synaptic_weight_fraction",
    ],
}
