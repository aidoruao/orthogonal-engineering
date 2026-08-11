#!/usr/bin/env python3
"""Verify the paper's '10% KV cache vs V3.2' claim with real configs.
V3.2: kv_lora 512 + rope 64 = 576 dims/token/layer, 61 layers, full attention
V4-Flash: 1088 dims, 2 sliding + 21 CSA(4) + 20 HCA(128) @ 43 layers
V4-Pro: 1600 dims, 30 CSA + 30 HCA + 1 full @ 61 layers (compress_ratios: 128,128,(4,128)x29,4,0)
"""
CTX = 1_048_576

# --- V3.2 ---
v32_dims = 512 + 64
v32_layers = 61
v32_kv_fp8 = v32_dims * v32_layers * CTX / 1e9
v32_kv_bf16 = v32_kv_fp8 * 2

# --- V4-Flash ---
f_dims = 1024 + 64
f_sliding, f_csa, f_hca = 2, 21, 20
f_kv = (f_dims * f_csa * CTX / 4 + f_dims * f_hca * CTX / 128 + f_dims * f_sliding * 128) / 1e9

# --- V4-Pro (61 layers; csa=30, hca=30, full=1) ---
p_dims = 1536 + 64
p_csa, p_hca, p_full = 30, 30, 1
p_kv = (p_dims * p_csa * CTX / 4 + p_dims * p_hca * CTX / 128 + p_dims * p_full * CTX) / 1e9

print(f"V3.2 KV @1M: {v32_kv_fp8:.1f} GB fp8 / {v32_kv_bf16:.1f} GB bf16")
print(f"V4-Flash KV @1M: {f_kv:.1f} GB fp8  -> vs V3.2: {f_kv/v32_kv_fp8*100:.0f}% (fp8) / {f_kv/v32_kv_bf16*100:.0f}% (bf16)")
print(f"V4-Pro KV @1M:   {p_kv:.1f} GB fp8  -> vs V3.2: {p_kv/v32_kv_fp8*100:.0f}% (fp8) / {p_kv/v32_kv_bf16*100:.0f}% (bf16)")
print(f"paper claims 10% for Pro; our arithmetic: 20-40% depending on baseline dtype")
print(f"(FLOPs 27% claim not resolvable from configs alone — official activated params:")
print(f" V3.2 37B | V4-Flash ~13-16.8B | V4-Pro 49B — the 27% needs the paper's attention-cost accounting)")
