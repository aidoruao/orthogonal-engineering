# CORE METHODOLOGY ANALYSIS

## Key Concepts from README
# Orthogonal Engineering
**Methodology for extracting reliable outputs from unreliable AI systems**
[![Status](https://img.shields.io/badge/status-v0.7.0_falsified-orange)](https://github.com/aidoruao/orthogonal-engineering)
- Identifies truly reliable outputs (invariants) amid AI verbosity
- Provides falsifiable statistical validation
- **7.57% verified invariant density** (5,301 invariants found)
### DeepSeek Analysis (Falsified ❌)
- **FALSIFIED: 70% false positive rate, 96% mimicry repetition**
- See: `evidence/deepseek-analysis/FALSIFICATION_RESULTS.md`
- Forensic methodology validated
- Formal invariant registry and verification structure
- Methodology for finding truth in contradictory AI outputs
- See: `methodology/EPISTEMIC_FORENSICS_TOOLS.md`
- `analysis/canal_detector.py` - Find canal patterns
- `analysis/canal_refiner.py` - Mutual agreement detection (⚠️ 30% precision, needs fix)
- `analysis/falsify_density_claim.py` - Three-test falsification framework
**What we said:** DeepSeek shows 45.30% verified invariant density (6x better than baseline)
**Why this matters:** The falsification methodology WORKED. We caught the error before peer review.
## 📖 Core Methodology
### Proven Invariants (ChatGPT-Validated)

## Proven Invariants (from README)
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

## Validation Results
[![Status](https://img.shields.io/badge/status-v0.7.0_falsified-orange)](https://github.com/aidoruao/orthogonal-engineering)
## 📊 Validated Results
### Chat Canon Analysis (Proven ✅)
- **7.57% verified invariant density** (5,301 invariants found)
### DeepSeek Analysis (Falsified ❌)
- **CLAIMED: 45.30% density** 
- **FALSIFIED: 70% false positive rate, 96% mimicry repetition**
### Narrative Leak Case Study (Proven ✅)
- Forensic methodology validated
- `analysis/falsify_density_claim.py` - Three-test falsification framework
**What we said:** DeepSeek shows 45.30% verified invariant density (6x better than baseline)
### Proven Invariants (ChatGPT-Validated)
**Invariant 1:** Invariant density is measurable
- Formula: `verified_invariants / total_turns = density`
├── INVARIANTS.md (proven invariants only)
