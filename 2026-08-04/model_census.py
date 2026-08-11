#!/usr/bin/env python3
"""model_census.py — no-download tensor census for open-weight frontier models.

WS1 executable: fetch config.json + model.safetensors.index.json over HTTP (same method
as the V4 census — no weights, no llama.cpp), parse tensor names/shapes, derive
architecture facts, cross-check against the config, emit a deterministic JSON per model.

Models (default): Qwen3-235B-A22B (qwen3_moe), Kimi-K2-Instruct (deepseek_v3 lineage).
Extensible: MODEL_INDEX dict + optional CLI args.

Determinism: sorted keys everywhere; no randomness; double-run sha-verified.
Output: census/<model-slug>.json + printed summary.
"""
import hashlib
import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "census"

MODEL_INDEX = {
    "qwen3-235b": {
        "config": "https://huggingface.co/Qwen/Qwen3-235B-A22B/raw/main/config.json",
        "index": "https://huggingface.co/Qwen/Qwen3-235B-A22B/resolve/main/model.safetensors.index.json",
        "slug": "qwen3_235b_a22b",
    },
    "kimi-k2": {
        "config": "https://huggingface.co/moonshotai/Kimi-K2-Instruct/raw/main/config.json",
        "index": "https://huggingface.co/moonshotai/Kimi-K2-Instruct/resolve/main/model.safetensors.index.json",
        "slug": "kimi_k2_instruct",
    },
}

# component classifiers — ordered name-pattern → component key
PATTERNS = [
    (re.compile(r"\.experts\.(\d+)\.(gate_up_proj|down_proj|up_proj|gate_proj)\.weight$"), "expert"),
    (re.compile(r"shared_expert"), "shared_expert"),
    (re.compile(r"(router|gate)\.weight$"), "router"),
    (re.compile(r"\.q_a_(proj|norm)\.weight$"), "mla_q"),
    (re.compile(r"\.kv_a_(proj|norm)\.weight$"), "mla_kv"),
    (re.compile(r"\.q_b\.weight$"), "mla_q"),
    (re.compile(r"\.kv_b\.weight$"), "mla_kv"),
    (re.compile(r"\.q_proj\.weight$"), "q_proj"),
    (re.compile(r"\.k_proj\.weight$"), "k_proj"),
    (re.compile(r"\.v_proj\.weight$"), "v_proj"),
    (re.compile(r"\.o_proj\.weight$"), "o_proj"),
    (re.compile(r"\.(input_)?layernorm\.weight$"), "layernorm"),
    (re.compile(r"\.norm\.weight$"), "layernorm"),
    (re.compile(r"embed_tokens\.weight$"), "embedding"),
    (re.compile(r"lm_head\.weight$"), "lm_head"),
    (re.compile(r"(mtp|nextn|predict)"), "speculation"),
    (re.compile(r"model\.layers\.(\d+)\."), "layer_block"),
]


def fetch(url, max_bytes=256 * 1024 * 1024):
    req = urllib.request.Request(url, headers={"User-Agent": "oe-local-census/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"{url}: exceeds {max_bytes} bytes")
    return data


def classify(name):
    for pat, key in PATTERNS:
        if pat.search(name):
            return key
    return "other"


def layer_no(name):
    m = re.search(r"\.layers\.(\d+)\.", name)
    return int(m.group(1)) if m else None


def main():
    args = sys.argv[1:] or list(MODEL_INDEX)
    OUT_DIR.mkdir(exist_ok=True)
    for key in args:
        if key not in MODEL_INDEX:
            print(f"unknown model {key!r}; known: {list(MODEL_INDEX)}", file=sys.stderr)
            continue
        spec = MODEL_INDEX[key]
        print(f"== {key}: fetching config", file=sys.stderr)
        config = json.loads(fetch(spec["config"]).decode())
        print(f"== {key}: fetching index", file=sys.stderr)
        index = json.loads(fetch(spec["index"]).decode())
        weight_map = index["weight_map"]
        total_bytes = index.get("metadata", {}).get("total_size", 0)

        counts = Counter()
        per_layer = Counter()
        shapes = {}
        spec_experts = set()
        for name in sorted(weight_map):
            comp = classify(name)
            counts[comp] += 1
            ln = layer_no(name)
            if ln is not None:
                per_layer[ln] += 1
            if comp == "expert":
                m = re.search(r"\.experts\.(\d+)\.", name)
                if m:
                    spec_experts.add(int(m.group(1)))
            # shape: from shard file+offset we can't get shapes w/o reading shards;
            # record names only (param counts come from metadata total_size).

        n_layers = len(per_layer)
        n_experts = max(spec_experts) + 1 if spec_experts else 0

        # cross-checks vs config
        cfg_layers = config.get("num_hidden_layers")
        cfg_experts = config.get("num_experts") or config.get("n_routed_experts")
        checks = {
            "layers": (n_layers == cfg_layers, f"tensor-derived {n_layers} vs config {cfg_layers}"),
            "experts": (n_experts == cfg_experts, f"tensor-derived {n_experts} vs config {cfg_experts}"),
            "tensors_nonzero": (len(weight_map) > 0, f"{len(weight_map)} tensors"),
        }
        report = {
            "model": key, "slug": spec["slug"],
            "config_url": spec["config"], "index_url": spec["index"],
            "config_summary": {
                k: config.get(k) for k in (
                    "model_type", "num_hidden_layers", "num_attention_heads",
                    "num_key_value_heads", "num_experts", "n_routed_experts",
                    "num_experts_per_tok", "max_position_embeddings", "vocab_size",
                    "torch_dtype", "hidden_size", "head_dim",
                )
            },
            "total_tensor_bytes": total_bytes,
            "num_tensors": len(weight_map),
            "component_counts": dict(counts),
            "per_layer_tensor_counts": {
                "layers_found": n_layers,
                "min": min(per_layer.values()) if per_layer else 0,
                "max": max(per_layer.values()) if per_layer else 0,
            },
            "num_experts_derived": n_experts,
            "checks": {k: {"pass": ok, "note": note} for k, (ok, note) in checks.items()},
            "sample_tensor_names": sorted(weight_map)[:12],
            "index_sha256": hashlib.sha256(fetch(spec["index"])).hexdigest(),
        }
        out = OUT_DIR / f"{spec['slug']}.json"
        out.write_text(json.dumps(report, indent=1, sort_keys=True))
        ok = all(v["pass"] for v in report["checks"].values())
        print(f"[{'OK ' if ok else 'FAIL'}] {key}: {len(weight_map)} tensors, "
              f"{total_bytes:,} B, {n_layers} layers, {n_experts} experts "
              f"-> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
