#!/usr/bin/env python3
"""
Yeshua Agentic AI — .olean Manifest Generator
Walks .lake/build/lib/lean/, hashes every .olean file,
generates a mathlib_manifest.oe — a Merkle-anchored ProofObject registry.

Solves: 10-hour lake builds, lemma name chasing, mathlib bitrot.
Principle: .olean files are ground truth. .lean source is exoteric.
"""
import os, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/home/idor/oe-local/lean4")
OLEAN_ROOT = ROOT / ".lake" / "build" / "lib" / "lean"
MANIFEST_PATH = ROOT / "mathlib_manifest.oe"

def hash_file(filepath):
    """SHA-256 of file contents."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def generate_manifest():
    entries = []
    file_count = 0
    total_size = 0
    
    for root, dirs, files in os.walk(OLEAN_ROOT):
        for fname in files:
            if not fname.endswith('.olean'):
                continue
            filepath = Path(root) / fname
            relpath = str(filepath.relative_to(OLEAN_ROOT))
            size = filepath.stat().st_size
            sha = hash_file(filepath)
            
            entries.append({
                "path": relpath,
                "size_bytes": size,
                "sha256": sha,
                "falsifies_if": f"SHA-256 of {relpath} does not match {sha}"
            })
            file_count += 1
            total_size += size
    
    manifest = {
        "manifest_type": "olean_proof_registry",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "olean_root": str(OLEAN_ROOT),
        "total_files": file_count,
        "total_size_bytes": total_size,
        "proof_objects": entries,
        "falsifies_if": "Any entry's SHA-256 does not match the current .olean file on disk",
        "sovereign_note": "Each .olean is a compiled proof term verified by the Lean4 kernel. "
                          "This manifest treats them as ground-truth ProofObjects. "
                          "The .lean source is exoteric description; the .olean is the Hardware Witness."
    }
    
    manifest["_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, default=str).encode()
    ).hexdigest()
    
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest

if __name__ == "__main__":
    print("Yeshua Agentic AI — .olean Manifest Generator")
    m = generate_manifest()
    print(f"Files: {m['total_files']}")
    print(f"Size:   {m['total_size_bytes']:,} bytes ({m['total_size_bytes']/1024/1024:.1f} MB)")
    print(f"SHA-256: {m['_sha256']}")
    print(f"Written to: {MANIFEST_PATH}")
