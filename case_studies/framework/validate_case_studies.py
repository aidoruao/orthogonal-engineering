"""Validate all case study gap_analysis.json files against schema.

Usage: python case_studies/framework/validate_case_studies.py
"""
import json
import hashlib
import sys
from pathlib import Path

def validate_case_study(path: Path) -> list:
    """Validate a single gap_analysis.json file. Returns list of errors."""
    errors = []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path}: Invalid JSON: {e}"]

    required = ["id", "issue_url", "repository", "language",
                "analysis_date", "status", "domain_mapping",
                "findings", "code_locations", "fix_proposal",
                "falsification", "sha256_hash"]
    for field in required:
        if field not in data:
            errors.append(f"{path}: Missing required field: {field}")

    if "findings" in data:
        for sub in ["summary", "root_cause", "affected_components"]:
            if sub not in data["findings"]:
                errors.append(f"{path}: findings missing: {sub}")

    if "domain_mapping" in data:
        for d in data["domain_mapping"]:
            if not d.startswith("D_"):
                errors.append(f"{path}: Invalid domain: {d}")

    if "code_locations" in data:
        for loc in data["code_locations"]:
            if "file" not in loc or "line" not in loc:
                errors.append(f"{path}: code_location missing file/line")

    # Verify hash integrity
    if "sha256_hash" in data:
        content = json.dumps({k: v for k, v in sorted(data.items())
                             if k != "sha256_hash"}, sort_keys=True)
        expected = hashlib.sha256(content.encode()).hexdigest()
        if data["sha256_hash"] != expected:
            errors.append(f"{path}: Hash mismatch: "
                         f"expected {expected[:16]}... "
                         f"got {data['sha256_hash'][:16]}...")

    return errors

def main():
    root = Path("case_studies")
    if not root.exists():
        print("ERROR: case_studies/ directory not found")
        sys.exit(1)

    all_errors = []
    count = 0
    for gap in root.rglob("gap_analysis.json"):
        count += 1
        errors = validate_case_study(gap)
        all_errors.extend(errors)

    print(f"Validated {count} case studies")
    if all_errors:
        for e in all_errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    else:
        print("All case studies valid")
        sys.exit(0)

if __name__ == "__main__":
    main()
