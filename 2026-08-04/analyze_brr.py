#!/usr/bin/env python3
"""Analyze BRR v1 + v2 results; emit a markdown comparison report."""
import json
import statistics

def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def summarize(runs, label):
    lines = [f"\n### {label}\n"]
    if not runs:
        lines.append("(no data)")
        return lines
    # group by (model, primed)
    groups = {}
    for r in runs:
        groups.setdefault((r["model"], r.get("primed", None)), []).append(r)
    for (model, primed), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1] is None)):
        scores_first = [r["scores"][0] for r in rs]
        scores_best = [r["best_score"] for r in rs]
        best_depth = [r["best_depth"] for r in rs]
        peak_qpt = [r["peak_qpt"] for r in rs]
        final_qpt = [r["final_qpt"] for r in rs]
        d40 = [r["depth_to_40"] for r in rs if "depth_to_40" in r]
        degraded = sum(1 for r in rs if r.get("degraded"))
        plateaus = [r["plateau_depth"] for r in rs]
        toks = [r["total_tokens"] for r in rs]
        arm = "blank" if primed is None else ("primed" if primed else "unprimed")
        lines.append(
            f"- **{model} / {arm}** (n={len(rs)}): first={mean(scores_first):.0f} "
            f"best={mean(scores_best):.0f} (depth {mean(best_depth):.1f}), "
            f"peak qpt={mean(peak_qpt):.5f}, final qpt={mean(final_qpt):.5f}, "
            f"tokens={mean(toks):.0f}"
            + (f", depth-to-40={mean([x for x in d40 if x is not None]):.1f} (of {sum(1 for x in d40 if x is not None)} reached)" if d40 else "")
            + f", degraded runs={degraded}/{len(rs)}, plateau@{mean([p for p in plateaus if p is not None]):.1f}")
    return lines

def mean(xs):
    return statistics.mean(xs) if xs else 0.0

def main():
    v1 = load("brr_results.json")
    v2 = load("brr_results_v2.json")
    out = ["# BRR Results Summary (2026-08-04)\n"]
    if v1:
        out += summarize(v1["runs"], "v1 — blank init, strict parse (both models, D=4, 3 seeds)")
    if v2:
        out += summarize(v2["runs"], "v2 — priming A/B (exemplar vs blank, D=4, 3 seeds)")
    out.append("\n### Priming effect (F15 test)\n")
    if v2:
        for model in {"qwen2.5-1.5b", "tinyllama-1.1b"}:
            p = [r for r in v2["runs"] if r["model"] == model and r["primed"]]
            u = [r for r in v2["runs"] if r["model"] == model and not r["primed"]]
            if p and u:
                db = mean([r["best_score"] for r in p]) - mean([r["best_score"] for r in u])
                dq = mean([r["peak_qpt"] for r in p]) - mean([r["peak_qpt"] for r in u])
                dt = mean([r["total_tokens"] for r in u]) - mean([r["total_tokens"] for r in p])
                out.append(f"- {model}: priming Δbest={db:+.1f}, Δpeak_qpt={dq:+.6f}, Δtokens={dt:+.0f} (positive = priming wins)")
    else:
        out.append("(v2 data not yet available)")
    with open("brr_results_summary.md", "w") as f:
        f.write("\n".join(out))
    print("\n".join(out))

if __name__ == "__main__":
    main()
