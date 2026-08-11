#!/usr/bin/env python3
"""Inventory of oe-local post-training data assets."""
import json
import os
from collections import Counter

for f in ["combined_v4.jsonl", "combined_v5.jsonl", "combined_v6.jsonl", "combined_v7.jsonl"]:
    if os.path.exists(f):
        cats = Counter()
        n = 0
        with open(f) as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                n += 1
                cats[o.get("category", "?")] += 1
        print(f"{f}: {n} entries, cats={dict(cats)}")

for f in ["combined_v8.json", "knowledge_pairs_governance.json"]:
    if os.path.exists(f):
        d = json.load(open(f))
        print(f"{f}: {len(d)} entries, cats={dict(Counter(x.get('category', '?') for x in d))}")
        print("  sample keys:", sorted(d[0].keys()) if d else "empty")
