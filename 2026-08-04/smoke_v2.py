#!/usr/bin/env python3
"""Runtime smoke test for brr_experiment_v2.py — the verifier gate I skipped."""
import importlib.util

spec = importlib.util.spec_from_file_location("v2", "brr_experiment_v2.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

good = ("FORMULA: $$V_{tot} = \\sum_{i=1}^{N} \\tau_i v_i - \\kappa H(S)$$\n"
        "VAR: tau_i = tick rate\n"
        "VAR: v_i = value\n"
        "VAR: kappa = loss\n"
        "VAR: H = entropy\n"
        "DOMAINS: game AI, entropy, math")
s, r = m.score_formula(good)
assert s >= 80, f"known-good scored only {s}"
assert r["format_adherence"] is True
print(f"known-good score: {s} | adherence: {r['format_adherence']}")

bad = "no formula here at all"
s2, r2 = m.score_formula(bad)
assert s2 < 40, f"garbage scored {s2}"
assert r2["format_adherence"] is False
print(f"garbage score: {s2} | adherence: {r2['format_adherence']}")

partial = "$$V = A / 0$$"
s3, r3 = m.score_formula(partial)
assert r3["boundary_issues"], "expected boundary issue"
print(f"boundary case: issues={r3['boundary_issues']}")

print("SMOKE OK")
