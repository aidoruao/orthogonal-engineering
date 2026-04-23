"""D_HLE implementation — Humanity's Last Exam Excedent

Layer: 3 (Regulatory/Research)
CardinalStrength: PREDICATIVE

Humanity's Last Exam evaluation, proof-chain validity, domain breadth.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class HLEProblem:
    """Single HLE problem evaluation."""
    problem_id: str
    domain: str                        # math, physics, philosophy, etc.
    requires_tools: bool
    solved: bool
    proof_chain_valid: bool


@dataclass(frozen=True)
class HLEScore:
    """Aggregate HLE score for a model."""
    model_id: str
    score: Fraction
    text_only_score: Fraction
    tool_assisted_score: Fraction
    domains_covered: int
    proof_chains_valid: int
    proof_chains_total: int
