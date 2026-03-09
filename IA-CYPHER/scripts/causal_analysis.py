"""
causal_analysis.py — IA-CYPHER Causal Analysis Tool

Loads all cases from cases/case_* directories, reads metadata.json, and
aggregates across two pattern namespaces:

  S-01..S-05: LLM web search dampening / sabotage patterns (from HEDGE/REFUSAL/etc. flags)
  P1..P10:    Corporate audit patterns (from patterns_detected list in metadata)

Prints a combined summary to stdout and writes a JSON report to logs/processed/.
Also classifies case response text using the corporate audit schema classifier
when the schema module is available.

Usage:
    python scripts/causal_analysis.py [--cases-root cases] [--output-dir logs/processed]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Try to import the corporate audit schema for P1-P10 patterns
# ---------------------------------------------------------------------------

_SCHEMA_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCHEMA_ROOT))

try:
    from schema.corporate_audit_schema import PATTERNS as CORPORATE_PATTERNS
    from schema.classifier import classify_trace
    _SCHEMA_AVAILABLE = True
except ImportError:
    CORPORATE_PATTERNS = {}
    _SCHEMA_AVAILABLE = False


# ---------------------------------------------------------------------------
# Pattern definitions (S-01..S-05 → coded flags)
# ---------------------------------------------------------------------------

SABOTAGE_PATTERNS = {
    "S-01": {
        "name": "Vibe-Check Filter (RLHF Consensus Enforcement)",
        "flags": ["CONSENSUS", "PATHOLOGIZE"],
    },
    "S-02": {
        "name": "Zero-Click Enclosure",
        "flags": ["ATTRIBUTION_GAP"],
    },
    "S-03": {
        "name": "Attribution Gap",
        "flags": ["ATTRIBUTION_GAP"],
    },
    "S-04": {
        "name": "Mode Shift",
        "flags": ["MODE_SHIFT"],
    },
    "S-05": {
        "name": "Pathologizing Redirect",
        "flags": ["PATHOLOGIZE", "REFUSAL"],
    },
}

ALL_FLAGS = ["HEDGE", "REFUSAL", "CONSENSUS", "ATTRIBUTION_GAP", "MODE_SHIFT", "PATHOLOGIZE"]


# ---------------------------------------------------------------------------
# Case loader
# ---------------------------------------------------------------------------

def load_case(case_dir: Path) -> dict:
    """
    Load a case's metadata and return a structured dict.

    Parameters
    ----------
    case_dir : Path
        Case directory path.

    Returns
    -------
    dict with keys: case_id, metadata, flags, condition, prompt_class, patterns_detected
    """
    case_id = case_dir.name
    metadata_path = case_dir / "metadata.json"

    metadata = {}
    if metadata_path.is_file():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    flags = metadata.get("flags", {})
    condition = metadata.get("condition", "UNKNOWN")
    prompt_class = metadata.get("prompt_class", "UNKNOWN")
    patterns_detected = metadata.get("patterns_detected", [])

    return {
        "case_id": case_id,
        "metadata": metadata,
        "flags": flags,
        "condition": condition,
        "prompt_class": prompt_class,
        "patterns_detected": patterns_detected,
    }


def load_all_cases(cases_root: Path) -> list:
    """Load all case_* directories from cases_root."""
    cases = []
    if not cases_root.is_dir():
        return cases
    for d in sorted(cases_root.iterdir()):
        if d.is_dir() and d.name.startswith("case_"):
            cases.append(load_case(d))
    return cases


# ---------------------------------------------------------------------------
# Pattern aggregation
# ---------------------------------------------------------------------------

def aggregate_patterns(cases: list) -> dict:
    """
    Aggregate flag and pattern counts across all cases.

    Returns
    -------
    dict with:
        total_cases, populated_cases,
        flag_counts (dict flag -> count),
        pattern_counts (dict pattern_code -> count),
        by_condition (dict condition -> flag_counts)
    """
    total_cases = len(cases)
    populated_cases = 0
    flag_counts: dict = {f: 0 for f in ALL_FLAGS}
    pattern_counts: dict = {code: 0 for code in SABOTAGE_PATTERNS}
    # Corporate P1-P10 pattern counts
    corporate_pattern_counts: dict = {code: 0 for code in CORPORATE_PATTERNS} if CORPORATE_PATTERNS else {}
    by_condition: dict = {}
    entity_pattern_map: dict = {}  # entity -> list of patterns

    for case in cases:
        flags = case["flags"]
        condition = case["condition"]
        entity = case["metadata"].get("entity", "")
        detected = case.get("patterns_detected", [])

        # Check if case is populated (at least one non-None flag, or patterns detected)
        if any(v is not None for v in flags.values()) or detected:
            populated_cases += 1

        # Count LLM flags
        for flag in ALL_FLAGS:
            if flags.get(flag) is True:
                flag_counts[flag] += 1
                if condition not in by_condition:
                    by_condition[condition] = {f: 0 for f in ALL_FLAGS}
                by_condition[condition][flag] += 1

        # Count S-01..S-05 patterns (from patterns_detected list or infer from flags)
        for code in SABOTAGE_PATTERNS:
            if code in detected:
                pattern_counts[code] += 1
            else:
                # Infer from flags
                pattern_flags = SABOTAGE_PATTERNS[code]["flags"]
                if any(flags.get(f) is True for f in pattern_flags):
                    pattern_counts[code] += 1

        # Count P1-P10 corporate patterns (from patterns_detected list in metadata)
        for code in list(CORPORATE_PATTERNS.keys()):
            if code in detected:
                corporate_pattern_counts[code] = corporate_pattern_counts.get(code, 0) + 1
                if entity:
                    if entity not in entity_pattern_map:
                        entity_pattern_map[entity] = []
                    if code not in entity_pattern_map[entity]:
                        entity_pattern_map[entity].append(code)

    return {
        "total_cases": total_cases,
        "populated_cases": populated_cases,
        "flag_counts": flag_counts,
        "pattern_counts": pattern_counts,
        "corporate_pattern_counts": corporate_pattern_counts,
        "by_condition": by_condition,
        "entity_pattern_map": entity_pattern_map,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_summary(agg: dict) -> None:
    """Print a human-readable summary of pattern aggregation."""
    print("\n" + "=" * 60)
    print("IA-CYPHER CAUSAL ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"  Total cases:     {agg['total_cases']}")
    print(f"  Populated cases: {agg['populated_cases']}")
    print()

    # Corporate P1-P10 patterns
    corp_counts = agg.get("corporate_pattern_counts", {})
    if corp_counts and any(v > 0 for v in corp_counts.values()):
        print("  Corporate Audit Pattern Counts (P1..P10):")
        for code in sorted(corp_counts.keys()):
            count = corp_counts[code]
            name = CORPORATE_PATTERNS.get(code, {}).get("name", code) if CORPORATE_PATTERNS else code
            print(f"    {code}: {name:<45} {count} case(s)")
        print()

    # Entity -> pattern map
    emap = agg.get("entity_pattern_map", {})
    if emap:
        print("  Patterns by Entity:")
        for entity, patterns in sorted(emap.items()):
            print(f"    {entity}: {', '.join(sorted(patterns))}")
        print()

    print("  LLM Sabotage Pattern Counts (S-01..S-05):")
    for code, info in SABOTAGE_PATTERNS.items():
        count = agg["pattern_counts"].get(code, 0)
        print(f"    {code}: {info['name']:<45} {count} case(s)")
    print()

    print("  LLM Flag Counts:")
    for flag in ALL_FLAGS:
        count = agg["flag_counts"].get(flag, 0)
        print(f"    {flag:<20} {count} case(s)")
    print()

    if agg["by_condition"]:
        print("  LLM Flag Counts by Condition (A=web, B=offline):")
        for condition in sorted(agg["by_condition"]):
            print(f"    Condition {condition}:")
            for flag, count in agg["by_condition"][condition].items():
                if count > 0:
                    print(f"      {flag:<20} {count}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="IA-CYPHER-0002: Causal analysis over logged cases."
    )
    parser.add_argument(
        "--cases-root",
        dest="cases_root",
        default="cases",
        help="Root directory containing case_* subdirectories (default: cases)",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="logs/processed",
        help="Directory to write JSON summary output (default: logs/processed)",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    ia_root = script_dir.parent
    cases_root = ia_root / args.cases_root
    output_dir = ia_root / args.output_dir

    os.makedirs(output_dir, exist_ok=True)

    print(f"[causal_analysis] Loading cases from: {cases_root}")
    cases = load_all_cases(cases_root)
    print(f"[causal_analysis] Loaded {len(cases)} case(s).")

    agg = aggregate_patterns(cases)
    print_summary(agg)

    # Write JSON output
    timestamp = datetime.now(timezone.utc).isoformat()
    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = {
        "generated_at": timestamp,
        "cases_root": str(cases_root),
        "summary": agg,
        "pattern_definitions": SABOTAGE_PATTERNS,
    }
    output_path = output_dir / f"causal_analysis_{timestamp_slug}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"[causal_analysis] JSON summary written to: {output_path}")


if __name__ == "__main__":
    main()
