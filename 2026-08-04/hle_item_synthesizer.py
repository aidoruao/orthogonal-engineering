#!/usr/bin/env python3
"""hle_item_synthesizer.py — materialize the HLE harness dev set (spec-compatible items).

HLE_HARNESS_SPEC.md §1/§6: dev 50 / test 250 items, 10 options, single correct index,
answer keys verifier-constructed (no LLM self-grading). This synthesizer builds the dev
set deterministically from the on-disk arxiv corpus:

  Template (falsification reasoning): given a paper's main claim, identify the condition
  under which it would fail. Correct option = the paper's own stated limitation (verbatim,
  from the same deterministic extraction as arxiv_reasoning_pairs.py). Distractors = other
  papers' limitations (deterministic selection). Answer key is correct by construction and
  re-verified on output.

  Items: math+logic papers (math.CT, math.LO, cs.LO, cs.FL) whose abstract states a real
  limitation — 56 papers measured. Each item: {id, domain, question, options[10],
  answer_index} — the HLE harness format.

Deterministic: sorted iteration, seeded-free hash placement of the correct option.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arxiv_reasoning_pairs import extract  # noqa: E402  (same deterministic pipeline)

META = Path("/home/idor/oe-local/arxiv_vendor/metadata")
MATH_LOGIC = {"math.CT", "math.LO", "cs.LO", "cs.FL"}
OUT = Path(__file__).resolve().parent / "hle_items_dev.jsonl"

QUESTION = (
    "A research paper makes the following claim: \"{result}\" "
    "(paper: {title}). Which ONE of the following conditions, stated in the paper's own "
    "abstract, would make the claim fail or not hold?"
)


def load_papers():
    papers = {}
    for f in sorted(META.glob("*.jsonl")):
        if f.name.endswith("_hashes.jsonl"):
            continue
        for line in f.open():
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            pid = e["arxiv_id"]
            if pid not in papers and e.get("primary_category", "") in MATH_LOGIC:
                papers[pid] = (e["title"], e.get("abstract", ""))
    return papers


def main():
    papers = load_papers()
    print(f"math+logic papers: {len(papers)}", file=sys.stderr)
    # (paper_id, title, result, limit) for papers with a real stated limitation
    with_limit = []
    for pid, (title, abstract) in sorted(papers.items()):
        _, _, result, limit = extract(abstract)
        if limit != "(not stated in abstract)":
            with_limit.append((pid, title, result, limit))
    print(f"with real stated limitation: {len(with_limit)}", file=sys.stderr)

    all_limits = [lim for _, _, _, lim in with_limit]
    items = []
    for i, (pid, title, result, limit) in enumerate(with_limit):
        # distractors: other papers' limitations, distinct, deterministic order
        distractors = [l for l in all_limits if l != limit]
        distractors = sorted(set(distractors))[:9]
        while len(distractors) < 9:  # pad deterministically if too few unique
            distractors.append(f"(not stated in abstract) variant {len(distractors)}")
        options = distractors + [limit]
        # deterministic placement of the correct option
        slot = int(hashlib.sha256(pid.encode()).hexdigest(), 16) % 10
        options[slot], options[-1] = options[-1], options[slot]
        items.append({
            "id": f"hle-dev-{i:03d}",
            "domain": "logic",
            "question": QUESTION.format(result=result, title=title),
            "options": options,
            "answer_index": slot,
        })

    with OUT.open("w") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")

    # verification pass: key correct by construction + option count + slot validity
    bad = 0
    for it, (_, _, _, limit) in zip(items, with_limit):
        if len(it["options"]) != 10 or not (0 <= it["answer_index"] <= 9):
            bad += 1
            continue
        if it["options"][it["answer_index"]] != limit:
            bad += 1
            continue
        if len(set(it["options"])) < 9:  # at least 9 distinct options
            bad += 1
    print(f"wrote {len(items)} items -> {OUT} (verification failures: {bad})", file=sys.stderr)
    print(f"answer-index distribution: "
          f"{ {k: sum(1 for it in items if it['answer_index'] == k) for k in range(10)} }", file=sys.stderr)


if __name__ == "__main__":
    main()
