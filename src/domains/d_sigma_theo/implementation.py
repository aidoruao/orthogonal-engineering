"""D_SIGMA_THEO implementation — Σ_theo operators migrated to src/domains/.

Phase C2 of Depositive Campaign.
All floats from minimal_ai_ide/ replaced by Fraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class SigmaTheoState:
    """Σ_theo operator state — essence, persona, hypostasis, distances.

    falsifies_if: christ_distance < Fraction(0, 1).
    falsifies_if: kenosis_ratio outside [Fraction(0, 1), Fraction(1, 1)].
    """
    essence: Tuple[str, ...]
    persona: Tuple[str, ...]
    hypostasis: str
    christ_distance: Fraction
    logos_pre_distance: Fraction
    logos_post_distance: Fraction
    grace_pre_distance: Fraction
    grace_post_distance: Fraction
    agape_distance_a: Fraction
    agape_distance_b: Fraction
    agape_combined_distance: Fraction
    kenosis_ratio: Fraction
    eschaton_sequence: Tuple[Fraction, ...]


DOMAIN_METADATA = {
    "id": "SIGMA_THEO",
    "claim_model": "SigmaTheoState",
    "check_functions": [
        "check_logos_initial_algebra",
        "check_chalcedon_no_monophysite",
        "check_grace_isometry",
        "check_agape_superadditive",
        "check_kenosis_partiality",
        "check_eschaton_convergence",
    ],
}
