#!/usr/bin/env python3
"""verify_chain_root.py — independently re-verify the 1B-corpus chain root.

Replicates scale_run_300.py's canonical root construction exactly:
    root = sha256( concat( sorted(rglob("*.py")) per-file sha256 hexdigests ) )
and compares against the manifest's recorded chain_root (full 64-hex match).

Usage: python3 verify_chain_root.py [corpus_dir] [manifest_path]
Exit 0 = full root match, 1 = mismatch, 2 = manifest missing.
"""
import hashlib
import json
import sys
from pathlib import Path

CORPUS = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/locgen7")
MANIFEST = Path(sys.argv[2] if len(sys.argv) > 2 else
                "/home/idor/oe-local/2026-08-04/locgen7_MANIFEST.json")


def main():
    if not MANIFEST.is_file():
        print("FAIL: manifest not found"); sys.exit(2)
    recorded = json.loads(MANIFEST.read_text())["chain_root"]
    chain = hashlib.sha256()
    n = 0
    for p in sorted(CORPUS.rglob("*.py")):
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        chain.update(h.hexdigest().encode())
        n += 1
    root = chain.hexdigest()
    print(f"files hashed: {n}")
    print(f"recorded: {recorded}")
    print(f"recomputed: {root}")
    ok = root == recorded
    print(f"verdict: {'ROOT MATCH' if ok else 'ROOT MISMATCH'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
