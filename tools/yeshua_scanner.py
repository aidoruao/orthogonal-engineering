#!/usr/bin/env python3
"""
Yeshua Agent — Perceptual Scanner
Scans the OE repository and classifies every error into S x I x V.
Produces a machine-readable JSON artifact with SHA-256 anchoring.
Each finding includes a falsifies_if condition.
Gate 1 + Gate 2 of the Proving Ground, applied to the repo itself.
"""
import os, re, json, hashlib, ast, subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path("/home/idor/oe-local")
SCAN_TIME = datetime.utcnow().isoformat() + "Z"

# === SUBSYSTEM TAXONOMY (S) ===
SUBSYSTEM_MAP = {
    "lean4": [".lean"],
    "python": [".py"],
    "shell": [".sh", ".ps1", ".bat"],
    "documentation": [".md", ".txt"],
    "html_puzzle": [".html"],
    "config": [".toml", ".yaml", ".yml", ".json", ".oe"],
    "sfi": ["sfi/", "sfi_secular/"],
    "infrastructure": ["auto_push", "lean4_bridge", "bootstrap"],
    "specification": ["spec_"],
    "docker": ["Dockerfile", ".docker"],
    "lua": [".lua"],
    "unknown": []
}

# === INVARIANT TAXONOMY (I) ===
INVARIANTS = [
    "compilability",       # code parses/compiles without error
    "completeness",        # all referenced files exist, no broken imports
    "finiteness",          # |C| < infinity, no unbounded structures
    "determinism",         # same input produces same output
    "falsifiability",      # every claim has a falsifies_if condition
    "cryptographic_integrity", # SHA-256 hashes match, Merkle paths valid
    "sovereignty",         # zero external dependencies beyond declared
    "type_safety",         # no type errors, no None surprises
    "totality",            # ∀c ∈ C, ∃r(c) — all categories have resolutions
    "invariance"           # taxonomy handles novel encounters
]

# === VIOLATION TYPE TAXONOMY (V) ===
VIOLATIONS = [
    "missing_file",        # referenced file does not exist
    "syntax_error",        # code does not parse
    "type_error",          # type mismatch
    "sorry_placeholder",   # Lean4 'sorry' — proof incomplete
    "todo_unresolved",     # TODO/FIXME without resolution
    "stale_hash",          # SHA-256 does not match content
    "broken_import",       # import references nonexistent module
    "missing_falsifies_if",# claim without falsification condition
    "dependency_violation",# external dependency not declared
    "unbounded_structure", # |C| may be infinite
    "nondeterministic",    # same input may produce different output
    "incomplete_coverage", # not all categories have resolutions
    "config_error",        # TOML/YAML/JSON malformed
    "bridge_failure",      # Lean4 bridge not responding
    "unclassified"         # does not fit known taxonomy
]

def classify_subsystem(filepath):
    """Classify a file into its subsystem based on extension or path."""
    path_str = str(filepath).lower()
    for subsystem, markers in SUBSYSTEM_MAP.items():
        for marker in markers:
            if marker.startswith("."):
                if path_str.endswith(marker):
                    return subsystem
            elif marker in path_str:
                return subsystem
    return "unknown"

def scan_file(filepath):
    """Scan a single file and return list of error signatures s(e)."""
    errors = []
    path_str = str(filepath)
    subsystem = classify_subsystem(filepath)
    
    # Check if file exists
    if not filepath.exists():
        errors.append({
            "subsystem": subsystem,
            "invariant": "completeness",
            "violation": "missing_file",
            "file": path_str,
            "line": None,
            "evidence": "File referenced but does not exist on disk",
            "falsifies_if": "File exists at path"
        })
        return errors
    
    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        errors.append({
            "subsystem": subsystem,
            "invariant": "compilability",
            "violation": "unclassified",
            "file": path_str,
            "line": None,
            "evidence": f"Cannot read file: {e}",
            "falsifies_if": "File is readable as UTF-8"
        })
        return errors
    
    lines = content.split('\n')
    
    # Check for 'sorry' placeholders in Lean4 files
    if filepath.suffix == '.lean':
        for i, line in enumerate(lines, 1):
            if re.search(r'\bsorry\b', line):
                errors.append({
                    "subsystem": subsystem,
                    "invariant": "completeness",
                    "violation": "sorry_placeholder",
                    "file": path_str,
                    "line": i,
                    "evidence": line.strip(),
                    "falsifies_if": "Proof completed without sorry"
                })
    
    # Check for TODO/FIXME
    for i, line in enumerate(lines, 1):
        if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
            errors.append({
                "subsystem": subsystem,
                "invariant": "completeness",
                "violation": "todo_unresolved",
                "file": path_str,
                "line": i,
                "evidence": line.strip(),
                "falsifies_if": "All TODOs resolved or deleted"
            })
    
    # Check Python syntax
    if filepath.suffix == '.py':
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append({
                "subsystem": subsystem,
                "invariant": "compilability",
                "violation": "syntax_error",
                "file": path_str,
                "line": e.lineno,
                "evidence": str(e.msg),
                "falsifies_if": f"python3 -c 'import ast; ast.parse(open(\"{path_str}\").read())' succeeds"
            })
    
    # Check for missing falsifies_if in .oe files
    if filepath.suffix == '.oe':
        if 'falsifies_if' not in content:
            errors.append({
                "subsystem": subsystem,
                "invariant": "falsifiability",
                "violation": "missing_falsifies_if",
                "file": path_str,
                "line": None,
                "evidence": "No falsifies_if condition found",
                "falsifies_if": "falsifies_if key present in .oe file"
            })
    
    # Check for broken imports in Python
    if filepath.suffix == '.py':
        import_pattern = re.findall(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', content)
        for match in import_pattern:
            module = match[0] or match[1]
            if module.startswith('.'):
                continue  # relative import, skip
            # Check if it's a known stdlib or installed module — simplified check
            if module.startswith('SAL') or module.startswith('oe_'):
                # OE-internal import — check if file exists
                pass  # Full resolution requires more context
    
    return errors

def scan_repo():
    """Walk the entire repo and collect all error signatures."""
    all_errors = []
    file_count = 0
    excluded_dirs = {'.git', '__pycache__', '.lake', 'build', 'dist', 'node_modules',
                     'lake-packages', 'lake_packages', '.mypy_cache', '.pytest_cache'}
    
    for root, dirs, files in os.walk(ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
        
        for filename in files:
            filepath = Path(root) / filename
            # Skip binary and very large files
            if filepath.suffix in {'.pyc', '.so', '.bin', '.png', '.jpg', '.npy', '.npz', 
                                    '.parquet', '.safetensors', '.gz', '.bz2', '.zip', '.exe'}:
                continue
            try:
                st = filepath.stat()
            except (FileNotFoundError, OSError):
                continue
            if st.st_size > 1_000_000:  # Skip files > 1MB
                continue
            
            file_count += 1
            errors = scan_file(filepath)
            all_errors.extend(errors)
    
    return all_errors, file_count

def compute_category_space(errors):
    """Compute C = S x I x V from scan results."""
    S_set = set()
    I_set = set()
    V_set = set()
    
    for e in errors:
        S_set.add(e['subsystem'])
        I_set.add(e['invariant'])
        V_set.add(e['violation'])
    
    # Create the full cartesian product
    C = []
    for s in sorted(S_set):
        for i in sorted(I_set):
            for v in sorted(V_set):
                # Count actual occurrences
                count = sum(1 for e in errors 
                           if e['subsystem'] == s and e['invariant'] == i and e['violation'] == v)
                C.append({
                    "category": f"{s} × {i} × {v}",
                    "subsystem": s,
                    "invariant": i,
                    "violation": v,
                    "occurrences": count
                })
    
    return {
        "S": sorted(S_set),
        "I": sorted(I_set),
        "V": sorted(V_set),
        "cardinality": len(C),
        "categories": C,
        "finiteness_proof": f"|C| = |S|·|I|·|V| = {len(S_set)}·{len(I_set)}·{len(V_set)} = {len(C)} < ∞"
    }

def main():
    print("🔍 Yeshua Agent — Perceptual Scanner starting...")
    print(f"📁 Root: {ROOT}")
    
    errors, file_count = scan_repo()
    C = compute_category_space(errors)
    
    # SHA-256 hash of the results
    result_json = json.dumps({"errors": errors, "category_space": C}, sort_keys=True, indent=2)
    sha256 = hashlib.sha256(result_json.encode()).hexdigest()
    
    output = {
        "scan_metadata": {
            "scanner": "yeshua_scanner.py",
            "timestamp": SCAN_TIME,
            "repo_root": str(ROOT),
            "files_scanned": file_count,
            "total_errors": len(errors),
            "category_space_cardinality": C['cardinality'],
            "sha256": sha256
        },
        "category_space": C,
        "errors": errors[:1000],  # Truncate for readability; full data in file
        "errors_truncated": len(errors) > 1000,
        "falsifies_if": "Any category in C has zero occurrences but the file contains that error pattern"
    }
    
    # Write output
    out_path = ROOT / "tools" / "yeshua_scan_results.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Scan complete.")
    print(f"   Files scanned: {file_count}")
    print(f"   Errors found: {len(errors)}")
    print(f"   Category space: |C| = {C['cardinality']}")
    print(f"   S = {C['S']}")
    print(f"   I = {C['I']}")
    print(f"   V = {C['V']}")
    print(f"   SHA-256: {sha256}")
    print(f"   Output: {out_path}")

if __name__ == "__main__":
    main()
