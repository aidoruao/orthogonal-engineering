#!/usr/bin/env python3
"""margin_stream_collector.py — dump raw per-token logit margins/probs for the PLL sim.

Same 6 deterministic prompts as jitter_gate_feasibility.py; writes
/tmp/margin_streams.json  [{domain, prompt, margins[], probs[]}] (deterministic greedy).
"""
import json
import sys

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen2.5-1.5B"
MAX_NEW = 200
OUT = "/tmp/margin_streams.json"

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
    streams = []
    for domain, prompts in PROMPTS.items():
        for prompt in prompts:
            enc = tok(prompt, return_tensors="pt").input_ids.to(dev)
            margins, probs = [], []
            for _ in range(MAX_NEW):
                with torch.no_grad():
                    out = model(enc)
                logits = out.logits[0, -1].float()
                top2 = torch.topk(logits, 2)
                margins.append((top2.values[0] - top2.values[1]).item())
                probs.append(torch.softmax(logits, dim=-1)[top2.indices[0]].item())
                nxt = top2.indices[0].unsqueeze(0).unsqueeze(0)
                enc = torch.cat([enc, nxt], dim=-1)
                if nxt.item() == tok.eos_token_id:
                    break
            streams.append({"domain": domain, "prompt": prompt[:40], "margins": margins, "probs": probs})
    json.dump(streams, open(OUT, "w"))
    print(f"collected {len(streams)} streams -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
