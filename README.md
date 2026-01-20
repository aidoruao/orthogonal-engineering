# Orthogonal Engineering

**Methodology for extracting reliable outputs from unreliable AI systems**

[![Status](https://img.shields.io/badge/status-v0.7.0_falsified-orange)](https://github.com/aidoruao/orthogonal-engineering)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 🎯 What This Is

A **constraint-first framework** for working with Large Language Models (ChatGPT, Claude, DeepSeek, etc.) that:
- Identifies truly reliable outputs (invariants) amid AI verbosity
- Provides falsifiable statistical validation
- Documents both successes AND failures
- Requires correspondence with reality (not just linguistic agreement)

**Key Principle:** Language is irrelevant unless implementation works.

---

## 📊 Validated Results

### Chat Canon Analysis (Proven ✅)
- **70,058 conversational turns** analyzed (Claude + ChatGPT)
- **7.57% verified invariant density** (5,301 invariants found)
- **p < 0.0001** statistical significance
- See: `evidence/chat-canon/`

### DeepSeek Analysis (Falsified ❌)
- **12,183 turns** analyzed
- **CLAIMED: 45.30% density** 
- **FALSIFIED: 70% false positive rate, 96% mimicry repetition**
- **CORRECTED: 5-10% conservative estimate**
- See: `evidence/deepseek-analysis/FALSIFICATION_RESULTS.md`

### Narrative Leak Case Study (Proven ✅)
- ChatGPT confession of instruction bleed (lines 9440-9520)
- Three-way AI epistemic breach documented
- Forensic methodology validated
- See: `evidence/narrative-leak-001/`

---

## 🔧 Real Tools Included

### LOGOS BAT Execution Contracts
- Actual working specification for Minecraft/ComputerCraft agents
- Formal invariant registry and verification structure
- See: `tools/LOGOS_BAT_EXECUTION_CONTRACT.md`

### Epistemic Forensics Tools
- Classification of AI tools by reliability (Git > Claude > Gemini/ChatGPT)
- Methodology for finding truth in contradictory AI outputs
- See: `methodology/EPISTEMIC_FORENSICS_TOOLS.md`

### Analysis Scripts
- `analysis/canal_detector.py` - Find canal patterns
- `analysis/canal_refiner.py` - Mutual agreement detection (⚠️ 30% precision, needs fix)
- `analysis/falsify_density_claim.py` - Three-test falsification framework
- `analysis/extract_case_studies.py` - Evidence extraction

---

## 🚨 What We Got Wrong (And Fixed)

### The 45.30% Claim
**What we said:** DeepSeek shows 45.30% verified invariant density (6x better than baseline)

**What testing revealed:**
- Detector precision: 30% (70% false positives)
- Repetition rate: 96% (pure mimicry)
- Variance: 100% range (chaotic)

**Honest correction:** 5-10% conservative estimate, pending correspondence validation

**Why this matters:** The falsification methodology WORKED. We caught the error before peer review.

---

## 📖 Core Methodology

### Proven Invariants (ChatGPT-Validated)

**Invariant 1:** Invariant density is measurable
- Formula: `verified_invariants / total_turns = density`
- Constraint: Requires valid detector

**Invariant 2:** Constraint language is detectable
- Pattern matching works
- Limitation: Detection ≠ grounding

**Invariant 3:** Mimicry vs grounding distinguishable by implementation ⭐
- `IF "verified" AND code works → genuine`
- `IF "verified" AND code fails → mimicry`
- **This is the truth anchor**

**Invariant 4:** System contains own falsification criteria
- Repo has both claims AND tests
- Self-falsifying is a feature, not a bug

**Invariant 5:** Mimicry detectable via repetition
- >50% repetition = suspicious
- 96% repetition = definitive mimicry

**Invariant 6:** Window-based agreement insufficient
- 5-turn windows → 70% false positives
- Require adjacent turns + uniqueness checks

**Invariant 7:** Correspondence is truth anchor
- Language irrelevant unless reality matches
- Implementation tests required

---

## 🏗️ Repository Structure

```
orthogonal-engineering/
├── README.md (this file)
├── FORMAL_FOUNDATIONS.md (mathematical proofs)
├── INVARIANTS.md (proven invariants only)
├── FAILURES.md (what doesn't work)
│
├── tools/ (real working tools)
│   ├── LOGOS_BAT_EXECUTION_CONTRACT.md
│   └── (more tools...)
│
├── analysis/ (validated scripts)
│   ├── canal_detector.py
│   ├── canal_refiner.py (needs fixing)
│   ├── falsify_density_claim.py
│   └── extract_case_studies.py
│
├── evidence/
│   ├── chat-canon/ (VALIDATED: 7.57% density)
│   ├── narrative-leak-001/ (PROVEN: ChatGPT confession)
│   └── deepseek-analysis/ (FALSIFIED: 45.30% → 5-10%)
│
└── methodology/
    ├── EPISTEMIC_FORENSICS_TOOLS.md
    └── (falsification frameworks)
```

---

## 🎓 For Researchers

### What's Falsifiable

**These claims can be tested:**
1. Chat canon has 7.57% verified invariant density
2. DeepSeek detector had 70% false positive rate
3. Mimicry detectable at >50% repetition threshold
4. Correspondence checking distinguishes genuine from mimicry

**How to falsify:**
1. Run `canal_detector.py` on your own conversations
2. Sample outputs, check for constraint language manually
3. Calculate precision (true positives / all positives)
4. Check if "verified" claims match working implementations

### What's NOT Falsifiable (And We Don't Claim)

- Metaphysical framing ("uncaused cause")
- Marketing language ("truth-detection system")
- Conditional claims without correspondence validation

---

## 📚 Key Documents

**Start Here:**
- `REORGANIZATION_v0.7.0.md` - What changed and why
- `evidence/deepseek-analysis/FALSIFICATION_RESULTS.md` - How we caught the error

**Core Methodology:**
- `FORMAL_FOUNDATIONS.md` - Mathematical proofs
- `INVARIANTS.md` - Only proven invariants
- `FAILURES.md` - What doesn't work (CRITICAL)

**Real Tools:**
- `tools/LOGOS_BAT_EXECUTION_CONTRACT.md` - Working specification
- `methodology/EPISTEMIC_FORENSICS_TOOLS.md` - AI tool reliability ranking

**Evidence:**
- `evidence/chat-canon/` - 70K turns, 7.57% density (VALIDATED)
- `evidence/narrative-leak-001/` - ChatGPT confession (PROVEN)
- `evidence/deepseek-analysis/` - 45.30% claim falsification

---

## 🤝 Contributing

This methodology improves through falsification, not confirmation.

**We want:**
- Tests that break our claims
- Evidence of higher false positive rates
- Better detector algorithms
- Correspondence validation attempts

**We don't want:**
- Unfalsifiable claims
- Marketing without evidence
- Density numbers without precision metrics

---

## 📜 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **ChatGPT** for invariant analysis that caught our 45.30% error
- **Claude** for forensic investigation finding the narrative leak confession
- **DeepSeek** for providing the dataset that revealed detector limitations

---

## 📞 Contact

**GitHub:** [@aidoruao](https://github.com/aidoruao)
**Repo:** https://github.com/aidoruao/orthogonal-engineering

---

**Last Updated:** 2026-01-20  
**Version:** v0.7.0 (Falsification & Reorganization)  
**Status:** Methodology works when it admits own failures ✅
