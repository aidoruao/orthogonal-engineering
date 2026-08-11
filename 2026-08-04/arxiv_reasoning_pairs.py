#!/usr/bin/env python3
"""
arxiv_reasoning_pairs.py — deterministic arXiv-abstract → SFT reasoning pairs.

Closes the measured thinnest gap in the post-train data layer (canonical SFT has
4–5 unique mathematics/logic/science pairs) by converting the on-disk arxiv_vendor
metadata (1,200 papers, 12 categories) into canonical-schema reasoning pairs.

Deterministic by construction: regex sentence extraction only, no LLM, no randomness.
Re-running produces byte-identical output (verify: run twice, compare sha256).

Output schema (canonical_sft_v1.jsonl compatible):
  instruction, input, output, category, source="arxiv_vendor", dedup_group

Templates:
  A (all papers)      — 4-part verbatim claim decomposition (problem/method/result/limit)
  B (math+logic only) — falsification-condition extraction, only when the abstract states
                        a real limitation (marker-only rows collapse under the canonical
                        sha256(instruction|output) dedup key — constant in, constant out)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

META_DIR = Path(__file__).resolve().parent.parent / "arxiv_vendor" / "metadata"
OUT_PATH = Path(__file__).resolve().parent / "arxiv_reasoning_pairs.jsonl"

CATEGORY_MAP = {
    "math.CT": "mathematics",
    "math.LO": "mathematics",
    "cs.LO": "logic",
    "cs.FL": "logic",
    "stat.ML": "science",
    "cs.AI": "science",
    # everything else → domain_knowledge (default)
}

PROBLEM_RE = re.compile(
    r"\b(problem|challenge|open question|limitation|existing|prior work|current|however|but|gap)\b",
    re.IGNORECASE,
)
METHOD_RE = re.compile(
    r"\bwe (propose|introduce|present|develop|design|use|extend|apply|employ|adopt|construct|build)\b"
    r"|\b(this paper|this work|our approach|our method|the proposed|the presented)\b",
    re.IGNORECASE,
)
RESULT_RE = re.compile(
    r"\bwe (show|prove|demonstrate|establish|find|achieve|report|obtain|derive|validate|outperform|improve)\b",
    re.IGNORECASE,
)
LIMIT_RE = re.compile(
    r"\b(limitation|fails?|break|only when|only if|requires?|requiring|assum(e|ption|ing)|"
    r"restrict(ed|ion|ing)?|counterexample|negative result|future work|cannot|unable|may not|"
    r"does not hold|subject to)\b",
    re.IGNORECASE,
)
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z"\'(\[\$])')


def split_sentences(text: str):
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]


def extract(text: str):
    """Deterministic 4-part verbatim extraction: (problem, method, result, limit)."""
    sents = split_sentences(text)
    if not sents:
        return "(no sentences)", "(not stated in abstract)", "(not stated in abstract)", "(not stated in abstract)"
    problem = next((s for s in sents if PROBLEM_RE.search(s)), sents[0])
    method = [s for s in sents if METHOD_RE.search(s)] or [
        s for s in sents if re.search(r"\b(propose|introduce|present|develop|design)\b", s, re.IGNORECASE)
    ]
    result = [s for s in sents if RESULT_RE.search(s)]
    if not result:
        # fall back to the sentence containing "result" or the final sentence
        result = [s for s in sents if re.search(r"\b(resul|outperform|accuracy|improve|gain)\b", s, re.IGNORECASE)] or sents[-1:]
    limit = [s for s in sents if LIMIT_RE.search(s)]
    return (
        problem,
        " ".join(method) if method else "(not stated in abstract)",
        " ".join(result),
        " ".join(limit) if limit else "(not stated in abstract)",
    )


INSTR_A = (
    "Extract from this research abstract, verbatim: (1) the problem addressed, "
    "(2) the proposed method, (3) the main claimed result, (4) one limitation or "
    "condition under which the claim could fail. Answer exactly as: "
    "PROBLEM: ... METHOD: ... RESULT: ... LIMIT: ... using verbatim sentences from "
    "the abstract, or '(not stated in abstract)' when absent."
)
INSTR_B = (
    "Given the paper's main claim, state one stated condition, assumption, or "
    "limitation under which the result would fail or not hold. Answer with verbatim "
    "sentences from the abstract, or '(not stated in abstract)'."
)


def row(instruction, input_text, output, category, paper_id, template):
    body = json.dumps(
        {"instruction": instruction, "input": input_text, "output": output, "category": category},
        sort_keys=True,
    ).encode()
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
        "category": category,
        "source": "arxiv_vendor",
        "dedup_group": hashlib.sha1(f"{paper_id}|{template}".encode()).hexdigest()[:12],
        "_row_sha256": hashlib.sha256(body).hexdigest(),
    }


def main():
    papers = []  # (arxiv_id, primary_category, title, abstract)
    for f in sorted(META_DIR.glob("*.jsonl")):
        if f.name.endswith("_hashes.jsonl"):
            continue
        for line in f.open():
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            papers.append(
                (e["arxiv_id"], e.get("primary_category", ""), e.get("title", ""), e.get("abstract", ""))
            )

    # dedup by arxiv_id (cross-category files overlap); keep first occurrence
    # (deterministic: files processed in sorted order)
    seen = {}
    for p in papers:
        pid, prim, *_ = p
        if pid not in seen:
            seen[pid] = p
    uniq = list(seen.values())
    print(f"loaded {len(papers)} rows, {len(uniq)} unique papers", file=sys.stderr)

    out = []
    counts = {}
    for pid, prim, title, abstract in sorted(uniq, key=lambda x: x[0]):
        category = CATEGORY_MAP.get(prim, "domain_knowledge")
        problem, method, result, limit = extract(abstract)
        input_text = f"{title}\n\nABSTRACT: {abstract}"
        out.append(row(INSTR_A, input_text,
                       f"PROBLEM: {problem}\nMETHOD: {method}\nRESULT: {result}\nLIMIT: {limit}",
                       category, pid, "A"))
        counts[category] = counts.get(category, 0) + 1
        if category in ("mathematics", "logic") and limit != "(not stated in abstract)":
            out.append(row(INSTR_B, input_text, limit, category, pid, "B"))
            counts[category] = counts.get(category, 0) + 1

    with OUT_PATH.open("w") as f:
        for r in out:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    print(f"wrote {len(out)} pairs -> {OUT_PATH}", file=sys.stderr)
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}", file=sys.stderr)


if __name__ == "__main__":
    main()
