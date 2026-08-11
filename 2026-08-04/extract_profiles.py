#!/usr/bin/env python3
"""Extract all model profiles from oe-local benchmarks/model_profiles into one target matrix."""
import json
from pathlib import Path

profiles_dir = Path("/home/idor/oe-local/benchmarks/model_profiles")
profiles = {}
for p in sorted(profiles_dir.glob("*.json")):
    try:
        d = json.load(open(p))
        profiles[d.get("model_name", p.stem)] = d
    except Exception as e:
        print(f"skip {p}: {e}")

# union of benchmark keys
keys = set()
for d in profiles.values():
    keys.update(d.get("benchmark_scores", {}).keys())
keys = sorted(keys)

print(f"{'benchmark':<28}", end="")
for name in profiles:
    print(f"{name[:14]:>15}", end="")
print()
for k in keys:
    print(f"{k:<28}", end="")
    for name, d in profiles.items():
        v = d.get("benchmark_scores", {}).get(k)
        print(f"{str(v):>15}", end="")
    print()

print("\n=== architecture params ===")
for name, d in profiles.items():
    arch = d.get("architecture", {})
    print(f"{name}: {arch.get('parameters')} | ctx {arch.get('context_window')} | {arch.get('type')}")

print("\n=== failure modes ===")
for name, d in profiles.items():
    fms = d.get("failure_modes", [])
    if fms:
        print(f"{name}: {len(fms)} failure modes -> " +
              ", ".join(f"{f.get('benchmark')}={f.get('score')}" for f in fms[:6]))
