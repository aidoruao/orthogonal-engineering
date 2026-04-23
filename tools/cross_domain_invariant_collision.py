"""tools/cross_domain_invariant_collision.py — Cross-domain invariant collision detector.

Phase 6 of Depositive Campaign.

Scans src/domains/*/invariants.py for check_* functions, extracts metadata
from docstrings, and detects collisions: shared mathematical roots across
domains that create propagation risk.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import List, Optional, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class InvariantMetadata:
    """Extracted metadata for a single check_* function."""
    domain: str
    check_name: str
    standard: str
    falsifies_if: str


@dataclass(frozen=True)
class InvariantCollision:
    """Detected collision between two invariants."""
    domain_a: str
    check_a: str
    domain_b: str
    check_b: str
    shared_root: str
    collision_type: str
    propagation_risk: Fraction


def _extract_docstring_meta(docstring: Optional[str]) -> Tuple[str, str]:
    """Extract Standard and falsifies_if from docstring."""
    if not docstring:
        return "", ""
    standard_match = re.search(r"Standard:\s*([^\n]+)", docstring, re.IGNORECASE)
    standard = standard_match.group(1).strip() if standard_match else ""
    falsifies_match = re.search(r"falsifies_if:\s*([^\n]+)", docstring, re.IGNORECASE)
    falsifies_if = falsifies_match.group(1).strip() if falsifies_match else ""
    return standard, falsifies_if


def scan_domain_invariants(domain_path: Path) -> List[InvariantMetadata]:
    """Parse a single domain's invariants.py and extract check_* metadata."""
    invariants_file = domain_path / "invariants.py"
    if not invariants_file.exists():
        return []

    try:
        tree = ast.parse(invariants_file.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    results: List[InvariantMetadata] = []
    domain_name = domain_path.name

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):
            docstring = ast.get_docstring(node)
            standard, falsifies_if = _extract_docstring_meta(docstring)
            results.append(InvariantMetadata(
                domain=domain_name,
                check_name=node.name,
                standard=standard,
                falsifies_if=falsifies_if,
            ))

    return results


def scan_all_domains(root: Path = Path("src/domains")) -> List[InvariantMetadata]:
    """Scan all domains under src/domains/ for invariants."""
    all_invariants: List[InvariantMetadata] = []
    if not root.exists():
        return all_invariants
    for domain_dir in sorted(root.iterdir()):
        if domain_dir.is_dir():
            all_invariants.extend(scan_domain_invariants(domain_dir))
    return all_invariants


def detect_collisions(invariants: List[InvariantMetadata]) -> List[InvariantCollision]:
    """Detect collisions between invariants sharing mathematical roots."""
    collisions: List[InvariantCollision] = []
    n = len(invariants)

    for i in range(n):
        for j in range(i + 1, n):
            a = invariants[i]
            b = invariants[j]

            if a.domain == b.domain:
                continue

            shared_root = ""
            collision_type = ""
            risk = Fraction(0, 1)

            # Standard collision
            if a.standard and b.standard and a.standard == b.standard:
                shared_root = a.standard
                collision_type = "standard"
                risk = Fraction(3, 4)

            # Pattern collision: same falsifies_if structure
            elif a.falsifies_if and b.falsifies_if:
                a_patterns = _extract_patterns(a.falsifies_if)
                b_patterns = _extract_patterns(b.falsifies_if)
                common = a_patterns & b_patterns
                if common:
                    shared_root = sorted(common)[0]
                    collision_type = "pattern"
                    risk = Fraction(1, 2)

            if shared_root:
                collisions.append(InvariantCollision(
                    domain_a=a.domain,
                    check_a=a.check_name,
                    domain_b=b.domain,
                    check_b=b.check_name,
                    shared_root=shared_root,
                    collision_type=collision_type,
                    propagation_risk=risk,
                ))

    return collisions


def _extract_patterns(falsifies_if: str) -> set:
    """Extract inequality patterns from falsifies_if text."""
    patterns = set()
    if ">" in falsifies_if:
        patterns.add("greater_than")
    if "<" in falsifies_if:
        patterns.add("less_than")
    if "!=" in falsifies_if:
        patterns.add("not_equal")
    if "==" in falsifies_if or "== False" in falsifies_if or "== True" in falsifies_if:
        patterns.add("equality")
    if "outside" in falsifies_if.lower():
        patterns.add("bounded_interval")
    if "monotonic" in falsifies_if.lower():
        patterns.add("monotonicity")
    if "bayes" in falsifies_if.lower():
        patterns.add("bayesian")
    return patterns


def demonstrate_propagation(collision: InvariantCollision) -> ProofObject:
    """Produce a ProofObject showing propagation risk for a collision."""
    return ProofObject(
        conclusion=(
            f"If {collision.domain_a}/{collision.check_a} changes, "
            f"{collision.domain_b}/{collision.check_b} must be reviewed "
            f"because both depend on {collision.shared_root}"
        ),
        premises=[
            f"Domain A: {collision.domain_a}",
            f"Check A: {collision.check_a}",
            f"Domain B: {collision.domain_b}",
            f"Check B: {collision.check_b}",
            f"Shared root: {collision.shared_root}",
            f"Collision type: {collision.collision_type}",
            f"Risk: {collision.propagation_risk}",
        ],
        rule="cross_domain_collision_propagation",
    )


def main() -> int:
    """CLI entry point. Prints collision report."""
    root = Path("src/domains")
    invariants = scan_all_domains(root)
    collisions = detect_collisions(invariants)

    print("=" * 55)
    print("CROSS-DOMAIN INVARIANT COLLISION REPORT")
    print("=" * 55)
    print(f"Domains scanned: {len({inv.domain for inv in invariants})}")
    print(f"Invariants extracted: {len(invariants)}")
    print(f"Collisions detected: {len(collisions)}")
    print()

    if collisions:
        print(f"{'Domain A':<28} {'Check A':<30} {'Domain B':<28} {'Check B':<30} {'Shared Root':<25} {'Risk'}")
        print("-" * 145)
        for c in collisions:
            print(
                f"{c.domain_a:<28} {c.check_a:<30} {c.domain_b:<28} {c.check_b:<30} "
                f"{c.shared_root:<25} {c.propagation_risk}"
            )
        print()
        highest = max(collisions, key=lambda c: c.propagation_risk)
        print("PROPAGATION EXAMPLE:")
        proof = demonstrate_propagation(highest)
        print(proof.conclusion)
    else:
        print("No collisions detected.")

    print("=" * 55)
    return 0


if __name__ == "__main__":
    sys.exit(main())
