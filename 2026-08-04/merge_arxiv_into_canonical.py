#!/usr/bin/env python3
"""Merge arxiv_reasoning_pairs.jsonl into canonical_sft_v1.jsonl → canonical_sft_v2.jsonl.

Reuses merge_sft.py's canonical dedup scheme: sha256(norm(instruction)|norm(output))[:12].
- v1 rows keep their source; arxiv rows get source="arxiv_vendor".
- The arxiv rows' internal _row_sha256 field is stripped (v2 schema = canonical 6 fields).
- Deterministic: input files are stable, output preserves input order (v1 then arxiv).
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1 = HERE / "canonical_sft_v1.jsonl"
ARXIV = HERE / "arxiv_reasoning_pairs.jsonl"
OUT = HERE / "canonical_sft_v2.jsonl"


def norm(x):
    return " ".join(str(x).split())


def dedup_key(rec):
    return hashlib.sha256(
        (norm(rec.get("instruction", "")) + "|" + norm(rec.get("output", ""))).encode()
    ).hexdigest()


def load(p):
    rows = []
    with open(p) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    v1 = load(V1)
    arxiv = load(ARXIV)
    seen = {}
    dups = Counter()
    out_rows = []

    for rec in v1 + arxiv:
        key = dedup_key(rec)
        if key in seen:
            dups[seen[key]] += 1
            continue
        seen[key] = rec.get("source", "?")
        clean = {
            "instruction": rec["instruction"],
            "input": rec.get("input", ""),
            "output": rec["output"],
            "category": rec["category"],
            "source": rec.get("source", "?"),
            "dedup_group": key[:12],
        }
        out_rows.append(clean)

    with open(OUT, "w") as fh:
        for rec in out_rows:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    cats = Counter(r["category"] for r in out_rows)
    srcs = Counter(r["source"] for r in out_rows)
    print(f"v1 rows: {len(v1)} · arxiv rows: {len(arxiv)}")
    print(f"canonical v2 output: {len(out_rows)} (duplicates dropped: {len(v1) + len(arxiv) - len(out_rows)}, first-seen in: {dict(dups)})")
    print(f"sources: {dict(srcs)}")
    print(f"categories: {dict(cats)}")
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
