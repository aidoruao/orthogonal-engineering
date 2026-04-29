"""Invariant checks for D_ARXIV_RISK_MANAGEMENT_BOWTIE.

Paper: arXiv 2604.09153v1 (cs.CR)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    BowtieModel,
    DAGTransform,
    ProbabilityCapture,
    RiskManagementClaim,
    RiskManagementEvidence,
)


# ---------------------------------------------------------------------------
# 1. Bowtie complete
# ---------------------------------------------------------------------------

def check_bowtie_complete(
    # TODO: Expand check_bowtie_complete() - stub detected by Yeshua Agent
    claim: RiskManagementClaim,
) -> Tuple[bool, ProofObject]:
    """Bowtie model must have all required components.

    Standard: arXiv 2604.09153v1 claim operationalization.
    Falsifies if: any Bowtie component is missing.
    falsifies_if: Bowtie model is incomplete.
    """
    bt = claim.bowtie
    violations = []
    if not bt.has_causes:
        violations.append("has_causes=False")
    if not bt.has_top_event:
        violations.append("has_top_event=False")
    if not bt.has_barriers:
        violations.append("has_barriers=False")
    if not bt.has_consequences:
        violations.append("has_consequences=False")

    if violations:
        return False, ProofObject(
            rule="check_bowtie_complete",
            premises=violations,
            conclusion="VIOLATION: Bowtie model is incomplete",
        )
    return True, ProofObject(
        rule="check_bowtie_complete",
        premises=[
            "has_causes=True",
            "has_top_event=True",
            "has_barriers=True",
            "has_consequences=True",
        ],
        conclusion="PASS: Bowtie model is complete",
    )


# ---------------------------------------------------------------------------
# 2. DAG valid
# ---------------------------------------------------------------------------

def check_dag_valid(
    # TODO: Expand check_dag_valid() - stub detected by Yeshua Agent
    claim: RiskManagementClaim,
) -> Tuple[bool, ProofObject]:
    """DAG transformation must be valid and support Bayesian inference.

    Standard: arXiv 2604.09153v1 claim operationalization.
    Falsifies if: DAG is not valid or does not support Bayesian inference.
    falsifies_if: DAG transformation is invalid.
    """
    dag = claim.dag
    violations = []
    if not dag.is_dag:
        violations.append("is_dag=False")
    if not dag.supports_bayesian_inference:
        violations.append("supports_bayesian_inference=False")

    if violations:
        return False, ProofObject(
            rule="check_dag_valid",
            premises=violations,
            conclusion="VIOLATION: DAG transformation is invalid",
        )
    return True, ProofObject(
        rule="check_dag_valid",
        premises=[
            "is_dag=True",
            "supports_bayesian_inference=True",
        ],
        conclusion="PASS: DAG transformation is valid",
    )


# ---------------------------------------------------------------------------
# 3. Probability capture
# ---------------------------------------------------------------------------

def check_probability_capture(
    # TODO: Expand check_probability_capture() - stub detected by Yeshua Agent
    claim: RiskManagementClaim,
) -> Tuple[bool, ProofObject]:
    """Probability capture must generate questionnaires and analyze disagreement.

    Standard: arXiv 2604.09153v1 claim operationalization.
    Falsifies if: questionnaire not generated or disagreement not analyzed.
    falsifies_if: probability capture is incomplete.
    """
    pc = claim.probability
    violations = []
    if not pc.questionnaire_generated:
        violations.append("questionnaire_generated=False")
    if not pc.expert_disagreement_analyzed:
        violations.append("expert_disagreement_analyzed=False")

    if violations:
        return False, ProofObject(
            rule="check_probability_capture",
            premises=violations,
            conclusion="VIOLATION: Probability capture is incomplete",
        )
    return True, ProofObject(
        rule="check_probability_capture",
        premises=[
            "questionnaire_generated=True",
            "expert_disagreement_analyzed=True",
        ],
        conclusion="PASS: Probability capture is complete",
    )


# ---------------------------------------------------------------------------
# 4. Safe state semantics
# ---------------------------------------------------------------------------

def check_safe_state_semantics(
    # TODO: Expand check_safe_state_semantics() - stub detected by Yeshua Agent
    claim: RiskManagementClaim,
) -> Tuple[bool, ProofObject]:
    """DAG must have explicit safe-state semantics and activation nodes.

    Standard: arXiv 2604.09153v1 claim operationalization.
    Falsifies if: safe-state semantics or activation nodes are missing.
    falsifies_if: safe-state semantics are missing.
    """
    dag = claim.dag
    violations = []
    if not dag.has_safe_state_semantics:
        violations.append("has_safe_state_semantics=False")
    if not dag.has_activation_nodes:
        violations.append("has_activation_nodes=False")

    if violations:
        return False, ProofObject(
            rule="check_safe_state_semantics",
            premises=violations,
            conclusion="VIOLATION: Safe-state semantics or activation nodes missing",
        )
    return True, ProofObject(
        rule="check_safe_state_semantics",
        premises=[
            "has_safe_state_semantics=True",
            "has_activation_nodes=True",
        ],
        conclusion="PASS: Safe-state semantics and activation nodes present",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_RISK_MANAGEMENT_BOWTIE invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    bowtie = BowtieModel(
        model_name="instant_payments",
        has_causes=True,
        has_top_event=True,
        has_barriers=True,
        has_consequences=True,
    )
    dag = DAGTransform(
        is_dag=True,
        has_safe_state_semantics=True,
        has_activation_nodes=True,
        supports_bayesian_inference=True,
    )
    prob = ProbabilityCapture(
        questionnaire_generated=True,
        expert_disagreement_analyzed=True,
        uses_prior_regularization=True,
    )
    claim_safe = RiskManagementClaim(
        bowtie=bowtie,
        dag=dag,
        probability=prob,
    )

    # FAIL case: incomplete Bowtie
    bowtie_incomplete = BowtieModel(
        model_name="incomplete",
        has_causes=True,
        has_top_event=False,
        has_barriers=True,
        has_consequences=True,
    )
    claim_bad_bowtie = RiskManagementClaim(
        bowtie=bowtie_incomplete,
        dag=dag,
        probability=prob,
    )

    # FAIL case: invalid DAG
    dag_invalid = DAGTransform(
        is_dag=False,
        has_safe_state_semantics=True,
        has_activation_nodes=True,
        supports_bayesian_inference=False,
    )
    claim_bad_dag = RiskManagementClaim(
        bowtie=bowtie,
        dag=dag_invalid,
        probability=prob,
    )

    # FAIL case: no probability capture
    prob_missing = ProbabilityCapture(
        questionnaire_generated=False,
        expert_disagreement_analyzed=False,
        uses_prior_regularization=False,
    )
    claim_bad_prob = RiskManagementClaim(
        bowtie=bowtie,
        dag=dag,
        probability=prob_missing,
    )

    checks = [
        ("check_bowtie_complete_pass", lambda: check_bowtie_complete(claim_safe)),
        ("check_dag_valid_pass", lambda: check_dag_valid(claim_safe)),
        ("check_probability_capture_pass", lambda: check_probability_capture(claim_safe)),
        ("check_safe_state_semantics_pass", lambda: check_safe_state_semantics(claim_safe)),
        ("check_bowtie_complete_fail", lambda: check_bowtie_complete(claim_bad_bowtie)),
        ("check_dag_valid_fail", lambda: check_dag_valid(claim_bad_dag)),
        ("check_probability_capture_fail", lambda: check_probability_capture(claim_bad_prob)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    unexpected = [
        k for k, v in results.items()
        if k.endswith("_fail") and not v.startswith("FAIL")
    ]
    failures.extend(unexpected)
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARXIV_RISK_MANAGEMENT_BOWTIE invariants: PASS")
