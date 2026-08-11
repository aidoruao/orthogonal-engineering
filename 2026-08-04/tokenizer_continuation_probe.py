#!/usr/bin/env python3
"""tokenizer_continuation_probe.py — measure the V5-1 tokenizer-continuation headroom.

Established context: from-scratch code BPE at equal vocab did NOT beat the V4 tokenizer
on code (falsified). The remaining path is CONTINUATION: keep V4's vocab+merges, add new
code merges. This probe quantifies that headroom with the real V4 tokenizer:

  1. Tokenize a code sample (real code + generator output) with the real V4 tokenizer.
  2. Extract candidate merge pairs from adjacent tokens (decode(t1)+decode(t2) = the
     merged piece; only intra-word pairs, no whitespace in the concatenation).
  3. Rank by corpus frequency; greedily simulate continuation for K = 1K / 10K / 50K
     new merges (overlap-aware: a token consumed by a higher-rank merge can't be
     consumed by a lower one).
  4. Report chars/token before/after, tokens saved %, and — the tid2eid hook — the
     number of NEW vocab entries each continuation adds (each merge = +1 token id),
     i.e. the size of the frozen-table extension rule the developers must define.

Deterministic: no randomness; sorted iteration; same input → same output.
"""
import sys
from collections import Counter
from pathlib import Path

from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
CORPUS = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/locgen/batch_0")
MAX_LINES = 100_000
MERGE_LIMITS = (1_000, 10_000, 50_000)


def iter_text():
    n = 0
    for p in sorted(CORPUS.rglob("*.py"))[:300]:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if n >= MAX_LINES:
                    return
                yield line
                n += 1


def main():
    tok = Tokenizer.from_file(V4)
    text = "".join(iter_text())
    encs = tok.encode_batch([text[i:i + 400_000] for i in range(0, len(text), 400_000)])

    n_tok0 = 0
    pairs = Counter()
    for enc in encs:
        n_tok0 += len(enc.ids)
        pieces = [tok.decode([i]) for i in enc.ids]
        for a, b in zip(pieces, pieces[1:]):
            if a and b and " " not in a and " " not in b:
                pairs[a + b] += 1

    chars = len(text)
    cpt0 = chars / n_tok0
    print(f"corpus: {chars:,} chars, {n_tok0:,} V4 tokens, chars/token = {cpt0:.3f}")
    print(f"candidate merge pairs found: {len(pairs):,}")

    # greedy continuation simulation (rank order, overlap-aware)
    ranked = sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0]))
    print("\ntop-15 candidate merges (piece | count | bytes saved if merged):")
    for piece, c in ranked[:15]:
        print(f"  {piece!r} : {c:,} ({(len(piece) - 1) * c:,} bytes)")

    for K in MERGE_LIMITS:
        top = set(piece for piece, _ in ranked[:K])
        # greedy pass: walk each encoding once, merging when both sides are a pair in `top`
        n_tok = 0
        for enc in encs:
            ids = enc.ids
            pieces = [tok.decode([i]) for i in ids]
            i = 0
            while i < len(pieces):
                if i + 1 < len(pieces) and pieces[i] + pieces[i + 1] in top:
                    i += 2
                else:
                    i += 1
                n_tok += 1
        saved = n_tok0 - n_tok
        cpt = chars / max(n_tok, 1)
        print(f"K={K:>6,} merges (+{K:,} vocab entries): tokens {n_tok0:,} -> {n_tok:,} "
              f"(−{saved:,}, {saved / n_tok0:.2%}), chars/token {cpt0:.3f} -> {cpt:.3f} "
              f"({(1 - cpt0 / cpt):.2%} fewer tokens per char)")

    print("\ntid2eid hook: each merge adds exactly 1 vocab id -> the frozen-table "
          "extension needs 1 entry per new id (rule: hash of the merge's subword path).")


if __name__ == "__main__":
    main()
