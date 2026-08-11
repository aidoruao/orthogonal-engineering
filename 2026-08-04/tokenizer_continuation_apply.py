#!/usr/bin/env python3
"""tokenizer_continuation_apply.py — emit the ORDERED apply-file for the tokenizer team.

Consumes merge_order_check.py's findings:
  - P3 prefix-order constraints (5,678): candidates whose candidate-prefix exists must
    be applied AFTER that prefix — topological order by length (prefix < piece).
  - P1 failures (22 multi-step pieces): flagged `steps: 2+` (they need >1 merge; kept
    in the file but marked, since the continuation trainer may still want them).

Output: tokenizer_continuation_apply_v1.jsonl — one row per piece:
  {piece, count, bytes_saved, corpora, prefix_required, steps, order}
order = global application index (prefix-first, stable by (len, piece)).

Deterministic; verify pass: every row's required prefixes have lower order.
"""
import json
from pathlib import Path

from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
CANDIDATES = Path(__file__).resolve().parent / "tokenizer_continuation_candidates_v2.jsonl"
OUT = Path(__file__).resolve().parent / "tokenizer_continuation_apply_v1.jsonl"


def main():
    tok = Tokenizer.from_file(V4)
    rows = [json.loads(l) for l in open(CANDIDATES)]
    uniq = {r["piece"]: r for r in rows}
    pieces = sorted(uniq, key=lambda p: (len(p), p))  # length order = prefix-first

    # multi-step flag (P1): piece must decode to exactly 2 tokens under V4
    steps = {}
    for p in pieces:
        enc = tok.encode(p)
        steps[p] = 1 if (len(enc.ids) == 2 and
                         tok.decode(enc.ids[:1]) + tok.decode(enc.ids[1:]) == p) else 2

    # prefix_required: any candidate proper prefix of p
    prefix_of = {}
    for p in pieces:
        prefs = [p[:k] for k in range(1, len(p)) if p[:k] in uniq]
        prefix_of[p] = sorted(prefs, key=len)

    order = {}
    for i, p in enumerate(pieces):
        order[p] = i

    # verify: every required prefix has lower order (guaranteed by length sort)
    bad = 0
    with OUT.open("w") as fh:
        for i, p in enumerate(pieces):
            req = prefix_of[p]
            if any(order[q] > i for q in req):
                bad += 1
            row = dict(uniq[p])
            row.update({"prefix_required": req, "steps": steps[p], "order": i})
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    n_multi = sum(1 for s in steps.values() if s == 2)
    n_req = sum(1 for r in prefix_of.values() if r)
    print(f"apply-file: {len(pieces)} rows ordered | multi-step flagged: {n_multi} "
          f"| with prefix requirements: {n_req} | order-verification failures: {bad}")
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
