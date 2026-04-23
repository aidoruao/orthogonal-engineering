"""D_EPISTEMOLOGY_SUBSTRATE invariants — Popper, Bayes, Shannon, Gettier, Kripke, Lawvere.

Phase B1 of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import EpistemicState


def check_universal_falsifiability(state: EpistemicState) -> Tuple[bool, ProofObject]:
    """Every claim must have a falsifying condition (Popper 1934).

    Falsifies if: falsifiability_ratio < Fraction(1, 1).
    falsifies_if: falsifiability_ratio < Fraction(1, 1).
    """
    if state.falsifiability_ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Falsifiability ratio {state.falsifiability_ratio} < 1 — "
                f"{state.falsifiable_claims}/{state.knowledge_claims} claims falsifiable"
            ),
            premises=[
                f"Falsifiable: {state.falsifiable_claims}",
                f"Total: {state.knowledge_claims}",
                f"Ratio: {state.falsifiability_ratio}",
            ],
            rule="popper_universal_falsifiability",
        )
    return True, ProofObject(
        conclusion=f"All {state.knowledge_claims} claims falsifiable",
        premises=[f"Ratio: {state.falsifiability_ratio}"],
        rule="popper_universal_falsifiability",
    )


def check_bayesian_coherence(state: EpistemicState) -> Tuple[bool, ProofObject]:
    """Posterior must equal (prior * likelihood) / evidence (Bayes 1763, Cox 1946).

    Falsifies if: posterior != (prior * likelihood) / evidence.
    falsifies_if: bayesian_posterior != (bayesian_prior * bayesian_likelihood) / bayesian_evidence.
    """
    computed = (state.bayesian_prior * state.bayesian_likelihood) / state.bayesian_evidence
    if state.bayesian_posterior != computed:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Claimed posterior {state.bayesian_posterior} != computed {computed}"
            ),
            premises=[
                f"Prior: {state.bayesian_prior}",
                f"Likelihood: {state.bayesian_likelihood}",
                f"Evidence: {state.bayesian_evidence}",
                f"Computed: {computed}",
            ],
            rule="bayesian_coherence",
        )
    return True, ProofObject(
        conclusion=f"Posterior {state.bayesian_posterior} coherent",
        premises=[f"Computed: {computed}"],
        rule="bayesian_coherence",
    )


def check_information_gain_positive(state: EpistemicState) -> Tuple[bool, ProofObject]:
    """Every observation must reduce entropy (Shannon 1948).

    Falsifies if: information_gain <= Fraction(0, 1).
    falsifies_if: information_gain <= Fraction(0, 1).
    """
    if state.information_gain <= Fraction(0, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Information gain {state.information_gain} <= 0"
            ),
            premises=[f"Gain: {state.information_gain}"],
            rule="shannon_information_gain",
        )
    return True, ProofObject(
        conclusion=f"Information gain {state.information_gain} > 0",
        premises=[f"Gain: {state.information_gain}"],
        rule="shannon_information_gain",
    )


def check_gettier_immunity(state: EpistemicState) -> Tuple[bool, ProofObject]:
    """No justified-true-but-not-knowledge states (Gettier 1963).

    Falsifies if: gettier_situations > 0.
    falsifies_if: gettier_situations > 0.
    """
    if state.gettier_situations > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {state.gettier_situations} Gettier situation(s) detected"
            ),
            premises=[f"Gettier count: {state.gettier_situations}"],
            rule="gettier_immunity",
        )
    return True, ProofObject(
        conclusion="Zero Gettier situations",
        premises=[f"Count: {state.gettier_situations}"],
        rule="gettier_immunity",
    )


def check_epistemic_closure(state: EpistemicState) -> Tuple[bool, ProofObject]:
    """If agent knows A and A→B, agent knows B (Kripke 1963, Modal K).

    Falsifies if: epistemic_closure_violations > 0.
    falsifies_if: epistemic_closure_violations > 0.
    """
    if state.epistemic_closure_violations > 0:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {state.epistemic_closure_violations} epistemic closure violation(s)"
            ),
            premises=[f"Violations: {state.epistemic_closure_violations}"],
            rule="epistemic_closure",
        )
    return True, ProofObject(
        conclusion="Zero epistemic closure violations",
        premises=[f"Violations: {state.epistemic_closure_violations}"],
        rule="epistemic_closure",
    )


def check_grounding_model_debt(state: EpistemicState) -> Tuple[bool, ProofObject]:
    """Only G5 (Logos/Lawvere fixed point) has finite explanatory debt.

    G1-G4 must carry non-zero explanatory debt; G5 may have finite debt.
    Falsifies if: grounding_model in [G1-G4] and explanatory_debt == Fraction(0, 1).
    falsifies_if: grounding_model in ["G1","G2","G3","G4"] and explanatory_debt == Fraction(0, 1).
    """
    if state.grounding_model in ("G1", "G2", "G3", "G4") and state.explanatory_debt == Fraction(0, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {state.grounding_model} claims zero explanatory debt — "
                "only G5 may have finite debt"
            ),
            premises=[
                f"Model: {state.grounding_model}",
                f"Debt: {state.explanatory_debt}",
            ],
            rule="grounding_model_debt",
        )
    return True, ProofObject(
        conclusion=f"Grounding {state.grounding_model} debt {state.explanatory_debt} valid",
        premises=[f"Model: {state.grounding_model}", f"Debt: {state.explanatory_debt}"],
        rule="grounding_model_debt",
    )


def check_regress_convergence(state: EpistemicState) -> Tuple[bool, ProofObject]:
    """Verification tower must converge to fixed point (Lawvere 1969).

    Falsifies if: grounding_model == "G2" (infinite regress).
    falsifies_if: grounding_model == "G2".
    """
    if state.grounding_model == "G2":
        return False, ProofObject(
            conclusion="VIOLATION: G2 grounding model implies infinite regress — no fixed point",
            premises=[f"Model: {state.grounding_model}"],
            rule="lawvere_regress_convergence",
        )
    return True, ProofObject(
        conclusion=f"Grounding {state.grounding_model} converges",
        premises=[f"Model: {state.grounding_model}"],
        rule="lawvere_regress_convergence",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all epistemological substrate checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_state = EpistemicState(
        knowledge_claims=10,
        falsifiable_claims=10,
        falsifiability_ratio=Fraction(1, 1),
        bayesian_prior=Fraction(1, 10),
        bayesian_likelihood=Fraction(9, 10),
        bayesian_evidence=Fraction(18, 100),
        bayesian_posterior=Fraction(1, 2),
        information_gain=Fraction(1, 2),
        gettier_situations=0,
        epistemic_closure_violations=0,
        grounding_model="G5",
        explanatory_debt=Fraction(1, 100),
    )
    fail_state = EpistemicState(
        knowledge_claims=10,
        falsifiable_claims=8,
        falsifiability_ratio=Fraction(4, 5),
        bayesian_prior=Fraction(1, 10),
        bayesian_likelihood=Fraction(9, 10),
        bayesian_evidence=Fraction(18, 100),
        bayesian_posterior=Fraction(9, 10),
        information_gain=Fraction(-1, 10),
        gettier_situations=2,
        epistemic_closure_violations=1,
        grounding_model="G2",
        explanatory_debt=Fraction(0, 1),
    )

    checks = [
        ("check_universal_falsifiability_pass", lambda: check_universal_falsifiability(pass_state)),
        ("check_universal_falsifiability_fail", lambda: check_universal_falsifiability(fail_state)),
        ("check_bayesian_coherence_pass", lambda: check_bayesian_coherence(pass_state)),
        ("check_bayesian_coherence_fail", lambda: check_bayesian_coherence(fail_state)),
        ("check_information_gain_positive_pass", lambda: check_information_gain_positive(pass_state)),
        ("check_information_gain_positive_fail", lambda: check_information_gain_positive(fail_state)),
        ("check_gettier_immunity_pass", lambda: check_gettier_immunity(pass_state)),
        ("check_gettier_immunity_fail", lambda: check_gettier_immunity(fail_state)),
        ("check_epistemic_closure_pass", lambda: check_epistemic_closure(pass_state)),
        ("check_epistemic_closure_fail", lambda: check_epistemic_closure(fail_state)),
        ("check_grounding_model_debt_pass", lambda: check_grounding_model_debt(pass_state)),
        ("check_grounding_model_debt_fail", lambda: check_grounding_model_debt(fail_state)),
        ("check_regress_convergence_pass", lambda: check_regress_convergence(pass_state)),
        ("check_regress_convergence_fail", lambda: check_regress_convergence(fail_state)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
