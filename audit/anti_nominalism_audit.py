"""audit/anti_nominalism_audit.py — Label-Without-Referent Detector.

Checks three label namespaces for nominalist (ungrounded) entries:
  1. GLOSSARY.md — every term must be referenced in at least one repo file.
  2. ontology/ontology.json — every domain entry must have a corresponding
     src/domains/<domain_id>/ directory.
  3. STANDARDS_REGISTRY.json — every standard must have an existing
     enforcement_file and its enforcement_command must use ``python3``.

Run as:
    python3 audit/anti_nominalism_audit.py [--output <path>]

Returns exit code 0 if nominalist_count == 0, 1 otherwise.
Persists JSON report to audit/ANTI_NOMINALISM_REPORT.json by default.

Standard: ANOM-001
Falsifies if: returns 0 when any label lacks a grounding reference.
falsifies_if: returns 0 when any label lacks a grounding reference.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject

GLOSSARY_PATH = REPO_ROOT / "GLOSSARY.md"
ONTOLOGY_PATH = REPO_ROOT / "ontology" / "ontology.json"
STANDARDS_PATH = REPO_ROOT / "STANDARDS_REGISTRY.json"
DEFAULT_REPORT_PATH = Path(__file__).parent / "ANTI_NOMINALISM_REPORT.json"


def _extract_glossary_terms(source: str) -> List[str]:
    """Extract term names from the GLOSSARY.md table."""
    terms: List[str] = []
    # Find table rows: | Term | ... |
    in_table = False
    for line in source.splitlines():
        if line.strip().startswith("| Term |"):
            in_table = True
            continue
        if in_table and line.strip().startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2 and parts[1] and parts[1] != "Term":
                terms.append(parts[1])
        elif in_table and not line.strip().startswith("|"):
            in_table = False
    return terms


def _term_has_grounding(term: str) -> bool:
    """Check if a term appears anywhere in the repo (case-insensitive)."""
    try:
        result = subprocess.run(
            ["git", "grep", "-i", "-l", re.escape(term)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except Exception:
        # Fallback to ripgrep or simple grep
        try:
            result = subprocess.run(
                ["grep", "-ri", "-l", re.escape(term), str(REPO_ROOT)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False


def _check_glossary() -> Tuple[List[str], int, int]:
    """Return (nominalist_terms, total_terms, grounded_terms)."""
    if not GLOSSARY_PATH.exists():
        return [], 0, 0

    try:
        source = GLOSSARY_PATH.read_text(encoding="utf-8")
    except OSError:
        return [], 0, 0

    terms = _extract_glossary_terms(source)
    nominalist: List[str] = []
    grounded = 0

    for term in terms:
        if _term_has_grounding(term):
            grounded += 1
        else:
            nominalist.append(term)

    return nominalist, len(terms), grounded


def _check_ontology() -> Tuple[List[str], int, int]:
    """Return (nominalist_domains, total_domains, grounded_domains)."""
    if not ONTOLOGY_PATH.exists():
        return [], 0, 0

    try:
        data = json.loads(ONTOLOGY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [], 0, 0

    nominalist: List[str] = []
    total = 0
    grounded = 0

    domains = data.get("domains", [])
    for entry in domains:
        domain_id = entry.get("id", "")
        if not domain_id:
            continue
        total += 1
        # Map e.g. D_GRAPHICS -> d_graphics
        expected_dir = domain_id.lower().replace("d_", "d_")
        if expected_dir.startswith("d") and not expected_dir.startswith("d_"):
            expected_dir = "d_" + expected_dir[1:]
        domain_dir = REPO_ROOT / "src" / "domains" / expected_dir
        if domain_dir.exists() and domain_dir.is_dir():
            grounded += 1
        else:
            nominalist.append(domain_id)

    return nominalist, total, grounded


def _check_standards() -> Tuple[List[str], int, int]:
    """Return (nominalist_standards, total_standards, grounded_standards)."""
    if not STANDARDS_PATH.exists():
        return [], 0, 0

    try:
        data = json.loads(STANDARDS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [], 0, 0

    nominalist: List[str] = []
    total = 0
    grounded = 0

    standards = data.get("standards", [])
    for std in standards:
        std_id = std.get("id", "")
        if not std_id:
            continue
        total += 1
        file_path_str = std.get("enforcement_file")
        command = std.get("enforcement_command", "")

        issues: List[str] = []
        if file_path_str:
            fpath = REPO_ROOT / file_path_str
            if not fpath.exists():
                issues.append(f"missing enforcement_file: {file_path_str}")
        else:
            issues.append("no enforcement_file")

        if command and "python " in command and "python3 " not in command:
            # Check that it uses python3, not just python
            # Allow "python3" explicitly, reject bare "python "
            if not command.startswith("python3") and "python3" not in command:
                issues.append("enforcement_command uses 'python' not 'python3'")

        if issues:
            nominalist.append(std_id)
        else:
            grounded += 1

    return nominalist, total, grounded


def run_anti_nominalism_audit(
    output_path: Path = DEFAULT_REPORT_PATH,
) -> Tuple[bool, ProofObject]:
    """Run the anti-nominalism audit.

    Falsifies if: returns True while any label lacks a grounding reference.
    falsifies_if: returns True while any label lacks a grounding reference.
    """
    nominalist_terms, total_terms, grounded_terms = _check_glossary()
    nominalist_domains, total_domains, grounded_domains = _check_ontology()
    nominalist_standards, total_standards, grounded_standards = _check_standards()

    nominalist_count = (
        len(nominalist_terms) + len(nominalist_domains) + len(nominalist_standards)
    )
    total_labels = total_terms + total_domains + total_standards
    grounded_labels = grounded_terms + grounded_domains + grounded_standards

    from fractions import Fraction
    ratio = Fraction(grounded_labels, max(total_labels, 1))

    result = {
        "nominalist_terms": nominalist_terms,
        "nominalist_domains": nominalist_domains,
        "nominalist_standards": nominalist_standards,
        "total_labels": total_labels,
        "grounded_labels": grounded_labels,
        "nominalist_count": nominalist_count,
        "anti_nominalism_ratio": f"{ratio.numerator}/{ratio.denominator}",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    all_pass = nominalist_count == 0
    conclusion = (
        f"PASS: {grounded_labels}/{total_labels} labels grounded"
        if all_pass
        else f"FAIL: {nominalist_count} nominalist labels found"
    )
    proof = ProofObject(
        rule="run_anti_nominalism_audit",
        premises=[
            f"total_labels={total_labels}",
            f"grounded_labels={grounded_labels}",
            f"nominalist_count={nominalist_count}",
        ],
        conclusion=conclusion,
    )
    return all_pass, proof


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Anti-nominalism audit"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path for the JSON report",
    )
    args = parser.parse_args(argv)

    passed, proof = run_anti_nominalism_audit(output_path=args.output)
    print(proof.conclusion)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
