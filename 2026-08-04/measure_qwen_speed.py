#!/usr/bin/env python3
"""Measure qwen2.5-1.5b real inference speed on this GPU (E_inference data point for CIIF)."""
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

NAME = "Qwen/Qwen2.5-1.5B"
tok = AutoTokenizer.from_pretrained(NAME)
model = AutoModelForCausalLM.from_pretrained(NAME, torch_dtype=torch.float16).to("cuda")

# prompt: code-adjacent task (CIIF software-use context)
prompt = "Write a Python function that computes the factorial of n recursively."
ids = tok(prompt, return_tensors="pt").input_ids.cuda()
print(f"prompt tokens: {ids.shape[1]}")

# warmup
model.generate(ids, max_new_tokens=16, do_sample=False)
torch.cuda.synchronize()

# measure: 256 new tokens, greedy
t0 = time.time()
out = model.generate(ids, max_new_tokens=256, do_sample=False)
torch.cuda.synchronize()
dt = time.time() - t0
n = out.shape[1] - ids.shape[1]
print(f"generate: {n} tokens in {dt:.2f}s => {n / dt:.1f} tok/s (greedy, fp16, RTX 4050)")

# power draw estimate
try:
    p = torch.cuda.power_draw() if hasattr(torch.cuda, "power_draw") else None
    print("power_draw API:", p)
except Exception as e:
    print("no power API:", e)

toks = 512
t0 = time.time()
out = model.generate(ids, max_new_tokens=toks, do_sample=True, temperature=0.7)
torch.cuda.synchronize()
dt = time.time() - t0
n = out.shape[1] - ids.shape[1]
print(f"sampled: {n} tokens in {dt:.2f}s => {n / dt:.1f} tok/s")
print(f"tokens-per-second average: {(n / dt):.1f}")
