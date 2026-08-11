#!/usr/bin/env python3
"""Token economics at scale: real V4 + Qwen tokenizers on generated code corpus.
Measures tokens/LOC, tokens/byte, compression ratio, context fit vs 1M ctx."""
import sys
import time
from pathlib import Path

from tokenizers import Tokenizer

V4 = "/tmp/v4_tokenizer.json"
QWEN = "/tmp/qwen_tokenizer.json"
CORPUS = Path("/tmp/locgen/batch_0")


def iter_lines():
    for p in sorted(CORPUS.rglob("*.py")):
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                yield line


def tokenize_stream(tok, max_lines, label):
    """Tokenize up to max_lines lines, measuring throughput and aggregates."""
    n_lines = 0
    n_chars = 0
    n_tokens = 0
    t0 = time.time()
    buf = []
    for line in iter_lines():
        buf.append(line)
        n_lines += 1
        if n_lines >= max_lines:
            break
        if len(buf) >= 512:
            n_tokens += sum(len(e.ids) for e in tok.encode_batch(buf))
            n_chars += sum(len(b) for b in buf)
            buf = []
    if buf:
        n_tokens += sum(len(e.ids) for e in tok.encode_batch(buf))
        n_chars += sum(len(b) for b in buf)
    dt = time.time() - t0
    print(f"\n[{label}] {max_lines:,} lines, {n_chars:,} chars, {n_tokens:,} tokens "
          f"in {dt:.1f}s ({n_tokens / dt:,.0f} tok/s)")
    print(f"  tokens/line = {n_tokens / n_lines:.3f}")
    print(f"  chars/token = {n_chars / n_tokens:.3f}  (bytes/token)")
    print(f"  tokens/KB  = {n_tokens / (n_chars / 1024):.1f}")
    # scale projections
    for loc in (100_000, 1_000_000, 10_000_000):
        toks = n_tokens / n_lines * loc
        print(f"  {loc/1e6:.1f}M LOC => ~{toks/1e6:.2f}M tokens "
              f"({('FITS 1M ctx' if toks <= 1_000_000 else f'{toks/1e6:.1f}x OVER 1M ctx')})")
    return n_tokens, n_lines, n_chars


def main():
    max_lines = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    v4 = Tokenizer.from_file(V4)
    qw = Tokenizer.from_file(QWEN)
    v4.enable_truncation(max_length=1_048_576)  # 1M ctx cap like the model
    qw.enable_truncation(max_length=131_072)    # qwen 2.5 default 128K ctx
    print(f"V4 tokenizer vocab: {v4.get_vocab_size()}  Qwen vocab: {qw.get_vocab_size()}")
    t_v4, l_v4, c_v4 = tokenize_stream(v4, max_lines, "DeepSeek-V4")
    t_qw, l_qw, c_qw = tokenize_stream(qw, max_lines, "Qwen2.5")
    print(f"\nV4/Qwen token ratio: {t_v4 / max(t_qw, 1):.3f} "
          f"(<1 means V4 is more token-efficient on code)")


if __name__ == "__main__":
    main()
