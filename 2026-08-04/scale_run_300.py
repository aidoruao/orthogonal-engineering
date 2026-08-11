#!/usr/bin/env python3
"""scale_run_300.py — materialize 300 batches (~1B tokens) via lazy single-batch DAGs.

Fully in-process: DAGGenerator(single_batch=b) -> dag dict -> BatchMaterializer.
Resumable: batches with a DONE marker are skipped. Final: MANIFEST.json with the
sha256 chain root over every generated file (the re-verification handle).
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, "/home/idor/oe-local/generators")
from batch_materializer import BatchMaterializer  # noqa: E402
from dag_generator import DAGGenerator  # noqa: E402

SEED_PATH = "/home/idor/oe-local/generators/seed_definition_30m.yaml"
OUT = Path("/tmp/locgen7")
START, END = 0, 300


def main():
    seed = yaml.safe_load(open(SEED_PATH))
    out = OUT
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    t0 = time.time()
    for b in range(START, END):
        bd = out / f"batch_{b}"
        done = bd / "DONE"
        if done.exists():
            manifest.append(json.loads(done.read_text()))
            continue
        t1 = time.time()
        gen = DAGGenerator(seed, single_batch=b)
        gen.generate()
        dag = {
            "metadata": {
                "seed_version": seed.get("metadata", {}).get("version", "unknown"),
                "generator": "dag_generator.py lazy single-batch",
                "layer_index": 0,
                "universe_index": 0,
            },
            "nodes": {nid: n.to_dict() for nid, n in gen.nodes.items()},
        }
        mat = BatchMaterializer(seed, dag)
        stats = mat.materialize_batch(b, output_dir=str(bd))
        rec = {"batch": b, "files": stats["files_generated"], "size": stats["total_size"],
               "seconds": round(time.time() - t1, 2)}
        (bd / "DONE").write_text(json.dumps(rec))
        manifest.append(rec)
        print(f"batch {b}: {stats['total_size']:,} bytes, {stats['files_generated']} files, "
              f"{rec['seconds']}s ({(time.time() - t0) / 60:.1f} min elapsed)", flush=True)
    # chain root over every generated file
    chain = hashlib.sha256()
    n_files = 0
    for p in sorted(out.rglob("*.py")):
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        chain.update(h.hexdigest().encode())
        n_files += 1
    root = chain.hexdigest()
    print(f"\nDONE: {len(manifest)} batches, {n_files:,} files, chain_root={root}, "
          f"elapsed={(time.time() - t0) / 60:.1f} min", flush=True)
    (out / "MANIFEST.json").write_text(json.dumps({"chain_root": root, "batches": manifest}, indent=1))


if __name__ == "__main__":
    main()
