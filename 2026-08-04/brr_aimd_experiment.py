#!/usr/bin/env python3
"""brr_aimd_experiment.py — AIMD budget control vs fixed budget on the BRR training loop.

Tests hypothesis F4 (BOUNDED_RECURSION_RESEARCH.md): "if score_d - score_{d-1} >= theta:
B_{d+1} = B_d + alpha (additive increase), else: B_{d+1} = B_d / 2 (multiplicative
decrease)" — a closed-loop guard against recursive overshoot (the TCP congestion
analog). Question: does AIMD beat a fixed budget on quality-per-token?

Same task/verifier/system as brr_experiment_v2 (imported — identical scoring), same
model, 3 seeds, 2 arms (FIXED 400/round vs AIMD start 400, theta 5, alpha 50, min 100),
depth 4. Deterministic except model sampling (labeled).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import torch  # noqa: E402
from brr_experiment_v2 import (  # noqa: E402
    TASK, SYSTEM_PRIMED, critique, score_formula, load,
)

MODEL = "Qwen/Qwen2.5-1.5B"
DEPTH = 4
SEEDS = 3
OUT = Path(__file__).resolve().parent / "brr_aimd_results.json"


def run_arm(model, tok, dev, arm, seed):
    budgets = []
    b = 400
    prev_score = 0.0
    best = 0
    total_tok = 0
    degraded = 0
    scores = []
    msgs = [{"role": "system", "content": SYSTEM_PRIMED},
            {"role": "user", "content": TASK}]
    for d in range(DEPTH):
        if arm == "aimd":
            b = max(100, b)
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model.generate(
                **inputs, max_new_tokens=b, do_sample=True, temperature=0.9,
                top_p=0.9, pad_token_id=tok.eos_token_id)
        gen = out[0][inputs["input_ids"].shape[1]:]
        resp = tok.decode(gen, skip_special_tokens=True)
        n_tok = len(gen)
        total_tok += n_tok
        score, report = score_formula(resp)
        scores.append(score)
        best = max(best, score)
        if d > 0 and score < prev_score:
            degraded += 1
        if arm == "aimd":
            if score - prev_score >= 5:
                b += 50  # additive increase
            else:
                b = b // 2  # multiplicative decrease
        budgets.append(b)
        prev_score = score
        msgs.append({"role": "assistant", "content": resp})
        msgs.append({"role": "user", "content": critique(report)})
    qpt = best / max(total_tok, 1)
    return {"arm": arm, "seed": seed, "scores": scores, "best": best,
            "total_tokens": total_tok, "qpt": qpt, "degraded": degraded,
            "budgets": budgets}


def main():
    model, tok = load(MODEL)
    dev = "cuda"
    results = []
    t0 = time.time()
    for arm in ("fixed", "aimd"):
        for seed in range(SEEDS):
            torch.manual_seed(seed)
            results.append(run_arm(model, tok, dev, arm, seed))
            r = results[-1]
            print(f"{arm} s{seed}: best={r['best']} qpt={r['qpt']:.5f} "
                  f"tok={r['total_tokens']} degraded={r['degraded']} budgets={r['budgets']}",
                  file=sys.stderr, flush=True)
    OUT.write_text(json.dumps({"results": results,
                               "elapsed_s": round(time.time() - t0, 1)}, indent=1))
    for arm in ("fixed", "aimd"):
        rs = [r for r in results if r["arm"] == arm]
        b = sum(r["best"] for r in rs) / len(rs)
        q = sum(r["qpt"] for r in rs) / len(rs)
        t = sum(r["total_tokens"] for r in rs) / len(rs)
        d = sum(r["degraded"] for r in rs)
        print(f"== {arm}: mean best {b:.0f} | mean qpt {q:.5f} | mean tokens {t:.0f} | degraded {d}/{len(rs)}")
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()
