#!/usr/bin/env python3
"""v4_bootstrap_load_probe.py — quantify the hash-MoE bootstrap edge (#6 in the catalog).

Question: V4 routes the first 3 layers through a frozen tid2eid (token-id → expert-id)
hash table (256 experts). If the hash were uniform-random, what expert-load skew would
the real code-token distribution produce? And what does the adversarial (collision)
worst case look like?

Method (all deterministic):
  1. Load the REAL V4 tokenizer (/tmp/v4_tokenizer.json).
  2. Tokenize a sample of the generator code corpus (/tmp/locgen/batch_0).
  3. Fit Zipf: log f = log C - s*log r  (least squares on the top-N ranks).
  4. Balls-into-bins simulation (seeded): assign each token id in the top-K (covering
     ~99.9% of mass) to a uniform-random expert, sum frequency mass per expert, report
     max/mean skew. Repeat for 3 independent hash draws (3 bootstrap layers) - same
     expectation (i.i.d.).
  5. Adversarial worst case: all top-K mass forced onto one expert.

Caveat (honest): real tid2eid mapping is unknown (weights); this measures the
distributional risk under the standard uniform-hash assumption the design presumes.
"""
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

V4_TOK = "/tmp/v4_tokenizer.json"
CORPUS = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/locgen/batch_0")
MAX_LINES = 120_000
TOPK_MASS = 0.999  # fraction of token mass covered by the simulation's top tokens
EXPERTS = 256
SEED = 20260805


def main():
    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(V4_TOK)
    counts = Counter()
    n_lines = 0
    for p in sorted(CORPUS.rglob("*.py"))[:400]:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if n_lines >= MAX_LINES:
                    break
                ids = tok.encode(line).ids
                counts.update(ids)
                n_lines += 1
        if n_lines >= MAX_LINES:
            break

    total = sum(counts.values())
    print(f"tokenized {n_lines:,} lines, {total:,} tokens, {len(counts):,} unique ids")

    # --- Zipf fit on top 5,000 ranks ---
    ranked = counts.most_common(5000)
    n = len(ranked)
    sx = sy = sxx = sxy = 0.0
    for r, (tid, f) in enumerate(ranked, start=1):
        x, y = math.log(r), math.log(f)
        sx += x; sy += y; sxx += x * x; sxy += x * y
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    print(f"Zipf exponent: s = {abs(slope):.3f} (classic Zipf s=1; s>1 = heavy head, s<1 = flat)")

    # --- mass coverage of top-K ---
    mass = 0.0
    k = 0
    for r, (tid, f) in enumerate(ranked, start=1):
        mass += f
        if mass / total >= TOPK_MASS:
            k = r
            break
    if k == 0:
        k = len(ranked)  # heavy-tailed Zipf: threshold needs the full unique set
    print(f"top-{k} token ids cover {mass / total:.1%} of token mass (of {len(ranked)} unique)")

    # --- seeded uniform-hash simulation over 3 independent draws ---
    top = ranked[:k]
    rng = random.Random(SEED)
    skews = []
    for draw in range(3):
        bins = [0] * EXPERTS
        for tid, f in top:
            bins[rng.randrange(EXPERTS)] += f
        mx, mn = max(bins), min(b for b in bins if b > 0)
        mean = total / EXPERTS
        skews.append(mx / mean)
        print(f"draw {draw + 1}: max-load expert = {mx / total:.3%} of mass "
              f"(mean {mean / total:.4%}), skew max/mean = {mx / mean:.2f}x, "
              f"min/mean = {mn / mean:.2f}x")
    print(f"uniform-hash skew (max/mean): {max(skews):.2f}x worst draw")

    # --- adversarial worst case ---
    worst = sum(f for _, f in top) / (total / EXPERTS)
    print(f"adversarial (all top mass to one expert): {worst:.0f}x the mean load")

    print("\nTop-10 tokens (id, count, freq):")
    for tid, f in ranked[:10]:
        print(f"  {tid}: {f:,} ({f / total:.4%})")


if __name__ == "__main__":
    main()
