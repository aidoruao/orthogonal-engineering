"""Implementation models for Visual Arts."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class VisualArtsClaim:
    """Structured claim parameters for Visual Arts domain invariants."""

    color_harmony_complementary: bool
    golden_ratio_proportion: bool
    perspective_converges: bool
    composition_balanced: bool
    chroma_saturation: Fraction


def create_nominal_claim() -> VisualArtsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return VisualArtsClaim(
        color_harmony_complementary=True,
        golden_ratio_proportion=True,
        perspective_converges=True,
        composition_balanced=True,
        chroma_saturation=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "VISUAL_ARTS",
    "claim_model": "VisualArtsClaim",
    "check_functions": [
        "check_color_harmony_complementary",
        "check_golden_ratio_proportion",
        "check_perspective_convergence",
        "check_compositional_balance",
        "check_chroma_saturation_fraction",
    ],
}
