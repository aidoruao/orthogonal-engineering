#!/usr/bin/env python3
"""jitter_gate_feasibility.py — feasibility study for catalog #12 (jitter-gated speculation).

Question: can a FREE per-token signal (top-1/top-2 logit margin, top-1 probability) act
as the DSpark jitter gate? If code (low-jitter, high-consensus) shows systematically
higher margins / lower probability variance than reasoning (high-jitter), the gate is
feasible: shrink speculative blocks where margin < threshold.

Method (deterministic):
  1. Load cached qwen2.5-1.5b (the same local model used by the BRR harness).
  2. Greedy decode 6 fixed prompts (3 code, 3 reasoning), max ~200 tokens each,
     recording per-token top-1/top-2 logits (margin = l1 - l2) and top-1 softmax p.
  3. Per prompt: token count, mean margin, margin std, %tokens with margin > 1.0,
     window-jitter (std of p over sliding 8-token windows, mean + max).
  4. Aggregate by domain; report separation (the gate's discrimination power).

Caveat: qwen2.5-1.5b is NOT V4; this validates the SIGNAL, not the model. The V4
confidence_head/markov variance will be the production source; this shows whether a
logit-only gate can drive block sizing at all.
"""
import json
import math
import sys
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen2.5-1.5B"  # base model, as cached (BRR harness uses this id)
MAX_NEW = 200

PROMPTS = {
    "code": [
        "Write a Python function that computes the Fibonacci sequence iteratively.",
        "Write a Python class implementing a stack with push, pop, and peek methods.",
        "Write a Python function that checks whether a string is a palindrome.",
    ],
    "reasoning": [
        "A train travels at 60 mph for 2 hours, then at 40 mph for 1.5 hours. What is the average speed over the whole trip? Show your work.",
        "If all A are B, and some B are C, can we conclude that some A are C? Explain your reasoning carefully.",
        "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Show your reasoning.",
    ],
}


def main():
    tok = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL, local_files_only=True, torch_dtype=torch.float16)
    model.eval()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev)
    print(f"device: {dev}, params: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B", file=sys.stderr)

    summary = {}
    t0 = time.time()
    for domain, prompts in PROMPTS.items():
        for i, prompt in enumerate(prompts):
            enc = tok(prompt, return_tensors="pt").input_ids
            enc = enc.to(dev)
            margins = []
            probs = []
            input_ids = enc
            for step in range(MAX_NEW):
                with torch.no_grad():
                    out = model(input_ids)
                logits = out.logits[0, -1].float()
                top2 = torch.topk(logits, 2)
                l1, l2 = top2.values
                margin = (l1 - l2).item()
                p = torch.softmax(logits, dim=-1)[top2.indices[0]].item()
                margins.append(margin)
                probs.append(p)
                nxt = top2.indices[0].unsqueeze(0).unsqueeze(0)
                input_ids = torch.cat([input_ids, nxt], dim=-1)
                if nxt.item() == tok.eos_token_id:
                    break
            # window jitter: std of p over sliding 8-token windows
            W = 8
            win_std = [
                torch.tensor(probs[i:i + W]).std().item()
                for i in range(0, len(probs) - W + 1)
            ]
            rec = {
                "domain": domain,
                "prompt": prompt[:60],
                "tokens": len(margins),
                "mean_margin": sum(margins) / len(margins),
                "std_margin": torch.tensor(margins).std().item(),
                "pct_margin_gt_1": sum(1 for m in margins if m > 1.0) / len(margins),
                "mean_window_jitter": (sum(win_std) / len(win_std)) if win_std else 0.0,
                "max_window_jitter": max(win_std) if win_std else 0.0,
                "mean_p": sum(probs) / len(probs),
            }
            summary[f"{domain}_{i}"] = rec
            print(json.dumps(rec))

    print(f"\nelapsed {time.time() - t0:.0f}s", file=sys.stderr)

    # domain aggregates
    for d in ("code", "reasoning"):
        rs = [v for k, v in summary.items() if k.startswith(d)]
        n = sum(r["tokens"] for r in rs)
        mm = sum(r["mean_margin"] * r["tokens"] for r in rs) / n
        jit = sum(r["mean_window_jitter"] * r["tokens"] for r in rs) / n
        pct = sum(r["pct_margin_gt_1"] * r["tokens"] for r in rs) / n
        print(f"\n== {d}: {n} tokens | mean margin {mm:.2f} | mean window jitter {jit:.3f} "
              f"| %margin>1.0 {pct:.1%}", file=sys.stderr)


if __name__ == "__main__":
    main()
