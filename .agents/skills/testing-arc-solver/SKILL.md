# Testing: ARC-AGI Solver & Benchmark Pipeline

## Overview
The ARC-AGI solver is a bounded symbolic solver in `axioms/arc_solver.py` that uses DSL enumeration and pattern recognition (`axioms/pattern_recognition.py`) to solve ARC-AGI tasks. The benchmark runner (`benchmarks/run_arc_benchmark.py`) runs the solver against full datasets and generates Merkle-anchored evidence.

## Prerequisites

### ARC-AGI Data
The full ARC-AGI dataset (800 tasks) is needed for benchmark testing:
```bash
git clone --depth 1 https://github.com/fchollet/ARC-AGI.git /tmp/ARC-AGI
```
This provides:
- 400 training tasks at `/tmp/ARC-AGI/data/training/`
- 400 evaluation tasks at `/tmp/ARC-AGI/data/evaluation/`

### Python Dependencies
```bash
pip install pytest
```
Note: `pytest-timeout` is NOT installed in this repo. Do not use `--timeout` flag.

## Test Commands

### ARC Solver Unit Tests (fastest, run first)
```bash
python -m pytest tests/test_arc_solver.py -v
```
Expected: 5/5 pass in ~2s. Tests demo task solving, prediction hashes, program compilation, DSL enumeration.

### All PR-Relevant Tests
```bash
python -m pytest tests/test_arc_solver.py tests/test_pattern_recognition.py tests/test_ai_invariants.py tests/test_conditional_patterns.py tests/test_cross_model.py tests/test_forgiveness_integration.py -v
```
Expected: 15/15 pass in ~5s.

### Benchmark Runner (Demo Mode)
```bash
python benchmarks/run_arc_benchmark.py --demo-only --evidence-dir /tmp/test_evidence
```
Expected: `10/10 solved (100.00%)`. Writes `benchmark_demo.json` and `manifest_demo.sha256` to the evidence dir.

### Benchmark Runner (Full Dataset)
```bash
python benchmarks/run_arc_benchmark.py --data-dir /tmp/ARC-AGI/data --timeout 3 --evidence-dir /tmp/test_evidence
```
Expected: ~20/400 training (5%), ~2/400 evaluation (0.5%). Takes ~5-10 minutes.

### Verify a Specific Solved Task
```python
import json, sys
sys.path.insert(0, '.')
from axioms.arc_solver import load_arc_task_from_json, benchmark_arc_task

with open('/tmp/ARC-AGI/data/training/1cf80156.json') as f:
    data = json.load(f)
task, expected = load_arc_task_from_json('1cf80156', data)
solved, proof = benchmark_arc_task(task, expected, max_depth=3)
print(f'Solved: {solved}, Proof valid: {proof.is_valid()}')
```

### Verify Evidence Chain Integrity
```python
import json, hashlib
with open('evidence/arc_agi_3/benchmark_demo.json') as f:
    data = json.load(f)
payload = json.dumps(
    [{'task_id': r['task_id'], 'solved': r['solved'], 'prediction_hash': r['prediction_hash']} for r in data['task_results']],
    sort_keys=True, separators=(',', ':'),
)
computed = hashlib.sha256(payload.encode('utf-8')).hexdigest()
print(f'Match: {computed == data["manifest_hash"]}')
```

## Full Test Suite
```bash
python -m pytest tests/ -v --ignore=tests/test_f_platform_001.py --ignore=tests/test_f_platform_002.py --ignore=tests/test_f_platform_003.py --ignore=tests/test_f_platform_004.py --ignore=tests/test_f_platform_005.py --ignore=tests/test_pr45_uvdtl.py
```

### Known Pre-Existing Failures (Not Related to ARC Solver)
These tests fail due to missing build artifacts (`out/` directory) or missing modules. They are NOT caused by ARC solver changes:
- `test_f_platform_001-005.py` — `ModuleNotFoundError: No module named 'test_falsification'` (collection error, must be `--ignore`d)
- `test_pr45_uvdtl.py` — `ModuleNotFoundError: No module named 'pr45_uvdtl.build'` (collection error, must be `--ignore`d)
- `test_food_cart_universe.py` — missing `out/food_cart_dag.json`
- `test_skate4_multiplayer_universe.py` — missing `out/skate4_mp_dag.json`
- `test_uncharted_multiplayer_universe.py` — missing `out/uncharted_mp_dag.json`
- `test_successor_readiness.py` — missing `canonical/hash_manifest.json`
- `test_pr34_audit.py`, `test_pr50_bar_exam.py`, `test_repository_compliance.py` — various pre-existing issues

## Key Architecture Notes
- `_select_best_rule()` in `pattern_recognition.py` validates full operation chains before MDL tiebreaker
- Multi-object decomposition is wired via `_infer_per_object_rule` in `_candidate_rules_for_pair`
- Evidence files use SHA-256 manifest hashes computed from JSON-serialized task results
- The benchmark runner uses `signal.SIGALRM` for per-task timeouts (Linux only)

## CI Notes
- CI workflow (`constitution.yml`) may not include `test_arc_solver.py` — OAuth `workflow` scope might be needed to push changes to this file
- 27 CI checks run on push; all should pass

## Devin Secrets Needed
None — this is a pure Python library with no external service dependencies.
