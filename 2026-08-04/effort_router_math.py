#!/usr/bin/env python3
"""effort_router_math.py — escalation policy cost model (catalog #10, multi-signal router).

Measured anchors: HLE 8.1 (non-think) -> 34.8 (max) = 4.3x test-time scaling (Flash).
Falsification (hle_margin_probe): confidence alone cannot detect hard items -> the
router uses a multi-signal hard-probability p_hat (margin/lock + self-consistency +
verifier disagreement). This tool computes the escalation policy's economics:

  levels: non-think (acc 8.1, cost 1x), think (interp 20.0, cost 3x [assumed]),
          max (34.8, cost 10x [assumed])
  per item: escalate if p_hat > threshold -> tokens and expected accuracy under the
  threshold sweep; find the threshold meeting the pre-registered contract
  (0.40+ overall at <= 2x total tokens on hard queries; mixed workload 50% hard).

Assumptions labeled [assumed]; arithmetic only. Deterministic.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "effort_router_math.json"
LEVELS = [("non_think", 8.1, 1.0), ("think", 20.0, 3.0), ("max", 34.8, 10.0)]
FRAC_HARD = 0.5  # mixed workload: half the queries are hard


def main():
    rows = []
    best = None
    for t in [x / 100 for x in range(0, 101, 5)]:
        tok = 0.0
        acc = 0.0
        for frac_hard in (FRAC_HARD,):
            # easy items (1 - frac_hard): non-think always
            tok += (1 - frac_hard) * LEVELS[0][2]
            acc += (1 - frac_hard) * LEVELS[0][1]
            # hard items: escalate past threshold
            if t > 0.5:
                lvl = LEVELS[0]
            elif t > 0.2:
                lvl = LEVELS[1]
            else:
                lvl = LEVELS[2]
            tok += frac_hard * lvl[2]
            acc += frac_hard * lvl[1]
        rows.append({"threshold": t, "tokens_x": round(tok, 2), "accuracy": round(acc, 2)})
        if acc >= 40.0 and tok <= 2.0 and (best is None or tok < best["tokens_x"]):
            best = {"threshold": t, "tokens_x": round(tok, 2), "accuracy": round(acc, 2)}
    OUT.write_text(json.dumps({"levels": LEVELS, "frac_hard": FRAC_HARD, "sweep": rows,
                               "contract_met": best}, indent=1))
    for r in rows[::5]:
        print(f"threshold {r['threshold']:.2f}: {r['accuracy']:.1f} acc @ {r['tokens_x']:.2f}x tokens")
    print(f"\ncontract (>=40 acc, <=2x tokens): {best}")
    print("interpretation: under assumed costs (3x/10x) and a 50/50 hard split, perfect")
    print("routing reaches 21.4 acc @ 5.5x tokens — the 40+ target is a MAX-LEVEL")
    print("CAPABILITY number (needs the reasoning block to lift max-level accuracy), not")
    print("a routing number. The router's value = approaching max-level score at lower")
    print("cost; recompute the frontier with measured V4 level costs on hardware.")
    print("note: p_hat must come from the multi-signal router (margin/lock + self-")
    print("consistency + verifier) — confidence alone is falsified (hle_margin_probe).")


if __name__ == "__main__":
    main()
