---
tags: [evidence, deepseek-analysis, falsification-results]
register: audit
---

# FALSIFICATION RESULTS - DEEPSEEK 45.30% CLAIM

**Date:** 2026-01-20  
**Status:** ❌ CLAIM REJECTED  
**Method:** Three independent falsification tests

---

## ORIGINAL CLAIM

> "DeepSeek shows 45.30% verified invariant density (vs 7.57% baseline)"

**This claim is FALSE.**

---

## FALSIFICATION TESTS

### TEST 1: DETECTOR PRECISION

**Question:** Does "verified_invariant=True" actually mean constraint language exists?

**Method:** Sample 100 "verified" turns, manually check for constraint patterns

**Results:**
- True positives: 30 (30.0%)
- False positives: 70 (70.0%)
- **Detector precision: 30.00%**

**Threshold:** ≥80% required
**Verdict:** ❌ FAIL - **70% false positive rate is unacceptable**

---

### TEST 2: DENSITY VARIANCE

**Question:** Is density consistent across sessions or chaotic?

**Method:** Calculate density per session, check variance

**Results:**
- Average density: 36.96%
- Median density: 35.71%
- Min: 0.00%
- Max: 100.00%
- **Range: 100.00%**

**Threshold:** <60% variance required
**Verdict:** ❌ FAIL - **Completely chaotic distribution**

---

### TEST 3: MIMICRY DETECTION

**Question:** Are constraint phrases contextually adapted or repetitive?

**Method:** Extract constraint phrases, check repetition rate

**Results:**
- Total phrases found: 446
- Unique phrases: 18
- **Repetition rate: 95.96%**

**Top repeated words:**
1. "exactly" (89x)
2. "must" (72x)
3. "critical" (68x)
4. "cannot" (50x)
5. "specifically" (34x)

**Threshold:** <50% repetition required
**Verdict:** ❌ FAIL - **96% repetition = pure mimicry**

---

## CORRECTED CLAIM

**True invariant density (precision-adjusted):**

```
Claimed: 45.30%
Actual precision: 30%
Adjusted: 45.30% × 0.30 = 13.59%
```

**Even this is generous** given:
- Chaotic variance (100% range)
- Extreme mimicry (96% repetition)

**Conservative estimate: 5-10% genuine invariant density**

---

## WHAT WENT WRONG

### The Detector Over-Flagged

**Mutual agreement detection failed because:**
1. Window size too large (5 turns)
2. Pattern matching too loose
3. No context verification
4. No phrase uniqueness check

**Example false positive:**
```
User: "This is critical"
[4 turns of unrelated chat]
Assistant: "The solution must work"
→ Detector flags as "mutual agreement"
→ WRONG: No actual agreement occurred
```

### The Mimicry Pattern

**DeepSeek learned to say constraint words without grounding:**
- Says "must" 72 times
- Says "exactly" 89 times
- Says "critical" 68 times
- **But doesn't actually enforce constraints**

This is **textbook mimicry** as defined in narrative-leak-001.

---

## CORRESPONDENCE CHECK (Still Required)

Even with adjusted density, must verify:
1. Did "verified" claims lead to working code?
2. Did "must/shall" language produce actual constraints?
3. Can we find examples where constraint language = constraint reality?

**Until correspondence validated: All density claims are suspect**

---

## IMPLICATIONS FOR REPO

### What Must Change:

1. ❌ **Remove "45.30% density" claim** from all files
2. ✅ **Add "Falsification revealed 70% false positive rate"**
3. ✅ **Document detector failure mode**
4. ✅ **Revise to conservative 5-10% estimate**
5. ✅ **Mark DeepSeek analysis as "METHODOLOGY FAILURE CASE STUDY"**

### What Stays:

1. ✅ The falsification methodology itself (it worked!)
2. ✅ The three tests (precision, variance, repetition)
3. ✅ Evidence that mimicry can be detected
4. ✅ Lesson: High density ≠ genuine constraint

---

## CHATGPT WAS CORRECT

**Quote from ChatGPT's analysis:**

> "The numerical claim is conditional... It becomes invariant only if:
> - The detector is valid
> - The definition of 'verified invariant' is consistent
> - False positives are controlled"

**All three conditions FAILED.**

The 45.30% was **not an invariant** - it was a **detector artifact**.

---

## NEW INVARIANTS (Actually True)

What CAN we claim with confidence:

**Invariant 1:** Mimicry can be detected via repetition analysis
- **Proven:** 96% repetition rate found

**Invariant 2:** Window-based mutual agreement is insufficient
- **Proven:** 70% false positive rate

**Invariant 3:** Correspondence checking is essential
- **Proven:** Linguistic agreement ≠ real constraint

**Invariant 4:** The falsification methodology works
- **Proven:** It correctly identified the false claim

---

## LESSONS FOR METHODOLOGY

### What Works:
- ✅ Falsification tests (precision, variance, repetition)
- ✅ Sampling + manual verification
- ✅ Correspondence as truth anchor

### What Doesn't Work:
- ❌ Window-based mutual agreement (too loose)
- ❌ Keyword frequency alone (mimicry vulnerability)
- ❌ Assuming high density = success

### What's Required:
- Implementation correspondence checks
- Stricter detector (require adjacent turns, not 5-turn window)
- Uniqueness verification (penalize repetition)
- Reality grounding (does "verified" match outcomes?)

---

## STATUS

**45.30% claim:** ❌ FALSIFIED  
**Detector validity:** ❌ 30% precision  
**Methodology integrity:** ✅ Falsification worked  
**Repo correction:** ⏳ IN PROGRESS

---

**The good news:** We caught this BEFORE peer review.  
**The bad news:** Must rebuild with stricter criteria.  
**The lesson:** ChatGPT's skepticism was warranted.

**Falsification complete. Repo reorganization in progress.**
