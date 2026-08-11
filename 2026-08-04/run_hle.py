#!/usr/bin/env python3
"""run_hle.py — HLE harness runner (spec §2/§5). Decode + score + registry append.

Modes:
  score-only   python3 run_hle.py score hle_run_<model>_<sha>.json
               (re-score an existing run file — usable NOW, no hardware)
  decode       python3 run_hle.py decode --model <id> --server <url> [--effort think|max]
               (hardware-gated: talks to a vLLM/runner OpenAI-compatible endpoint)

Run file schema (hle_run_<model>_<sha>_<date>.json):
  {model, model_sha, date, effort, config, items: [{id, options, answer_index, predicted,
   tokens}]}  — answer_index only in dev; scoring requires the local key file.

Registry append: benchmarks/MODEL_PERFORMANCE_REGISTRY.md row derived from the run file
(never hand-entered).
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEV = HERE / "hle_items_dev.jsonl"
REGISTRY = Path("/home/idor/oe-local/benchmarks/MODEL_PERFORMANCE_REGISTRY.md")


def load_items(path=DEV):
    return [json.loads(l) for l in open(path)]


def score_run(run_path):
    run = json.load(open(run_path))
    items = {it["id"]: it for it in load_items()}
    n = correct = 0
    per_domain = {}
    tok_total = 0
    for res in run["items"]:
        it = items.get(res["id"])
        if it is None:
            continue
        n += 1
        tok_total += res.get("tokens", 0)
        hit = res.get("predicted") == it["answer_index"]
        correct += hit
        d = it.get("domain", "?")
        per_domain.setdefault(d, [0, 0])
        per_domain[d][0] += hit
        per_domain[d][1] += 1
    acc = correct / max(n, 1)
    print(f"model {run['model']} ({run.get('effort', '?')}): {correct}/{n} = {acc:.4f} "
          f"| tokens/query {tok_total / max(n, 1):.0f}")
    for d, (c, t) in sorted(per_domain.items()):
        print(f"  {d}: {c}/{t} = {c / max(t, 1):.3f}")
    return {"n": n, "correct": correct, "accuracy": acc, "tokens": tok_total}


def append_registry(run_path, score):
    run = json.load(open(run_path))
    row = (f"| {run['model']} | {run.get('model_sha', '?')[:8]} | {run['date']} | "
           f"{run.get('effort', '?')} | {score['accuracy']:.4f} | {score['tokens'] // max(score['n'], 1)} | "
           f"{run.get('config', '')} |")
    with open(REGISTRY, "a") as fh:
        fh.write(row + "\n")
    print(f"registry row appended: {REGISTRY}")


def decode(model_id, server, effort, max_tokens=4096):
    items = load_items()
    out_items = []
    url = f"{server.rstrip('/')}/v1/completions"
    for it in items:
        prompt = (f"{it['question']}\n\nOptions:\n" +
                  "\n".join(f"{chr(65 + i)}. {o}" for i, o in enumerate(it["options"])) +
                  "\n\nAnswer with the single letter of the correct option.")
        payload = {
            "model": model_id,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0,
            "extra_body": {"reasoning_effort": effort} if effort else {},
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=600) as resp:
            data = json.loads(resp.read())
        text = data["choices"][0]["text"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        letters = [ch for ch in text if ch.isalpha()]
        predicted = ord(letters[0].upper()) - 65 if letters else None
        out_items.append({"id": it["id"], "predicted": predicted, "tokens": tokens,
                          "elapsed_s": round(time.time() - t0, 1)})
    run = {
        "model": model_id, "model_sha": "?", "date": datetime.now(timezone.utc).isoformat(),
        "effort": effort or "greedy", "config": f"server={server}",
        "items": out_items,
    }
    path = HERE / f"hle_run_{model_id.replace('/', '_')}_{run['date'][:10]}.json"
    path.write_text(json.dumps(run, indent=1))
    print(f"run written: {path}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "score"
    if mode == "score":
        if len(sys.argv) < 3:
            print("usage: run_hle.py score <run.json>")
            sys.exit(1)
        s = score_run(sys.argv[2])
        append_registry(sys.argv[2], s)
    elif mode == "decode":
        args = dict(zip(sys.argv[2::2], sys.argv[3::2]))
        decode(args.get("--model"), args.get("--server"), args.get("--effort"))
    else:
        print(f"unknown mode: {mode}")
