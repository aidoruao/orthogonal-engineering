"""
Falsification test: Actuarial risk model is deterministic.
Same inputs produce same risk score.

# @falsification_id: F-INSURANCE-001
"""
import hashlib
import pytest

def compute_risk_score(age: int, claim_history: int, credit_score: int) -> float:
    base = (claim_history * 0.4 + (100 - credit_score/10) * 0.3 + max(0, age-30) * 0.01)
    return round(base, 6)

INPUTS = (45, 2, 750)

def test_risk_score_deterministic():
    scores = [compute_risk_score(*INPUTS) for _ in range(100)]
    assert len(set(scores)) == 1, "Risk model produced different scores for identical inputs"
