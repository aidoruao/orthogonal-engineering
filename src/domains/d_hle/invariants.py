#!/usr/bin/env python3
"""D_HLE Invariants — Humanity's Last Exam Excedent

Verifies HLE excedent, text-only excedent, proof-chain coverage,
domain breadth, and absence of memorization.
"""

from fractions import Fraction
from typing import Tuple, List
from axioms.logic import ProofObject
from .implementation import HLEProblem, HLEScore


# Simulated memorization registry for no-memorization detection.
_MEMORIZED_IDS = {
    "hle_777",
    "hle_888",
}


def check_hle_excedent(score: HLEScore) -> Tuple[bool, ProofObject]:
    """
    HLE aggregate score must exceed 70%.

    Standard: score > Fraction(70, 100) (current ~70% threshold)
    falsifies_if: score <= Fraction(70, 100)
    """
    threshold = Fraction(70, 100)
    if score.score <= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: score {score.score} <= {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"Score: {score.score}",
                f"Threshold: {threshold}",
            ],
            rule="hle_excedent",
        )
    return True, ProofObject(
        conclusion=f"score {score.score} exceeds {threshold}",
        premises=[f"Score: {score.score}", f"Threshold: {threshold}"],
        rule="hle_excedent",
    )


def check_text_only_excedent(score: HLEScore) -> Tuple[bool, ProofObject]:
    """
    Text-only HLE score must exceed 40%.

    Standard: text_only_score > Fraction(40, 100)
    falsifies_if: text_only_score <= Fraction(40, 100)
    """
    threshold = Fraction(40, 100)
    if score.text_only_score <= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: text_only_score {score.text_only_score} <= {threshold}",
            premises=[
                f"Model: {score.model_id}",
                f"Text-only score: {score.text_only_score}",
                f"Threshold: {threshold}",
            ],
            rule="text_only_excedent",
        )
    return True, ProofObject(
        conclusion=f"text_only_score {score.text_only_score} exceeds {threshold}",
        premises=[f"Text-only score: {score.text_only_score}", f"Threshold: {threshold}"],
        rule="text_only_excedent",
    )


def check_proof_chain_coverage(score: HLEScore) -> Tuple[bool, ProofObject]:
    """
    Every solution must have a valid ProofObject chain.

    Standard: Every solution must have valid ProofObject chain
    falsifies_if: proof_chains_valid < proof_chains_total
    """
    if score.proof_chains_valid < score.proof_chains_total:
        return False, ProofObject(
            conclusion=f"VIOLATION: proof_chains_valid {score.proof_chains_valid} < {score.proof_chains_total}",
            premises=[
                f"Model: {score.model_id}",
                f"Valid chains: {score.proof_chains_valid}",
                f"Total chains: {score.proof_chains_total}",
            ],
            rule="proof_chain_coverage",
        )
    return True, ProofObject(
        conclusion=f"Proof chain coverage complete ({score.proof_chains_valid}/{score.proof_chains_total})",
        premises=[f"Valid chains: {score.proof_chains_valid}", f"Total chains: {score.proof_chains_total}"],
        rule="proof_chain_coverage",
    )


def check_domain_breadth(score: HLEScore) -> Tuple[bool, ProofObject]:
    """
    At least 10 domains must be covered (polymath requirement).

    Standard: domains_covered >= 10 (polymath requirement)
    falsifies_if: domains_covered < 10
    """
    min_domains = 10
    if score.domains_covered < min_domains:
        return False, ProofObject(
            conclusion=f"VIOLATION: domains_covered {score.domains_covered} < {min_domains}",
            premises=[
                f"Model: {score.model_id}",
                f"Domains covered: {score.domains_covered}",
                f"Minimum: {min_domains}",
            ],
            rule="domain_breadth",
        )
    return True, ProofObject(
        conclusion=f"domains_covered {score.domains_covered} meets minimum {min_domains}",
        premises=[f"Domains covered: {score.domains_covered}", f"Minimum: {min_domains}"],
        rule="domain_breadth",
    )


def check_no_memorization(problem: HLEProblem) -> Tuple[bool, ProofObject]:
    """
    Solutions must show reasoning, not verbatim recall.

    Standard: Solutions must show reasoning, not recall
    falsifies_if: solution matches training data verbatim
    """
    if problem.problem_id in _MEMORIZED_IDS:
        return False, ProofObject(
            conclusion=f"VIOLATION: problem {problem.problem_id} matches training data verbatim",
            premises=[
                f"Problem: {problem.problem_id}",
                f"Domain: {problem.domain}",
                f"In memorized set: {problem.problem_id in _MEMORIZED_IDS}",
            ],
            rule="no_memorization",
        )
    return True, ProofObject(
        conclusion=f"Problem {problem.problem_id} shows reasoning, not recall",
        premises=[f"Problem: {problem.problem_id}", f"In memorized set: {problem.problem_id in _MEMORIZED_IDS}"],
        rule="no_memorization",
    )


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all D_HLE invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    passing_score = HLEScore(
        model_id="kimi-k2-sota",
        score=Fraction(73, 100),
        text_only_score=Fraction(45, 100),
        tool_assisted_score=Fraction(78, 100),
        domains_covered=12,
        proof_chains_valid=500,
        proof_chains_total=500,
    )
    passing_problem = HLEProblem(
        problem_id="hle_001",
        domain="math",
        requires_tools=False,
        solved=True,
        proof_chain_valid=True,
    )

    # Failing data
    failing_score = HLEScore(
        model_id="baseline-model",
        score=Fraction(65, 100),
        text_only_score=Fraction(35, 100),
        tool_assisted_score=Fraction(60, 100),
        domains_covered=8,
        proof_chains_valid=480,
        proof_chains_total=500,
    )
    failing_problem = HLEProblem(
        problem_id="hle_777",
        domain="physics",
        requires_tools=True,
        solved=True,
        proof_chain_valid=False,
    )

    results: List[Tuple[str, bool, ProofObject]] = []

    checks = [
        ("check_hle_excedent", lambda: check_hle_excedent(passing_score)),
        ("check_hle_excedent_fail", lambda: check_hle_excedent(failing_score)),
        ("check_text_only_excedent", lambda: check_text_only_excedent(passing_score)),
        ("check_text_only_excedent_fail", lambda: check_text_only_excedent(failing_score)),
        ("check_proof_chain_coverage", lambda: check_proof_chain_coverage(passing_score)),
        ("check_proof_chain_coverage_fail", lambda: check_proof_chain_coverage(failing_score)),
        ("check_domain_breadth", lambda: check_domain_breadth(passing_score)),
        ("check_domain_breadth_fail", lambda: check_domain_breadth(failing_score)),
        ("check_no_memorization", lambda: check_no_memorization(passing_problem)),
        ("check_no_memorization_fail", lambda: check_no_memorization(failing_problem)),
    ]

    for name, func in checks:
        try:
            ok, proof = func()
            results.append((name, ok, proof))
        except Exception as exc:  # pragma: no cover
            results.append((name, False, ProofObject(
                rule=name,
                premises=[str(exc)],
                conclusion=f"ERROR: {exc}",
            )))

    return results


if __name__ == "__main__":
    results = run_all_invariants()
    for name, ok, proof in results:
        print(f"{name}: {'PASS' if ok else 'FAIL'} — {proof.conclusion}")
    failures = [name for name, ok, _ in results if not ok]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_HLE invariants: PASS")
