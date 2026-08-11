#!/usr/bin/env python3
"""merge_order_check.py — property gate over the continuation candidate list.

Classic BPE merge-ordering theory (Sennrich et al. 2016; tokenizers' merge machinery):
merges are a TOTAL ORDER; a candidate list is only feasible if it can be ordered without
conflicts. Properties checked (QuickCheck-style, deterministic):

  P1  Decomposability: every candidate piece must be the concatenation of two token
      decodes under the CURRENT V4 tokenizer (else it can never be formed by one merge).
  P2  Pair-conflict: no candidate piece is also produced as the *same* merge from two
      different splits (a piece has a unique (left,right) split only if the tokenizer's
      own decode of it splits identically — approximate: check both halves exist).
  P3  Prefix-order feasibility: if piece A is a prefix of piece B and B's second half
      starts inside A, B can only apply after A exists — order constraint; cycles are
      impossible in BPE (pieces grow) but cross-conflicts (A inside B AND B inside A)
      would indicate a cycle.
  P4  Duplicate check: identical pieces (should be 0 — the generator dedupes).

Output: pass/fail counts per property + the conflict list, JSON + summary.
"""
import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
CANDIDATES = Path(__file__).resolve().parent / "tokenizer_continuation_candidates_v2.jsonl"
OUT = Path(__file__).resolve().parent / "merge_order_check.json"


def main():
    tok = Tokenizer.from_file(V4)
    pieces = [json.loads(l)["piece"] for l in open(CANDIDATES)]
    n = len(pieces)
    uniq = set(pieces)
    print(f"candidates: {n:,} | unique pieces: {len(uniq):,} (P4 dupes: {n - len(uniq)})")

    # P1: each piece must be exactly two V4 tokens' decoded concatenation
    p1_fail = []
    for p in sorted(uniq):
        enc = tok.encode(p)
        if len(enc.ids) != 2 or tok.decode(enc.ids[:1]) + tok.decode(enc.ids[1:]) != p:
            p1_fail.append(p)
    print(f"P1 decomposability: {len(uniq) - len(p1_fail)}/{len(uniq)} pass"
          + (f" | FAIL: {p1_fail[:5]}" if p1_fail else ""))

    # P3: prefix containment — if a proper prefix of a piece is ALSO a candidate,
    #     the prefix must merge first (feasibility constraint). Set-membership over
    #     all proper prefixes: O(n * max_len), not O(n^2).
    order_reqs = 0
    prefix_conflicts = []
    for p in sorted(uniq):
        for k in range(1, len(p)):
            pref = p[:k]
            if pref in uniq:
                order_reqs += 1
                prefix_conflicts.append((pref, p))
                break  # one constraint per piece is enough for the count
    print(f"P3 prefix-order constraints: {order_reqs} (the prefix must merge before the piece)")

    # P2: same-piece from different splits — for each piece, the V4 encoding split is
    #     unique by construction of BPE; we check the two halves are both real tokens.
    p2_fail = []
    for p in sorted(uniq):
        enc = tok.encode(p)
        if len(enc.ids) == 2:
            left, right = tok.decode([enc.ids[0]]), tok.decode([enc.ids[1]])
            if not left or not right:
                p2_fail.append(p)
    print(f"P2 half-token check: {len(uniq) - len(p2_fail)}/{len(uniq)} pass"
          + (f" | FAIL: {p2_fail[:5]}" if p2_fail else ""))

    result = {
        "candidates": n, "unique": len(uniq), "p4_dupes": n - len(uniq),
        "p1_pass": len(uniq) - len(p1_fail), "p1_fail": p1_fail[:10],
        "p2_pass": len(uniq) - len(p2_fail), "p2_fail": p2_fail[:10],
        "p3_prefix_order_constraints": order_reqs,
        "p3_sample": prefix_conflicts[:10],
        "verdict": "APPLICABLE" if not p1_fail and not p2_fail else "REVIEW",
    }
    OUT.write_text(json.dumps(result, indent=1))
    print(f"verdict: {result['verdict']} | saved: {OUT}")


if __name__ == "__main__":
    main()
