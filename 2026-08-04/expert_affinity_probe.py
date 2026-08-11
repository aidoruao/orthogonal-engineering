#!/usr/bin/env python3
"""expert_affinity_probe.py — per-domain hash-MoE skew + tid2eid extension-rule simulation.

Child-handoff spec (slash_agent), executed in the parent lane:
  1. Per-domain token-profile: Zipf exponent, unique ids, uniform-hash expert-load skew
     (seeded 3 draws, 256 experts) for: generator corpus, benchmarks, hvac real-clean,
     canonical_sft_v2 mathematics/logic text.
  2. **tid2eid extension-rule simulation** (catalog #6 open thread): the top-20K
     continuation candidates become NEW vocab ids; their expert slot = stable hash of the
     merge piece (subword path). Report: naive-hash load skew + collision count vs the
     load-balanced fix (pin top-100 pieces to distinct experts, hash the tail).

Deterministic (fixed seed, sorted iteration); double-run sha-verified.
"""
import hashlib
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
EXPERTS = 256
SEED = 20260805
MAX_LINES = 80_000

DOMAINS = {
    "generator": "/tmp/locgen7",
    "benchmarks": "/home/idor/oe-local/benchmarks",
    "hvac_real": "/home/idor/hvac-simulation",
}
CANDIDATES = Path(__file__).resolve().parent / "tokenizer_continuation_candidates_v2.jsonl"
OUT = Path(__file__).resolve().parent / "expert_affinity_probe.json"


def iter_text(root):
    n = 0
    for p in sorted(Path(root).rglob("*.py"))[:300]:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if n >= MAX_LINES:
                        return
                    yield line
                    n += 1
        except Exception:
            pass


def zipf_slope(ranked):
    n = len(ranked)
    sx = sy = sxx = sxy = 0.0
    for r, (_, f) in enumerate(ranked, start=1):
        x, y = math.log(r), math.log(f)
        sx += x; sy += y; sxx += x * x; sxy += x * y
    return abs((n * sxy - sx * sy) / (n * sxx - sx * sx)) if n > 2 else 0.0


def hash_skew(tokens, draws=3):
    """Uniform-random assignment of token ids -> 256 experts, frequency-weighted skew."""
    total = sum(tokens.values())
    rng = random.Random(SEED)
    best = 0.0
    for _ in range(draws):
        bins = [0] * EXPERTS
        for tid, f in tokens.items():
            bins[rng.randrange(EXPERTS)] += f
        best = max(best, max(bins) / (total / EXPERTS))
    return best


def main():
    tok = Tokenizer.from_file(V4)
    report = {}
    for name, root in DOMAINS.items():
        counts = Counter()
        for line in iter_text(root):
            counts.update(tok.encode(line).ids)
        ranked = counts.most_common(100_000)
        report[name] = {
            "tokens": sum(counts.values()),
            "unique_ids": len(counts),
            "zipf_s": round(zipf_slope(ranked), 3),
            "hash_skew": round(hash_skew(counts), 2),
        }
        print(f"{name}: {report[name]}", file=sys.stderr)

    # canonical v2 math+logic text domain
    cc = Counter()
    with open("/home/idor/oe-local/2026-08-04/canonical_sft_v2.jsonl") as fh:
        for line in fh:
            r = json.loads(line)
            if r["category"] in ("mathematics", "logic"):
                cc.update(tok.encode(r["instruction"] + " " + r.get("input", "")).ids)
    ranked = cc.most_common(100_000)
    report["canonical_mathlogic"] = {
        "tokens": sum(cc.values()), "unique_ids": len(cc),
        "zipf_s": round(zipf_slope(ranked), 3), "hash_skew": round(hash_skew(cc), 2),
    }
    print(f"canonical_mathlogic: {report['canonical_mathlogic']}", file=sys.stderr)

    # --- tid2eid extension-rule simulation over the top-20K candidates ---
    pieces = [json.loads(l)["piece"] for l in open(CANDIDATES)]
    total = len(pieces)

    def slot_naive(piece):
        return int(hashlib.sha256(piece.encode()).hexdigest(), 16) % EXPERTS

    naive_bins = Counter(slot_naive(p) for p in pieces)
    collisions = total - len(naive_bins)
    mean = total / EXPERTS

    # load-balanced: pin top-100 pieces (by list order = count order) to distinct experts
    pinned = set()
    bins_fixed = Counter()
    for i, p in enumerate(pieces):
        if i < 100:
            e = i % EXPERTS
            pinned.add(p)
        else:
            e = slot_naive(p)
        bins_fixed[e] += 1
    report["extension_rule"] = {
        "candidates": total,
        "naive_max_load": max(naive_bins.values()),
        "naive_max_over_mean": round(max(naive_bins.values()) / mean, 2),
        "naive_collisions": collisions,
        "fixed_max_load": max(bins_fixed.values()),
        "fixed_max_over_mean": round(max(bins_fixed.values()) / mean, 2),
        "fixed_collisions": total - len(bins_fixed),
        "pinned": len(pinned),
    }
    print(f"extension_rule: {report['extension_rule']}", file=sys.stderr)

    OUT.write_text(json.dumps(report, indent=1))
    print(f"saved: {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
