#!/usr/bin/env python3
"""
ingest_codebase.py — Full structural ingestion of any codebase into OE.
Produces: DAG, AST summary, Merkle tree, ontology classification, build gate audit.
One command. One output directory. No iterative loop.

Usage: python3 tools/ingest_codebase.py ~/godot-OE godot_oe_ingestion
"""
import os, sys, json, hashlib, re, ast as pyast
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except: return None

def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 tools/ingest_codebase.py <target_dir> <output_name>")
        sys.exit(1)
    
    target = Path(sys.argv[1]).resolve()
    out_name = sys.argv[2]
    out_dir = Path.home() / "oe-local" / "ingested" / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    
    EXCLUDE = {'.git', 'bin', 'obj', '__pycache__', 'node_modules', '.lake', 'build', 'thirdparty'}
    SKIP = {'.png','.jpg','.svg','.woff','.ttf','.ico','.wasm','.bin','.pck','.zip','.a','.o','.so'}
    
    # === PASS 1: Walk everything, collect data ===
    files = []
    dirs = defaultdict(list)
    from collections import Counter
    ext_counts = Counter()
    gates = []
    total_size = 0
    
    for root, dnames, fnames in os.walk(target):
        dnames[:] = [d for d in dnames if d not in EXCLUDE and not d.startswith('.')]
        rel_dir = str(Path(root).relative_to(target))
        
        # Classify directory
        if any(k in rel_dir for k in ['core','servers','scene','editor']): cat = 'engine_core'
        elif any(k in rel_dir for k in ['platform','drivers']): cat = 'platform'
        elif any(k in rel_dir for k in ['modules/mono','modules/dotnet']): cat = 'csharp_mono'
        elif any(k in rel_dir for k in ['platform/web']): cat = 'web_platform'
        elif any(k in rel_dir for k in ['thirdparty']): cat = 'third_party'
        elif any(k in rel_dir for k in ['doc','docs']): cat = 'docs'
        elif any(k in rel_dir for k in ['test']): cat = 'tests'
        else: cat = 'other'
        dirs[cat].append(rel_dir)
        
        for fname in fnames:
            ext = Path(fname).suffix.lower()
            if ext in SKIP: continue
            
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(target))
            sha = hash_file(fpath)
            if not sha: continue
            
            size = fpath.stat().st_size
            total_size += size
            ext_counts[ext] += 1
            
            # Extract imports/dependencies
            deps = []
            try:
                content = fpath.read_text(errors='ignore')[:10000]
                if ext in ['.cpp','.c','.h','.hpp']:
                    deps = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
                elif ext == '.py':
                    deps = re.findall(r'^(?:from\s+(\S+)\s+import|import\s+(\S+))', content, re.MULTILINE)
                    deps = [d[0] or d[1] for d in deps]
                elif ext == '.cs':
                    deps = re.findall(r'using\s+(\S+);', content)
                elif ext == '.lean':
                    deps = re.findall(r'^import\s+(\S+)', content, re.MULTILINE)
            except: pass
            
            files.append({
                "path": rel, "ext": ext, "sha256": sha, "size": size,
                "deps": deps[:20], "dep_count": len(deps)
            })
            
            # Build gate detection
            if ext in ['.py'] and fname in ['config.py','detect.py','SCsub']:
                for i, line in enumerate(content.split('\n'), 1):
                    if 'print_error' in line or 'sys.exit' in line:
                        gates.append({"file": rel, "line": i, "message": line.strip()[:120]})
    
    # === PASS 2: Build outputs ===
    
    # 1. DAG
    dag = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "source": str(target),
        "total_files": len(files),
        "total_edges": sum(f["dep_count"] for f in files),
        "nodes": [{"id": f["path"], "ext": f["ext"], "sha256": f["sha256"][:16]} for f in files],
        "edges": [{"from": f["path"], "to": d} for f in files for d in f["deps"][:5]],
        "falsifies_if": "Any edge target not found in nodes"
    }
    dag["_sha256"] = hash_string(json.dumps(dag, sort_keys=True))
    
    # 2. Merkle tree
    leaf_hashes = sorted([f["sha256"] for f in files])
    while len(leaf_hashes) > 1:
        if len(leaf_hashes) % 2 == 1: leaf_hashes.append(leaf_hashes[-1])
        leaf_hashes = [hash_string(leaf_hashes[i] + leaf_hashes[i+1]) for i in range(0, len(leaf_hashes), 2)]
    merkle = {"root": leaf_hashes[0] if leaf_hashes else "empty", "leaves": len(files)}
    
    # 3. Ontology
    ontology = {
        "directories": {k: len(v) for k, v in dirs.items()},
        "extensions": dict(ext_counts.most_common(30)),
        "total_files": len(files),
        "total_size_mb": round(total_size / (1024*1024), 1)
    }
    
    # 4. Build gates
    gate_report = {
        "total_gates": len(gates),
        "by_file": defaultdict(int)
    }
    for g in gates: gate_report["by_file"][g["file"]] += 1
    gate_report["by_file"] = dict(gate_report["by_file"])
    gate_report["gates"] = gates
    
    # 5. AST summary (Python files only)
    ast_summary = {"total_python_files": 0, "total_functions": 0, "total_classes": 0}
    for f in files:
        if f["ext"] == '.py':
            ast_summary["total_python_files"] += 1
            try:
                tree = pyast.parse(Path(target)/f["path"]).read_text()
                # rough count
                ast_summary["total_functions"] += tree.count("def ")
                ast_summary["total_classes"] += tree.count("class ")
            except: pass
    
    # === WRITE ALL OUTPUTS ===
    outputs = {
        "dag.json": dag,
        "merkle.json": merkle,
        "ontology.json": ontology,
        "build_gates.json": gate_report,
        "ast_summary.json": ast_summary,
    }
    
    for fname, data in outputs.items():
        with open(out_dir / fname, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Master manifest
    manifest = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": str(target),
        "outputs": {fname: str(out_dir / fname) for fname in outputs},
        "falsifies_if": "Any output file missing or hash mismatched"
    }
    manifest["_sha256"] = hash_string(json.dumps(manifest, sort_keys=True))
    with open(out_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Ingested: {len(files)} files, {total_size/1024/1024:.0f} MB")
    print(f"DAG: {dag['total_nodes']} nodes, {dag['total_edges']} edges")
    print(f"Merkle root: {merkle['root'][:32]}...")
    print(f"Build gates: {len(gates)} found")
    print(f"Output: {out_dir}")
    for fname in outputs:
        print(f"  {out_dir / fname}")

if __name__ == "__main__":
    main()
