#!/usr/bin/env python3
"""Verify DeepSeek-V4 architecture numbers from the real config.json (CIIF recursive check)."""
import json
import math

cfg = json.load(open("/home/idor/oe-local/2026-08-04/ds_v4_config.json"))

H = cfg["hidden_size"]                 # 4096
L = cfg["num_hidden_layers"]           # 43
V = cfg["vocab_size"]                  # 129280
hd = cfg["head_dim"]                   # 512
n_heads = cfg["num_attention_heads"]   # 64
kv_heads = cfg["num_key_value_heads"]  # 1 (MLA)
q_lr = cfg["q_lora_rank"]              # 1024
o_lr = cfg["o_lora_rank"]              # 1024
rope_d = cfg["qk_rope_head_dim"]       # 64
mie = cfg["moe_intermediate_size"]     # 2048
n_rt = cfg["n_routed_experts"]         # 256
n_sh = cfg["n_shared_experts"]         # 1
n_tok = cfg["num_experts_per_tok"]     # 6
idx_hd = cfg["index_head_dim"]         # 128
idx_nh = cfg["index_n_heads"]          # 64
idx_topk = cfg["index_topk"]           # 512
max_ctx = cfg["max_position_embeddings"]  # 1048576

# --- layer census from compress_ratios ---
cr = cfg["compress_ratios"]
n_full = cr.count(0)
n_c4a = cr.count(4)
n_c128a = cr.count(128)
print(f"layers={L} compress_ratios len={len(cr)} full(0)={n_full} c4a(4)={n_c4a} c128a(128)={n_c128a}")
print("per-layer pattern:", "".join("0" if c == 0 else ("4" if c == 4 else "8") for c in cr))

# --- params (BF16) ---
emb = V * H
mha_q = H * (q_lr + rope_d)            # MLA q down-proj + rope
mha_kv = (q_lr + rope_d) * hd          # kv latent (u + k rope) -> hd
mha_o = hd * o_lr + o_lr * H           # o up + down
attn_per = mha_q + mha_kv + mha_o
# indexer (c4a layers only): per CIIF/impl, index Q projection
idx_per = H * (idx_hd * idx_nh)        # approx
# MoE per layer
exp_per = mie * H * 2 * 2              # swiglu: 2 gates + up+down in fp4/bf16 count
shared_per = n_sh * mie * H * 2 * 2
moe_per = exp_per * n_rt + shared_per
total = emb * 2  # embed + lm_head (untied)
per_layer = []
for i, c in enumerate(cr):
    pl = attn_per + moe_per
    if c in (4, 128):
        pl += idx_per
    per_layer.append(pl)
total += sum(per_layer)
params = total / 1e9
print(f"\nparams total ~ {params:.1f}B")
print(f"per-layer attn={attn_per/1e6:.1f}M idx={idx_per/1e6:.1f}M moe={moe_per/1e9:.2f}B")
print(f"embedding+head {emb*2/1e9:.2f}B")

# --- sizes ---
for name, bytes_per in [("bf16", 2), ("fp8", 1), ("int4", 0.5)]:
    print(f"weights {name}: {total * bytes_per / 1e9:.0f} GB")

# --- KV cache: MLA latent + compressed-layer savings ---
# MLA kv per layer (latent only): q_lr + rope_d floats; c4a/c128a keep index-selected entries
kv_float_per_layer = (q_lr + rope_d) * 2  # per token, fp8 storage
kv_fp8_per_layer = (q_lr + rope_d)
# compressed layers keep index_topk tokens of compressed kv per token block
kv_full = (q_lr + rope_d) * max_ctx * 1  # bytes fp8 per layer
kv_comp = kv_full  # ratio applied via token retention
print(f"\nKV per layer (fp8, 1M ctx, latent {q_lr+rope_d} dims): {kv_full/1e9:.1f} GB")
print(f"KV all layers: {kv_full*L/1e9:.0f} GB (upper bound, no sparsity)")
print(f"KV c128a layers @1/128 retention: {kv_full*n_c128a/128/1e9:.1f} GB")
print(f"KV c4a layers @1/4 retention: {kv_full*n_c4a/4/1e9:.1f} GB")
print(f"KV full layers (0): {kv_full*n_full/1e9:.1f} GB")
total_kv = kv_full * (n_full + n_c4a / 4 + n_c128a / 128) / 1e9
print(f"KV total with compress ratios: {total_kv:.1f} GB (fp8)")
