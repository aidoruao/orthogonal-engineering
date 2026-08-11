#!/usr/bin/env python3
"""Compare compress_ratios from both configs vs tensor-map truth."""
import json
from collections import Counter

t = json.load(open("ds_v4_config.json"))["compress_ratios"]
inf = json.load(open("ds_v4_inference_config.json"))["compress_ratios"]

for name, arr in [("transformers", t), ("inference", inf)]:
    print(f"{name}: len={len(arr)} full0={arr.count(0)} c4a={arr.count(4)} c128a={arr.count(128)}")
    print("  pattern:", "".join("0" if c == 0 else ("4" if c == 4 else "8") for c in arr))
