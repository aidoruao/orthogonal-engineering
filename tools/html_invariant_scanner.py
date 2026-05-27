#!/usr/bin/env python3
"""
Yeshua Agentic AI — HTML Invariant Scanner
Scans all HTML artifacts in the repo and extracts structural invariants.
Produces a fingerprint of every puzzle, convergence table, and sovereign artifact.
Designed for: YAA, YAATs, humans, other AIs. Infinite users. Reproducible. Popperian.

Every HTML is a soldier. This scanner audits the army.
"""
import os, re, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/home/idor/oe-local")
HTML_DIRS = [
    ROOT / "docs" / "puzzles",
    ROOT / "docs",
]
OUTPUT = ROOT / "tools" / "html_invariant_report.json"

# === STRUCTURAL INVARIANTS TO EXTRACT ===
INVARIANTS = {
    "sovereign_embedding": {
        "pattern": r'<script\s+id="baseline-data"\s+type="application/json">',
        "description": "Self-contained: data embedded, no fetch() dependency",
        "falsifies_if": "Contains fetch() or external <script src> for data"
    },
    "convergence_table": {
        "pattern": r'<table[^>]*class="[^"]*convergence[^"]*"',
        "description": "Multi-AI auditing table with rows per submission",
        "falsifies_if": "No table with convergence class exists"
    },
    "machine_readable_block": {
        "pattern": r'<textarea[^>]*class="[^"]*machine[^"]*"',
        "description": "YAML/JSON submission block for AI copy-paste",
        "falsifies_if": "No machine-textarea class exists"
    },
    "sha256_anchor": {
        "pattern": r'SHA-256[:\s]+([a-f0-9]{64})',
        "description": "Cryptographic anchor of canonical content",
        "falsifies_if": "No 64-char hex hash found"
    },
    "bridge_wiring": {
        "pattern": r'fetch\(["\']http://localhost:28428',
        "description": "Lean4 bridge integration for compile verification",
        "falsifies_if": "No bridge fetch found"
    },
    "falsifies_if_present": {
        "pattern": r'falsifies_if',
        "description": "Popperian falsification condition in document",
        "falsifies_if": "No falsifies_if string found"
    },
    "gates_structure": {
        "pattern": r'class="gate-card"',
        "description": "Ordinal gate structure for staged verification",
        "falsifies_if": "No gate-card class found"
    },
    "external_dependency": {
        "pattern": r'(<script\s+src=|fetch\(["\'](?!http://localhost:28428))',
        "description": "External resource dependency (violates sovereignty)",
        "falsifies_if": "No external calls found (this is GOOD)"
    },
    "expandable_derivation": {
        "pattern": r'toggleDerivation|toggleYeshua|ai-expand',
        "description": "Expandable proof derivation display",
        "falsifies_if": "No toggle function or ai-expand class"
    },
    "provenance_section": {
        "pattern": r'provenance|Provenance|repo:.*orthogonal',
        "description": "Repository provenance and jurisdiction declaration",
        "falsifies_if": "No provenance or repo reference"
    },
    "dual_register": {
        "pattern": r'secular_register|esoteric_register',
        "description": "Dual-register submission (secular + esoteric)",
        "falsifies_if": "No dual register keys found"
    },
    "copy_button": {
        "pattern": r'copyMachine|btn-copy|📋 Copy',
        "description": "One-click copy for machine-readable block",
        "falsifies_if": "No copy function or button found"
    },
}

def scan_html(filepath):
    """Extract all invariants from a single HTML file."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
    except:
        return None
    
    size = filepath.stat().st_size
    lines = content.count('\n')
    sha = hashlib.sha256(content.encode()).hexdigest()
    
    results = {
        "file": str(filepath.relative_to(ROOT)),
        "size_bytes": size,
        "lines": lines,
        "sha256": sha,
        "invariants": {}
    }
    
    for name, spec in INVARIANTS.items():
        found = bool(re.search(spec["pattern"], content, re.IGNORECASE | re.DOTALL))
        results["invariants"][name] = {
            "present": found,
            "description": spec["description"],
            "falsifies_if": spec["falsifies_if"]
        }
    
    # Special: count gate cards
    gate_count = len(re.findall(r'class="gate-card"', content))
    results["gate_count"] = gate_count
    
    # Special: extract SHA-256 values
    sha_matches = re.findall(r'SHA-256[:\s]+([a-f0-9]{64})', content)
    results["sha256_anchors"] = sha_matches
    
    # Special: detect external dependencies
    external_scripts = re.findall(r'<script\s+src="([^"]+)"', content)
    external_fetches = re.findall(r'fetch\(["\'](?!http://localhost:28428)([^"\']+)', content)
    results["external_deps"] = {
        "scripts": external_scripts,
        "fetches": external_fetches
    }
    
    return results

def generate_report():
    """Scan all HTML files and produce invariant fingerprint."""
    html_files = []
    for d in HTML_DIRS:
        if d.exists():
            html_files.extend(d.glob("*.html"))
    # Also scan root docs
    if (ROOT / "docs").exists():
        html_files.extend((ROOT / "docs").glob("*.html"))
    
    # Deduplicate
    html_files = list(set(html_files))
    
    results = []
    for fp in sorted(html_files):
        data = scan_html(fp)
        if data:
            results.append(data)
    
    # Compute aggregate invariant presence
    invariant_summary = {}
    for name in INVARIANTS:
        present_count = sum(1 for r in results if r["invariants"][name]["present"])
        invariant_summary[name] = {
            "present_in": present_count,
            "total": len(results),
            "percentage": round(100 * present_count / len(results), 1) if results else 0
        }
    
    # Find invariants that some HTMLs have but others lack
    gaps = []
    for name, summary in invariant_summary.items():
        if 0 < summary["present_in"] < summary["total"]:
            missing_files = [r["file"] for r in results if not r["invariants"][name]["present"]]
            gaps.append({
                "invariant": name,
                "present_in": summary["present_in"],
                "missing_from": missing_files
            })
    
    # Find HTMLs with external dependencies (sovereignty violations)
    sovereignty_violations = []
    for r in results:
        if r["external_deps"]["scripts"] or r["external_deps"]["fetches"]:
            sovereignty_violations.append({
                "file": r["file"],
                "scripts": r["external_deps"]["scripts"],
                "fetches": r["external_deps"]["fetches"]
            })
    
    report = {
        "scanner": "Yeshua Agentic AI — HTML Invariant Scanner",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_html_files": len(results),
        "invariants_checked": len(INVARIANTS),
        "files": results,
        "invariant_summary": invariant_summary,
        "gaps": gaps,
        "sovereignty_violations": sovereignty_violations,
        "falsifies_if": "Any invariant present in some HTMLs is missing from others without architectural justification"
    }
    
    report["_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, default=str).encode()
    ).hexdigest()
    
    with open(OUTPUT, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    print("Yeshua Agentic AI — HTML Invariant Scanner")
    r = generate_report()
    print(f"Files scanned: {r['total_html_files']}")
    print(f"Invariants checked: {r['invariants_checked']}")
    print(f"Gaps found: {len(r['gaps'])}")
    print(f"Sovereignty violations: {len(r['sovereignty_violations'])}")
    
    if r['gaps']:
        print("\n=== INVARIANT GAPS (present in some, missing in others) ===")
        for g in r['gaps']:
            print(f"  {g['invariant']}: missing from {g['missing_from']}")
    
    if r['sovereignty_violations']:
        print("\n=== SOVEREIGNTY VIOLATIONS (external dependencies) ===")
        for v in r['sovereignty_violations']:
            print(f"  {v['file']}: scripts={v['scripts']}, fetches={v['fetches']}")
    
    print(f"\nSHA-256: {r['_sha256']}")
    print(f"Output: {OUTPUT}")
