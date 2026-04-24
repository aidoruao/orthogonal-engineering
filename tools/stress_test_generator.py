"""tools/stress_test_generator.py -- Generate Kimi CLI stress test sessions.

Part 7E of Forensic Offensive Campaign.

Given a domain's invariants, generates a Kimi CLI session that maximally
exercises them -- the "edge case arsenal" from Gemini's strategy.
"""

from __future__ import annotations

import ast
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject


def _extract_check_functions(invariants_path: Path) -> List[str]:
    """Extract check_* function names from an invariants.py file.

    falsifies_if: returns empty list when check functions exist.
    """
    try:
        source = invariants_path.read_text(encoding="utf-8")
    except OSError:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("check_")
    ]


def generate_stress_test(
    domain_name: str,
) -> Tuple[bool, ProofObject]:
    """Generate a stress test spec for a given domain.

    Standard: STRESS-001 test generation.
    Falsifies if: domain exists but no check functions are found.
    falsifies_if: domain exists but no check functions are found.
    """
    domain_path = REPO_ROOT / "src" / "domains" / domain_name / "invariants.py"
    if not domain_path.exists():
        return False, ProofObject(
            rule="stress_test_generator",
            premises=[f"domain={domain_name}"],
            conclusion=f"FAIL: Domain {domain_name} has no invariants.py",
        )

    checks = _extract_check_functions(domain_path)
    if not checks:
        return False, ProofObject(
            rule="stress_test_generator",
            premises=[f"domain={domain_name}"],
            conclusion=f"FAIL: No check_* functions found in {domain_name}/invariants.py",
        )

    spec = {
        "domain": domain_name,
        "check_functions": checks,
        "stress_intensity": "maximal",
        "execution_plan": [
            f"Exercise {check} with boundary inputs"
            for check in checks
            if not check.endswith("_fail")
        ],
    }

    output_path = REPO_ROOT / "benchmarks" / f"stress_test_{domain_name}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        __import__("json").dumps(spec, indent=2), encoding="utf-8"
    )

    proof = ProofObject(
        rule="stress_test_generator",
        premises=[f"domain={domain_name}", f"checks={len(checks)}"],
        conclusion=f"PASS: Generated stress test spec with {len(checks)} check function(s)",
    )
    return True, proof


def main() -> int:
    """CLI entry point.

    falsifies_if: exit code 0 when no domain argument is provided.
    """
    if len(sys.argv) < 2:
        print("Usage: python tools/stress_test_generator.py <domain_name>")
        return 1
    domain = sys.argv[1]
    ok, proof = generate_stress_test(domain)
    print(proof.conclusion)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
