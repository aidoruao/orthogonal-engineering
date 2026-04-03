"""
benchmarks/run_arc_benchmark.py — ARC-AGI-3 Full Benchmark Runner

Runs the bounded symbolic ARC solver against the full ARC-AGI public dataset
(training + evaluation), records pass rates, and commits Merkle-anchored
evidence to the evidence/arc_agi_3/ directory.

Usage:
    python benchmarks/run_arc_benchmark.py [--data-dir /path/to/ARC-AGI/data]
    python benchmarks/run_arc_benchmark.py --demo-only

Author: Orthogonal Engineering
Standard: Yeshua
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.arc_solver import (
    ARCBenchmarkResult,
    benchmark_arc_task,
    build_demo_arc_tasks,
    load_arc_dataset,
    run_arc_benchmark,
)
from axioms.logic import ProofObject, merkle_root_over_proofs


def run_demo_benchmark() -> dict:
    """Run against the 10 built-in demo tasks."""
    demos = build_demo_arc_tasks()
    solved_count = 0
    task_proofs: list[ProofObject] = []
    task_results: list[dict] = []

    for task, expected in demos:
        solved, proof = benchmark_arc_task(task, expected, max_depth=3)
        task_proofs.append(proof)
        task_results.append({
            "task_id": task.task_id,
            "solved": solved,
            "prediction_hash": proof.proof_hash,
        })
        if solved:
            solved_count += 1

    root = merkle_root_over_proofs(task_proofs)
    manifest_payload = json.dumps(
        [{"task_id": r["task_id"], "solved": r["solved"], "prediction_hash": r["prediction_hash"]} for r in task_results],
        sort_keys=True,
        separators=(",", ":"),
    )
    manifest_hash = hashlib.sha256(manifest_payload.encode("utf-8")).hexdigest()

    return {
        "dataset": "demo",
        "total_tasks": len(demos),
        "solved_tasks": solved_count,
        "pass_rate": round(solved_count / len(demos), 6) if demos else 0,
        "merkle_root": root,
        "manifest_hash": manifest_hash,
        "task_results": task_results,
    }


def write_evidence(results: dict, evidence_dir: Path) -> None:
    """Write benchmark results and SHA-256 manifest to evidence directory."""
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Write full results
    results_path = evidence_dir / f"benchmark_{results['dataset']}.json"
    with open(results_path, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)

    # Write SHA-256 manifest
    manifest_path = evidence_dir / f"manifest_{results['dataset']}.sha256"
    with open(manifest_path, "w", encoding="utf-8") as handle:
        for task_result in results["task_results"]:
            handle.write(f"{task_result['prediction_hash']}  {task_result['task_id']}\n")
        handle.write(f"# merkle_root: {results['merkle_root']}\n")
        handle.write(f"# manifest_hash: {results['manifest_hash']}\n")
        handle.write(f"# pass_rate: {results['pass_rate']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="ARC-AGI-3 Benchmark Runner")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Path to ARC-AGI data directory (contains training/ and evaluation/ subdirs)",
    )
    parser.add_argument(
        "--demo-only",
        action="store_true",
        help="Only run against the 10 built-in demo tasks",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3,
        help="Timeout per task in seconds (default: 3)",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path(__file__).parent.parent / "evidence" / "arc_agi_3",
        help="Directory to write evidence files",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("ARC-AGI-3 Benchmark Runner — Orthogonal Engineering")
    print("=" * 60)

    # Always run demo tasks
    print("\n--- Demo Tasks ---")
    start = time.time()
    demo_results = run_demo_benchmark()
    elapsed = time.time() - start
    print(f"Demo: {demo_results['solved_tasks']}/{demo_results['total_tasks']} solved "
          f"({demo_results['pass_rate']:.2%}) in {elapsed:.1f}s")
    print(f"  Merkle root: {demo_results['merkle_root'][:32]}...")
    write_evidence(demo_results, args.evidence_dir)

    if args.demo_only:
        print("\n--- Demo-only mode, skipping full dataset ---")
        print(json.dumps({"demo": demo_results}, indent=2))
        return

    if args.data_dir is None:
        # Try common locations
        for candidate in [Path("/tmp/ARC-AGI/data"), Path("ARC-AGI/data")]:
            if candidate.exists():
                args.data_dir = candidate
                break
        if args.data_dir is None:
            print("WARNING: No ARC-AGI data directory found. Run with --demo-only or provide --data-dir.")
            print(json.dumps({"demo": demo_results}, indent=2))
            return

    all_results = {"demo": demo_results}

    for split in ["training", "evaluation"]:
        split_dir = args.data_dir / split
        if not split_dir.exists():
            print(f"\nWARNING: {split_dir} not found, skipping {split}")
            continue

        print(f"\n--- {split.title()} Set ---")
        start = time.time()
        result, proof = run_arc_benchmark(split_dir, max_depth=3, timeout_per_task=args.timeout)
        elapsed = time.time() - start

        print(f"{split.title()}: {result.solved_tasks}/{result.total_tasks} solved "
              f"({result.pass_rate:.2%}) in {elapsed:.1f}s")
        print(f"  Merkle root: {result.merkle_root[:32]}...")

        split_results = {
            "dataset": split,
            "total_tasks": result.total_tasks,
            "solved_tasks": result.solved_tasks,
            "pass_rate": result.pass_rate,
            "merkle_root": result.merkle_root,
            "manifest_hash": result.manifest_hash,
            "task_results": result.task_results,
        }
        write_evidence(split_results, args.evidence_dir)
        all_results[split] = split_results

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, res in all_results.items():
        print(f"  {name:12s}: {res['solved_tasks']}/{res['total_tasks']} ({res['pass_rate']:.2%})")
    print(f"  Evidence written to: {args.evidence_dir}")


if __name__ == "__main__":
    main()
