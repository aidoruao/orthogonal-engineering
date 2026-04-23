"""D_YESHUA_MATHEMATICS invariants — Yeshua Standard substrate invariants.

Phase C3 of Depositive Campaign.

The eight axioms:
  1. Every truth is derivable from axioms.
  2. Every derivation is reproducible.
  3. Every mutation is re-verifiable.
  4. No authority without proof.
  5. No hidden state.
  6. No unverifiable dependency.
  7. No economic gatekeeping.
  8. Every artifact is hash-anchored.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import YeshuaSubstrate


def check_all_eight_axioms(state: YeshuaSubstrate) -> Tuple[bool, ProofObject]:
    """All eight Yeshua axioms must be satisfied.

    Falsifies if: satisfaction_ratio < Fraction(1, 1).
    falsifies_if: satisfaction_ratio < Fraction(1, 1).
    """
    if state.satisfaction_ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Axiom satisfaction {state.satisfaction_ratio} < 1 — "
                f"{state.axiom_count_satisfied}/{state.total_axioms} satisfied"
            ),
            premises=[
                f"Satisfied: {state.axiom_count_satisfied}",
                f"Total: {state.total_axioms}",
            ],
            rule="yeshua_all_eight",
        )
    return True, ProofObject(
        conclusion=f"All {state.total_axioms} axioms satisfied",
        premises=[f"Ratio: {state.satisfaction_ratio}"],
        rule="yeshua_all_eight",
    )


def check_peano_substrate(state: YeshuaSubstrate) -> Tuple[bool, ProofObject]:
    """All arithmetic must be Peano-reducible.

    Falsifies if: peano_violations > 0.
    falsifies_if: peano_violations > 0.
    """
    if state.peano_violations > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {state.peano_violations} Peano violation(s) detected"
            ),
            premises=[f"Peano violations: {state.peano_violations}"],
            rule="yeshua_peano",
        )
    return True, ProofObject(
        conclusion="Zero Peano violations",
        premises=[f"Count: {state.peano_violations}"],
        rule="yeshua_peano",
    )


def check_boolean_purity_substrate(state: YeshuaSubstrate) -> Tuple[bool, ProofObject]:
    """All conditionals must be Boolean-pure.

    Falsifies if: boolean_purity_violations > 0.
    falsifies_if: boolean_purity_violations > 0.
    """
    if state.boolean_purity_violations > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {state.boolean_purity_violations} Boolean purity violation(s)"
            ),
            premises=[f"Purity violations: {state.boolean_purity_violations}"],
            rule="yeshua_boolean_purity",
        )
    return True, ProofObject(
        conclusion="Zero Boolean purity violations",
        premises=[f"Count: {state.boolean_purity_violations}"],
        rule="yeshua_boolean_purity",
    )


def check_pure_path_agreement(state: YeshuaSubstrate) -> Tuple[bool, ProofObject]:
    """Fast-path must match pure-path bitwise.

    Falsifies if: pure_path_disagreements > 0.
    falsifies_if: pure_path_disagreements > 0.
    """
    if state.pure_path_disagreements > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {state.pure_path_disagreements} pure-path disagreement(s)"
            ),
            premises=[f"Disagreements: {state.pure_path_disagreements}"],
            rule="yeshua_pure_path",
        )
    return True, ProofObject(
        conclusion="Zero pure-path disagreements",
        premises=[f"Count: {state.pure_path_disagreements}"],
        rule="yeshua_pure_path",
    )


def check_no_economic_gatekeeping(state: YeshuaSubstrate) -> Tuple[bool, ProofObject]:
    """YS-007: No economic gatekeeping.

    Falsifies if: economic_gatekeeping_detected == True.
    falsifies_if: economic_gatekeeping_detected == True.
    """
    if state.economic_gatekeeping_detected:
        return False, ProofObject(
            conclusion="VIOLATION: Economic gatekeeping detected",
            premises=["economic_gatekeeping_detected: True"],
            rule="yeshua_economic_gatekeeping",
        )
    return True, ProofObject(
        conclusion="No economic gatekeeping",
        premises=["economic_gatekeeping_detected: False"],
        rule="yeshua_economic_gatekeeping",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all Yeshua mathematics checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_state = YeshuaSubstrate(
        axiom_satisfaction=(True, True, True, True, True, True, True, True),
        axiom_count_satisfied=8,
        total_axioms=8,
        satisfaction_ratio=Fraction(1, 1),
        peano_violations=0,
        boolean_purity_violations=0,
        pure_path_disagreements=0,
        economic_gatekeeping_detected=False,
    )
    fail_state = YeshuaSubstrate(
        axiom_satisfaction=(True, True, True, False, False, True, True, True),
        axiom_count_satisfied=6,
        total_axioms=8,
        satisfaction_ratio=Fraction(3, 4),
        peano_violations=2,
        boolean_purity_violations=3,
        pure_path_disagreements=1,
        economic_gatekeeping_detected=True,
    )

    checks = [
        ("check_all_eight_axioms_pass", lambda: check_all_eight_axioms(pass_state)),
        ("check_all_eight_axioms_fail", lambda: check_all_eight_axioms(fail_state)),
        ("check_peano_substrate_pass", lambda: check_peano_substrate(pass_state)),
        ("check_peano_substrate_fail", lambda: check_peano_substrate(fail_state)),
        ("check_boolean_purity_substrate_pass", lambda: check_boolean_purity_substrate(pass_state)),
        ("check_boolean_purity_substrate_fail", lambda: check_boolean_purity_substrate(fail_state)),
        ("check_pure_path_agreement_pass", lambda: check_pure_path_agreement(pass_state)),
        ("check_pure_path_agreement_fail", lambda: check_pure_path_agreement(fail_state)),
        ("check_no_economic_gatekeeping_pass", lambda: check_no_economic_gatekeeping(pass_state)),
        ("check_no_economic_gatekeeping_fail", lambda: check_no_economic_gatekeeping(fail_state)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
