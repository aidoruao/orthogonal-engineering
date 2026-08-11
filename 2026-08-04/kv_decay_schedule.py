#!/usr/bin/env python3
"""kv_decay_schedule.py — arithmetic simulator for catalog #4 (CSA-first KV decay).

Verified facts (catalog #4): KV ≈ 6 GB fp8 @1M ctx = 21 CSA (rate 4, ≈5.7 GB, 94%) +
20 HCA (rate 128, ≈0.17 GB) + sliding ≈ 0. Per-pool storage = MLA latent 1088 B fp8.

Schedules simulated (deterministic arithmetic, no model):
  baseline : all pools retained
  coarsen  : after age threshold, merge adjacent CSA pool pairs (halve the old region)
  evict    : importance-ranked retention — evict the lowest X% of CSA pools
             (importance = indexer amplitude proxy: uniform rank assumption)
  rate8    : CSA pooling rate 4 -> 8 for the old half of the sequence

Target check: the V5-2 goal (2-4M ctx at ≈ the same 6 GB budget).
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "kv_decay_schedule.json"
BYTES_PER_POOL = 1088  # MLA latent, fp8
CSA_LAYERS, HCA_LAYERS = 21, 20
CSA_RATE, HCA_RATE = 4, 128
GB = 1e9


def pools_csa(L):  return L // CSA_RATE
def pools_hca(L):  return L // HCA_RATE


def gb(n_pools):
    return n_pools * BYTES_PER_POOL / GB


def main():
    seqs = [1_000_000, 2_000_000, 4_000_000]
    rows = []
    for L in seqs:
        csa, hca = pools_csa(L), pools_hca(L)
        base = gb(csa * CSA_LAYERS + hca * HCA_LAYERS)
        # coarsen: merge adjacent pairs in the oldest half of CSA pools
        old = csa // 2
        coarsened = csa - old // 2
        c_coarse = gb(coarsened * CSA_LAYERS + hca * HCA_LAYERS)
        # evict: drop the lowest 25% of CSA pools (importance-ranked)
        evicted = csa - csa // 4
        c_evict = gb(evicted * CSA_LAYERS + hca * HCA_LAYERS)
        # rate8: old half of CSA pools at rate 8
        old8 = (L // 2) // 8
        new_csa = csa // 2 + old8
        c_rate8 = gb(new_csa * CSA_LAYERS + hca * HCA_LAYERS)
        rows.append({
            "seq": L, "baseline_gb": round(base, 2),
            "coarsen_half_gb": round(c_coarse, 2),
            "evict_25pct_gb": round(c_evict, 2),
            "rate8_oldhalf_gb": round(c_rate8, 2),
            "target_met": {p: round(v, 2) <= 6.5 for p, v in
                           (("coarsen", c_coarse), ("evict", c_evict), ("rate8", c_rate8))},
        })
        # SOLVE: CSA retention fraction f such that total GB == 6.5 (V5-2 budget)
        f = None
        for frac in [x / 100 for x in range(100, 0, -1)]:
            if gb(int(csa * frac) * CSA_LAYERS + hca * HCA_LAYERS) <= 6.5:
                f = frac
                break  # largest qualifying fraction
        rows[-1]["retention_for_6_5gb"] = f
        print(f"L={L/1e6:.0f}M: baseline {base:.2f} GB | coarsen-half {c_coarse:.2f} "
              f"| evict-25% {c_evict:.2f} | rate8-old {c_rate8:.2f}"
              + (f" | retention-for-6.5GB: {f:.0%}" if f else " | 6.5GB unreachable"))
    OUT.write_text(json.dumps(rows, indent=1))
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
