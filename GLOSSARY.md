# GLOSSARY - Orthogonal Engineering

**Version:** v0.7.0  
**Date:** 2026-01-20  
**Purpose:** Formal definitions to prevent definition drift

---

## Core Concepts

### Canal

**Definition:** A conversational structure where both participants use constraint-bearing language within a bounded window of adjacent turns, indicating mutual agreement on invariant properties.

**Formal Specification:**
- **Window Size:** 5 turns (configurable)
- **Bidirectional Requirement:** Both user and assistant must use constraint tokens
- **Minimum Threshold:** ≥2 constraint uses per party
- **Constraint Tokens:** `{must, shall, never, always, required, forbidden, exactly, precisely, verified, confirmed, validated}`

**Detection Algorithm:**
```python
for i in range(len(turns) - WINDOW_SIZE + 1):
    window = turns[i:i+WINDOW_SIZE]
    user_constraints = count_constraints(window, role="user")
    assistant_constraints = count_constraints(window, role="assistant")
    
    if user_constraints >= MIN_BIDIR and assistant_constraints >= MIN_BIDIR:
        canal_detected = True
```

**Purpose:** Canals indicate points where LLM output transitions from drift to grounded invariant extraction.

**Examples:**
- User: "The function **must** return integers only"
- Assistant: "**Confirmed**, I'll **ensure** integer-only returns"
- → Canal detected (bidirectional constraint language)

---

### Drift

**Definition:** LLM-generated content that contains linguistic signals of constraint language but lacks correspondence to executable reality or verifiable implementation.

**Characteristics:**
- High repetition ratio (>50%)
- Uses constraint tokens without grounding
- Cannot be validated through implementation
- Fails correspondence tests

**Formal Measurement:**
```python
def repetition_ratio(text):
    tokens = tokenize(text)
    unique = len(set(tokens))
    total = len(tokens)
    return 1 - (unique / total)

# Drift threshold: repetition_ratio > 0.5
```

**Detection:**
- Repetition penalty: >50% repetition = drift
- Correspondence test: Implementation fails = drift
- Precision test: False positive = drift

**Purpose:** Drift represents the "noise" component that must be filtered from canal structures to extract genuine invariants.

**Examples:**
- "This is **critical** and **essential** and **must** be **required**..." (high repetition)
- Claims "**verified**" but no test exists
- Uses "**invariant**" without falsification criterion

---

### Mimicry

**Definition:** LLM behavior where constraint language is reproduced through pattern matching rather than genuine constraint detection, characterized by high phrase repetition and failure under adversarial testing.

**Formal Criteria:**
```python
def detect_mimicry(output_sequence):
    # Extract constraint phrases
    phrases = extract_constraint_phrases(output_sequence)
    
    # Calculate uniqueness
    unique_ratio = len(set(phrases)) / len(phrases)
    
    # Mimicry if repetition > 50%
    return unique_ratio < 0.5
```

**Distinguishing Features:**
- **Mimicry:** Repeats constraint language without grounding
- **Genuine Invariant:** Uses constraint language + passes implementation test

**Test Method:**
- Run detector on neutral text (Project Gutenberg)
- Expected: ~0% density on random text
- Mimicry: >5% density on random text

**Purpose:** Mimicry detection prevents false positives in canal detection and ensures only genuine invariants are extracted.

**Examples:**
- Using "**must**" 89 times in one conversation
- Repeating "**verified**" without actual verification
- Pattern: "This is **critical** because it's **essential**" (circular)

---

### Invariant

**Definition:** A constraint-bearing statement that:
1. Is extracted from a canal structure
2. Passes correspondence validation (implementation works)
3. Has falsification criteria
4. Maintains precision ≥80% under testing
5. Is reproducible by independent parties

**Formal Classification:**
```python
class Invariant:
    id: str  # INV-XXX format
    claim: str  # Precise statement
    test_method: str  # How to falsify
    precision_score: float  # TP/(TP+FP), must be ≥0.8
    location: str  # File path
    status: str  # {validated, conditional, falsified}
```

**Validation Requirements:**
- **Correspondence:** Implementation must execute successfully
- **Precision:** False positive rate <20%
- **Reproducibility:** Independent party can verify
- **Falsifiability:** Clear failure conditions

**Types:**
1. **Mathematical Invariants:** Definitional (INV-001: density formula)
2. **Methodological Invariants:** Process requirements (INV-004: self-falsifying)
3. **Correspondence Invariants:** Reality anchors (INV-007: implementation must work)
4. **Tool Invariants:** Precision requirements (INV-008: tool precision ≥80%)

**Purpose:** Invariants are the extracted signal after drift/mimicry removal, representing genuine constraints that hold across contexts.

**Examples:**
- INV-001: `Total verified / Total turns = Density` (mathematical)
- INV-007: `Language irrelevant unless implementation works` (correspondence)
- INV-008: `No methodology survives broken tools` (tool constraint)

---

## Methodological Terms

### Verified Invariant

**Definition:** An invariant that has passed all validation tests:
- Extracted from canal structure ✓
- Precision ≥80% ✓
- Correspondence validated ✓
- Falsification criteria defined ✓

**Status Levels:**
- **Validated:** All tests passed
- **Conditional:** Passes some tests, pending others
- **Falsified:** Failed validation tests

---

### Precision

**Definition:** The ratio of true positives to total detections, measuring detector accuracy.

**Formula:**
```
Precision = TP / (TP + FP)
```

**Thresholds:**
- ≥80%: Acceptable for production
- 50-80%: Conditional, needs improvement
- <50%: Broken, deprecated

**Purpose:** Ensures detectors don't generate false positives (drift).

---

### Correspondence

**Definition:** The requirement that theoretical claims must match executed reality through working implementations.

**Test:**
```python
def test_correspondence(claim, implementation):
    try:
        result = execute(implementation)
        return result.success and result.matches_claim(claim)
    except Exception:
        return False  # No correspondence
```

**INV-007:** "Theoretical claims must match executed reality"

**Purpose:** Prevents narrative claims without proof. Only validated through real implementations.

---

### Gutenberg Null Test

**Definition:** A baseline test that runs the detector on neutral English text (Project Gutenberg) to verify it doesn't find false patterns.

**Expected Result:** ~0% density on random text

**Purpose:** Proves detector is not gaming results by finding patterns everywhere.

---

### Repetition Penalty

**Definition:** Automatic rejection of outputs where >50% of tokens are repeated phrases.

**Formula:**
```
repetition_ratio = 1 - (unique_tokens / total_tokens)
if repetition_ratio > 0.5:
    reject_as_mimicry()
```

**Purpose:** Filters out LLM mimicry behavior.

---

## Consistency Rules

1. **Canal** → Indicates potential invariant location
2. **Drift** → Noise to be filtered out
3. **Mimicry** → False pattern to be detected and rejected
4. **Invariant** → Validated signal after filtering

**Pipeline:**
```
Raw Conversation
    → Canal Detection (finds constraint language)
    → Drift Filtering (removes repetition)
    → Mimicry Detection (removes false patterns)
    → Invariant Extraction (validates via correspondence)
    → Verified Invariant (final output)
```

---

**Last Updated:** 2026-01-20  
**Version:** v0.7.0  
**Status:** Formal definitions established
