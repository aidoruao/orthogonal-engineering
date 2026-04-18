"""Implementation models for d_arxiv_game_endgame_verification."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class EndgameVerificationClaim:
    """Structured claim parameters derived from arXiv paper 2604.07907v1 (cs.LO)."""

    positions_verified: Fraction
    capture_quiet_ratio: Fraction
    decomposition_depth: Fraction
    is_complete: bool
    is_consistent: bool


def create_nominal_claim() -> EndgameVerificationClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return EndgameVerificationClaim(
        positions_verified=Fraction(100000),
        capture_quiet_ratio=Fraction(3, 4),
        decomposition_depth=Fraction(6),
        is_complete=True,
        is_consistent=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_GAME_ENDGAME_VERIFICATION",
    "paper_id": "2604.07907v1",
    "claim_model": "EndgameVerificationClaim",
    "check_functions": [
        "check_tablebase_completeness",
        "check_tablebase_consistency",
        "check_positions_positive",
        "check_capture_quiet_ratio_valid",
        "check_decomposition_depth_positive",
    ],
}
