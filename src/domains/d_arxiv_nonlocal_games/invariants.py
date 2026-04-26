"""Invariant checks for D_ARXIV_NONLOCAL_GAMES.

Paper: arXiv 2604.09458v1 (quant-ph)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    GameConfig,
    Strategy,
    NonlocalGameClaim,
    NonlocalGameEvidence,
)


# ---------------------------------------------------------------------------
# 1. Quantum beats classical
# ---------------------------------------------------------------------------

def check_quantum_beats_classical(
    claim: NonlocalGameClaim,
) -> Tuple[bool, ProofObject]:
    """Quantum strategy must outperform classical bound.

    Standard: arXiv 2604.09458v1 claim operationalization.
    Falsifies if: strategy is quantum but winning_probability <= classical_bound.
    falsifies_if: quantum strategy does not beat classical bound.
    """
    s = claim.strategy
    if s.strategy_type == "quantum" and s.winning_probability <= claim.classical_bound:
        return False, ProofObject(
            rule="check_quantum_beats_classical",
            premises=[
                f"strategy_type={s.strategy_type}",
                f"winning_probability={s.winning_probability}",
                f"classical_bound={claim.classical_bound}",
            ],
            conclusion="VIOLATION: Quantum strategy does not beat classical bound",
        )
    return True, ProofObject(
        rule="check_quantum_beats_classical",
        premises=[
            f"strategy_type={s.strategy_type}",
            f"winning_probability={s.winning_probability}",
            f"classical_bound={claim.classical_bound}",
        ],
        conclusion="PASS: Quantum strategy beats classical bound",
    )


# ---------------------------------------------------------------------------
# 2. No-signaling upper bound
# ---------------------------------------------------------------------------

def check_no_signaling_upper_bound(
    claim: NonlocalGameClaim,
) -> Tuple[bool, ProofObject]:
    """Winning probability must not exceed no-signaling bound.

    Standard: arXiv 2604.09458v1 claim operationalization.
    Falsifies if: winning_probability > no_signaling_bound.
    falsifies_if: winning probability exceeds no-signaling bound.
    """
    if claim.strategy.winning_probability > claim.no_signaling_bound:
        return False, ProofObject(
            rule="check_no_signaling_upper_bound",
            premises=[
                f"winning_probability={claim.strategy.winning_probability}",
                f"no_signaling_bound={claim.no_signaling_bound}",
            ],
            conclusion="VIOLATION: Winning probability exceeds no-signaling bound",
        )
    return True, ProofObject(
        rule="check_no_signaling_upper_bound",
        premises=[
            f"winning_probability={claim.strategy.winning_probability}",
            f"no_signaling_bound={claim.no_signaling_bound}",
        ],
        conclusion="PASS: Winning probability within no-signaling bound",
    )


# ---------------------------------------------------------------------------
# 3. Entanglement required
# ---------------------------------------------------------------------------

def check_entanglement_required(
    claim: NonlocalGameClaim,
) -> Tuple[bool, ProofObject]:
    """Quantum strategy must use entanglement.

    Standard: arXiv 2604.09458v1 claim operationalization.
    Falsifies if: strategy_type is quantum but uses_entanglement is False.
    falsifies_if: quantum strategy does not use entanglement.
    """
    s = claim.strategy
    if s.strategy_type == "quantum" and not s.uses_entanglement:
        return False, ProofObject(
            rule="check_entanglement_required",
            premises=[
                f"strategy_type={s.strategy_type}",
                f"uses_entanglement={s.uses_entanglement}",
            ],
            conclusion="VIOLATION: Quantum strategy does not use entanglement",
        )
    return True, ProofObject(
        rule="check_entanglement_required",
        premises=[
            f"strategy_type={s.strategy_type}",
            f"uses_entanglement={s.uses_entanglement}",
        ],
        conclusion="PASS: Quantum strategy uses entanglement",
    )


# ---------------------------------------------------------------------------
# 4. Winning probability bounded
# ---------------------------------------------------------------------------

def check_winning_probability_bounded(
    claim: NonlocalGameClaim,
) -> Tuple[bool, ProofObject]:
    """Winning probability must be in [0, 1].

    Standard: arXiv 2604.09458v1 claim operationalization.
    Falsifies if: winning_probability < 0 or > 1.
    falsifies_if: winning probability outside [0, 1].
    """
    p = claim.strategy.winning_probability
    if p < Fraction(0) or p > Fraction(1):
        return False, ProofObject(
            rule="check_winning_probability_bounded",
            premises=[f"winning_probability={p}"],
            conclusion="VIOLATION: Winning probability outside [0, 1]",
        )
    return True, ProofObject(
        rule="check_winning_probability_bounded",
        premises=[f"winning_probability={p}"],
        conclusion="PASS: Winning probability within [0, 1]",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_NONLOCAL_GAMES invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    game = GameConfig(
        game_name="chsh",
        player_count=2,
        question_count=2,
        answer_count=2,
    )
    strategy_quantum = Strategy(
        strategy_type="quantum",
        uses_entanglement=True,
        winning_probability=Fraction(85, 100),  # ~cos²(π/8)
    )
    claim_safe = NonlocalGameClaim(
        game=game,
        strategy=strategy_quantum,
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )

    # FAIL case: quantum does not beat classical
    strategy_weak = Strategy(
        strategy_type="quantum",
        uses_entanglement=True,
        winning_probability=Fraction(7, 10),
    )
    claim_weak = NonlocalGameClaim(
        game=game,
        strategy=strategy_weak,
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )

    # FAIL case: exceeds no-signaling
    strategy_cheating = Strategy(
        strategy_type="quantum",
        uses_entanglement=True,
        winning_probability=Fraction(11, 10),
    )
    claim_cheating = NonlocalGameClaim(
        game=game,
        strategy=strategy_cheating,
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )

    # FAIL case: no entanglement
    strategy_no_ent = Strategy(
        strategy_type="quantum",
        uses_entanglement=False,
        winning_probability=Fraction(85, 100),
    )
    claim_no_ent = NonlocalGameClaim(
        game=game,
        strategy=strategy_no_ent,
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )

    checks = [
        ("check_quantum_beats_classical_pass", lambda: check_quantum_beats_classical(claim_safe)),
        ("check_no_signaling_upper_bound_pass", lambda: check_no_signaling_upper_bound(claim_safe)),
        ("check_entanglement_required_pass", lambda: check_entanglement_required(claim_safe)),
        ("check_winning_probability_bounded_pass", lambda: check_winning_probability_bounded(claim_safe)),
        ("check_quantum_beats_classical_fail", lambda: check_quantum_beats_classical(claim_weak)),
        ("check_no_signaling_upper_bound_fail", lambda: check_no_signaling_upper_bound(claim_cheating)),
        ("check_entanglement_required_fail", lambda: check_entanglement_required(claim_no_ent)),
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
    print("All D_ARXIV_NONLOCAL_GAMES invariants: PASS")
