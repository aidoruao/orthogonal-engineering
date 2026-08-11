#!/usr/bin/env python3
"""Per-layer tensor presence for boundary layers + router/mtp census."""
import json
import re
from collections import defaultdict

d = json.load(open("ds_v4_index.json"))
wm = set(d["weight_map"].keys())

def has(layer, sub):
    return any(k.startswith(f"layers.{layer}.") and sub in k and "experts." not in k for k in wm)

print("layer | compressor | indexer | tid2eid | gate.bias | attn_sink")
for l in range(43):
    print(f"{l:5d} | {has(l,'attn.compressor'):^9} | {has(l,'attn.indexer'):^9} | {has(l,'gate.tid2eid'):^7} | {has(l,'ffn.gate.bias'):^9} | {has(l,'attn_sink'):^9}")

# mtp count
mtp_layers = sorted(set(int(m.group(1)) for k in wm if (m := re.match(r"mtp\.(\d+)\.", k))))
print("\nmtp layers:", mtp_layers)
for m in mtp_layers:
    n_exp = len(set(int(e.group(1)) for k in wm
                    if (e := re.match(rf"mtp\.{m}\.ffn\.experts\.(\d+)\.w\d\.weight", k))))
    markov = any(k.startswith(f"mtp.{m}.") and "markov" in k for k in wm)
    conf = any(k.startswith(f"mtp.{m}.") and "confidence" in k for k in wm)
    print(f"  mtp.{m}: experts={n_exp} markov_head={markov} confidence_head={conf}")
