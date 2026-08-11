#!/usr/bin/env python3
"""Probe: real DeepSeek-V4 tokenizer on real repo code (workspace repos)."""
from pathlib import Path
from tokenizers import Tokenizer

v4 = Tokenizer.from_file("/tmp/v4_tokenizer.json")
roots = ["/home/idor/standardgalactic-library", "/home/idor/godot-OE",
         "/home/idor/shampoo-ontology-v4", "/home/idor/oe-fps-agent"]
texts = []
for r in roots:
    for p in sorted(Path(r).rglob("*.py")):
        if any(x in str(p) for x in ("node_modules", "__pycache__", ".venv", "venv")):
            continue
        try:
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass
corpus = "".join(texts)
print("real-repo corpus:", len(texts), "files,", len(corpus), "chars")
encs = v4.encode_batch([corpus[i:i + 400000] for i in range(0, len(corpus), 400000)])
nt = sum(len(e.ids) for e in encs)
print(f"V4 on real repos: chars/token = {len(corpus) / nt:.3f}  (tokens={nt:,})")
print(f"implied 1M-ctx LOC capacity: {1_000_000 / (nt / max(sum(len(t) for t in texts), 1)):,.0f} chars")
