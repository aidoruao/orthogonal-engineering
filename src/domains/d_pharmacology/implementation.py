"""D_PHARMACOLOGY implementation — Drug interactions and pharmacokinetics.

Component 6 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class DrugInteraction:
    """Single-drug pharmacokinetic model.

    falsifies_if: half_life is not positive.
    falsifies_if: therapeutic_window_min > therapeutic_window_max.
    """
    dose: Fraction
    bioavailability: Fraction
    half_life: Fraction
    time_elapsed: Fraction
    therapeutic_window_min: Fraction
    therapeutic_window_max: Fraction
    initial_concentration: Fraction
    expected_concentration: Fraction


@dataclass(frozen=True)
class CombinedDrugs:
    """Polypharmacy safety envelope.

    falsifies_if: combined effect exceeds max_safe_effect.
    """
    drugs: Tuple[DrugInteraction, ...]
    max_safe_effect: Fraction


def compute_half_life_concentration(drug: DrugInteraction) -> Fraction:
    """Compute C(t) via iterative halving plus linear interpolation.

    C(t) = C_0 / 2^{n}  where n = floor(time_elapsed / half_life).
    Remainder r = time_elapsed mod half_life.
    Linear interpolation between C_after and C_after/2 over the next half_life:
        C_estimated = C_after * (1 - r / (2 * half_life)).
    """
    n_halves = int(drug.time_elapsed / drug.half_life)
    remaining = drug.time_elapsed - Fraction(n_halves, 1) * drug.half_life
    denominator = 2 ** n_halves
    c_after = drug.initial_concentration * Fraction(1, denominator)
    if remaining == Fraction(0, 1):
        return c_after
    # Linear interpolation factor: 1 - r/(2*h)
    factor = Fraction(1, 1) - remaining / (Fraction(2, 1) * drug.half_life)
    return c_after * factor


DOMAIN_METADATA = {
    "id": "PHARMACOLOGY",
    "claim_model": "DrugInteraction",
    "check_functions": [
        "check_dose_in_therapeutic_window",
        "check_half_life_decay",
        "check_drug_interaction_safety",
    ],
}
