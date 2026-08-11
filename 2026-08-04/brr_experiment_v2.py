#!/usr/bin/env python3
"""
BRR v2 — Bounded Recursive Refinement, priming A/B (2026-08-04)

v1 finding: small models sat at 20/100 for all rounds — format compliance
is the binding constraint; recursion budget spent on compliance noise.

v2 tests F15 (Priming Gain): does a format exemplar in the system prompt
(primed) beat no exemplar (blank) on quality-per-token and depth-to-quality?

Arms: PRIMED=1 (exemplar provided) vs PRIMED=0 (blank). Same verifier,
same task, same budgets. Saves to brr_results_v2.json.
"""
import json
import re
import sys
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELS = {
    "qwen2.5-1.5b":   "Qwen/Qwen2.5-1.5B",
    "tinyllama-1.1b": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
}
MAX_DEPTH = 4
MAX_NEW_TOKENS = 400
SEEDS = 3
OUT = "brr_results_v2.json"

EXEMPLAR = (
    "FORMULA: $$V_{tot} = \\sum_{i=1}^{N} \\tau_i \\cdot v_i \\; - \\; \\kappa \\cdot H(S)$$\n"
    "VAR: tau_i = A-Life-style tick rate of recursion branch i, proportional to relevance\n"
    "VAR: v_i = expected value of one tick of branch i\n"
    "VAR: kappa = consolidation loss coefficient of state compression\n"
    "VAR: H(S) = Shannon entropy of the compressed recursion state S\n"
    "DOMAINS: game AI (A-Life), information theory, entropy\n"
)

SYSTEM_BASE = (
    "You are a research mathematician inventing a NEW custom formula that improves "
    "BOUNDED RECURSIVENESS: how much recursive reasoning value an agent extracts per "
    "unit of consumed budget (context tokens, compute, time). Synthesize from multiple "
    "domains: mathematics, video-game AI (S.T.A.L.K.E.R. Call of Pripyat's A-Life "
    "simulation budgeting), biology, physics, information theory, compilers, control "
    "theory. Be concrete, measurable, and original."
)

SYSTEM_PRIMED = (
    SYSTEM_BASE +
    "\n\nFormat exemplar (copy the FORMAT only, NOT the content):\n" + EXEMPLAR
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

KNOWN_FUNCS = {"sin", "cos", "tan", "exp", "log", "ln", "sqrt", "max", "min", "sum", "prod",
               "abs", "floor", "ceil", "argmin", "argmax", "inf", "lim"}

# --- lenient extraction: find blocks anywhere in the response ---
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

def score_formula(text):
    report = {}
    formula = extract_formula(text)
    vars_ = extract_vars(text)
    domains = re.findall(r"DOMAINS:\s*(.+)", text)
    domain_hits = [d.strip() for d in (domains[0].split(",") if domains else [])
                   if d.strip().lower() in DOMAIN_KEYWORDS]

    report["format_adherence"] = formula is not None and len(vars_) > 0 and len(domain_hits) > 0

    s_parse = 20 if (formula and dollar_balance(formula) and brace_balance(formula)) else (5 if formula else 0)
    report["parseable"] = s_parse

    undefined = []
    s_vars = 0
    s_boundary = 0
    s_novelty = 0
    idents = set()
    if formula:
        used = used_symbols(formula)
        defined = set(vars_.keys()) | KNOWN_FUNCS | {"i", "e", "pi"}
        undefined = sorted(used - defined)
        s_vars = max(0, 20 - 4 * len(undefined))
        issues = boundary_issues(formula)
        s_boundary = max(0, 20 - 10 * len(issues))
        idents = used_symbols(formula)
        s_novelty = min(20, 4 * len(idents - KNOWN_FUNCS))
    report["undefined_symbols"] = undefined
    report["n_vars"] = len(vars_)

    s_domain = min(20, 10 * len(domain_hits))
    report["domains"] = domain_hits

    report["boundary_issues"] = [] if not formula else boundary_issues(formula)

    report["n_identifiers"] = len(idents)

    score = s_parse + s_vars + s_domain + s_boundary + s_novelty
    report["score"] = score
    return score, report

def critique(report):
    lines = []
    if report["parseable"] < 20:
        lines.append("Formula block missing/malformed: exactly one FORMULA: $$...$$ pair with balanced braces.")
    if report["undefined_symbols"]:
        lines.append("Undefined symbols: " + ", ".join(report["undefined_symbols"][:8]) + ". Define every symbol in a VAR line.")
    if report["n_vars"] == 0:
        lines.append("No VAR lines. Add at least 2 VAR: <symbol> = <meaning> lines after the formula.")
    if not report["domains"]:
        lines.append("No recognized DOMAINS line. End with DOMAINS: domain1, domain2.")
    if report["boundary_issues"]:
        lines.append("Fix boundary hazards: " + "; ".join(report["boundary_issues"]) + ".")
    if report["n_identifiers"] < 4:
        lines.append("Formula too thin: use at least 4 distinct symbols, make it a multi-term relation.")
    if not lines:
        lines.append("Solid. Strengthen novelty: merge a game-system budgeting idea with a formal quantity.")
    return " ".join(lines)

def load(model_id):
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, dtype=torch.float16, attn_implementation="sdpa", low_cpu_mem_usage=True)
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
    return tok.decode(gen, skip_special_tokens=True).strip(), len(gen.tolist())

def run_arm(model_name, model_id, primed, results):
    model, tok = load(model_id)
    system = SYSTEM_PRIMED if primed else SYSTEM_BASE
    t0 = time.time()
    for seed in range(SEEDS):
        history = [{"role": "system", "content": system},
                   {"role": "user", "content": TASK}]
        scores, toks, cum, qpts, rounds = [], [], 0, [], []
        best, plateau, degraded = 0.0, None, False
        for d in range(MAX_DEPTH + 1):
            text, ntok = generate(model, tok, history, seed)
            toks.append(ntok); cum += ntok
            score, rep = score_formula(text)
            scores.append(score)
            best = max(best, score)
            qpts.append(score / cum if cum else 0.0)
            rounds.append({"depth": d, "tokens": ntok, "cumulative_tokens": cum,
                           "score": score, "qpt": round(qpts[-1], 6), "report": rep,
                           "output": text[:500]})
            if d >= 2 and plateau is None and abs(scores[-1]-scores[-2]) < 3 and abs(scores[-2]-scores[-3]) < 3:
                plateau = d
            if score < best - 5 and d > 0:
                degraded = True
            history.append({"role": "assistant", "content": text})
            history.append({"role": "user",
                            "content": f"Verifier: score {score}/100. Critique: {critique(rep)} Revise and output the same format."})
        depth_to_40 = next((d for d, s in enumerate(scores) if s >= 40), None)
        results["runs"].append({
            "model": model_name, "primed": primed, "seed": seed,
            "scores": scores, "tokens": toks, "qpts": qpts,
            "best_score": best, "best_depth": scores.index(best),
            "depth_to_40": depth_to_40,
            "final_qpt": round(qpts[-1], 6), "peak_qpt": round(max(qpts), 6),
            "plateau_depth": plateau, "degraded": degraded,
            "total_tokens": cum, "rounds": rounds,
        })
        print(f"[{model_name}] primed={primed} seed={seed}: scores={scores} "
              f"d40={depth_to_40} qpt_final={qpts[-1]:.6f} peak={max(qpts):.6f} "
              f"plateau@{plateau} degraded={degraded}", flush=True)
    torch.cuda.empty_cache()
    del model, tok
    results["models"][f"{model_name}_p{int(primed)}"] = {"wall_sec": round(time.time() - t0, 1)}

def main():
    which = sys.argv[1:] or list(MODELS.keys())
    results = {"models": {}, "runs": [], "meta": {
        "max_depth": MAX_DEPTH, "max_new_tokens": MAX_NEW_TOKENS, "seeds": SEEDS,
        "gpu": torch.cuda.get_device_name(0),
        "vram_mib": torch.cuda.get_device_properties(0).total_memory // 1048576}}
    for name in which:
        for primed in (False, True):
            run_arm(name, MODELS[name], primed, results)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"saved -> {OUT}")

if __name__ == "__main__":
    main()
