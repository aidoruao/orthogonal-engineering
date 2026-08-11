#!/usr/bin/env python3
"""Tokenizer-v2 experiment (U1): train a code-optimized byte-level BPE on oe-local Python,
compare chars/token vs the real DeepSeek-V4 tokenizer on held-out code distributions.
Usage: python3 train_code_tokenizer.py
"""
import time
from pathlib import Path

from tokenizers import Tokenizer, models, pre_tokenizers, trainers
from tokenizers import Tokenizer as T

ROOT = Path("/home/idor/oe-local")
V4 = "/tmp/v4_tokenizer.json"
OUT = "/home/idor/oe-local/2026-08-04/code_tokenizer_v1.json"
VOCAB = 129280  # match V4 vocab size


def py_files(root, exclude):
    for p in sorted(root.rglob("*.py")):
        if any(x in str(p) for x in exclude):
            continue
        yield p


def collect(paths):
    buf = []
    for p in paths:
        try:
            buf.append(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass
    return "".join(buf)


def tokenize_stats(tok, text, label):
    import time
    t0 = time.time()
    encs = tok.encode_batch([text[i:i + 400_000] for i in range(0, len(text), 400_000)])
    n_tok = sum(len(e.ids) for e in encs)
    dt = time.time() - t0
    cpt = len(text) / max(n_tok, 1)
    print(f"  {label}: {n_tok:,} tokens, chars/token={cpt:.3f} ({dt:.1f}s)")
    return cpt


def main():
    exclude = ["node_modules", "oe-train", "__pycache__", "chat_logs",
               "tests", "benchmarks", "generators", "2026-08-04", "witness"]
    # TRAIN: oe-local python minus test dirs
    train_files = list(py_files(ROOT, exclude))
    train_text = collect(train_files)
    # TEST sets (held out)
    gen_files = list(py_files(ROOT / "generators", ["__pycache__"]))
    gen_text = collect(gen_files)
    bench_text = collect(py_files(ROOT / "benchmarks", ["__pycache__"]))
    batch0_text = collect(list(Path("/tmp/locgen/batch_0").rglob("*.py")))
    print(f"train: {len(train_files)} files, {len(train_text):,} chars")
    print(f"test-gen: {len(gen_files)} files, {len(gen_text):,} chars")
    print(f"test-bench: {len(bench_text):,} chars | test-batch0: {len(batch0_text):,} chars")

    # baseline: real V4 tokenizer
    print("\n=== BASELINE: real DeepSeek-V4 tokenizer ===")
    v4 = T.from_file(V4)
    for label, text in [("generators src", gen_text), ("benchmarks src", bench_text),
                        ("generator output (batch0)", batch0_text)]:
        tokenize_stats(v4, text, label)

    # train code BPE
    print(f"\n=== TRAINING code BPE (vocab {VOCAB}) ===")
    tok = Tokenizer(models.BPE())
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    trainer = trainers.BpeTrainer(vocab_size=VOCAB, special_tokens=["<|endoftext|>", "<|pad|>"])
    t0 = time.time()
    tok.train_from_iterator([train_text], trainer=trainer)
    print(f"trained in {time.time() - t0:.0f}s")
    tok.save(OUT)
    print(f"saved: {OUT}")

    print("\n=== CODE BPE (v1) on same test sets ===")
    code = T.from_file(OUT)
    for label, text in [("generators src", gen_text), ("benchmarks src", bench_text),
                        ("generator output (batch0)", batch0_text)]:
        tokenize_stats(code, text, label)


if __name__ == "__main__":
    main()
