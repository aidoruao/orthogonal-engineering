#!/usr/bin/env python3
"""hle_margin_probe.py — effort-router signal study on HLE dev items (catalog #10).

Question: can the free logit-margin stream rank HLE items by difficulty, i.e. which
items would need max-effort escalation? Method: greedy-decode a deterministic sample of
the dev set with qwen-1.5b, collect per-token margins, run the PLL lock sim (pll_jitter_sim)
per item -> per-item locked fraction + unlock rate = the escalation signal.

Items that stay locked (high consensus) -> non-think suffices; items with frequent
unlocks -> escalate (think/max). On V4 the same stream comes from confidence_head.

Deterministic: items 0..7 of hle_items_dev.jsonl; writes /tmp/hle_margin_streams.json
and hle_effort_signals.json. [needs hardware] for the real V4 validation.
"""
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pll_jitter_sim import simulate  # noqa: E402

MODEL = "Qwen/Qwen2.5-1.5B"
N_ITEMS = 3  # bounded: no-KV-cache decode is quadratic in item length
MAX_NEW = 120
STREAMS = "/tmp/hle_margin_streams.json"
OUT = HERE / "hle_effort_signals.json"


def main():
    items = [json.loads(l) for l in open(HERE / "hle_items_dev.jsonl")][:N_ITEMS]
    tok = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL, local_files_only=True, torch_dtype=torch.float16)
    model.eval()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(dev)

    streams = []
    for it in items:
        prompt = (f"{it['question']}\n\nOptions:\n" +
                  "\n".join(f"{chr(65 + i)}. {o}" for i, o in enumerate(it["options"])) +
                  "\n\nAnswer with the single letter of the correct option.")
        enc = tok(prompt, return_tensors="pt").input_ids.to(dev)
        margins = []
        for _ in range(MAX_NEW):
            with torch.no_grad():
                out = model(enc)
            logits = out.logits[0, -1].float()
            top2 = torch.topk(logits, 2)
            margins.append((top2.values[0] - top2.values[1]).item())
            nxt = top2.indices[0].unsqueeze(0).unsqueeze(0)
            enc = torch.cat([enc, nxt], dim=-1)
            if nxt.item() == tok.eos_token_id:
                break
        streams.append({"id": it["id"], "margins": margins})
    json.dump(streams, open(STREAMS, "w"))

    signals = []
    for s in streams:
        states = simulate(s["margins"])
        locked = sum(states) / len(states)
        unlocks = sum(1 for a, b in zip(states, states[1:]) if a and not b)
        signals.append({"id": s["id"], "locked_frac": round(locked, 3),
                        "unlock_events": unlocks, "tokens": len(s["margins"]),
                        "escalate": locked < 0.8})
    OUT.write_text(json.dumps(signals, indent=1))
    for sig in signals:
        print(f"{sig['id']}: locked {sig['locked_frac']:.1%} | unlocks {sig['unlock_events']} "
              f"| {'ESCALATE' if sig['escalate'] else 'non-think'}")
    n_esc = sum(1 for s in signals if s["escalate"])
    print(f"\n{n_esc}/{len(signals)} items would escalate under the <80% lock policy "
          f"-> saved {OUT} (V4 validation: same signal from confidence_head, hardware-gated)")


if __name__ == "__main__":
    main()
