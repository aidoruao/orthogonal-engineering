"""src/semiotics/engine.py -- Semiotic engine with Fraction coverage and ProofObject audit.

Part 4B of Forensic Offensive Campaign.

Maps signs to referents via interpretants, with falsifiable invariants.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject


@dataclass(frozen=True)
class Sign:
    """A sign in the semiotic triad.

    falsifies_if: signifier is empty or referent is empty.
    """
    signifier: str
    referent: str
    interpretant: str


@dataclass(frozen=True)
class SemioticState:
    """State of the semiotic engine.

    falsifies_if: coverage < Fraction(1, 1) while claiming completeness.
    """
    state_id: str
    signs: Tuple[Sign, ...]
    coverage: Fraction
    ambiguity: Fraction


def check_sign_referent_mapping(state: SemioticState) -> Tuple[bool, ProofObject]:
    """Every signifier must map to exactly one referent.

    Standard: SEM-001 unambiguous mapping.
    Falsifies if: one signifier maps to multiple distinct referents.
    falsifies_if: one signifier maps to multiple distinct referents.
    """
    mapping: Dict[str, set] = {}
    for sign in state.signs:
        mapping.setdefault(sign.signifier, set()).add(sign.referent)
    ambiguous = {s: refs for s, refs in mapping.items() if len(refs) > 1}
    if ambiguous:
        return False, ProofObject(
            rule="semiotic_unambiguous_mapping",
            premises=[f"ambiguous_signifiers={len(ambiguous)}"],
            conclusion=f"VIOLATION: {len(ambiguous)} signifier(s) map to multiple referents",
        )
    return True, ProofObject(
        rule="semiotic_unambiguous_mapping",
        premises=[f"unique_signifiers={len(mapping)}"],
        conclusion="All signifiers map to exactly one referent",
    )


def check_coverage_fraction(state: SemioticState) -> Tuple[bool, ProofObject]:
    """Semiotic coverage must be >= Fraction(3, 4).

    Standard: SEM-002 coverage threshold.
    Falsifies if: coverage < Fraction(3, 4).
    falsifies_if: coverage < Fraction(3, 4).
    """
    success = state.coverage >= Fraction(3, 4)
    proof = ProofObject(
        rule="semiotic_coverage",
        premises=[f"coverage={state.coverage}"],
        conclusion=(
            "PASS: Semiotic coverage above 3/4 threshold"
            if success else f"FAIL: Coverage {state.coverage} < 3/4"
        ),
    )
    return success, proof


def check_ambiguity_bounded(state: SemioticState) -> Tuple[bool, ProofObject]:
    """Ambiguity must be <= Fraction(1, 10).

    Standard: SEM-003 ambiguity bound.
    Falsifies if: ambiguity > Fraction(1, 10).
    falsifies_if: ambiguity > Fraction(1, 10).
    """
    success = state.ambiguity <= Fraction(1, 10)
    proof = ProofObject(
        rule="semiotic_ambiguity",
        premises=[f"ambiguity={state.ambiguity}"],
        conclusion=(
            "PASS: Ambiguity within acceptable bounds"
            if success else f"FAIL: Ambiguity {state.ambiguity} > 1/10"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all semiotic engine invariants.

    falsifies_if: any non-_fail invariant returns False.
    falsifies_if: any non-_fail invariant returns False.
    """
    pass_state = SemioticState(
        state_id="SEM001",
        signs=(
            Sign("cat", "feline", "domestic pet"),
            Sign("dog", "canine", "domestic pet"),
        ),
        coverage=Fraction(1, 1),
        ambiguity=Fraction(0),
    )
    fail_state = SemioticState(
        state_id="SEM002",
        signs=(
            Sign("bank", "river_edge", "geography"),
            Sign("bank", "financial_institution", "economics"),
        ),
        coverage=Fraction(1, 2),
        ambiguity=Fraction(1, 2),
    )

    results: dict = {}
    checks = [
        ("check_sign_referent_mapping", lambda: check_sign_referent_mapping(pass_state)),
        ("check_sign_referent_mapping_fail", lambda: check_sign_referent_mapping(fail_state)),
        ("check_coverage_fraction", lambda: check_coverage_fraction(pass_state)),
        ("check_coverage_fraction_fail", lambda: check_coverage_fraction(fail_state)),
        ("check_ambiguity_bounded", lambda: check_ambiguity_bounded(pass_state)),
        ("check_ambiguity_bounded_fail", lambda: check_ambiguity_bounded(fail_state)),
    ]
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    results = run_all_invariants()
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All semiotic engine invariants: PASS")
