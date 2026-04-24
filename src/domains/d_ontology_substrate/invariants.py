"""D_ONTOLOGY_SUBSTRATE invariants — Precedents, Lawvere, operational necessities.

Phase B2 of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import OntologicalState


def check_all_precedents_satisfied(state: OntologicalState) -> Tuple[bool, ProofObject]:
    """All ontological precedents must be satisfied.

    Falsifies if: precedent_ratio < Fraction(1, 1).
    falsifies_if: precedent_ratio < Fraction(1, 1).
    """
    if state.precedent_ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Precedent ratio {state.precedent_ratio} < 1 — "
                f"{state.precedent_count}/{state.total_precedents} satisfied"
            ),
            premises=[
                f"Satisfied: {state.precedent_count}",
                f"Total: {state.total_precedents}",
            ],
            rule="ontology_all_precedents",
        )
    return True, ProofObject(
        conclusion=f"All {state.total_precedents} precedents satisfied",
        premises=[f"Ratio: {state.precedent_ratio}"],
        rule="ontology_all_precedents",
    )


def check_consistent_reality(state: OntologicalState) -> Tuple[bool, ProofObject]:
    """Reality must be consistent for correspondence validation (Precedent 1).

    Falsifies if: reality_consistent == False.
    falsifies_if: reality_consistent == False.
    """
    if not state.reality_consistent:
        return False, ProofObject(
            conclusion="VIOLATION: Reality inconsistent",
            premises=["reality_consistent: False"],
            rule="ontology_consistent_reality",
        )
    return True, ProofObject(
        conclusion="Reality consistent",
        premises=["reality_consistent: True"],
        rule="ontology_consistent_reality",
    )


def check_structural_order(state: OntologicalState) -> Tuple[bool, ProofObject]:
    """Structural order must be present for pattern detection (Precedent 2).

    Falsifies if: structural_order_present == False.
    falsifies_if: structural_order_present == False.
    """
    if not state.structural_order_present:
        return False, ProofObject(
            conclusion="VIOLATION: Structural order absent",
            premises=["structural_order_present: False"],
            rule="ontology_structural_order",
        )
    return True, ProofObject(
        conclusion="Structural order present",
        premises=["structural_order_present: True"],
        rule="ontology_structural_order",
    )


def check_deterministic_causality(state: OntologicalState) -> Tuple[bool, ProofObject]:
    """Deterministic causality must hold for extraction proofs (Precedent 3).

    Falsifies if: deterministic_causality == False.
    falsifies_if: deterministic_causality == False.
    """
    if not state.deterministic_causality:
        return False, ProofObject(
            conclusion="VIOLATION: Causality non-deterministic",
            premises=["deterministic_causality: False"],
            rule="ontology_deterministic_causality",
        )
    return True, ProofObject(
        conclusion="Deterministic causality holds",
        premises=["deterministic_causality: True"],
        rule="ontology_deterministic_causality",
    )


def check_lawvere_convergence(state: OntologicalState) -> Tuple[bool, ProofObject]:
    """G5 grounding requires Lawvere fixed point existence.

    Falsifies if: grounding_model == "G5" and lawvere_fixed_point_exists == False.
    falsifies_if: grounding_model == "G5" and lawvere_fixed_point_exists == False.
    """
    if state.grounding_model == "G5" and not state.lawvere_fixed_point_exists:
        return False, ProofObject(
            conclusion="VIOLATION: G5 grounding lacks Lawvere fixed point",
            premises=[
                f"Model: {state.grounding_model}",
                "lawvere_fixed_point_exists: False",
            ],
            rule="ontology_lawvere_convergence",
        )
    return True, ProofObject(
        conclusion=f"Grounding {state.grounding_model} converges",
        premises=[f"Model: {state.grounding_model}"],
        rule="ontology_lawvere_convergence",
    )


def check_operational_necessities(state: OntologicalState) -> Tuple[bool, ProofObject]:
    """Code execution and hashing must both work (NECESSITY_INVENTORY.md Section D).

    Falsifies if: not (code_executes_predictably and hashing_works).
    falsifies_if: code_executes_predictably == False or hashing_works == False.
    """
    if not (state.code_executes_predictably and state.hashing_works):
        return False, ProofObject(
            conclusion=(
                "VIOLATION: Operational necessity failed — "
                f"code_executes_predictably={state.code_executes_predictably}, "
                f"hashing_works={state.hashing_works}"
            ),
            premises=[
                f"code_executes_predictably: {state.code_executes_predictably}",
                f"hashing_works: {state.hashing_works}",
            ],
            rule="ontology_operational_necessities",
        )
    return True, ProofObject(
        conclusion="Operational necessities satisfied",
        premises=[
            f"code_executes_predictably: {state.code_executes_predictably}",
            f"hashing_works: {state.hashing_works}",
        ],
        rule="ontology_operational_necessities",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------



def check_ontological_coverage_fraction(data: OntologicalState) -> Tuple[bool, ProofObject]:
    """Fraction of ontological categories that have corresponding invariants must be >= 3/4.

    Standard: ONTOLOGY-006 coverage.
    Falsifies if: coverage_ratio < Fraction(3, 4).
    falsifies_if: coverage_ratio < Fraction(3, 4).
    """
    if data.total_categories == 0:
        return False, ProofObject(
            rule="ontology_coverage_fraction",
            premises=["total_categories=0"],
            conclusion="FAIL: No ontological categories to measure coverage",
        )
    coverage = Fraction(data.covered_categories, data.total_categories)
    success = coverage >= Fraction(3, 4)
    proof = ProofObject(
        rule="ontology_coverage_fraction",
        premises=[
            f"covered={data.covered_categories}",
            f"total={data.total_categories}",
            f"coverage={coverage}",
        ],
        conclusion=(
            "PASS: Ontological coverage above 3/4 threshold"
            if success else f"FAIL: Coverage {coverage} < 3/4"
        ),
    )
    return success, proof

def run_all_invariants() -> dict:
    """Run all ontological substrate checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_state = OntologicalState(
        reality_consistent=True,
        structural_order_present=True,
        deterministic_causality=True,
        truth_anchorable=True,
        knowledge_possible=True,
        patterns_detectable=True,
        code_executes_predictably=True,
        hashing_works=True,
        precedent_count=10,
        total_precedents=10,
        precedent_ratio=Fraction(1, 1),
        grounding_model="G5",
        lawvere_fixed_point_exists=True,
        covered_categories=4,
        total_categories=4,
    )
    fail_state = OntologicalState(
        reality_consistent=False,
        structural_order_present=False,
        deterministic_causality=False,
        truth_anchorable=True,
        knowledge_possible=True,
        patterns_detectable=True,
        code_executes_predictably=False,
        hashing_works=True,
        precedent_count=8,
        total_precedents=10,
        precedent_ratio=Fraction(4, 5),
        grounding_model="G5",
        lawvere_fixed_point_exists=False,
        covered_categories=2,
        total_categories=4,
    )

    checks = [
        ("check_all_precedents_satisfied_pass", lambda: check_all_precedents_satisfied(pass_state)),
        ("check_all_precedents_satisfied_fail", lambda: check_all_precedents_satisfied(fail_state)),
        ("check_consistent_reality_pass", lambda: check_consistent_reality(pass_state)),
        ("check_consistent_reality_fail", lambda: check_consistent_reality(fail_state)),
        ("check_structural_order_pass", lambda: check_structural_order(pass_state)),
        ("check_structural_order_fail", lambda: check_structural_order(fail_state)),
        ("check_deterministic_causality_pass", lambda: check_deterministic_causality(pass_state)),
        ("check_deterministic_causality_fail", lambda: check_deterministic_causality(fail_state)),
        ("check_lawvere_convergence_pass", lambda: check_lawvere_convergence(pass_state)),
        ("check_lawvere_convergence_fail", lambda: check_lawvere_convergence(fail_state)),
        ("check_operational_necessities_pass", lambda: check_operational_necessities(pass_state)),
        ("check_operational_necessities_fail", lambda: check_operational_necessities(fail_state)),
        ("check_ontological_coverage_fraction_pass", lambda: check_ontological_coverage_fraction(pass_state)),
        ("check_ontological_coverage_fraction_fail", lambda: check_ontological_coverage_fraction(fail_state)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            ok, proof = func()
            results[name] = "PASS" if ok else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
