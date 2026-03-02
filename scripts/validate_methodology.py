#!/usr/bin/env python3
"""
validate_methodology.py
-----------------------
Validates the DeepSeek-style methodology schema files under ontology/:
  - search_lens.json
  - case_studies.json
  - falsification_tests.json
  - ontology.json

Checks performed:
  1. All JSON files parse without error.
  2. Required top-level keys are present in each schema.
  3. All cross-references are consistent (F-IDs, OI-IDs, domain IDs, case IDs).
  4. (Optional) When --check-tags is passed, scans test files in tests/ for
     @falsification_id: F-XXX comments and reports F-IDs that have no
     corresponding test file tag.

Exit codes:
  0  All checks passed.
  1  One or more checks failed (details printed to stdout).

Usage:
  python scripts/validate_methodology.py
  python scripts/validate_methodology.py --check-tags
"""

import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
ONTOLOGY_DIR = REPO_ROOT / "ontology"
TESTS_DIR = REPO_ROOT / "tests"

SCHEMA_FILES = {
    "search_lens":         ONTOLOGY_DIR / "search_lens.json",
    "case_studies":        ONTOLOGY_DIR / "case_studies.json",
    "falsification_tests": ONTOLOGY_DIR / "falsification_tests.json",
    "ontology":            ONTOLOGY_DIR / "ontology.json",
}

# Legacy ontological-issues files whose OI-IDs are still valid references.
LEGACY_OI_FILES = [
    ONTOLOGY_DIR / "pr26_ontological_issues.json",
]

REQUIRED_KEYS = {
    "search_lens":         ["metadata", "domains", "artifact_types", "root_cause_signals"],
    "case_studies":        ["metadata", "cases"],
    "falsification_tests": ["metadata", "falsification_tests"],
    "ontology":            ["metadata", "domains", "issues"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_required_keys(name: str, data: dict, keys: list) -> list:
    errors = []
    for k in keys:
        if k not in data:
            errors.append(f"[{name}] Missing required top-level key: '{k}'")
    return errors


# ---------------------------------------------------------------------------
# Cross-reference checks
# ---------------------------------------------------------------------------

def collect_ids(schemas: dict) -> dict:
    """Return sets of all declared IDs across schemas."""
    ids = {
        "domain_ids":     set(),
        "f_ids":          set(),
        "oi_ids":         set(),
        "case_ids":       set(),
        "rcs_ids":        set(),
    }

    # search_lens
    sl = schemas["search_lens"]
    for d in sl.get("domains", []):
        ids["domain_ids"].add(d["id"])
    for rcs in sl.get("root_cause_signals", []):
        ids["rcs_ids"].add(rcs["id"])

    # falsification_tests
    ft = schemas["falsification_tests"]
    for t in ft.get("falsification_tests", []):
        ids["f_ids"].add(t["id"])

    # ontology
    ont = schemas["ontology"]
    for issue in ont.get("issues", []):
        ids["oi_ids"].add(issue["id"])
    for d in ont.get("domains", []):
        ids["domain_ids"].add(d["id"])

    # case_studies
    cs = schemas["case_studies"]
    for c in cs.get("cases", []):
        ids["case_ids"].add(c["id"])

    # legacy OI files (e.g. pr26_ontological_issues.json)
    for legacy_path in LEGACY_OI_FILES:
        if legacy_path.exists():
            try:
                legacy = load_json(legacy_path)
            except (json.JSONDecodeError, OSError):
                continue
            for issue in legacy.get("issues", []):
                ids["oi_ids"].add(issue["id"])

    return ids


def crossref_errors(schemas: dict, ids: dict) -> list:
    errors = []

    # case_studies: check domain, rcs, f-id, oi-id references
    for case in schemas["case_studies"].get("cases", []):
        cid = case["id"]
        d = case.get("domain", "")
        if d and d not in ids["domain_ids"]:
            errors.append(f"[case_studies] {cid}: unknown domain '{d}'")
        for rcs in case.get("root_cause_signals", []):
            if rcs not in ids["rcs_ids"]:
                errors.append(f"[case_studies] {cid}: unknown root_cause_signal '{rcs}'")
        for f in case.get("falsification_tests", []):
            if f not in ids["f_ids"]:
                errors.append(f"[case_studies] {cid}: unknown falsification_test '{f}'")
        for oi in case.get("ontological_issues", []):
            if oi not in ids["oi_ids"]:
                errors.append(f"[case_studies] {cid}: unknown ontological_issue '{oi}'")

    # falsification_tests: check domain, oi-id, case references
    for ft in schemas["falsification_tests"].get("falsification_tests", []):
        fid = ft["id"]
        d = ft.get("domain", "")
        if d and d not in ids["domain_ids"]:
            errors.append(f"[falsification_tests] {fid}: unknown domain '{d}'")
        for oi in ft.get("ontological_issues", []):
            if oi not in ids["oi_ids"]:
                errors.append(f"[falsification_tests] {fid}: unknown ontological_issue '{oi}'")
        for cs in ft.get("case_studies", []):
            if cs not in ids["case_ids"]:
                errors.append(f"[falsification_tests] {fid}: unknown case_study '{cs}'")

    # ontology issues: check domain, f-id, case references
    for issue in schemas["ontology"].get("issues", []):
        iid = issue["id"]
        d = issue.get("domain", "")
        if d and d not in ids["domain_ids"]:
            errors.append(f"[ontology] {iid}: unknown domain '{d}'")
        for f in issue.get("falsification_tests", []):
            if f not in ids["f_ids"]:
                errors.append(f"[ontology] {iid}: unknown falsification_test '{f}'")
        for cs in issue.get("related_cases", []):
            if cs not in ids["case_ids"]:
                errors.append(f"[ontology] {iid}: unknown related_case '{cs}'")

    return errors


# ---------------------------------------------------------------------------
# Tag-coverage check
# ---------------------------------------------------------------------------

TAG_RE = re.compile(r"@falsification_id:\s*(F-[\w-]+)")


def check_tags(ids: dict) -> list:
    """Return list of F-IDs that have no @falsification_id tag in any test file."""
    tagged = set()
    if not TESTS_DIR.exists():
        return []
    for path in TESTS_DIR.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in TAG_RE.finditer(text):
            tagged.add(m.group(1))

    untagged = []
    for fid in sorted(ids["f_ids"]):
        if fid not in tagged:
            untagged.append(f"F-ID '{fid}' has no @falsification_id tag in any test file under tests/")
    return untagged


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    check_tags_flag = "--check-tags" in sys.argv

    errors = []
    warnings = []
    schemas = {}

    # 1. Load and parse all JSON files
    for name, path in SCHEMA_FILES.items():
        if not path.exists():
            errors.append(f"Missing schema file: {path}")
            continue
        try:
            schemas[name] = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"JSON parse error in {path}: {exc}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    # 2. Required-key checks
    for name, keys in REQUIRED_KEYS.items():
        errors.extend(check_required_keys(name, schemas[name], keys))

    # 3. Cross-reference checks
    ids = collect_ids(schemas)
    errors.extend(crossref_errors(schemas, ids))

    # 4. Tag coverage (warnings, not errors)
    if check_tags_flag:
        untagged = check_tags(ids)
        for w in untagged:
            warnings.append(f"WARNING (tag-coverage): {w}")

    # Report
    if warnings:
        for w in warnings:
            print(w)

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"\n{len(errors)} error(s) found. Schema validation FAILED.")
        return 1

    domain_count = len(ids["domain_ids"])
    f_count = len(ids["f_ids"])
    oi_count = len(ids["oi_ids"])
    case_count = len(ids["case_ids"])
    print(
        f"Schema validation PASSED: "
        f"{domain_count} domains, {f_count} F-IDs, {oi_count} OI-IDs, {case_count} case studies."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
