#!/usr/bin/env python3
"""merge_refine_benchmarks.py — refine the 20K continuation list on a benchmarks-only sample.

The V2 candidate list (tokenizer_continuation_candidates_v2.jsonl) was ranked by MIXED
corpus frequency (generator + real_clean + benchmarks). The tokenizer team spends a
finite budget (each merge = +1 vocab id = +1 tid2eid entry = expert-load cost), so the
list should be re-ranked by value on the surface that matters for the next cycle's evals:
clean real code (oe-local/benchmarks/ is the purest available sample).

Three questions, all deterministic (same pair-count method as
tokenizer_continuation_candidates.py: adjacent intra-word token decodes, no whitespace):

  Q1 coverage   — of the 20,000 mixed-corpus candidates, how many occur in the
                  benchmarks-only sample? Cross-checked against the per-piece "corpora"
                  tags recorded at generation time.
  Q2 re-ranking — re-rank candidates by benchmarks-only pair count; how much does the
                  top-K pick set change vs the mixed ranking (top-1K / 10K overlap)?
  Q3 headroom   — greedy continuation at K = 1K / 10K / 20K on the benchmarks sample,
                  mixed ranking vs refined ranking: tokens saved %. (At K = 20K both
                  rankings span the same 20K pieces, so headroom must be equal — a
                  built-in sanity check.)

Output: merge_refine_benchmarks.json (stats) + tokenizer_continuation_candidates_v3.jsonl
(refined list, same schema + benchmarks_count field; lineage v2 untouched).
"""
import json
from collections import Counter
from pathlib import Path

from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
BENCH = Path("/home/idor/oe-local/benchmarks")
CAND = Path(__file__).resolve().parent / "tokenizer_continuation_candidates_v2.jsonl"
OUT_JSON = Path(__file__).resolve().parent / "merge_refine_benchmarks.json"
OUT_LIST = Path(__file__).resolve().parent / "tokenizer_continuation_candidates_v3.jsonl"
MAX_LINES = 100_000
K_LEVELS = (1_000, 10_000, 20_000)


def iter_text(root):
    n = 0
    for p in sorted(root.rglob("*.py")):
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if n >= MAX_LINES:
                        return
                    yield line
                    n += 1
        except Exception:
            pass


def count_pairs(tok, root):
    text = "".join(iter_text(root))
    encs = tok.encode_batch([text[i:i + 400_000] for i in range(0, len(text), 400_000)])
    pairs = Counter()
    n_tok0 = 0
    for enc in encs:
        n_tok0 += len(enc.ids)
        pieces = [tok.decode([i]) for i in enc.ids]
        for a, b in zip(pieces, pieces[1:]):
            if a and b and " " not in a and " " not in b:
                pairs[a + b] += 1
    return pairs, encs, n_tok0, len(text)


def greedy_tokens(encs, top, tok):
    n_tok = 0
    for enc in encs:
        pieces = [tok.decode([i]) for i in enc.ids]
        i = 0
        while i < len(pieces):
            if i + 1 < len(pieces) and pieces[i] + pieces[i + 1] in top:
                i += 2
            else:
                i += 1
            n_tok += 1
    return n_tok


def main():
    tok = Tokenizer.from_file(V4)
    pairs, encs, n_tok0, chars = count_pairs(tok, BENCH)
    print(f"benchmarks-only sample: {chars:,} chars, {n_tok0:,} V4 tokens, "
          f"{len(pairs):,} unique mergeable pairs")

    cands = [json.loads(l) for l in open(CAND)]
    by_piece = {c["piece"]: c for c in cands}
    assert len(cands) == len(by_piece) == 20_000

    # Q1 coverage + cross-check vs generation-time tags
    present = [p for p in by_piece if p in pairs]
    tagged = [p for p in by_piece if "benchmarks" in by_piece[p]["corpora"]]
    tagged_missing = [p for p in tagged if p not in pairs]
    print(f"Q1 coverage: {len(present):,}/20,000 candidates occur in benchmarks-only code "
          f"({len(present) / len(cands):.1%}); generation-time 'benchmarks' tags: "
          f"{len(tagged):,} (missing from this sample: {len(tagged_missing)})")

    # Q2 re-ranking: refined order = (-benchmarks_count, -mixed_count, piece)
    mixed_rank = {p: i for i, p in enumerate(c["piece"] for c in cands)}
    refined = sorted(
        cands,
        key=lambda c: (-pairs.get(c["piece"], 0), -c["count"], c["piece"]),
    )
    refined_pieces = [c["piece"] for c in refined]
    for k in K_LEVELS[:2]:
        m = set(c["piece"] for c in cands[:k])
        r = set(refined_pieces[:k])
        print(f"Q2 top-{k:,}: mixed vs refined overlap {len(m & r)}/{k} "
              f"({len(m & r) / k:.1%})")

    # Q3 headroom on the benchmarks sample, both orderings
    print("\nQ3 greedy continuation on benchmarks-only sample (tokens saved):")
    rows = []
    for k in K_LEVELS:
        top_mixed = set(c["piece"] for c in cands[:k])
        top_refined = set(refined_pieces[:k])
        t_m = greedy_tokens(encs, top_mixed, tok)
        t_r = greedy_tokens(encs, top_refined, tok)
        saved_m = n_tok0 - t_m
        saved_r = n_tok0 - t_r
        rows.append({
            "k": k,
            "mixed_tokens": t_m, "mixed_saved_pct": saved_m / n_tok0,
            "refined_tokens": t_r, "refined_saved_pct": saved_r / n_tok0,
            "delta_pp": (saved_r - saved_m) / n_tok0,
        })
        print(f"  K={k:>6,}: mixed {saved_m:,} ({saved_m / n_tok0:.2%}) | "
              f"refined {saved_r:,} ({saved_r / n_tok0:.2%}) | "
              f"delta {rows[-1]['delta_pp']:+.2%}")

    # sanity: at K = 20K both orderings span the same set
    assert set(c["piece"] for c in cands) == set(refined_pieces)
    assert rows[-1]["mixed_tokens"] == rows[-1]["refined_tokens"], \
        "K=20K headroom must match (same piece set)"

    result = {
        "sample": str(BENCH), "chars": chars, "tokens": n_tok0,
        "unique_pairs_in_sample": len(pairs),
        "q1_candidates_present": len(present),
        "q1_generation_time_benchmarks_tags": len(tagged),
        "q1_tagged_but_absent_now": len(tagged_missing),
        "q2_overlap": {str(k): len(set(c["piece"] for c in cands[:k])
                                     & set(refined_pieces[:k])) for k in K_LEVELS},
        "q3": rows,
        "verdict": "REFINEMENT MATTERS" if rows[0]["delta_pp"] > 0 else "ORDERING INERT",
    }
    OUT_JSON.write_text(json.dumps(result, indent=1))
    print(f"\nverdict: {result['verdict']} | saved: {OUT_JSON}")

    with OUT_LIST.open("w") as fh:
        for c in refined:
            row = dict(c)
            row["benchmarks_count"] = pairs.get(c["piece"], 0)
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"refined list (v3, {len(refined):,} rows): {OUT_LIST}")


if __name__ == "__main__":
    main()
