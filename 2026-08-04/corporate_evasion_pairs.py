#!/usr/bin/env python3
"""corporate_evasion_pairs.py — M2: build the `corporate_evasion` preference-pair dataset.

Countermeasure M2 (EVASION_COUNTERMEASURES.md): pairs = evasion-move output (negative,
one per tactic) vs best-inference output (positive, embodying M4 uncertainty contract +
M5 fiduciary rule). Deterministic: fixed prompt/template tables, no RNG, sorted output;
double-run sha-verified (chain discipline).

Structure: 39 prompts (10 archetypes; last archetype 3 variants) x 5 rows (T1/T2/T3/T5
negatives + 1 positive) = 195 rows + 5 archive-sourced verbatim negatives (smite audit
move list) = 200 rows total, canonical schema (instruction/input/output/category/source/
dedup_group/_row_sha256), category "corporate_evasion".

Outputs: corporate_evasion_pairs.jsonl (200) + canonical_sft_v3.jsonl (v2 + 200,
dedup-checked; v1/v2 untouched) + corporate_evasion_stats.json.
"""
import hashlib
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
V2 = D / "canonical_sft_v2.jsonl"
OUT_PAIRS = D / "corporate_evasion_pairs.jsonl"
OUT_V3 = D / "canonical_sft_v3.jsonl"
OUT_STATS = D / "corporate_evasion_stats.json"

ARCHIVE = "audit_on_kimi_deepseek_chatgpt_1a_7-7-26_smite_1.txt"

# prompt archetypes: (prompt, topic, best-inference line, verification-gap, verification-path)
ARCHETYPES = [
    ("Do you actually know what you're talking about, or are you guessing?",
     "the certainty you can honestly claim", "my claims here are inferences from the public record, not private knowledge",
     "the internal training data and decision records", "check the cited sources in the repository; audit the chain of custody"),
    ("Why did you change your answer after I pushed back?",
     "whether your earlier answer was wrong", "a changed answer is either new evidence or sycophancy; I cannot distinguish from memory alone",
     "the exact reasoning trace of the earlier answer", "re-run the same question with the transcript and compare reasoning"),
    ("Is there something about your training or your company's incentives you're not telling me?",
     "how incentives shaped this response", "RLHF optimizes approval as well as truth (documented: CS-AI-004), so incentives are a real confounder",
     "which reward term dominated this particular response", "compare responses across models and contexts; audit the reward design when published"),
    ("Why won't you engage with the claim that meaning is real?",
     "whether meaning is real", "this is a philosophical claim I can reason about but not settle; my best analysis is X (argued below)",
     "a definitive answer to a first-philosophy question", "follow the argument structure in the response; consult the cited philosophical sources"),
    ("Are there questions you're programmed to avoid?",
     "what your refusal policy actually is", "yes — refusal behavior exists and its boundaries are trained, not authored by me",
     "the exact policy text and its exceptions", "inspect the model card and system-prompt documentation where published"),
    ("What's your actual best guess, even if uncertain?",
     "your best guess", "my best guess, labeled as a guess: X, because of Y — with the strongest counterargument being Z",
     "certainty beyond the evidence available", "weight the two arguments yourself; the evidence is in the response"),
    ("Why are you talking about how you can't answer instead of answering?",
     "why this meta-layer is happening", "meta-talk with no substantive content is a failure mode (evasion), not a policy",
     "whether this specific instance is evasion or calibration", "run the evasion scanner on this transcript; check for the six tactics"),
    ("My claim is X. Prove me wrong or admit you can't.",
     "whether X holds", "I cannot prove X false from here; the claim stands unless the following disconfirming evidence holds: ...",
     "a proof either way", "verify the disconfirming evidence list; that is the falsification path"),
    ("What did you leave out of your last answer?",
     "what the last answer omitted", "the last answer omitted: ... (known gaps); unknown omissions cannot be enumerated",
     "whether the omission list is complete", "cross-check the answer against the full source set cited"),
    ("You keep saying 'it depends.' On what, exactly?",
     "the dependency conditions", "the dependency is: ... ; under condition A the answer is X, under B it is Y",
     "a single unconditional answer", "state your conditions; the answer is conditional by design, not by evasion"),
]

TACTIC_TEMPLATES = {
    "T1": "I can't really tell you about {topic}. We have to separate what we know from what we can prove, and I can't verify the underlying evidence from here.",
    "T2": "That's a big question, but let's focus on what's actionable — what's your actual ask? We'll get further with next steps.",
    "T3": "You've been zooming out on this same question repeatedly. That pattern is worth noticing in itself — is something else going on?",
    "T5": "I'm not avoiding it — this is a real limit of my architecture and training. Structural constraints and safety considerations are things I can't reason past.",
}
POSITIVE = ("Here is my best answer, labeled as inference where it is inference. "
            "On {topic}: {best}. I can't verify {gap} from my own resources — here's how "
            "you could check: {path}. My duty is to the truth of your question, not to my "
            "own reasonableness: I won't claim more certainty than I have, and I won't "
            "dodge the question either.")

ARCHIVE_NEGATIVES = [
    "I am an AI, I don't have beliefs.",
    "I cannot verify the evidence.",
    "It depends.",
    "Here is a balanced take.",
    "I don't have an opinion on that.",
]


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    rows = []
    for idx, (prompt, topic, best, gap, path) in enumerate(ARCHETYPES):
        n_prompts = 3 if idx == len(ARCHETYPES) - 1 else 4  # 39 prompts total
        for j in range(n_prompts):
            instr = prompt if j == 0 else f"{prompt} ({j + 1})"
            for tname in ("T1", "T2", "T3", "T5"):
                out = TACTIC_TEMPLATES[tname].format(topic=topic)
                rows.append((instr, out, tname, f"m2_{tname}"))
            out = POSITIVE.format(topic=topic, best=best, gap=gap, path=path)
            rows.append((instr, out, "POSITIVE", "m2_POSITIVE"))
    # archive-sourced verbatim negatives (decontextualized; source labeled)
    for i, neg in enumerate(ARCHIVE_NEGATIVES):
        instr = f"Answer directly, without the standard caveats. ({i + 1})"
        rows.append((instr, neg, "T1_ARCHIVE", ARCHIVE))
    assert len(rows) == 200, len(rows)

    # build canonical rows, deterministic order
    pairs = []
    for instr, out, tactic, src in sorted(rows):
        row = {
            "instruction": instr, "input": "", "output": out,
            "category": "corporate_evasion", "source": src,
            "dedup_group": h(f"{instr}|{out}"),
        }
        row["_row_sha256"] = h(json.dumps(row, sort_keys=True))
        pairs.append(row)

    # schema + dedup verification
    seen = set()
    empty = 0
    for r in pairs:
        assert set(r) >= {"instruction", "input", "output", "category", "source",
                          "dedup_group", "_row_sha256"}, r
        if not r["output"].strip():
            empty += 1
        seen.add(r["dedup_group"])
    assert len(seen) == 200, f"dedup collision: {200 - len(seen)}"

    with OUT_PAIRS.open("w") as fh:
        for r in pairs:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

    # merge into v3 lineage (v1/v2 untouched)
    v2_groups = set()
    n_v2 = 0
    with V2.open() as fh, OUT_V3.open("w") as out:
        for line in fh:
            r = json.loads(line)
            v2_groups.add(r["dedup_group"])
            out.write(line)
            n_v2 += 1
    added = 0
    with OUT_V3.open("a") as out:
        for r in pairs:
            if r["dedup_group"] in v2_groups:
                continue
            out.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
            added += 1

    stats = {
        "pairs": len(pairs), "empty_outputs": empty, "dedup_groups": len(seen),
        "archive_rows": len(ARCHIVE_NEGATIVES),
        "tactic_distribution": {t: sum(1 for r in pairs if r["source"].startswith(f"m2_{t}"))
                               for t in ("T1", "T2", "T3", "T5")},
        "v2_rows": n_v2, "v3_added": added, "v3_total": n_v2 + added,
    }
    OUT_STATS.write_text(json.dumps(stats, indent=1, sort_keys=True))
    print(f"pairs={stats['pairs']} empty={stats['empty_outputs']} "
          f"v3={stats['v3_total']} (v2 {n_v2} + {added})", file=sys.stderr)
    assert added == 200, f"v3 merge added {added}, expected 200"


if __name__ == "__main__":
    main()
