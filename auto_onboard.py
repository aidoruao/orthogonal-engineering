"""auto_onboard.py — The Wand. One command orients a new AI steward.

Closes the continuity gap: any AI instance can run this and receive
full context — current checkpoint, active RCS codes, project state,
and the next queued task. No human needed for orientation.

Usage: python3 auto_onboard.py
"""

import json, os, hashlib, subprocess, sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()

def onboard():
    report = {
        "onboarded_at": datetime.now(timezone.utc).isoformat() + "Z",
        "repo": os.path.basename(REPO_ROOT),
    }

    # 1. Health check — is the environment functional?
    report["health"] = {}
    report["health"]["python"] = sys.version.split()[0]
    report["health"]["git"] = run("git --version").replace("git version ", "")
    report["health"]["yeshua_agent"] = os.path.exists("yeshua_agent.py")
    report["health"]["cuda"] = os.path.exists("/usr/local/cuda") or run("which nvidia-smi") != ""
    report["health"]["bootstrap_verify"] = os.path.exists("bootstrap_verify.py")
    report["health"]["lean4_bridge"] = os.path.exists("tools/lean4_bridge.py")
    report["health"]["merkle_root"] = os.path.exists("merkle/global_root.json")

    # 2. Current state — what checkpoint are we at?
    report["current_commit"] = run("git rev-parse HEAD")[:8]
    report["branch"] = run("git branch --show-current")
    report["remote"] = run("git remote get-url origin")

    # 3. Last checkpoint
    checkpoints = run("git log --oneline -1 -- docs/CHECKPOINT*.md")
    report["last_checkpoint"] = checkpoints if checkpoints else "None found"

    # 4. Active RCS codes from the map
    rcs_section = run("grep -A20 'RCS Code' docs/ARCHITECTURAL_MAP_UNIFIED_2026-05-24.md 2>/dev/null | head -15")
    report["active_rcs_codes"] = rcs_section if rcs_section else "See architectural map"

    # 5. What's queued?
    report["queued"] = {}
    # Check the last checkpoint for "QUEUED" or "Next" lines
    last_cp = run("git log --oneline -1 --name-only -- docs/CHECKPOINT*.md | tail -1")
    if last_cp:
        queued_lines = run(f"grep -i -E 'queued|next:' docs/{last_cp} 2>/dev/null | head -10")
        report["queued"]["from_checkpoint"] = queued_lines if queued_lines else "Read the last checkpoint"

    # 6. Project structure — key directories
    report["structure"] = {}
    for d in ["src/domains", "automation", "docs", "bootstrap", "tools", "specs"]:
        report["structure"][d] = os.path.exists(d)

    # 7. State hash
    state_json = json.dumps(report, sort_keys=True, default=str)
    # 8. Current Merkle root
    try:
        with open("merkle/global_root.json") as f:
            mr = json.load(f)
            report["merkle"] = {"root_hash": mr["root_hash"], "file_count": mr["file_count"]}
    except: report["merkle"] = "Not found"

    report["_hash"] = hashlib.sha256(state_json.encode()).hexdigest()

    return report

if __name__ == "__main__":
    result = onboard()
    print(json.dumps(result, indent=2))
