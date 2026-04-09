"""Generate a new case study skeleton.

Usage: python case_studies/framework/generate_case_study.py \
  --id CS_GMOD_001 \
  --category game_mods \
  --name "vulkanmod_755" \
  --repo "https://github.com/xCollateral/VulkanMod" \
  --issue "https://github.com/xCollateral/VulkanMod/issues/755" \
  --language Java \
  --domain D_GRAPHICS
"""
import argparse
import json
import hashlib
from pathlib import Path
from datetime import date

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--domain", required=True, nargs="+")
    args = parser.parse_args()

    dir_path = Path(f"case_studies/category_{args.category}/{args.name}")
    dir_path.mkdir(parents=True, exist_ok=True)

    gap = {
        "id": args.id,
        "issue_url": args.issue,
        "repository": args.repo,
        "language": args.language,
        "framework": "",
        "analysis_date": str(date.today()),
        "status": "INVESTIGATION",
        "domain_mapping": args.domain,
        "findings": {
            "summary": "TODO: Describe the issue",
            "root_cause": "TODO: Identify root cause with code quotes",
            "affected_components": [],
            "invariant_violations": []
        },
        "code_locations": [],
        "fix_proposal": {
            "description": "TODO: Describe the fix",
            "changes": []
        },
        "falsification": {
            "condition": "TODO: Under what condition is this fix wrong?",
            "test_id": f"F_{args.domain[0].replace('D_', '')}_XXX"
        },
        "sha256_hash": ""
    }
    content = json.dumps({k: v for k, v in sorted(gap.items())
                         if k != "sha256_hash"}, sort_keys=True)
    gap["sha256_hash"] = hashlib.sha256(content.encode()).hexdigest()

    (dir_path / "gap_analysis.json").write_text(
        json.dumps(gap, indent=2) + "\n")

    (dir_path / "pr_description.md").write_text(
        f"# {args.name}\n\n"
        f"**Issue:** {args.issue}\n"
        f"**Repository:** {args.repo}\n"
        f"**Language:** {args.language}\n\n"
        "## Root Cause\n\nTODO\n\n"
        "## Fix\n\nTODO\n\n"
        "## Why This Works\n\nTODO\n\n"
        "## Testing\n\nTODO\n")

    (dir_path / "test_specification.md").write_text(
        f"# Test Specification: {args.name}\n\n"
        "## Positive Tests\n\nTODO\n\n"
        "## Negative Tests (Reproduce Original Bug)\n\nTODO\n\n"
        "## Regression Tests\n\nTODO\n")

    (dir_path / "ATTRIBUTION.md").write_text(
        f"# Attribution\n\n"
        f"- **Repository:** {args.repo}\n"
        f"- **Issue:** {args.issue}\n"
        f"- **License:** TODO (check repo license)\n"
        f"- **Original Authors:** TODO\n"
        f"- **Analysis Date:** {date.today()}\n"
        f"- **Non-Affiliation:** This analysis is independent. "
        f"aidoruao is not affiliated with the original repository.\n")

    print(f"Created case study at {dir_path}/")
    print(f"  gap_analysis.json (hash: {gap['sha256_hash'][:16]}...)")
    print(f"  pr_description.md")
    print(f"  test_specification.md")
    print(f"  ATTRIBUTION.md")

if __name__ == "__main__":
    main()
