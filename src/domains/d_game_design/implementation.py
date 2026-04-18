"""Implementation models for Game Design."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class GameDesignClaim:
    """Structured claim parameters for Game Design domain invariants."""

    core_loop_engaging: bool
    progression_monotonic: bool
    balance_fair_symmetric: bool
    feedback_immediate: bool
    difficulty_slope: Fraction


def create_nominal_claim() -> GameDesignClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return GameDesignClaim(
        core_loop_engaging=True,
        progression_monotonic=True,
        balance_fair_symmetric=True,
        feedback_immediate=True,
        difficulty_slope=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "GAME_DESIGN",
    "claim_model": "GameDesignClaim",
    "check_functions": [
        "check_core_loop_engagement",
        "check_progression_curve_monotonic",
        "check_balance_fairness_symmetric",
        "check_feedback_immediacy",
        "check_difficulty_slope_fraction",
    ],
}
