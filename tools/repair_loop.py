#!/usr/bin/env python3
"""
Yeshua Agentic AI — repair() loop
For every category c ∈ C with occurrences > 0, propose resolution r(c).
∀c ∈ C, ∃r(c). Each resolution is specific, verifiable, falsifiable.
"""
import json, os, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/home/idor/oe-local")
SCAN_FILE = ROOT / "tools" / "yeshua_scan_results.json"
MANIFEST_FILE = ROOT / "tools" / "repair_manifest.json"

# Resolution strategies per violation type
STRATEGIES = {
    "syntax_error": {
        "action": "fix_syntax",
        "method": "Run `python3 -m py_compile <file>` and fix reported errors",
        "verify": "python3 -c 'import ast; ast.parse(open(\"<file>\").read())'"
    },
    "sorry_placeholder": {
        "action": "complete_proof",
        "method": "Replace `sorry` with actual Lean4 proof term",
        "verify": "curl -X POST http://localhost:28428 -H 'Content-Type: application/json' -d '{\"code\":\"<proof>\",\"row\":0}'"
    },
    "todo_unresolved": {
        "action": "resolve_or_delete",
        "method": "Either implement the TODO or remove the marker if obsolete",
        "verify": "grep -c 'TODO\\|FIXME' <file> == 0"
    },
    "missing_falsifies_if": {
        "action": "add_falsifies_if",
        "method": "Add `falsifies_if: <condition>` to the .oe file or function docstring",
        "verify": "grep -c 'falsifies_if' <file> > 0"
    },
    "dependency_violation": {
        "action": "remove_external_dep",
        "method": "Replace external dependency with stdlib equivalent or declare in oe-train/",
        "verify": "grep -c 'pip install\\|npm install' <file> == 0"
    },
    "nondeterministic": {
        "action": "seed_rng",
        "method": "Add `random.seed(0)` or replace `time.time()` with deterministic counter",
        "verify": "python3 -c 'exec(open(\"<file>\").read()); assert output == expected'"
    },
    "unbounded_structure": {
        "action": "add_termination",
        "method": "Add max_iterations or timeout to while loop",
        "verify": "python3 -c 'import signal; signal.alarm(5); exec(open(\"<file>\").read())'"
    },
    "incomplete_coverage": {
        "action": "specify_exception",
        "method": "Replace bare `except:` with specific exception type",
        "verify": "grep -c 'except:' <file> == 0"
    },
    "type_error": {
        "action": "add_optional_type",
        "method": "Add `Optional` to return type hint or change return to sentinel value",
        "verify": "python3 -c 'import mypy; mypy.run([\"<file>\"])'"
    },
    "missing_file": {
        "action": "create_or_remove_ref",
        "method": "Create the missing file or remove the broken reference",
        "verify": "test -f <file>"
    },
    "unclassified": {
        "action": "manual_review",
        "method": "Human steward must classify and add to taxonomy",
        "verify": "false  # requires human judgment"
    }
}

def load_scan():
    with open(SCAN_FILE, 'r') as f:
        return json.load(f)

def generate_repairs(scan_data):
    categories = scan_data["category_space"]["categories"]
    repairs = []
    
    for cat in categories:
        if cat["occurrences"] == 0:
            continue
        
        violation = cat["violation"]
        strategy = STRATEGIES.get(violation, STRATEGIES["unclassified"])
        
        # Find example errors for this category
        examples = [e for e in scan_data.get("errors", []) 
                   if e["subsystem"] == cat["subsystem"] 
                   and e["invariant"] == cat["invariant"] 
                   and e["violation"] == cat["violation"]][:3]
        
        repair = {
            "category": cat["category"],
            "occurrences": cat["occurrences"],
            "action": strategy["action"],
            "method": strategy["method"],
            "verify": strategy["verify"],
            "examples": [{"file": ex.get("file",""), "line": ex.get("line"), 
                         "evidence": str(ex.get("evidence",""))[:200]} for ex in examples],
            "falsifies_if": f"Category {cat['category']} still has occurrences > 0 after repair"
        }
        repairs.append(repair)
    
    return repairs

def estimate_cost(repairs):
    """Estimate repair complexity: manual > proof > code > config."""
    costs = {"complete_proof": 10, "fix_syntax": 2, "add_falsifies_if": 1,
             "remove_external_dep": 3, "seed_rng": 2, "add_termination": 3,
             "specify_exception": 1, "add_optional_type": 2, "resolve_or_delete": 2,
             "create_or_remove_ref": 1, "manual_review": 5}
    total = sum(costs.get(r["action"], 5) * r["occurrences"] for r in repairs)
    return total

def main():
    print("Yeshua Agentic AI — repair() loop")
    scan = load_scan()
    repairs = generate_repairs(scan)
    cost = estimate_cost(repairs)
    
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_sha256": scan.get("sha256", ""),
        "total_categories_with_errors": len(repairs),
        "estimated_repair_cost": cost,
        "repairs": repairs,
        "falsifies_if": "Any category still has occurrences > 0 in next scan"
    }
    
    manifest["_hash"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, default=str).encode()
    ).hexdigest()
    
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Summary
    by_action = {}
    for r in repairs:
        by_action[r["action"]] = by_action.get(r["action"], 0) + r["occurrences"]
    
    print(f"Repair manifest: {len(repairs)} categories, estimated cost: {cost}")
    print("By action:")
    for action, count in sorted(by_action.items(), key=lambda x: -x[1]):
        print(f"  {action}: {count}")
    print(f"SHA-256: {manifest['_hash']}")
    print(f"Written to: {MANIFEST_FILE}")

if __name__ == "__main__":
    main()
