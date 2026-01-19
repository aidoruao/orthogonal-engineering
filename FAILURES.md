# FAILURES

## Known and Likely Failure Modes

This document catalogs where orthogonal engineering methodology is known to fail or is likely to encounter limitations.

---

## Domain Transfer Failures

### ❌ Not Yet Validated Across Domains

**Current validation:**
- AI conversation analysis ✅
- LLM output extraction ✅
- Chat export normalization ✅

**Untested domains:**
- Physical systems engineering
- Network protocol design  
- Chemical process optimization
- Financial trading systems
- Medical diagnostics

**Why this matters:**
The "benevolent absence" and "canal architecture" concepts were developed for LLM constraints. Whether they generalize to other constrained systems remains empirically unproven.

**Failure risk:** High - theoretical claims may not hold in non-AI domains

---

## Invariant Detection Failures

### ❌ Heuristic Definitions

**Current approach:**
- Manual classification of files as INVARIANT
- Pattern recognition based on extraction success
- No formal algorithm for invariant detection

**What fails:**
- Cannot automatically identify new invariants in novel outputs
- Ambiguous boundary between INVARIANT and CRAFTSMAN in hybrid workflows
- No mathematical proof that tagged invariants are truly stable

**Example failure case:**
```
User asks: "Analyze this code and improve it"
LLM responds with: Mixed original code + AI suggestions

Question: Is this INVARIANT (extractable) or CRAFTSMAN (human-created)?
Answer: Unclear - depends on use case
```

**Failure risk:** Medium - requires human judgment, prone to inconsistency

---

## Template Brittleness

### ❌ Assumption Failures

**The methodology assumes:**

LLMs will follow template structure (e.g., `[INVARIANT]...[/INVARIANT]`)

**What actually happens:**
- Models ignore delimiters
- Models invent their own structure
- Models misinterpret instructions
- Models break mid-generation

**Example failure:**
```
Prompt: "Put answer in [ANSWER] tags"

Expected: [ANSWER]42[/ANSWER]
Actual: "The answer is 42. Hope this helps!"
```

**When templates fail:**
- New model versions change behavior
- Complex prompts confuse instruction following
- Creative tasks resist rigid structure
- Multi-turn conversations lose context

**Failure risk:** Medium - requires testing and iteration per model/task

---

## Extraction Overwhelm

### ❌ Signal Drowning in Noise

**Occurs when:**
- LLM output is completely garbled or incomplete
- Drift exceeds extraction capacity
- Multiple competing structures in output
- No clear delimiter or pattern present

**Example failure:**
```
Prompt: "Extract the email addresses"

Output: "Well, there might be some emails here like john@... 
        or maybe sarah at example dot com, and possibly 
        others but I'm not sure about the format..."
```

**Result:** Pattern matching fails, regex returns nothing, signal is lost

**Mitigation:** Iterative refinement (Layer 4), but can still fail with poor initial outputs

**Failure risk:** High in adversarial or low-quality outputs

---

## Temporal Drift

### ❌ Model Updates Break Patterns

**Problem:**
What's stable in GPT-4 may not be stable in GPT-5

**Specific failures:**

- Training changes alter verbosity patterns
- New safety layers add unexpected drift
- Instruction following improves or degrades
- Output format preferences shift

**Example:**
```
GPT-3.5: Consistently verbose, predictable padding
GPT-4: More concise, less drift to route
GPT-4-Turbo: Back to verbose in different ways
```

**Your canals may need redesign with each model update**

**Failure risk:** Continuous - requires maintenance

---

## Context Window Limitations

### ❌ Long Conversations Lose Structure

**Problem:**
- Multi-turn conversations accumulate context
- Models lose track of extraction requirements
- Templates get forgotten deep in conversation
- Drift patterns change as context fills

**Example failure:**
```
Turn 1: Uses [ANSWER] tags correctly
Turn 5: Still uses tags
Turn 20: Forgets tags entirely
Turn 50: What tags?
```

**Mitigation:** Reset extraction prompts periodically, but adds overhead

**Failure risk:** Medium in long-running conversations

---

## Domain-Specific Limitations

### ❌ Creative Tasks Resist Structure

**Where orthogonal engineering struggles:**
- Poetry generation (structure kills creativity)
- Open-ended brainstorming (canals constrain ideation)
- Emotional support (templates feel robotic)
- Storytelling (extraction breaks narrative flow)

**The methodology is NOT universal**

Works best for:
- Data extraction
- Code generation
- Structured analysis
- Question answering

Works poorly for:
- Creative writing
- Emotional intelligence
- Nuanced judgment calls
- Exploratory dialogue

---

## Scale Limitations


### ❌ Personal Dataset ≠ Universal Validation

**Current validation:**
- 251,471 files (personal archive)
- 233.66 GB (one person's AI use)
- 600+ conversations (single user perspective)

**What this doesn't prove:**
- Works for other users
- Works in production systems
- Works at enterprise scale
- Works across cultures/languages

**Independent replication needed**

**Failure risk:** Unknown - no external validation yet

---

## Theoretical Foundations

### ✅ Formal Mathematical Framework

**Completed:**
- Mathematical definition of "invariant" (see FORMAL_FOUNDATIONS.md)
- Proof that canals preserve signal under drift
- Formal analysis of drift dynamics
- Algorithmic complexity bounds

**Current status:**
- Rigorous mathematical definitions provided
- Theorems proven within specified constraints
- Formal framework available for verification
- Not yet peer-reviewed by academic community

**This matters for:**
- Academic acceptance
- Safety-critical systems
- Regulatory compliance
- Long-term reliability guarantees

**Status:** Theoretical foundations established, awaiting peer review

---

## Integration Challenges

### ❌ Not Plug-and-Play

**Problems:**
- No standard library or framework
- Every use case needs custom templates
- Requires understanding of both LLMs and your domain
- Not suitable for non-technical users

**Example:**
You can't just `pip install orthogonal-engineering` and have it work

**Requires:**
- Custom prompt engineering
- Iterative testing
- Domain expertise
- Technical implementation

**Failure risk:** High for general adoption

---

## Summary of Failure Modes

| Failure Type | Risk Level | Mitigation |
|--------------|-----------|------------|
| Domain Transfer | High | Empirical testing in new domains |
| Invariant Detection | Medium | Formal algorithms needed |
| Template Brittleness | Medium | Continuous testing and iteration |
| Extraction Overwhelm | High | Fallback strategies, human review |
| Temporal Drift | Continuous | Monitor model updates, adapt canals |
| Context Window Limits | Medium | Periodic prompt resets |
| Creative Task Mismatch | High | Don't force structure on creative work |
| Scale Validation | Unknown | Independent replication needed |
| Theoretical Foundations | Low | Framework complete, peer review pending |
| Integration Complexity | High | Better tooling and frameworks |

---

## What to Do When It Fails

1. **Recognize the failure mode** - Is it extraction, template, or domain mismatch?
2. **Check assumptions** - Does your task actually have extractable invariants?
3. **Iterate on templates** - Test different canal designs
4. **Simplify** - Break complex tasks into smaller extraction steps
5. **Accept limitations** - Some tasks don't fit orthogonal engineering
6. **Document** - Share your failure cases to improve the methodology

---

## Honest Assessment

**This methodology is:**
- ✅ Proven for LLM output extraction (personal validation)
- ✅ Useful for structured data tasks
- ✅ Mathematically formalized (theoretical foundations complete)
- ⚠️ Unproven in many domains
- ⚠️ Requires technical expertise
- ❌ Not a silver bullet
- ❌ Not yet peer-reviewed

**Use appropriately. Test thoroughly. Expect failures.**

---

**Last Updated**: 2026-01-18  
**Status**: Living document · Add failure cases via GitHub issues
