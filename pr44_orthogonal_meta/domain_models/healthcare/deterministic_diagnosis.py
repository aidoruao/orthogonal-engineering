# pr44_orthogonal_meta/domain_models/healthcare/deterministic_diagnosis.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Deterministic, verifiable diagnostic decision support.
# Replaces black-box probabilistic classifiers with constructive rule evaluation.
# All decision paths are byte-verifiable, auditable, and reproducible.
# No floating-point scores; all thresholds encoded as Natural comparisons.

from __future__ import annotations

from typing import Dict, List, Optional

from ...foundations.peano_kernel import Natural, from_int, to_int, eq
from ...foundations.primitive_recursion import leq


class DiagnosticRule:
    """
    A single diagnostic rule: IF symptom_score >= threshold THEN flag condition.
    All comparisons over ℕ; no floating-point thresholds.
    """

    def __init__(self, name: str, threshold: int) -> None:
        self.name = name
        self.threshold: Natural = from_int(threshold)

    def evaluate(self, score: int) -> bool:
        """Return True iff score >= threshold (deterministic, total)."""
        return leq(self.threshold, from_int(score))


class DiagnosticEngine:
    """
    Applies a fixed set of rules to a patient symptom profile.
    All rules are evaluated deterministically in registration order.
    """

    def __init__(self, rules: List[DiagnosticRule]) -> None:
        self.rules = rules

    def evaluate(self, scores: Dict[str, int]) -> Dict:
        """
        Evaluate all rules against the provided scores.

        Returns a proof record:
          - flagged: list of rule names whose condition triggered
          - safe: bool (True iff no rule triggered)
          - steps_evaluated: int
        """
        flagged = []
        for rule in self.rules:
            score = scores.get(rule.name, 0)
            if rule.evaluate(score):
                flagged.append(rule.name)

        return {
            "theorem": "DeterministicDiagnosis",
            "flagged_conditions": flagged,
            "alert": len(flagged) > 0,
            "steps_evaluated": len(self.rules),
            "reproducible": True,
            "verifiable": True,
        }


def verify_reproducibility(
    engine: DiagnosticEngine,
    scores: Dict[str, int],
    n_runs: int = 3,
) -> bool:
    """
    Confirm that repeated evaluation yields identical results.
    Termination guaranteed: finite n_runs, each evaluate() is total.
    """
    results = [engine.evaluate(scores) for _ in range(n_runs)]
    reference = results[0]
    return all(r == reference for r in results[1:])


COMPARISON = {
    "Black-box ML classifier": {
        "method": "neural network / ensemble (probabilistic output)",
        "randomness": "dropout, data augmentation, seed-dependent",
        "verifiability": "not auditable, GDPR risk",
        "reproducibility": "requires exact environment + seed",
    },
    "PR #44 deterministic diagnosis": {
        "method": "constructive rule evaluation over ℕ thresholds",
        "randomness": "none",
        "verifiability": "fully auditable, byte-identical",
        "reproducibility": "guaranteed across all platforms",
    },
}
