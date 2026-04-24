"""tools/polymath_collision_report.py -- Cross-domain mathematical primitive collision reporter.

Part 4E of Forensic Offensive Campaign.

Scans all domain invariants for shared mathematical primitives
(Fraction thresholds, ProofObject rules, Peano axioms) and reports
the collision graph.
"""

from __future__ import annotations

import ast
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject


def _extract_fraction_literals(source: str) -> Set[str]:
    """Extract Fraction literal constructions from source.

    falsifies_if: returns empty set when Fraction literals exist.
    """
    return set(re.findall(r'Fraction\(\s*\d+\s*,\s*\d+\s*\)', source))


def _extract_proofobject_rules(source: str) -> Set[str]:
    """Extract ProofObject rule strings from source.

    falsifies_if: returns empty set when ProofObject rules exist.
    """
    return set(re.findall(r'rule\s*=\s*"([^"]+)"', source))


def _extract_peano_axioms(source: str) -> Set[str]:
    """Extract Peano axiom references from source.

    falsifies_if: returns empty set when Peano references exist.
    """
    return set(re.findall(r'peano_\w+', source, re.IGNORECASE))


def scan_domain_for_primitives(domain_path: Path) -> Dict[str, Set[str]]:
    """Scan a single domain's invariants.py for mathematical primitives.

    falsifies_if: file exists but scan returns empty dict.
    """
    inv_file = domain_path / "invariants.py"
    if not inv_file.exists():
        return {}
    try:
        source = inv_file.read_text(encoding="utf-8")
    except OSError:
        return {}

    return {
        "fractions": _extract_fraction_literals(source),
        "proofobject_rules": _extract_proofobject_rules(source),
        "peano_axioms": _extract_peano_axioms(source),
    }


def find_collisions(
    repo_root: Path,
) -> Tuple[bool, ProofObject]:
    """Find all cross-domain primitive collisions.

    Standard: POLYMATH-COLLISION-001.
    Falsifies if: two domains share a primitive but collision is not reported.
    falsifies_if: two domains share a primitive but collision is not reported.
    """
    domains_dir = repo_root / "src" / "domains"
    if not domains_dir.exists():
        return False, ProofObject(
            rule="polymath_collision_scan",
            premises=["domains_dir missing"],
            conclusion="FAIL: src/domains/ directory not found",
        )

    domain_scans: Dict[str, Dict[str, Set[str]]] = {}
    for domain_dir in sorted(domains_dir.iterdir()):
        if domain_dir.is_dir() and domain_dir.name.startswith("d_"):
            scan = scan_domain_for_primitives(domain_dir)
            if scan:
                domain_scans[domain_dir.name] = scan

    collisions: List[Dict[str, str]] = []
    domain_names = sorted(domain_scans.keys())

    for i, d1 in enumerate(domain_names):
        for d2 in domain_names[i + 1:]:
            shared_fractions = domain_scans[d1]["fractions"] & domain_scans[d2]["fractions"]
            shared_rules = domain_scans[d1]["proofobject_rules"] & domain_scans[d2]["proofobject_rules"]
            shared_peano = domain_scans[d1]["peano_axioms"] & domain_scans[d2]["peano_axioms"]
            if shared_fractions or shared_rules or shared_peano:
                collisions.append({
                    "domain_a": d1,
                    "domain_b": d2,
                    "shared_fractions": len(shared_fractions),
                    "shared_rules": len(shared_rules),
                    "shared_peano": len(shared_peano),
                })

    report_path = repo_root / "audit" / "POLYMATH_COLLISION_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        __import__("json").dumps(
            {
                "total_domains_scanned": len(domain_scans),
                "collision_pairs": len(collisions),
                "collisions": collisions,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    conclusion = (
        f"PASS: Scanned {len(domain_scans)} domains, found {len(collisions)} collision pair(s)"
        if collisions
        else f"PASS: Scanned {len(domain_scans)} domains, zero collisions detected"
    )
    proof = ProofObject(
        rule="polymath_collision_scan",
        premises=[
            f"domains_scanned={len(domain_scans)}",
            f"collision_pairs={len(collisions)}",
        ],
        conclusion=conclusion,
    )
    return True, proof


if __name__ == "__main__":
    ok, proof = find_collisions(REPO_ROOT)
    print(proof.conclusion)
    sys.exit(0 if ok else 1)
