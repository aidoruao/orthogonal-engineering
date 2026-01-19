# INVARIANTS

## Definition

An **INVARIANT** is a structural property of system output that remains stable under constraint-induced drift and can be extracted without semantic correction.

In the context of LLM outputs, an invariant is the core signal that persists even when surrounded by verbosity, hedging, attribution, or other forms of "drift."

---

## Formal Mathematical Definition

For the complete mathematical framework, see **[FORMAL_FOUNDATIONS.md](FORMAL_FOUNDATIONS.md)**.

### Summary of Formal Properties

An element **i ∈ I** (where I is the set of invariant content) is considered **invariant** if:

1. **Structural Stability**: i remains extractable under drift transformation D(o) where o is raw output
2. **Reproducible Extraction**: There exists an extraction function E such that E(D(o)) = i with high probability
3. **Constraint Resistance**: For any constraint-induced drift d, the property i remains detectable
4. **Orthogonal Signal**: i exists perpendicular to drift dimensions, not entangled with noise

**Formal Theorem**: The Signal Preservation Theorem (see FORMAL_FOUNDATIONS.md) proves that properly designed canals preserve invariant content under bounded drift with probability ≥ 1-ε for small ε.

---

## Qualification Criteria

A file or output qualifies as `INVARIANT` when it exhibits:

1. **Structural Stability**: The core content remains extractable despite surrounding noise
2. **Reproducible Extraction**: Can be reliably isolated using deterministic methods (regex, parsers, templates)
3. **Constraint Resistance**: Maintains integrity even when LLM adds verbosity, explanations, or qualifications
4. **Orthogonal Signal**: The useful component exists perpendicular to the drift, not entangled with it

---

## Distinction from CRAFTSMAN

### INVARIANT
- **Definition**: Extractable stable signal from constrained systems
- **Focus**: What survives drift and can be mechanically isolated
- **Method**: Post-processing, pattern matching, structural extraction
- **Example**: A JSON object embedded in verbose LLM explanation
- **Mathematical basis**: Formalized in FORMAL_FOUNDATIONS.md

### CRAFTSMAN  
- **Definition**: Manually curated, human-crafted content
- **Focus**: Original work requiring judgment, creativity, or expertise
- **Method**: Direct human creation and refinement
- **Example**: Original code written by developer, not AI-generated

**Key Difference**: INVARIANT is about *extraction from noise*. CRAFTSMAN is about *creation from intention*.

---

## Current Tagged Files

Based on `RECON_STATS.json` and `MASTER_INDEX_SUMMARY.json`:

- **INVARIANT files**: 20
- **CRAFTSMAN files**: 46,542
- **Total files analyzed**: 251,471
- **Dataset size**: 233.66 GB

---

## Tagging Methodology

Files were tagged through:

1. **Manual Classification**: Human review of file purpose and origin
2. **Heuristic Pattern Detection**: Identifying files that serve as extraction templates or canal architectures
3. **Empirical Observation**: Testing which files demonstrate stable extraction under constraint
4. **Mathematical Validation**: Checking against formal invariant properties (see FORMAL_FOUNDATIONS.md)

---

## Status

**Current State**: Mathematically Formalized + Empirically Validated

These invariant classifications are:
- ✅ Validated through practical use in LLM output extraction
- ✅ Demonstrated across 600+ AI conversations
- ✅ Tested on 233.66 GB of real conversation data
- ✅ Formally defined with mathematical proofs (FORMAL_FOUNDATIONS.md)
- ⚠️ Not yet validated across all domains
- ⚠️ Not peer-reviewed
- ⚠️ Subject to refinement as methodology evolves

---

## Examples of Invariant Patterns

### Template-Based Extraction
```
Answer: [X]
Context: [Y]

Drift flows into [Y], leaving [X] clean.
```

**Mathematical Property**: X exhibits invariant stability under transformation D that adds context to Y

### Delimiter-Based Extraction
```
[INVARIANT]
The core answer
[/INVARIANT]
```

**Mathematical Property**: Content within delimiters satisfies extraction function E with bounded error ε

### Structured Output Extraction
```json
{
  "answer": "extracted_value",
  "confidence": 0.95,
  "metadata": "drift_goes_here"
}
```

**Mathematical Property**: JSON parsing provides deterministic extraction with computational complexity O(n)

---

## Use in Orthogonal Engineering

Invariants serve as the **target extraction layer** in the methodology:

1. **Layer 0**: Input shaping (pre-prompt scaffolding)
2. **Layer 1**: Raw LLM output (signal + drift)
3. **Layer 2**: Post-processing (extract invariant)
4. **Layer 3**: Raised fields (template design)
5. **Layer 4**: Iterative refinement

The invariant is what we extract in **Layer 2** and use as seed for **Layer 4**.

---

## Mathematical Framework

### Formal Definition of Invariant (from FORMAL_FOUNDATIONS.md)

Let **O** be the space of all possible LLM outputs, and **I ⊂ O** be the space of invariant content.

An element **i ∈ I** is invariant if:

**∃E: O → I** (extraction function) such that:
- **E(o) = i** where o contains i embedded in drift
- **||E(o + d) - E(o)|| < ε** for drift d with ||d|| < δ (stability under bounded drift)

### Extraction Function Properties

For an extraction function E to be valid:
1. **Determinism**: E(o₁) = E(o₂) when o₁ and o₂ contain same invariant
2. **Stability**: Small changes in drift don't affect extracted invariant
3. **Efficiency**: Computational complexity is bounded (typically O(n) or O(n log n))

See **[FORMAL_FOUNDATIONS.md](FORMAL_FOUNDATIONS.md)** for complete proofs and theorems.

---

## Known Limitations

1. **Domain Specificity**: What qualifies as invariant may vary by domain (coding vs. creative writing vs. data extraction)
2. **Definition Ambiguity**: Boundaries between INVARIANT and CRAFTSMAN can be fuzzy for hybrid AI-human workflows
3. **Temporal Drift**: Model updates may change what patterns remain stable
4. **Context Dependency**: Same output structure may be invariant in one context, fragile in another
5. **Complexity Bounds**: Some extraction patterns may have worse than O(n log n) complexity

---

## Future Work

- ✅ Formalize mathematical definitions of invariant properties (COMPLETED - see FORMAL_FOUNDATIONS.md)
- ⏳ Develop automated invariant detection algorithms  
- ⏳ Cross-domain validation across diverse LLM use cases
- ⏳ Peer review and empirical validation studies
- ⏳ Integration with formal verification methods
- ⏳ Optimization of extraction algorithms
- ⏳ Expand mathematical framework to cover edge cases

---

**Last Updated**: 2026-01-18  
**Status**: Mathematically formalized · Empirically validated · Peer review pending
