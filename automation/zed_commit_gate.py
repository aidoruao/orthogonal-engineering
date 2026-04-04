#!/usr/bin/env python3
"""
ZED IDE / AI AGENT COMMIT ENFORCEMENT GATE
Prevents PHANTOM-EDIT-001 class failures.

Run at end of every AI agent session:
  python automation/zed_commit_gate.py

Exit codes:
  0 = All changes committed
  2 = Uncommitted changes detected (BOUNDARY VIOLATION)
"""
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


def check_uncommitted():
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    return [
        line for line in result.stdout.strip().split("\n")
        if line.strip()
    ]


def main():
    uncommitted = check_uncommitted()
    if not uncommitted:
        print("COMMIT GATE: PASS - No uncommitted changes.")
        sys.exit(0)

    print("COMMIT GATE: FAIL - BOUNDARY VIOLATION (exit code 2)")
    print(f"Uncommitted files ({len(uncommitted)}):")
    for f in uncommitted:
        print(f"  {f}")
    print()
    print("ACTION REQUIRED: git add + git commit + git push before ending session.")
    print("FAILURE CLASS: PHANTOM-EDIT-001")

    log_dir = Path("failure_log")
    log_dir.mkdir(exist_ok=True)
    violation = {
        "timestamp": datetime.now().isoformat(),
        "type": "PHANTOM-EDIT-PREVENTION",
        "uncommitted_files": uncommitted,
        "action": "Session blocked until committed"
    }
    log_file = log_dir / f"commit_gate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(violation, indent=2))
    sys.exit(2)


if __name__ == "__main__":
    main()
