#!/usr/bin/env python3
"""
BRR — Bounded Recursive Refinement experiment (2026-08-04)

Mirror of the Codewhale agent's recursive loop, scaled to a 6 GB GPU:
  generate -> deterministic verifier -> critique -> refine -> repeat (depth-bounded)

Measures the Compression-Intelligence Inversion claim locally:
  quality-per-token (I_eff proxy) as a function of recursion depth D,
  for two differently-sized small models.

Metrics per round: score (0-100), tokens consumed, cumulative tokens,
quality-per-token, plateau detection, degradation detection.
"""
import json
import re
import sys
import time
import math
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
MODELS = {
    "qwen2.5-1.5b":   "Qwen/Qwen2.5-1.5B",
    "tinyllama-1.1b": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
}
MAX_DEPTH = 4            # recursion budget (mirrors sub-agent max_depth)
MAX_NEW_TOKENS = 400     # per-generation budget
SEEDS = 3
OUT = "brr_results.json"

SYSTEM = (
    "You are a research mathematician inventing a NEW custom formula that improves "
    "BOUNDED RECURSIVENESS: how much recursive reasoning value an agent extracts per "
    "unit of consumed budget (context tokens, compute, time). You synthesize from "
    "multiple domains: mathematics, video-game AI (e.g. S.T.A.L.K.E.R. Call of Pripyat's "
    "A-Life simulation budgeting), biology, physics, information theory, compilers, "
    "control theory. Be concrete, measurable, and original."
)

TASK = (
    "Invent ONE new formula that improves bounded recursiveness. Output exactly this format, nothing else:\n"
    "FORMULA: $$<latex>$$\n"
    "VAR: <symbol> = <one-line meaning>\n"
    "VAR: <symbol> = <one-line meaning>\n"
    "DOMAINS: <comma-separated list of source domains>\n"
    "All symbols used in the formula must be defined in VAR lines. The formula must be "
    "dimensionally plausible and must not divide by zero or take log of zero in its domain."
)

DOMAIN_KEYWORDS = [
    "math", "game", "a-life", "stalker", "biology", "physics", "information", "compiler",
    "control", "agent", "recursion", "context", "cache", "entropy", "energy", "budget",
    "pruning", "simulation", "game theory", "thermo", "evolution", "economics", "network",
]

# ----------------------------------------------------------------------------
# Deterministic verifier (no LLM in the loop)
# ----------------------------------------------------------------------------
KNOWN_FUNCS = {"sin", "cos", "tan", "exp", "log", "ln", "sqrt", "max", "min", "sum", "prod",
               "abs", "floor", "ceil", "argmin", "argmax", "inf", "lim"}

def extract_formula(text):
    m = re.search(r"\$\$(.+?)\$\$", text, re.DOTALL)
    return m.group(1).strip() if m else None

def extract_vars(text):
    return dict(re.findall(r"VAR:\s*(\w+)\s*=\s*(.+)", text))

def brace_balance(s):
    return s.count("{") == s.count("}")

def dollar_balance(s):
    return s.count("$") % 2 == 0

def used_symbols(formula):
    return set(re.findall(r"(?<![A-Za-z])([A-Za-z][A-Za-z0-9_]*)(?![A-Za-z0-9_])", formula))

def boundary_issues(formula):
    issues = []
    low = formula.lower()
    if re.search(r"/\s*0(?!\.[0-9])", formula):
        issues.append("division by literal zero")
    if re.search(r"log\s*\(\s*0", low) or re.search(r"ln\s*\(\s*0", low):
        issues.append("log of zero")
    if re.search(r"sqrt\s*\(\s*-", low):
        issues.append("sqrt of negative literal")
    return issues

def score_formula(text, depth):
    """Return (score 0-100, report dict)."""
    report = {}
    formula = extract_formula(text)
    vars_ = extract_vars(text)
    domains = re.findall(r"DOMAINS:\s*(.+)", text)
    domain_hits = [d.strip() for d in (domains[0].split(",") if domains else [])
                   if d.strip().lower() in DOMAIN_KEYWORDS]

    s_parse = 0
    if formula:
        if dollar_balance(formula) and brace_balance(formula):
            s_parse = 20
        else:
            s_parse = 5
    report["parseable"] = s_parse

    s_vars = 0
    undefined = []
    if formula:
        used = used_symbols(formula)
        defined = set(vars_.keys()) | KNOWN_FUNCS | {"i", "e", "pi"}
        undefined = sorted(used - defined)
        s_vars = 20 - 4 * len(undefined)
        s_vars = max(s_vars, 0)
    report["undefined_symbols"] = undefined
    report["n_vars"] = len(vars_)

    s_domain = min(20, 10 * len(domain_hits))
    report["domains"] = domain_hits

    s_boundary = 20
    issues = boundary_issues(formula or "")
    s_boundary -= 10 * len(issues)
    report["boundary_issues"] = issues

    s_novelty = 0
    if formula:
        idents = used_symbols(formula)
        s_novelty = min(20, 4 * len(idents - KNOWN_FUNCS))
    report["n_identifiers"] = len(used_symbols(formula or ""))

    score = s_parse + s_vars + s_domain + s_boundary + s_novelty
    report["score"] = score
    return score, report

def critique(report):
    lines = []
    if report["parseable"] < 20:
        lines.append("Formula block is missing or malformed: emit exactly FORMULA: $$...$$ with balanced braces and one $$...$$ pair.")
    if report["undefined_symbols"]:
        lines.append("Undefined symbols used: " + ", ".join(report["undefined_symbols"][:8]) + ". Define every symbol in a VAR line.")
    if report["n_vars"] == 0:
        lines.append("No VAR lines found. Add at least 2 VAR: <symbol> = <meaning> lines.")
    if not report["domains"]:
        lines.append("No recognized DOMAINS listed. Cite at least two source domains (math, games, biology, physics, information theory, control, ...).")
    if report["boundary_issues"]:
        lines.append("Fix boundary hazards: " + "; ".join(report["boundary_issues"]) + ".")
    if report["n_identifiers"] < 4:
        lines.append("Formula is too thin. Use at least 4 distinct symbols; make it a real multi-term relation, not a definition.")
    if report["score"] >= 60:
        lines.append("Good structure. Improve novelty: combine a game-system budgeting idea (e.g. A-Life tick allocation) with a formal quantity (entropy, energy, tokens, context).")
    if not lines:
        lines.append("Solid. Strengthen by adding a measurable quantity and a boundary-condition note.")
    return " ".join(lines)

# ----------------------------------------------------------------------------
# Inference
# ----------------------------------------------------------------------------
def load(model_id):
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch.float16, attn_implementation="sdpa",
        low_cpu_mem_usage=True)
    model = model.to("cuda").eval()
    return model, tok

def generate(model, tok, messages, seed, max_new=MAX_NEW_TOKENS):
    torch.manual_seed(seed)
    prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=max_new, do_sample=True, temperature=0.7,
            top_p=0.9, pad_token_id=tok.eos_token_id)
    gen = out[0][inputs["input_ids"].shape[1]:]
    text = tok.decode(gen, skip_special_tokens=True).strip()
    return text, len(gen.tolist())

# ----------------------------------------------------------------------------
# Experiment
# ----------------------------------------------------------------------------
def run_model(model_name, model_id, results):
    model, tok = load(model_id)
    t0 = time.time()
    for seed in range(SEEDS):
        history = [{"role": "system", "content": SYSTEM},
                   {"role": "user", "content": TASK}]
        scores, toks, cum, qpts, rounds = [], [], 0, [], []
        best = 0.0
        plateau = None
        degraded = False
        for d in range(MAX_DEPTH + 1):
            text, ntok = generate(model, tok, history, seed)
            toks.append(ntok); cum += ntok
            score, rep = score_formula(text, d)
            scores.append(score)
            best = max(best, score)
            qpts.append(score / cum if cum else 0.0)
            rounds.append({"depth": d, "tokens": ntok, "cumulative_tokens": cum,
                           "score": score, "qpt": round(qpts[-1], 6),
                           "report": rep, "output": text[:600]})
            if d >= 2 and plateau is None and abs(scores[-1] - scores[-2]) < 3 and abs(scores[-2] - scores[-3]) < 3:
                plateau = d
            if score < best - 5 and d > 0:
                degraded = True
            history.append({"role": "assistant", "content": text})
            history.append({"role": "user",
                            "content": f"Verifier report: score {score}/100. Critique: {critique(rep)} "
                                       f"Revise the formula and output the same format."})
        results["runs"].append({
            "model": model_name, "seed": seed,
            "scores": scores, "tokens": toks, "qpts": qpts,
            "best_score": best, "best_depth": scores.index(best),
            "final_qpt": round(qpts[-1], 6), "peak_qpt": round(max(qpts), 6),
            "plateau_depth": plateau, "degraded": degraded,
            "total_tokens": cum, "rounds": rounds,
        })
        print(f"[{model_name}] seed={seed} done: scores={scores} "
              f"qpt_final={qpts[-1]:.6f} peak={max(qpts):.6f} "
              f"plateau@{plateau} degraded={degraded}", flush=True)
    torch.cuda.empty_cache()
    del model, tok
    results["models"][model_name] = {"wall_sec": round(time.time() - t0, 1)}

def main():
    which = sys.argv[1:] or list(MODELS.keys())
    results = {"models": {}, "runs": [], "meta": {
        "max_depth": MAX_DEPTH, "max_new_tokens": MAX_NEW_TOKENS,
        "seeds": SEEDS, "gpu": torch.cuda.get_device_name(0),
        "vram_mib": torch.cuda.get_device_properties(0).total_memory // 1048576}}
    for name in which:
        run_model(name, MODELS[name], results)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"saved -> {OUT}")

if __name__ == "__main__":
    main()
