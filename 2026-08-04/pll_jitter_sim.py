#!/usr/bin/env python3
"""pll_jitter_sim.py — second-order PLL as the DSpark jitter gate (aerospace transfer).

Aerospace: a phase-locked loop locks onto a carrier and *holds* lock through noise,
declaring loss-of-lock only on sustained phase error (hysteresis). Catalog #12's gate
becomes a dynamical tracker instead of a per-window threshold:

  carrier setpoint  : margin_lock = 4.0  (high-consensus rhythm)
  phase error       : err[n] = margin_lock - margin[n]
  loop filter       : second order — prop gain A, integrator gain B
  lock state        : |smoothed err| < unlock_hi  -> LOCKED (block=5)
                      |smoothed err| > unlock_hi  -> UNLOCKED (block=1)
  hysteresis        : lock re-acquires only below lock_lo < unlock_hi

Metrics: locked fraction, mean block size, drafted-token cost vs fixed-block-5
baseline, per domain. Simulated policy on qwen-1.5b margin streams — V4 validation
pre-registered (catalog #12 measure line). Deterministic.
"""
import json
import sys

STREAMS = "/tmp/margin_streams.json"
LOCK = 4.0
A, B = 0.3, 0.05
LOCK_LO, UNLOCK_HI = 1.5, 2.5
BLOCK_LOCKED, BLOCK_OPEN = 5, 1


def simulate(margins):
    err_smooth = 0.0
    integrator = 0.0
    locked = False
    states = []
    for m in margins:
        err = LOCK - m
        integrator += B * err
        err_smooth = A * err + integrator
        if locked:
            if err_smooth > UNLOCK_HI:
                locked = False
        else:
            if err_smooth < LOCK_LO:
                locked = True
        states.append(locked)
    return states


def main():
    streams = json.load(open(STREAMS))
    total_locked = total_n = 0
    base_drafted = 0
    pll_drafted = 0
    print(f"{'domain':<10} {'n':>4} {'locked%':>8} {'mean_block':>10} "
          f"{'draft_cost':>11} {'vs_baseline':>11}")
    per = {}
    for s in streams:
        n = len(s["margins"])
        states = simulate(s["margins"])
        locked_frac = sum(states) / n
        block = sum(BLOCK_LOCKED if st else BLOCK_OPEN for st in states) / n
        drafted = sum((BLOCK_LOCKED - 1) if st else 0 for st in states)
        base = (BLOCK_LOCKED - 1) * n
        per.setdefault(s["domain"], [0, 0, 0])
        per[s["domain"]][0] += n
        per[s["domain"]][1] += sum(states)
        per[s["domain"]][2] += drafted
        total_n += n
        total_locked += sum(states)
        base_drafted += base
        pll_drafted += drafted
        print(f"{s['domain']:<10} {n:>4} {locked_frac:>7.1%} {block:>10.1f} "
              f"{drafted:>11} {drafted - base:>+11}")
    for d, (n, lk, dr) in per.items():
        print(f"== {d}: locked {lk / n:.1%}, drafted {dr} (baseline {4 * n})", file=sys.stderr)
    print(f"\nTOTAL: locked {total_locked / total_n:.1%} | PLL drafted {pll_drafted:,} "
          f"vs fixed-block-5 baseline {base_drafted:,} "
          f"({(pll_drafted - base_drafted) / base_drafted:+.1%})")
    print("interpretation: the PLL spends draft budget only inside locked (low-jitter) "
          "regions; the delta vs baseline is the speculative-cost saved on unlocked "
          "(high-jitter) tokens — the tail-gate behavior, with hysteresis instead of "
          "a per-window threshold.")


if __name__ == "__main__":
    main()
