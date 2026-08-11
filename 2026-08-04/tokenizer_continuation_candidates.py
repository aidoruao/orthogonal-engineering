#!/usr/bin/env python3
"""tokenizer_continuation_candidates.py — emit the actual continuation merge candidate list.

Input: multiple code corpora (mixed: generator output + real code + benchmarks).
Method: tokenize each with the REAL V4 tokenizer; count adjacent token-piece pairs
(intra-word, no whitespace in the concatenated decode); aggregate across corpora;
emit top-K candidates as JSONL — the file the tokenizer team applies for the V5-1
continuation experiment (each candidate = one new merge = one new vocab id).

Deterministic: sorted file iteration, stable ranking (count desc, piece asc).
Output: tokenizer_continuation_candidates.jsonl  {piece, count, bytes_saved, corpora}
"""
import json
import sys
from collections import Counter
from pathlib import Path

from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
# v2 axes (8/5): clean real code (hvac-simulation + standardgalactic-*) instead of the
# contaminated oe-local tree; generator axis is now the full 1B-token corpus.
CORPORA = {
    "generator": "/tmp/locgen7",
    "real_clean": "/home/idor/hvac-simulation",
    "benchmarks": "/home/idor/oe-local/benchmarks",
}
EXTRA_CLEAN = [
    "/home/idor/standardgalactic-library",
    "/home/idor/standardgalactic-spherepop",
    "/home/idor/shampoo-ontology-v4",
    "/home/idor/truthsystems-mod",
    "/home/idor/ftb-quests-ontology",
]
MAX_LINES_PER_CORPUS = 100_000
TOP_K = 20_000
OUT_NAME = "tokenizer_continuation_candidates_v2.jsonl"


def iter_text(root):
    n = 0
    for p in sorted(Path(root).rglob("*.py"))[:300]:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if n >= MAX_LINES_PER_CORPUS:
                        return
                    yield line
                    n += 1
        except Exception:
            pass


def count_pairs(tok, root):
    """Tokenize a corpus root (up to MAX_LINES_PER_CORPUS lines) and count mergeable pairs."""
    text = "".join(iter_text(root))
    encs = tok.encode_batch([text[i:i + 400_000] for i in range(0, len(text), 400_000)])
    pairs = Counter()
    for enc in encs:
        pieces = [tok.decode([i]) for i in enc.ids]
        for a, b in zip(pieces, pieces[1:]):
            if a and b and " " not in a and " " not in b:
                pairs[a + b] += 1
    return pairs


def main():
    tok = Tokenizer.from_file(V4)
    agg = Counter()          # piece -> total count
    per_corpus = {}          # corpus -> piece -> count
    for name, root in CORPORA.items():
        pairs = count_pairs(tok, root)
        if name == "real_clean":
            for extra in EXTRA_CLEAN:
                pairs.update(count_pairs(tok, extra))
        per_corpus[name] = pairs
        agg.update(pairs)
        print(f"{name}: {sum(pairs.values()):,} pair occurrences, "
              f"{len(pairs):,} unique pairs", file=sys.stderr)

    out = Path(__file__).resolve().parent / OUT_NAME
    with out.open("w") as fh:
        for piece, count in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_K]:
            row = {
                "piece": piece,
                "count": count,
                "bytes_saved": (len(piece) - 1) * count,
                "corpora": sorted(c for c, pairs in per_corpus.items() if piece in pairs),
            }
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote top-{TOP_K} candidates -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
