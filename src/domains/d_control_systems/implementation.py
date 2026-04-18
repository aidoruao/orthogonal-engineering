"""Implementation models for Control Systems."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ControlSystemsClaim:
    """Structured claim parameters for Control Systems domain invariants."""

    lyapunov_stable: bool
    controllable_full_rank: bool
    observable_full_rank: bool
    settling_time_bounded: bool
    overshoot_percent: Fraction


def create_nominal_claim() -> ControlSystemsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ControlSystemsClaim(
        lyapunov_stable=True,
        controllable_full_rank=True,
        observable_full_rank=True,
        settling_time_bounded=True,
        overshoot_percent=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "CONTROL_SYSTEMS",
    "claim_model": "ControlSystemsClaim",
    "check_functions": [
        "check_stability_lyapunov",
        "check_controllability_rank",
        "check_observability_rank",
        "check_settling_time_bounded",
        "check_overshoot_fraction",
    ],
}
