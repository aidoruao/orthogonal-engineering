#!/usr/bin/env python3
"""registry_normalize.py — the E4 version-mismatch fix: one table, version labels.

The 11 profiles and the V4 READMEs use different eval versions under the same names
(SWE_Bench vs SWE Verified; MMLU-Pro 0.606 vs 86.2; LiveCodeBench_v6 vs LiveCodeBench).
This tool reads the profiles, emits a cross-model matrix PER benchmark with a
version_risk flag where the profile key's version is known to differ from the V4
README's — so no comparison is made across versions without the label.

Deterministic; writes registry_normalized.json + prints the matrix.
"""
import json
from pathlib import Path

PROFILES = Path("/home/idor/oe-local/benchmarks/model_profiles")
OUT = Path(__file__).resolve().parent / "registry_normalized.json"

# profile-key -> (label, version_risk vs V4 README naming)
BENCHMARKS = {
    "HLE": ("HLE", False),
    "HLE_Text": ("HLE (text-only)", False),
    "BrowseComp": ("BrowseComp", False),
    "LiveCodeBench_v6": ("LiveCodeBench", True),   # README: LiveCodeBench (v6? unstated)
    "MMLU": ("MMLU", False),
    "MMLU_Pro": ("MMLU-Pro", True),                # profile 0.606 vs README 86.2 (scale)
    "GPQA_Diamond": ("GPQA Diamond", False),
    "AIME_2025": ("AIME 2025", False),
    "HMMT_2025": ("HMMT 2025", False),
    "ARC_AGI_3": ("ARC-AGI-3", False),
    "MATH": ("MATH", False),
    "GSM8K": ("GSM8K", False),
    "HumanEval": ("HumanEval", False),
    "SWE_Bench": ("SWE Bench", True),              # README: SWE Verified
}


def main():
    models = {}
    for f in sorted(PROFILES.glob("*.json")):
        d = json.load(open(f))
        models[d["model_name"]] = d.get("benchmark_scores", {})
    matrix = {}
    for key, (label, risk) in BENCHMARKS.items():
        row = {}
        for m, scores in models.items():
            if key in scores:
                row[m] = scores[key]
        if row:
            matrix[label] = {"version_risk": risk, "scores": row}
    OUT.write_text(json.dumps(matrix, indent=1))
    for label, info in matrix.items():
        r = " [VERSION RISK — profile version differs from V4 README]" if info["version_risk"] else ""
        vals = ", ".join(f"{m}: {v}" for m, v in info["scores"].items())
        print(f"{label}:{r}\n  {vals}")


if __name__ == "__main__":
    main()
