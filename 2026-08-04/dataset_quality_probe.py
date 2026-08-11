#!/usr/bin/env python3
"""dataset_quality_probe.py — hygiene numbers for canonical_sft_v2 before training.

Questions the training team needs answered:
  1. How many unique instruction TEMPLATES (vs instructions that differ only by
     inlined content)? High template reuse = low diversity.
  2. Output length distribution (tokens/characters) per category — the reasoning block
     should be the longest-output, not the shortest.
  3. Empty/near-empty outputs and inputs.
  4. Category balance vs the stated targets.
  5. Near-dup rate at the instruction-prefix level (dedup_group catches exact dups only).

Deterministic; prints + writes dataset_quality.json.
"""
import json
import re
from collections import Counter
from pathlib import Path

V2 = Path("/home/idor/oe-local/2026-08-04/canonical_sft_v2.jsonl")
OUT = Path(__file__).resolve().parent / "dataset_quality.json"

TEMPLATE_RE = re.compile(r"\b([A-Za-z_]{3,})\b")


def main():
    rows = [json.loads(l) for l in open(V2)]
    n = len(rows)
    print(f"rows: {n:,}")

    # 1. instruction templates: normalize digits/hex/ids -> placeholders
    def template(inst):
        t = re.sub(r"0x[0-9a-fA-F]+", "HEX", inst)
        t = re.sub(r"\b\d+\b", "N", t)
        return re.sub(r"\s+", " ", t)[:200]

    temps = Counter(template(r["instruction"]) for r in rows)
    top_t = temps.most_common(5)
    print(f"unique instruction templates: {len(temps)}/{n} ({len(temps) / n:.1%})")
    for t, c in top_t:
        print(f"  [{c:>5}] {t[:90]}")
    single = sum(1 for c in temps.values() if c == 1)
    print(f"templates used once: {single} ({single / len(temps):.1%} of templates)")

    # 2. output length per category (chars)
    cat_len = {}
    empty_out = 0
    empty_in = 0
    for r in rows:
        c = r["category"]
        ol = len(r.get("output", ""))
        il = len(r.get("input", ""))
        cat_len.setdefault(c, []).append(ol)
        if not r.get("output", "").strip():
            empty_out += 1
        if not il:
            empty_in += 1
    print(f"empty outputs: {empty_out} | empty inputs: {empty_in}")
    print("category output-length (mean chars):")
    for c, lens in sorted(cat_len.items(), key=lambda kv: -sum(kv[1]) / max(len(kv[1]), 1)):
        print(f"  {c:>22}: n={len(lens):>5} mean={sum(lens) / len(lens):>7.1f} "
              f"max={max(lens):>7}")

    # 3. near-dup: rows sharing the same instruction template AND same category
    near = Counter((t, r["category"]) for r in rows for t in [template(r["instruction"])])
    multi = sum(1 for (_, _c), cnt in near.items() if cnt > 1)
    print(f"template+category groups with >1 row: {multi}")

    # 4. category balance
    cats = Counter(r["category"] for r in rows)
    print("categories:", dict(sorted(cats.items(), key=lambda kv: -kv[1])))

    OUT.write_text(json.dumps({
        "rows": n, "unique_templates": len(temps), "templates_once": single,
        "empty_outputs": empty_out, "empty_inputs": empty_in,
        "top_templates": [(t[:100], c) for t, c in top_t],
        "cat_mean_len": {c: round(sum(l) / len(l), 1) for c, l in cat_len.items()},
        "categories": dict(cats),
    }, indent=1))
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
