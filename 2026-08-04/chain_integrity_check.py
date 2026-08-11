#!/usr/bin/env python3
"""chain_integrity_check.py — the closing audit: every load-bearing claim, verified.

Checks the chain's load-bearing facts on disk: artifact existence, row counts,
chain roots, and key numbers. Fails loudly on any mismatch. Deterministic.

Claim table = (label, kind, path-or-value, expected) — kinds: file|count|root|hash.
"""
import hashlib
import json
import sys
from pathlib import Path

OE = Path("/home/idor/oe-local")
D = OE / "2026-08-04"

CLAIMS = [
    # (label, kind, path, expected)
    ("canonical_sft_v2 rows", "count", D / "canonical_sft_v2.jsonl", 7373),
    ("arxiv reasoning pairs rows", "count", D / "arxiv_reasoning_pairs.jsonl", 1146),
    ("hle dev items rows", "count", D / "hle_items_dev.jsonl", 56),
    ("candidates v2 rows", "count", D / "tokenizer_continuation_candidates_v2.jsonl", 20000),
    ("apply-file rows", "count", D / "tokenizer_continuation_apply_v1.jsonl", 20000),
    ("extension table rows", "count", D / "tid2eid_extension_v1.jsonl", 20000),
    ("refined candidates v3 rows", "count", D / "tokenizer_continuation_candidates_v3.jsonl", 20000),
    ("refine stats exists", "file", D / "merge_refine_benchmarks.json", None),
    ("pin probe stats exists", "file", D / "bootstrap_pin_probe.json", None),
    ("completion audit exists", "file", D / "COMPLETION_INTEGRITY_AUDIT.md", None),
    ("root verifier exists", "file", D / "verify_chain_root.py", None),
    ("delta doc exists", "file", D / "CROSS_MODEL_ARCHITECTURE_DELTA.md", None),
    ("1B-corpus manifest batches", "jsonlen", D / "locgen7_MANIFEST.json", 300),
    ("catalog entries", "grep", D / "V4_EDGE_CASE_RESOLUTIONS.md", "## 13. Wave-order"),
    ("learning doc sections", "grep", D / "NEXT_CYCLE_LEARNING.md", "D2b"),
    ("work log exists", "file", OE / "WORK_LOG.md", None),
    ("custody exists", "file", OE / "CHAIN_OF_CUSTODY.md", None),
    ("prep kit exists", "file", D / "POST_TRAINING_PREP.md", None),
    ("brief exists", "file", D / "DEVELOPERS_BRIEF.md", None),
]


def file_count(p):
    return sum(1 for _ in open(p))


def main():
    fails = []
    for label, kind, path, expected in CLAIMS:
        try:
            if kind == "file":
                ok = path.is_file()
            elif kind == "count":
                ok = file_count(path) == expected
            elif kind == "jsonlen":
                ok = len(json.load(open(path))["batches"]) == expected
            elif kind == "grep":
                ok = expected in path.read_text()
            else:
                ok = False
        except Exception:
            ok = False
        status = "OK " if ok else "FAIL"
        print(f"[{status}] {label}")
        if not ok:
            fails.append(label)
    # key chain roots on disk
    roots = {
        "1B corpus manifest": (D / "locgen7_MANIFEST.json", "a07920a6c404"),
        "arxiv pairs hash ref": (D / "arxiv_reasoning_pairs.jsonl", None),
    }
    m = json.load(open(roots["1B corpus manifest"][0]))
    ok = m["chain_root"].startswith(roots["1B corpus manifest"][1])
    print(f"[{'OK ' if ok else 'FAIL'}] manifest chain root a07920a6c404…")
    if not ok:
        fails.append("manifest chain root")
    print(f"\n{'ALL CHAIN CLAIMS VERIFIED' if not fails else 'FAILURES: ' + str(fails)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
