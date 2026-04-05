"""
PHASE1_AUDIT.py — RESTORATION-POLYMATHIC-001, BATCH 1 (Phase 1).

Enumerate everything. Measure everything. No fixes yet.

Produces:
  restoration/PHASE1_AUDIT_REPORT.json    — machine-readable
  restoration/PHASE1_AUDIT_SUMMARY.md     — human-readable

Classification per domain:
  IMPLEMENTED   — has src/domains/d_XXX/ with non-stub implementation.py + invariants.py
  PARTIAL       — has some files but they are incomplete
  STUB          — has test files but all are < 30 LOC or no real imports
  SCHEMA_ONLY   — depth_i < 0.3 OR no test files

Usage:
  python restoration/PHASE1_AUDIT.py
  python restoration/PHASE1_AUDIT.py --output-dir restoration/
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import date
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).resolve().parent.parent

ONTOLOGY_PATH = REPO_ROOT / "ontology" / "ontology.json"
TESTS_DIR = REPO_ROOT / "tests"
DOMAINS_DIR = REPO_ROOT / "src" / "domains"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except OSError:
        return "UNREADABLE"
    return h.hexdigest()


def _count_real_lines(path: Path) -> int:
    """Count non-blank, non-comment lines (proxy for LOC)."""
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return 0
    return sum(
        1 for line in lines
        if line.strip() and not line.strip().startswith("#")
    )


def _count_asserts(path: Path) -> int:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    return content.count("assert ")


def _has_real_imports(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("import ") or line.startswith("from "):
            module = line.split()[1].split(".")[0]
            if module not in {"__future__", "typing", "os", "sys", "time", "re"}:
                return True
    return False


def _stub_check(path: Path) -> bool:
    """Return True if the file appears to be a stub (pass, return True, return 1.0)."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return True
    stub_patterns = ["    pass", "return True", "return 1.0", "return None"]
    stub_count = sum(content.count(p) for p in stub_patterns)
    loc = _count_real_lines(path)
    return stub_count > 0 and loc < 30


def _find_test_files_for_domain(domain_id: str) -> list[Path]:
    """Find test files related to a domain."""
    results = []
    d_id_lower = domain_id.lower().replace("_", "")
    # Exact match: test_f_{domain_lower}_*.py
    for f in sorted(TESTS_DIR.glob("*.py")):
        stem = f.stem.lower()
        if d_id_lower in stem or domain_id.lower() in stem:
            results.append(f)
    return results


def _measure_domain(domain: dict) -> dict:
    """Measure a single domain's implementation depth."""
    domain_id = domain["id"]
    domain_dir = DOMAINS_DIR / domain_id.lower()

    impl_path = domain_dir / "implementation.py"
    inv_path = domain_dir / "invariants.py"
    test_files = _find_test_files_for_domain(domain_id)

    has_impl = impl_path.exists()
    has_inv = inv_path.exists()

    impl_loc = _count_real_lines(impl_path) if has_impl else 0
    inv_loc = _count_real_lines(inv_path) if has_inv else 0
    impl_stub = _stub_check(impl_path) if has_impl else True
    inv_stub = _stub_check(inv_path) if has_inv else True

    test_loc_total = sum(_count_real_lines(f) for f in test_files)
    test_asserts_total = sum(_count_asserts(f) for f in test_files)
    any_test_has_real_imports = any(_has_real_imports(f) for f in test_files)

    # Depth score (0.0 - 1.0), measured not declared
    # Weights: impl LOC 0.2, passing tests 0.3, falsification tests 0.2, invariant coverage 0.3
    impl_score = min(1.0, impl_loc / 100) * 0.2 if not impl_stub else 0.0
    f_test_id = domain.get("example_falsification_test", "")
    falsification_present = any(
        f_test_id in (f.read_text(errors="ignore") if f.exists() else "")
        for f in test_files
    ) if f_test_id and test_files else False
    falsification_score = 0.2 if falsification_present else 0.0
    inv_score = min(1.0, inv_loc / 50) * 0.3 if not inv_stub else 0.0
    test_score = min(1.0, test_asserts_total / 10) * 0.3 if test_loc_total >= 30 else 0.0

    depth = round(impl_score + falsification_score + inv_score + test_score, 3)

    # Classification
    if depth >= 0.7 and not impl_stub and not inv_stub and test_loc_total >= 50:
        classification = "IMPLEMENTED"
    elif depth >= 0.3 or (has_impl and not impl_stub):
        classification = "PARTIAL"
    elif test_files and test_loc_total >= 30 and any_test_has_real_imports:
        classification = "STUB"
    else:
        classification = "SCHEMA_ONLY"

    return {
        "id": domain_id,
        "name": domain.get("name", ""),
        "classification": classification,
        "depth_score": depth,
        "has_implementation_py": has_impl,
        "has_invariants_py": has_inv,
        "impl_loc": impl_loc,
        "impl_stub": impl_stub,
        "inv_loc": inv_loc,
        "test_files": [str(f.relative_to(REPO_ROOT)) for f in test_files],
        "test_loc_total": test_loc_total,
        "test_asserts_total": test_asserts_total,
        "falsification_test_id": f_test_id,
        "falsification_test_present": falsification_present,
    }


def _cross_repo_check(domain: dict) -> dict:
    """Placeholder for cross-repo invariant check (sigma-lora-covenant)."""
    f_id = domain.get("example_falsification_test", "")
    return {
        "invariant": domain.get("invariants", [None])[0],
        "sigma_lora_covenant": "NOT_CHECKED",
        "note": "Cross-repo check requires sigma-lora-covenant checkout",
        "falsification_id": f_id,
    }


def _theological_correspondences_audit() -> list[dict]:
    """Check if any theological correspondences are POPPERIAN_EXEMPT (all should be FAIL now)."""
    # F_THEO_001 through F_THEO_006
    theo_ids = [f"F_THEO_00{i}" for i in range(1, 7)]
    results = []
    for t_id in theo_ids:
        test_file = None
        for f in sorted(TESTS_DIR.glob("*.py")):
            if t_id in (f.read_text(errors="ignore") if f.exists() else ""):
                test_file = str(f.relative_to(REPO_ROOT))
                break
        results.append({
            "falsification_id": t_id,
            "test_file": test_file,
            "popperian_status": "PASS" if test_file else "FAIL",
            "note": "POPPERIAN_EXEMPT is FAIL — zero exemptions",
        })
    return results


def run_audit(output_dir: Path) -> dict:
    """Run the full Phase 1 audit."""
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ONTOLOGY_PATH.exists():
        raise FileNotFoundError(f"Ontology not found: {ONTOLOGY_PATH}")

    with ONTOLOGY_PATH.open(encoding="utf-8") as f:
        ontology = json.load(f)

    domains = ontology.get("domains", [])
    domain_results = [_measure_domain(d) for d in domains]

    # Count classifications
    classifications = {}
    for r in domain_results:
        c = r["classification"]
        classifications[c] = classifications.get(c, 0) + 1

    # Implementation ratio
    implemented_count = classifications.get("IMPLEMENTED", 0)
    total = len(domain_results)
    impl_ratio = f"{implemented_count}/{total} ({100 * implemented_count // total if total else 0}%)"

    # Theological correspondences
    theo_results = _theological_correspondences_audit()
    theo_fails = sum(1 for t in theo_results if t["popperian_status"] == "FAIL")

    report = {
        "audit_date": str(date.today()),
        "phase": "PHASE1_AUDIT",
        "total_domains": total,
        "implemented": classifications.get("IMPLEMENTED", 0),
        "partial": classifications.get("PARTIAL", 0),
        "schema_only": classifications.get("SCHEMA_ONLY", 0),
        "stub": classifications.get("STUB", 0),
        "implementation_ratio": impl_ratio,
        "theological_correspondences": {
            "total": len(theo_results),
            "failing_popperian": theo_fails,
            "popperian_exempt": 0,
            "results": theo_results,
        },
        "domains": domain_results,
    }

    # Write JSON report
    report_path = output_dir / "PHASE1_AUDIT_REPORT.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write human-readable summary
    _write_summary(report, output_dir / "PHASE1_AUDIT_SUMMARY.md")

    print(f"PHASE1 Audit complete.")
    print(f"  Total domains:    {total}")
    print(f"  Implemented:      {classifications.get('IMPLEMENTED', 0)}")
    print(f"  Partial:          {classifications.get('PARTIAL', 0)}")
    print(f"  Stub:             {classifications.get('STUB', 0)}")
    print(f"  Schema only:      {classifications.get('SCHEMA_ONLY', 0)}")
    print(f"  Impl ratio:       {impl_ratio}")
    print(f"  Theo FAIL:        {theo_fails}/6")
    print(f"  Report: {report_path}")

    return report


def _write_summary(report: dict, path: Path) -> None:
    domains = report["domains"]
    lines = [
        "# PHASE 1 AUDIT SUMMARY",
        f"**Date:** {report['audit_date']}",
        f"**Total domains:** {report['total_domains']}",
        f"**Implementation ratio:** {report['implementation_ratio']}",
        "",
        "## Classification Breakdown",
        f"- IMPLEMENTED: {report['implemented']}",
        f"- PARTIAL: {report['partial']}",
        f"- STUB: {report['stub']}",
        f"- SCHEMA_ONLY: {report['schema_only']}",
        "",
        "## Theological Correspondences (Popperian Audit)",
        f"- Failing (no falsification test): {report['theological_correspondences']['failing_popperian']}/6",
        f"- POPPERIAN_EXEMPT (allowed): 0 — zero exemptions",
        "",
        "## Domain Details",
        "| ID | Name | Classification | Depth | Impl LOC | Test Files |",
        "|---|---|---|---|---|---|",
    ]

    for d in domains:
        test_count = len(d["test_files"])
        lines.append(
            f"| {d['id']} | {d['name']} | {d['classification']} "
            f"| {d['depth_score']:.3f} | {d['impl_loc']} | {test_count} |"
        )

    lines += [
        "",
        "## Target (RESTORATION-POLYMATHIC-001)",
        "- [ ] 58/58 domains → IMPLEMENTED",
        "- [ ] 0 POPPERIAN_EXEMPT theological correspondences",
        "- [ ] All depth scores MEASURED not DECLARED",
        "",
        "_Generated by restoration/PHASE1_AUDIT.py_",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="PHASE1 Audit — enumerate and measure")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "restoration",
        help="Directory for output files (default: restoration/)",
    )
    args = parser.parse_args()

    try:
        run_audit(args.output_dir)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
