"""D_PHARMACOLOGY invariants — Drug interactions and pharmacokinetics.

Component 6 of 9a Therapeutic Pipeline.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import DrugInteraction, CombinedDrugs, compute_half_life_concentration


def check_dose_in_therapeutic_window(drug: DrugInteraction) -> Tuple[bool, ProofObject]:
    """Effective dose must lie within the therapeutic window.

    Falsifies if: dose * bioavailability < min or > max.
    falsifies_if: effective dose outside [therapeutic_window_min, therapeutic_window_max].
    """
    effective = drug.dose * drug.bioavailability
    if effective < drug.therapeutic_window_min or effective > drug.therapeutic_window_max:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Effective dose {effective} outside window "
                f"[{drug.therapeutic_window_min}, {drug.therapeutic_window_max}]"
            ),
            premises=[
                f"Dose: {drug.dose}",
                f"Bioavailability: {drug.bioavailability}",
                f"Effective: {effective}",
            ],
            rule="pharma_therapeutic_window",
        )
    return True, ProofObject(
        conclusion=f"Effective dose {effective} in therapeutic window",
        premises=[f"Effective: {effective}"],
        rule="pharma_therapeutic_window",
    )


def check_half_life_decay(drug: DrugInteraction) -> Tuple[bool, ProofObject]:
    """Measured concentration must match iterative halving + interpolation model.

    Falsifies if: expected_concentration != computed C(t).
    falsifies_if: expected_concentration differs from compute_half_life_concentration().
    """
    computed = compute_half_life_concentration(drug)
    if drug.expected_concentration != computed:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Expected {drug.expected_concentration} != computed {computed}"
            ),
            premises=[
                f"Initial: {drug.initial_concentration}",
                f"Time elapsed: {drug.time_elapsed}",
                f"Half-life: {drug.half_life}",
                f"Computed: {computed}",
            ],
            rule="pharma_half_life",
        )
    return True, ProofObject(
        conclusion=f"Concentration {computed} matches expected",
        premises=[f"Computed: {computed}"],
        rule="pharma_half_life",
    )


def check_drug_interaction_safety(combined: CombinedDrugs) -> Tuple[bool, ProofObject]:
    """Combined drug effect must not exceed max_safe_effect.

    Falsifies if: sum(initial_concentration for each drug) > max_safe_effect.
    falsifies_if: total combined effect exceeds max_safe_effect.
    """
    total = sum(d.initial_concentration for d in combined.drugs)
    if total > combined.max_safe_effect:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Combined effect {total} > max safe {combined.max_safe_effect}"
            ),
            premises=[
                f"Drugs: {len(combined.drugs)}",
                f"Total: {total}",
                f"Max safe: {combined.max_safe_effect}",
            ],
            rule="pharma_interaction",
        )
    return True, ProofObject(
        conclusion=f"Combined effect {total} <= {combined.max_safe_effect}",
        premises=[f"Total: {total}"],
        rule="pharma_interaction",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all pharmacology checks with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_drug = DrugInteraction(
        dose=Fraction(100, 1),
        bioavailability=Fraction(8, 10),
        half_life=Fraction(4, 1),
        time_elapsed=Fraction(8, 1),
        therapeutic_window_min=Fraction(50, 1),
        therapeutic_window_max=Fraction(150, 1),
        initial_concentration=Fraction(100, 1),
        expected_concentration=Fraction(25, 1),
    )
    fail_drug_dose = DrugInteraction(
        dose=Fraction(200, 1),
        bioavailability=Fraction(9, 10),
        half_life=Fraction(4, 1),
        time_elapsed=Fraction(8, 1),
        therapeutic_window_min=Fraction(50, 1),
        therapeutic_window_max=Fraction(150, 1),
        initial_concentration=Fraction(100, 1),
        expected_concentration=Fraction(25, 1),
    )
    fail_drug_decay = DrugInteraction(
        dose=Fraction(100, 1),
        bioavailability=Fraction(8, 10),
        half_life=Fraction(4, 1),
        time_elapsed=Fraction(8, 1),
        therapeutic_window_min=Fraction(50, 1),
        therapeutic_window_max=Fraction(150, 1),
        initial_concentration=Fraction(100, 1),
        expected_concentration=Fraction(99, 1),
    )
    pass_combined = CombinedDrugs(
        drugs=(pass_drug, pass_drug),
        max_safe_effect=Fraction(300, 1),
    )
    fail_combined = CombinedDrugs(
        drugs=(pass_drug, pass_drug),
        max_safe_effect=Fraction(150, 1),
    )

    checks = [
        ("check_dose_window_pass", lambda: check_dose_in_therapeutic_window(pass_drug)),
        ("check_dose_window_fail", lambda: check_dose_in_therapeutic_window(fail_drug_dose)),
        ("check_half_life_pass", lambda: check_half_life_decay(pass_drug)),
        ("check_half_life_fail", lambda: check_half_life_decay(fail_drug_decay)),
        ("check_interaction_pass", lambda: check_drug_interaction_safety(pass_combined)),
        ("check_interaction_fail", lambda: check_drug_interaction_safety(fail_combined)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
