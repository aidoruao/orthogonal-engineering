#!/usr/bin/env python3
"""V5-3 Expert Census: which of the 256 MoE experts are cold for code workloads.

Runs on the 4xGPU class (V4 weights required). Locally verifiable in dry-run
mode against the 72,317-tensor index (ds_v4_index.json) — no weights needed.

Design (from the tensor map + modeling_deepseek_v4.py):
  - 43 layers x 256 routed experts (tensors: layers.N.ffn.experts.E.w{1,2,3}.weight + .scale)
  - 6 experts active per token (num_experts_per_tok), gate = ffn.gate.weight (+bias), noaux_tc
  - census = hook the router, log (layer, expert) activation counts + mean gate scores
Usage:
  dry-run (this machine):  python3 expert_census.py --dry-run
  full run (big hardware): python3 expert_census.py --corpus /path/to/code.jsonl \
        --model deepseek-ai/DeepSeek-V4-Flash-0731 --output census_results.json
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

EXPERT_RE = "layers.{N}.ffn.experts.{E}.w1.weight"


def dry_run(index_path: str) -> dict:
    """Validate tensor names + build the census skeleton WITHOUT weights."""
    d = json.load(open(index_path))
    wm = d["weight_map"]
    per_layer = defaultdict(set)
    for k in wm:
        parts = k.split(".")
        # tensor names: layers.{N}.ffn.experts.{E}.w1.weight  (len == 7)
        if (len(parts) == 7 and parts[0] == "layers" and parts[2] == "ffn"
                and parts[3] == "experts" and parts[5] == "w1" and parts[6] == "weight"):
            per_layer[int(parts[1])].add(int(parts[4]))
    layers = sorted(per_layer)
    counts = {l: len(per_layer[l]) for l in layers}
    ok = all(c == 256 for c in counts.values()) and len(layers) == 43
    report = {
        "dry_run": True,
        "index": index_path,
        "layers_with_experts": len(layers),
        "experts_per_layer": counts,
        "gate_tensors_present": sum(
            1 for k in wm if k.endswith("ffn.gate.weight")),  # 43 main + 3 MTP = 46 expected
        "tid2eid_layers": sum(1 for k in wm if k.endswith("ffn.gate.tid2eid")),  # 3 expected (hash bootstrap)
        "schema_ok": ok and len(wm) == 72317,
    }
    return report


def full_run(model_id: str, corpus: Path, output: Path, max_tokens: int, batch: int):
    """Hook the routers and count activations per expert across a code corpus."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True, torch_dtype=torch.bfloat16, device_map="auto")

    counts = defaultdict(int)          # (layer, expert) -> activations
    scores = defaultdict(float)        # (layer, expert) -> summed gate score

    def make_hook(layer_idx):
        def hook(module, args, output):
            # SparseMoeBlock forward returns hidden states; gate logits come from
            # the TopKRouter (noaux_tc). Capture router weights: for each token,
            # active experts are argmax-k of gate scores. We approximate via the
            # module's router: grab gate.weight @ input if accessible, else fall
            # back to the routing result output's second element (indices).
            try:
                routed_in, routed_out = module.router(hidden_states=None), None
                # Robust approach: hook DeepseekV4TopKRouter.forward instead.
            except Exception:
                pass
        return hook

    # NOTE: transformers exposes routers as `model.layers[i].mlp.router`.
    # Prefer hooking `DeepseekV4TopKRouter.forward` (returns topk indices + weights).
    hooks = []
    for i in range(43):
        router = getattr(model.model.layers[i], "mlp", None)
        if router is None:
            router = getattr(model.model.layers[i], "ffn", None)
        if router is None or not hasattr(router, "router"):
            continue
        r = router.router

        def hook(module, args, kwargs, out, layer_idx=i, counts=counts, scores=scores):
            # out: (topk_idx [B,S,k], topk_weights [B,S,k]) or similar; adapt to impl.
            idx, w = out[0], out[1]
            for b in range(idx.shape[0]):
                for s in range(idx.shape[1]):
                    for k in range(idx.shape[2]):
                        e = int(idx[b, s, k].item())
                        counts[(layer_idx, e)] += 1
                        scores[(layer_idx, e)] += float(w[b, s, k].item())
        hooks.append(r.register_forward_hook(hook, with_kwargs=True))

    # tokenize corpus in batches
    texts = [json.loads(l)["code"] for l in open(corpus) if l.strip()] \
        if corpus.suffix == ".jsonl" else [p.read_text() for p in corpus.rglob("*.py")]
    n = 0
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        enc = tok(chunk, return_tensors="pt", padding=True, truncation=True,
                  max_length=max_tokens).to(model.device)
        with torch.no_grad():
            model(**enc)
        n += len(chunk)
        print(f"processed {n}/{len(texts)}", file=sys.stderr)

    for h in hooks:
        h.remove()

    rows = []
    for (l, e), c in sorted(counts.items()):
        rows.append({"layer": l, "expert": e, "activations": c,
                     "mean_gate_score": scores[(l, e)] / max(c, 1)})
    total = sum(r["activations"] for r in rows)
    for r in rows:
        r["share"] = r["activations"] / max(total, 1)
    rows.sort(key=lambda r: r["activations"])
    cold = [r for r in rows[: int(0.3 * len(rows))]]
    out = {
        "model": model_id,
        "corpus": str(corpus),
        "tokens_processed": n,
        "total_activations": total,
        "coldest_30pct": cold,
        "per_expert": rows,
        "prune_candidate_tensors": [
            f"layers.{r['layer']}.ffn.experts.{r['expert']}.w1.weight"
            f",layers.{r['layer']}.ffn.experts.{r['expert']}.w2.weight"
            f",layers.{r['layer']}.ffn.experts.{r['expert']}.w3.weight"
            for r in cold],
    }
    json.dump(out, open(output, "w"), indent=2)
    print(f"census written to {output}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--index", default="/home/idor/oe-local/2026-08-04/ds_v4_index.json")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash-0731")
    ap.add_argument("--corpus", type=Path)
    ap.add_argument("--output", type=Path, default=Path("census_results.json"))
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--batch", type=int, default=4)
    args = ap.parse_args()

    if args.dry_run:
        print(json.dumps(dry_run(args.index), indent=2))
        return
    if args.corpus is None:
        ap.error("--corpus required for full run")
    full_run(args.model, args.corpus, args.output, args.max_tokens, args.batch)


if __name__ == "__main__":
    main()
