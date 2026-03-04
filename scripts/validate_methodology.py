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
  5. (Optional) When --check-tests is passed, reports F-IDs whose test_file
     still starts with "TODO:".  Add --fail-on-missing to make this an error.
  6. (Optional) When --check-case-studies is passed, reports F-IDs with no
     linked case study and case studies with no linked F-ID.
  7. (Optional) When --check-domain-coverage is passed, reports domains that
     have fewer than --min-tests (default 3) falsification tests.

Exit codes:
  0  All checks passed.
  1  One or more checks failed (details printed to stdout).

Usage:
  python scripts/validate_methodology.py
  python scripts/validate_methodology.py --check-tags
  python scripts/validate_methodology.py --check-tests
  python scripts/validate_methodology.py --check-tests --fail-on-missing
  python scripts/validate_methodology.py --check-case-studies
  python scripts/validate_methodology.py --check-domain-coverage --min-tests=3
  python scripts/validate_methodology.py --check-tests --check-case-studies --check-domain-coverage
"""

import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import DefaultDict, List, Optional, Tuple


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


def check_tests(ids: dict, schemas: dict, fail_on_missing: bool) -> tuple:
    """Return (errors, warnings) about F-IDs whose test_file still starts with TODO:."""
    unimplemented = []
    for t in schemas["falsification_tests"].get("falsification_tests", []):
        tf = t.get("test_file", "")
        if tf.startswith("TODO:") or t.get("status", "") == "placeholder":
            unimplemented.append(t["id"])

    messages = [f"F-ID '{fid}' has no implemented test (status=placeholder)" for fid in unimplemented]

    if fail_on_missing:
        return messages, []
    return [], [f"WARNING (unimplemented-test): {m}" for m in messages]


def check_case_studies(ids: dict, schemas: dict, fail_on_missing: bool = False) -> tuple:
    """Return (errors, warnings) about F-IDs with no case study and case studies with no F-ID."""
    messages = []

    # Case studies with no linked F-ID
    for c in schemas["case_studies"].get("cases", []):
        if not c.get("falsification_tests"):
            messages.append(
                f"Case '{c['id']}' has no linked falsification test"
            )

    if fail_on_missing:
        return messages, []
    return [], [f"WARNING (case-study-coverage): {m}" for m in messages]


def check_domain_coverage(ids: dict, schemas: dict, min_tests: int, fail_on_missing: bool = False) -> tuple:
    """Return (errors, warnings) about domains with fewer than min_tests falsification tests."""
    # Count F-IDs per domain
    domain_f_count: dict = {d: 0 for d in ids["domain_ids"]}
    for t in schemas["falsification_tests"].get("falsification_tests", []):
        d = t.get("domain", "")
        if d in domain_f_count:
            domain_f_count[d] += 1

    messages = []
    for domain_id, count in sorted(domain_f_count.items()):
        if count < min_tests:
            messages.append(
                f"Domain '{domain_id}' has only {count} "
                f"falsification test(s) (required >= {min_tests})"
            )

    if fail_on_missing:
        return messages, []
    return [], [f"WARNING (domain-coverage): {m}" for m in messages]


# ---------------------------------------------------------------------------
# Tag-coverage check
# ---------------------------------------------------------------------------

ID_RE = re.compile(r"^[A-Z]+_[A-Z0-9]+_[0-9]{3}$")
TAG_CAPTURE_RE = re.compile(r"@falsification_id:\s*([A-Z0-9_-]+)")


def check_id_formats(ids: dict) -> list:
    """Enforce underscore-only IDs and required numeric suffix for F/OI/CS."""
    errors = []

    for fid in sorted(ids["f_ids"]):
        if "-" in fid:
            errors.append(f"[format] F-ID '{fid}' uses hyphenated form (disallowed)")
        if not ID_RE.match(fid):
            errors.append(f"[format] F-ID '{fid}' does not match ^[A-Z]+_[A-Z0-9]+_[0-9]{{3}}$")

    for oid in sorted(ids["oi_ids"]):
        if "-" in oid:
            errors.append(f"[format] OI-ID '{oid}' uses hyphenated form (disallowed)")
        if not ID_RE.match(oid):
            errors.append(f"[format] OI-ID '{oid}' does not match ^[A-Z]+_[A-Z0-9]+_[0-9]{{3}}$")

    for cid in sorted(ids["case_ids"]):
        if "-" in cid:
            errors.append(f"[format] CS-ID '{cid}' uses hyphenated form (disallowed)")
        if not ID_RE.match(cid):
            errors.append(f"[format] CS-ID '{cid}' does not match ^[A-Z]+_[A-Z0-9]+_[0-9]{{3}}$")

    for did in sorted(ids["domain_ids"]):
        if "-" in did:
            errors.append(f"[format] Domain ID '{did}' uses hyphenated form (disallowed)")

    return errors


def _collect_tag_metadata() -> tuple:
    tagged = set()
    counts = {}
    locations = {}
    per_file = {}
    invalid = []
    empty_files = []

    if not TESTS_DIR.exists():
        return tagged, counts, locations, invalid, per_file, empty_files

    for path in TESTS_DIR.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        rel = str(path.relative_to(REPO_ROOT)).replace(os.sep, "/")
        tokens = TAG_CAPTURE_RE.findall(text)
        per_file[rel] = tokens
        if not text:
            empty_files.append(rel)
        if len(tokens) > 1:
            invalid.append(f"[tags] {rel}: contains {len(tokens)} @falsification_id tags; expected exactly 1")

        for token in tokens:
            if "-" in token:
                invalid.append(f"[tags] {rel}: invalid hyphenated falsification_id '{token}'")
                continue
            if not token.startswith("F_"):
                invalid.append(f"[tags] {rel}: falsification_id must start with 'F_': '{token}'")
                continue
            if not ID_RE.match(token):
                invalid.append(f"[tags] {rel}: falsification_id '{token}' does not match ^[A-Z]+_[A-Z0-9]+_[0-9]{{3}}$")
                continue
            tagged.add(token)
            counts[token] = counts.get(token, 0) + 1
            locations.setdefault(token, set()).add(rel)

    return tagged, counts, locations, invalid, per_file, empty_files


def check_tag_bijection(ids: dict, schemas: dict, tag_state: Optional[tuple] = None) -> list:
    """Ensure test tags bijectively match registry and map to declared test_file paths."""
    errors = []
    if tag_state is None:
        tag_state = _collect_tag_metadata()
    tagged, counts, locations, invalid, per_file, empty_files = tag_state
    errors.extend(invalid)

    expected = ids["f_ids"]

    missing = sorted(expected - tagged)
    for fid in missing:
        errors.append(f"[tags] F-ID '{fid}' missing @falsification_id tag in tests/")

    extra = sorted(tagged - expected)
    for fid in extra:
        errors.append(f"[tags] Unknown @falsification_id '{fid}' present in tests/")

    # Path correspondence and per-file constraints
    ft_index = {t["id"]: t for t in schemas["falsification_tests"].get("falsification_tests", [])}
    for fid in expected:
        if fid not in ft_index:
            continue
        expected_path_raw = ft_index[fid].get("test_file", "")
        expected_path = expected_path_raw.split("::", 1)[0] if expected_path_raw else ""
        if not expected_path:
            errors.append(f"[tags] F-ID '{fid}' has empty test_file in registry")
            continue
        tag_paths = locations.get(fid, set())
        if counts.get(fid, 0) != 1:
            errors.append(f"[tags] F-ID '{fid}' must appear exactly once; found {counts.get(fid, 0)}")
        file_tags = per_file.get(expected_path, [])
        if expected_path in empty_files:
            errors.append(f"[tags] F-ID '{fid}' test_file '{expected_path}' is empty")
        if not file_tags:
            errors.append(f"[tags] Test file '{expected_path}' missing @falsification_id tag for F-ID '{fid}'")
        elif len(file_tags) != 1:
            errors.append(f"[tags] Test file '{expected_path}' must contain exactly one @falsification_id tag; found {len(file_tags)}")
        else:
            token = file_tags[0]
            if token != fid:
                errors.append(
                    f"[tags] Test file '{expected_path}' tag '{token}' does not match registry F-ID '{fid}'"
                )
        if tag_paths and expected_path not in tag_paths:
            errors.append(
                f"[tags] F-ID '{fid}' tag paths {sorted(tag_paths)} do not match registry test_file '{expected_path}'"
            )

    return errors


def check_total_ci_completion(schemas: dict, tag_state: tuple) -> list:
    """Enforce R==T and R⊆O,C invariants for Total CI Completion."""
    errors = []
    tagged, _, _, _, _, _ = tag_state
    r = {t["id"] for t in schemas["falsification_tests"].get("falsification_tests", [])}
    t = set(tagged)
    o = set()
    c = set()

    for issue in schemas["ontology"].get("issues", []):
        o.update(issue.get("falsification_tests", []))
    for case in schemas["case_studies"].get("cases", []):
        c.update(case.get("falsification_tests", []))

    if r != t:
        missing = sorted(r - t)
        extra = sorted(t - r)
        if missing:
            errors.append(f"[total-ci] Missing tags for F-IDs: {missing}")
        if extra:
            errors.append(f"[total-ci] Extra @falsification_id tags not in registry: {extra}")
    if not r.issubset(o):
        errors.append(f"[total-ci] Registry F-IDs not covered by ontology issues: {sorted(r - o)}")
    if not r.issubset(c):
        errors.append(f"[total-ci] Registry F-IDs not covered by case studies: {sorted(r - c)}")
    return errors


def check_required_fields(schemas: dict) -> list:
    errors = []
    for t in schemas["falsification_tests"].get("falsification_tests", []):
        fid = t["id"]
        for field in ["domain", "invariant", "falsifies_if", "definition"]:
            if not t.get(field):
                errors.append(f"[required] F-ID '{fid}' missing required field '{field}'")
    return errors


def check_domain_continuity(schemas: dict) -> list:
    errors = []
    domain_map: DefaultDict[str, List[Tuple[int, str]]] = defaultdict(list)
    for t in schemas["falsification_tests"].get("falsification_tests", []):
        fid = t["id"]
        domain = t.get("domain", "")
        suffix = fid.rsplit("_", 1)[-1]
        try:
            num = int(suffix)
        except ValueError:
            errors.append(f"[continuity] F-ID '{fid}' has non-numeric suffix '{suffix}'")
            continue
        domain_map[domain].append((num, fid))

    for domain, pairs in sorted(domain_map.items()):
        if not pairs:
            continue
        nums = [n for n, _ in pairs]
        max_n = max(nums)
        missing = [n for n in range(1, max_n + 1) if n not in nums]
        dup_counts = Counter(nums)
        dupes = sorted(n for n, c in dup_counts.items() if c > 1)
        if missing:
            errors.append(f"[continuity] Domain '{domain}' missing indices: {missing}")
        if dupes:
            ids_for_dupes = {
                n: sorted(fid for num, fid in pairs if num == n) for n in dupes
            }
            errors.append(
                f"[continuity] Domain '{domain}' has duplicate indices: {ids_for_dupes}"
            )
    return errors


def check_shard_hashes(schemas: dict) -> list:
    errors = []
    for t in schemas["falsification_tests"].get("falsification_tests", []):
        if not t.get("sharded"):
            continue
        fid = t["id"]
        shard_files = t.get("shard_files") or []
        shard_count = t.get("shard_count")
        canonical_hash = t.get("canonical_hash", "")
        if shard_count != len(shard_files):
            errors.append(
                f"[shard] F-ID '{fid}' shard_count={shard_count} does not match shard_files length {len(shard_files)}"
            )
            continue
        entry_failed = False
        if not canonical_hash:
            errors.append(f"[shard] F-ID '{fid}' missing canonical_hash for sharded entry")
            entry_failed = True
        hasher = hashlib.sha256()
        for sfile in shard_files:
            path = REPO_ROOT / sfile
            if not path.exists():
                errors.append(f"[shard] F-ID '{fid}' shard file missing: {sfile}")
                entry_failed = True
                continue
            with path.open("rb") as fh:
                for chunk in iter(lambda: fh.read(8192), b""):
                    hasher.update(chunk)
        if entry_failed:
            continue
        digest = hasher.hexdigest()
        if digest != canonical_hash:
            errors.append(
                f"[shard] F-ID '{fid}' canonical_hash mismatch: expected {canonical_hash}, got {digest}"
            )
    return errors


def check_totality_constraints(schemas: dict) -> list:
    """Enforce ontology totality conditions across OI, F, and CS entries."""
    errors = []

    for issue in schemas["ontology"].get("issues", []):
        if not issue.get("falsification_tests"):
            errors.append(f"[totality] OI-ID '{issue['id']}' must reference >=1 falsification_test")
        if not issue.get("related_cases"):
            errors.append(f"[totality] OI-ID '{issue['id']}' must reference >=1 related_case (CS)")

    for t in schemas["falsification_tests"].get("falsification_tests", []):
        fid = t["id"]
        domain = t.get("domain", "")
        if not domain:
            errors.append(f"[totality] F-ID '{fid}' missing domain")
        if len(t.get("ontological_issues", [])) < 1:
            errors.append(f"[totality] F-ID '{fid}' must reference >=1 ontological_issue")
        if not t.get("test_file"):
            errors.append(f"[totality] F-ID '{fid}' missing test_file path")
        else:
            tf_node = t["test_file"]
            tf_file = tf_node.split("::", 1)[0]
            tf_path = REPO_ROOT / tf_file
            if not tf_path.exists():
                errors.append(f"[totality] F-ID '{fid}' test_file does not exist: {tf_node}")
            else:
                try:
                    if tf_path.stat().st_size == 0:
                        errors.append(f"[totality] F-ID '{fid}' test_file is empty: {tf_node}")
                except OSError:
                    errors.append(f"[totality] F-ID '{fid}' test_file not readable: {tf_node}")

    for c in schemas["case_studies"].get("cases", []):
        cid = c["id"]
        if len(c.get("ontological_issues", [])) < 1:
            errors.append(f"[totality] CS-ID '{cid}' must reference >=1 ontological_issue")
        if len(c.get("falsification_tests", [])) < 1:
            errors.append(f"[totality] CS-ID '{cid}' must reference >=1 falsification_test")

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    check_tags_flag = "--check-tags" in sys.argv
    check_tests_flag = "--check-tests" in sys.argv
    fail_on_missing = "--fail-on-missing" in sys.argv
    check_cs_flag = "--check-case-studies" in sys.argv
    check_dc_flag = "--check-domain-coverage" in sys.argv

    # Parse --min-tests=N
    min_tests = 3
    for arg in sys.argv[1:]:
        if arg.startswith("--min-tests="):
            try:
                min_tests = int(arg.split("=", 1)[1])
            except ValueError:
                pass

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

    # 4. ID format & totality checks
    errors.extend(check_id_formats(ids))
    errors.extend(check_totality_constraints(schemas))
    errors.extend(check_required_fields(schemas))
    errors.extend(check_domain_continuity(schemas))
    errors.extend(check_shard_hashes(schemas))

    # 5. Tag bijection check (always enforced)
    tag_state = _collect_tag_metadata()
    errors.extend(check_tag_bijection(ids, schemas, tag_state))
    errors.extend(check_total_ci_completion(schemas, tag_state))

    # 6. Implemented-test check
    if check_tests_flag:
        test_errors, test_warnings = check_tests(ids, schemas, fail_on_missing)
        errors.extend(test_errors)
        warnings.extend(test_warnings)

    # 7. Case-study coverage
    if check_cs_flag:
        cs_errors, cs_warnings = check_case_studies(ids, schemas, fail_on_missing)
        errors.extend(cs_errors)
        warnings.extend(cs_warnings)

    # 8. Domain coverage
    if check_dc_flag:
        dc_errors, dc_warnings = check_domain_coverage(ids, schemas, min_tests, False)
        errors.extend(dc_errors)
        warnings.extend(dc_warnings)

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
