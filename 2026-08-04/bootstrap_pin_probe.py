#!/usr/bin/env python3
"""bootstrap_pin_probe.py — base-table pin-fix adequacy + cross-domain affinity telemetry.

Catalog #6's resolution recommends: assign the top-100 token ids to distinct experts at
frozen tid2eid table build time, then hash the tail. That construction was never MEASURED
— the recorded skews (9.9x real-code / 21.4x generator) are the PRE-pin distributional
worst case under the uniform-hash presumption (real weights unknown, `[needs hardware]`
to verify the actual table). This probe measures, with the REAL V4 tokenizer:

Per domain (generator / real_clean / benchmarks / canonical_mathlogic):
  zipf_s, base_skew (worst-of-3 uniform draws, same seed as expert_affinity_probe — the
  9.9x/21.4x anchor), pin-P residual skew for P in (50, 100, 256) under the actual
  recommended rule (pin top-P by frequency to distinct experts, sha256-tail the rest),
  head coverage (mass of the top-100 tids), affinity exemplars (top-5 tid decodes).

Cross-domain (the frozen table serves ALL surfaces, built once):
  top-100 Jaccard between every domain pair, and the pin-list TRANSFER test: for each
  (build, serve) pair, residual skew on `serve` when the pin list comes from `build` —
  quantifies how corpus-sensitive the pin choice is.

Deterministic: sorted iteration, stable ties, no RNG in the pin rule. Double-run
sha-verified (same method as expert_affinity_probe.py).

Output: bootstrap_pin_probe.json
"""
import hashlib
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
EXPERTS = 256
SEED = 20260805
MAX_LINES = 120_000
OUT = Path(__file__).resolve().parent / "bootstrap_pin_probe.json"

DOMAINS = {
    "generator": "/tmp/locgen7",
    "real_clean": None,  # assembled from EXTRA_CLEAN roots (same axes as candidates v2)
    "benchmarks": "/home/idor/oe-local/benchmarks",
}
EXTRA_CLEAN = [
    "/home/idor/hvac-simulation",
    "/home/idor/standardgalactic-library",
    "/home/idor/standardgalactic-spherepop",
    "/home/idor/shampoo-ontology-v4",
    "/home/idor/truthsystems-mod",
    "/home/idor/ftb-quests-ontology",
]


def iter_py(root, max_files=300, batch_cap=None):
    """Sorted *.py iteration with optional per-batch cap (generator: first 10 batches)."""
    if batch_cap is not None:
        batches = sorted(p for p in Path(root).iterdir() if p.is_dir())[:batch_cap]
        paths = []
        for b in batches:
            paths.extend(sorted(b.rglob("*.py"))[:max_files])
    else:
        paths = sorted(Path(root).rglob("*.py"))[:max_files]
    n = 0
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if n >= MAX_LINES:
                        return
                    yield line
                    n += 1
        except Exception:
            pass


def iter_mathlogic():
    with open("/home/idor/oe-local/2026-08-04/canonical_sft_v2.jsonl") as fh:
        for line in fh:
            r = json.loads(line)
            if r["category"] in ("mathematics", "logic"):
                yield r["instruction"] + " " + r.get("input", "")


def zipf_slope(ranked):
    n = len(ranked)
    sx = sy = sxx = sxy = 0.0
    for r, (_, f) in enumerate(ranked, start=1):
        x, y = math.log(r), math.log(f)
        sx += x; sy += y; sxx += x * x; sxy += x * y
    return abs((n * sxy - sx * sy) / (n * sxx - sx * sx)) if n > 2 else 0.0


def base_skew(counts):
    """Worst-of-3 uniform draws, SEED 20260805 — must reproduce the 9.9x/21.4x anchors."""
    total = sum(counts.values())
    rng = random.Random(SEED)
    best = 0.0
    for _ in range(3):
        bins = [0] * EXPERTS
        for tid, f in counts.items():
            bins[rng.randrange(EXPERTS)] += f
        best = max(best, max(bins) / (total / EXPERTS))
    return round(best, 2)


def tail_slot(tid):
    return int(hashlib.sha256(str(tid).encode()).hexdigest(), 16) % EXPERTS


def pin_skew(counts, pin_top, pin_from):
    """Residual max/mean skew under: pin `pin_top` tids (chosen from pin_from counts,
    frequency order, ties by tid asc) to experts 0..P-1, sha256-tail the rest of counts.
    The bins always carry `counts` (the served corpus) mass — a pinned tid absent from
    the served corpus contributes 0. When pin_from is counts, this is the self-pin case."""
    total = sum(counts.values())
    mean = total / EXPERTS
    order = sorted(pin_from.items(), key=lambda kv: (-kv[1], kv[0]))
    pinned_ids = {tid for tid, _ in order[:pin_top]}
    bins = [0] * EXPERTS
    for i, (tid, _) in enumerate(order[:pin_top]):
        bins[i % EXPERTS] += counts.get(tid, 0)
    for tid, f in counts.items():
        if tid not in pinned_ids:
            bins[tail_slot(tid)] += f
    mx = max(bins)
    return {
        "pin_top": pin_top,
        "max_load_mass_share": round(mx / total, 4),
        "skew_max_over_mean": round(mx / mean, 2),
    }


def head_coverage(counts, top_n=100):
    total = sum(counts.values())
    return round(sum(f for _, f in counts.most_common(top_n)) / total, 4)


def exemplars(tok, counts, n=5):
    out = []
    for tid, _ in counts.most_common(200):
        if len(out) >= n:
            break
        s = tok.decode([tid])
        if s and s.strip() and all(ord(c) >= 32 for c in s):
            out.append({"tid": tid, "text": s})
    return out


def main():
    tok = Tokenizer.from_file(V4)
    counts_by_domain = {}

    for name, root in DOMAINS.items():
        if name == "real_clean":
            gen = (l for root_ in EXTRA_CLEAN for l in iter_py(root_, max_files=300))
        elif name == "generator":
            gen = iter_py(root, max_files=40, batch_cap=10)  # 10 batches x 40 files
        else:
            gen = iter_py(root)
        counts = Counter()
        for line in gen:
            counts.update(tok.encode(line).ids)
        counts_by_domain[name] = counts
        print(f"{name}: {sum(counts.values()):,} tokens, {len(counts):,} unique ids",
              file=sys.stderr)

    counts = Counter()
    for line in iter_mathlogic():
        counts.update(tok.encode(line).ids)
    counts_by_domain["canonical_mathlogic"] = counts
    print(f"canonical_mathlogic: {sum(counts.values()):,} tokens, {len(counts):,} unique ids",
          file=sys.stderr)

    report = {"per_domain": {}, "cross_domain": {"jaccard_top100": {}, "transfer": {}}}
    for name, counts in counts_by_domain.items():
        ranked = counts.most_common(100_000)
        per = {
            "tokens": sum(counts.values()),
            "unique_ids": len(counts),
            "zipf_s": round(zipf_slope(ranked), 3),
            "base_skew": base_skew(counts),
            "head_coverage_top100": head_coverage(counts),
            "pin": {str(p): pin_skew(counts, p, counts) for p in (50, 100, 256)},
            "exemplars": exemplars(tok, counts),
        }
        report["per_domain"][name] = per
        p100 = per["pin"]["100"]
        print(f"{name}: zipf_s={per['zipf_s']} base_skew={per['base_skew']}x "
              f"top100_mass={per['head_coverage_top100']:.1%} "
              f"pin100_skew={p100['skew_max_over_mean']}x", file=sys.stderr)

    # cross-domain: top-100 overlap + pin-list transfer
    names = list(counts_by_domain)
    top100 = {n: {tid for tid, _ in counts_by_domain[n].most_common(100)}
              for n in names}
    for a in names:
        for b in names:
            if a >= b:
                continue
            inter = len(top100[a] & top100[b])
            report["cross_domain"]["jaccard_top100"][f"{a}|{b}"] = (
                round(inter / len(top100[a] | top100[b]), 3) if top100[a] | top100[b] else 0.0)
            print(f"Jaccard(top100 {a} vs {b}): "
                  f"{report['cross_domain']['jaccard_top100'][f'{a}|{b}']}", file=sys.stderr)

    for build in names:
        for serve in names:
            if build == serve:
                continue
            key = f"{build}->{serve}"
            sk = pin_skew(counts_by_domain[serve], 100, counts_by_domain[build])
            cov = sum(f for tid, f in counts_by_domain[serve].items()
                      if tid in top100[build]) / sum(counts_by_domain[serve].values())
            report["cross_domain"]["transfer"][key] = {
                "serve_skew": sk["skew_max_over_mean"],
                "serve_mass_covered_by_build_pin": round(cov, 4),
            }
            print(f"transfer {key}: serve_skew={sk['skew_max_over_mean']}x "
                  f"pin-covers {cov:.1%} of serve mass", file=sys.stderr)

    OUT.write_text(json.dumps(report, indent=1))
    print(f"saved: {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
