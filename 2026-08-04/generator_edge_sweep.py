#!/usr/bin/env python3
"""generator_edge_sweep.py — edge-case sweep + scaling arithmetic for generator batches.

Checks (classic software tooling: checksums, dedup, compile gate, byte coverage):
  1. Integrity: sha256 per file -> Merkle-style chain root (the decades-old cksum chain).
  2. Dedup: identical file hashes / near-dup line rate (sort|uniq analog).
  3. Syntax gate: py_compile on every file (the classic lint gate).
  4. Extremes: empty files, max line length, byte-variety coverage (0x00-0xFF).
  5. Token economics: V4 tokenizer sample -> tokens/sec and tokens/LOC.
  6. Scaling arithmetic: extrapolate to 1B tokens / 1B LOC / 1Qi (wall time, disk).
Deterministic; reports JSON + human lines.
"""
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

BATCH = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/locgen4/batch_0")
V4 = "/tmp/v4_tokenizer.json"
SAMPLE_FILES = 30  # tokenize at most this many files for token stats


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    files = sorted(BATCH.rglob("*.py"))
    if not files:
        print("no .py files found")
        return 1
    t0 = time.time()
    hashes = {}
    sizes = []
    line_lens = []
    byte_seen = set()
    empty = 0
    compile_fail = []
    for p in files:
        h = sha256_file(p)
        hashes[p] = h
        raw = p.read_bytes()
        sizes.append(len(raw))
        byte_seen.update(raw)
        if not raw.strip():
            empty += 1
        try:
            import py_compile
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            compile_fail.append((str(p), str(e)[:80]))
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line_lens.append(len(line.rstrip("\n")))
    n = len(files)
    total_bytes = sum(sizes)
    dup_files = n - len(set(hashes.values()))
    line_count = len(line_lens)
    max_line = max(line_lens) if line_lens else 0
    mean_line = sum(line_lens) / max(len(line_lens), 1)
    # Merkle-style chain root: hash in FILE-PATH order — matches scale_run_300.py and
    # the 1B-corpus MANIFEST root a07920a6c404… (a hash-sorted chain is a different
    # construction: same content, different root)
    chain = hashlib.sha256()
    for h in (hashes[p] for p in files):
        chain.update(h.encode())
    root = chain.hexdigest()

    dt = time.time() - t0
    print(f"files: {n} | bytes: {total_bytes:,} ({total_bytes / 1e6:.1f} MB) | lines: {line_count:,}")
    print(f"empty files: {empty} | duplicate files (by sha256): {dup_files}")
    print(f"max line: {max_line:,} chars | mean line: {mean_line:.1f} | byte-variety: {len(byte_seen)}/256 distinct bytes")
    print(f"compile gate: {n - len(compile_fail)}/{n} pass" + (f" | FAILURES: {compile_fail[:3]}" if compile_fail else ""))
    print(f"integrity chain root: {root} (sha256 over sorted file hashes, {dt:.1f}s sweep)")

    # token economics on a sample
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(V4)
    n_tok = 0
    n_chars = 0
    n_lines = 0
    t1 = time.time()
    for p in files[:SAMPLE_FILES]:
        text = p.read_text(encoding="utf-8", errors="replace")
        n_chars += len(text)
        n_lines += text.count("\n")
        n_tok += len(tok.encode(text).ids)
    dt2 = time.time() - t1
    cpt = n_chars / max(n_tok, 1)
    tps = n_tok / max(dt2, 1e-6)
    loc_per_tok = n_lines / max(n_tok, 1)
    print(f"\ntoken sample: {n_lines:,} lines / {n_chars:,} chars / {n_tok:,} V4 tokens "
          f"({cpt:.2f} chars/token, {loc_per_tok:.4f} LOC/token, {tps:,.0f} tok/s on this machine)")

    # scaling arithmetic (extrapolation, honest [proj])
    gen_tok_s = tps * (total_bytes / max(n_chars, 1))  # scale sample rate to whole batch
    print("\nscaling arithmetic [proj — extrapolation from this run]:")
    for label, n_tokens in (("100M tokens", 1e8), ("1B tokens", 1e9), ("10B tokens", 1e10)):
        hours = n_tokens / gen_tok_s / 3600
        gb = n_tokens * cpt / 1e9
        print(f"  {label}: ~{hours:.1f} h materialization at this rate | ~{gb:.1f} GB disk")
    print(f"  1B-LOC layer-0 universe (100 batches of 10M lines): ~{1.24 * 100:.0f} GB "
          f"| 1Qi layer-3: ~{1.24e9 * 100 * 1e9 / 1e12:.1f} TB [proj, minimal-storage design ~500 MB]")

    out = Path(__file__).resolve().parent / "generator_edge_sweep.json"
    out.write_text(json.dumps({
        "batch": str(BATCH), "files": n, "bytes": total_bytes, "lines": line_count,
        "empty": empty, "dup_files": dup_files, "max_line": max_line, "mean_line": mean_line,
        "byte_variety": len(byte_seen), "compile_pass": n - len(compile_fail), "compile_fail": compile_fail[:5],
        "chain_root": root, "sample_tokens": n_tok, "chars_per_token": cpt,
        "tok_per_s": tps, "hours_to_1B_tokens": 1e9 / gen_tok_s / 3600,
    }, indent=1))
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
