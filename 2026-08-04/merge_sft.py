#!/usr/bin/env python3
"""Merge + dedupe combined_v4-v7 + v8/knowledge_pairs into one canonical SFT/preference dataset.
Output: canonical_sft_v1.jsonl with schema {instruction, input, output, category, source, dedup_group}.
Usage: python3 merge_sft.py
"""
import hashlib
import json
import sys
from collections import Counter

FILES = {
    "v4": "/home/idor/oe-local/combined_v4.jsonl",
    "v5": "/home/idor/oe-local/combined_v5.jsonl",
    "v6": "/home/idor/oe-local/combined_v6.jsonl",
    "v7": "/home/idor/oe-local/combined_v7.jsonl",
}
OUT = "/home/idor/oe-local/2026-08-04/canonical_sft_v1.jsonl"


def load_jsonl(p):
    out = []
    with open(p) as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def norm(x):
    return " ".join(str(x).split())


def main():
    seen = {}
    dup = Counter()
    total = 0
    with open(OUT, "w") as out:
        for src, path in FILES.items():
            for rec in load_jsonl(path):
                total += 1
                key = hashlib.sha256(
                    (norm(rec.get("instruction", "")) + "|" + norm(rec.get("output", ""))).encode()
                ).hexdigest()
                rec["source"] = src
                rec["dedup_group"] = key[:12]
                if key in seen:
                    dup[seen[key]] += 1
                    continue
                seen[key] = src
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        # v8 governance pairs
        v8 = json.load(open("/home/idor/oe-local/combined_v8.json"))
        for rec in v8:
            total += 1
            key = hashlib.sha256(
                (norm(rec.get("instruction", "")) + "|" + norm(rec.get("output", ""))).encode()
            ).hexdigest()
            rec["source"] = "v8"
            rec["dedup_group"] = key[:12]
            if key in seen:
                dup[seen[key]] += 1
                continue
            seen[key] = "v8"
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    n_out = len(seen)
    print(f"input entries: {total}")
    print(f"canonical output: {n_out} ({(n_out / total * 100):.1f}% kept)")
    print(f"duplicates dropped: {total - n_out} (first-seen in: {dict(dup)})")

    # category census of the canonical set
    cats = Counter()
    with open(OUT) as fh:
        for line in fh:
            cats[json.loads(line).get("category", "?")] += 1
    print("canonical categories:", dict(cats))
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
