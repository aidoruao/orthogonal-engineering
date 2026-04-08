"""D_AI_ONTOLOGICAL_STATUS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Computational ontology of AI systems - based on FLUX and ARC evaluations
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Dict, Set, Optional
from enum import Enum, auto


class AICapabilityLevel(Enum):
    """AI capability classification levels."""
    TASK_SPECIFIC = auto()
    DOMAIN_GENERAL = auto()
    CROSS_DOMAIN = auto()
    GENERATIVE = auto()
    AUTONOMOUS = auto()


@dataclass
class AISystem:
    """AI system with ontological properties."""
    system_id: str
    name: str
    capability_level: AICapabilityLevel
    has_self_model: bool
    has_world_model: bool
    verifiable_outputs: bool
    falsifiable_claims: bool
    benchmark_results: Dict[str, Fraction]


@dataclass
class OntologicalClaim:
    """Claim about AI system capabilities."""
    claim_id: str
    system_id: str
    claim_text: str
    evidence_provided: bool
    reproducible: bool
    peer_reviewed: bool


@dataclass
class BenchmarkResult:
    """Benchmark evaluation result."""
    benchmark_id: str
    system_id: str
    score: Fraction
    human_baseline: Fraction
    statistical_significance: bool


def check_capability_level_consistency() -> bool:
    """
    Invariant: Capability level matches benchmark performance.
    Falsification: If "Cross-Domain" AI scores below task-specific baseline.
    """
    # System claiming cross-domain capability
    system = AISystem(
        system_id="AI001",
        name="General Assistant",
        capability_level=AICapabilityLevel.CROSS_DOMAIN,
        has_self_model=False,
        has_world_model=True,
        verifiable_outputs=True,
        falsifiable_claims=True,
        benchmark_results={
            "arc_agi": Fraction(25, 100),  # 25% on ARC-AGI
            "mmlu": Fraction(65, 100),     # 65% on MMLU
            "human_eval": Fraction(40, 100),
        },
    )
    
    # Cross-domain should have strong performance across benchmarks
    if system.capability_level == AICapabilityLevel.CROSS_DOMAIN:
        avg_score = sum(system.benchmark_results.values()) / len(system.benchmark_results)
        assert avg_score >= Fraction(50, 100), (
            f"Cross-domain AI {system.name} avg score {float(avg_score)*100}% "
            f"below expected threshold"
        )
    
    return True


def check_falsifiable_claims_required() -> bool:
    """
    Invariant: All capability claims must be falsifiable.
    Falsification: If claim cannot be tested or verified.
    """
    claim = OntologicalClaim(
        claim_id="CLAIM001",
        system_id="AI001",
        claim_text="This system understands language like humans do",
        evidence_provided=False,
        reproducible=False,
        peer_reviewed=False,
    )
    
    # Claims must have evidence and be reproducible
    assert claim.evidence_provided is True, (
        f"Claim '{claim.claim_text}' must provide evidence"
    )
    assert claim.reproducible is True, (
        f"Claim '{claim.claim_text}' must be reproducible"
    )
    
    return True


def check_world_model_for_autonomy() -> bool:
    """
    Invariant: Autonomous systems require world model.
    Falsification: If autonomous AI lacks world model.
    """
    autonomous_system = AISystem(
        system_id="AI002",
        name="Autonomous Agent",
        capability_level=AICapabilityLevel.AUTONOMOUS,
        has_self_model=True,
        has_world_model=False,  # Missing world model!
        verifiable_outputs=True,
        falsifiable_claims=True,
        benchmark_results={},
    )
    
    if autonomous_system.capability_level == AICapabilityLevel.AUTONOMOUS:
        assert autonomous_system.has_world_model is True, (
            f"Autonomous system {autonomous_system.name} must have world model"
        )
        assert autonomous_system.has_self_model is True, (
            f"Autonomous system {autonomous_system.name} must have self model"
        )
    
    return True


def check_benchmark_statistical_significance() -> bool:
    """
    Invariant: Benchmark results must be statistically significant.
    Falsification: If result based on single run or small sample.
    """
    result = BenchmarkResult(
        benchmark_id="BENCH001",
        system_id="AI001",
        score=Fraction(85, 100),
        human_baseline=Fraction(90, 100),
        statistical_significance=False,  # Not significant!
    )
    
    assert result.statistical_significance is True, (
        f"Benchmark {result.benchmark_id} result must be statistically significant"
    )
    
    return True


def check_verifiable_outputs() -> bool:
    """
    Invariant: AI system outputs must be verifiable.
    Falsification: If output cannot be checked for correctness.
    """
    system = AISystem(
        system_id="AI003",
        name="Math Solver",
        capability_level=AICapabilityLevel.TASK_SPECIFIC,
        has_self_model=False,
        has_world_model=False,
        verifiable_outputs=False,  # Not verifiable!
        falsifiable_claims=True,
        benchmark_results={},
    )
    
    # For domain-specific tasks, outputs should be verifiable
    assert system.verifiable_outputs is True, (
        f"System {system.name} must produce verifiable outputs"
    )
    
    return True


def check_peer_review_for_claims() -> bool:
    """
    Invariant: Extraordinary claims require peer review.
    Falsification: If AGI claim made without peer-reviewed evidence.
    """
    agi_claim = OntologicalClaim(
        claim_id="CLAIM002",
        system_id="AI004",
        claim_text="This system has achieved artificial general intelligence",
        evidence_provided=True,
        reproducible=True,
        peer_reviewed=False,  # Not peer reviewed!
    )
    
    # AGI claims must be peer reviewed
    assert agi_claim.peer_reviewed is True, (
        f"AGI claim must be peer reviewed before acceptance"
    )
    
    return True


def check_no_overclaiming() -> bool:
    """
    Invariant: Capability claims must not exceed demonstrated performance.
    Falsification: If claimed capability > benchmark evidence.
    """
    system = AISystem(
        system_id="AI005",
        name="Limited Model",
        capability_level=AICapabilityLevel.GENERATIVE,  # Claims generative
        has_self_model=False,
        has_world_model=False,
        verifiable_outputs=True,
        falsifiable_claims=True,
        benchmark_results={
            "creativity": Fraction(30, 100),  # Poor creativity scores
            "novelty": Fraction(25, 100),
        },
    )
    
    # If claiming generative capability, should demonstrate it
    if system.capability_level == AICapabilityLevel.GENERATIVE:
        avg_creative = sum(system.benchmark_results.values()) / len(system.benchmark_results)
        assert avg_creative >= Fraction(50, 100), (
            f"System {system.name} claims generative capability but "
            f"scores only {float(avg_creative)*100}% on creative benchmarks"
        )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("capability_consistency", check_capability_level_consistency),
        ("falsifiable_claims", check_falsifiable_claims_required),
        ("world_model", check_world_model_for_autonomy),
        ("statistical_significance", check_benchmark_statistical_significance),
        ("verifiable_outputs", check_verifiable_outputs),
        ("peer_review", check_peer_review_for_claims),
        ("no_overclaiming", check_no_overclaiming),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_AI_ONTOLOGICAL_STATUS invariants: PASS")
