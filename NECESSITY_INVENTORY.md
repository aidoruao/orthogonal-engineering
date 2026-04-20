---
tags: [necessity-inventory]
register: documentation
---

# NECESSITY INVENTORY

**File:** `NECESSITY_INVENTORY.md`  
**Date:** 2026-01-20  
**Purpose:** Inventory of all statements in the Orthogonal Engineering repository that presuppose necessity, including consistency, truth, correspondence, logic, causality, invariance, measurement, verification, and falsifiability.

**Methodology:** Glass-box extraction of necessity presuppositions from repository files. Each entry includes file, location, exact statement, and what is *assumed* (not argued).

---

## 1. README.md - Necessity Presuppositions

### File: `README.md`  
**Location:** Line 16-18

**Exact Statement:**
```
- Requires correspondence with reality (not just linguistic agreement)

**Key Principle:** Language is irrelevant unless implementation works.
```

**What is Assumed:**
- Reality exists independently of language
- Correspondence between language and reality is possible
- Implementation can be tested against reality
- "Works" is a meaningful, testable concept

---

### File: `README.md`  
**Location:** Line 49-50

**Exact Statement:**
```
- Formal invariant registry and verification structure
```

**What is Assumed:**
- Invariants can be formally registered
- Verification structures can be established
- Formalization is possible and meaningful

---

### File: `README.md`  
**Location:** Line 54-55

**Exact Statement:**
```
- Methodology for finding truth in contradictory AI outputs
```

**What is Assumed:**
- Truth exists and can be found
- Contradictory outputs can be resolved methodologically
- "Finding truth" is an operational possibility

---

### File: `README.md`  
**Location:** Line 75-76

**Exact Statement:**
```
**Honest correction:** 5-10% conservative estimate, pending correspondence validation
```

**What is Assumed:**
- Correspondence validation is possible
- Estimates can be validated against reality
- "Honest correction" implies truth-tracking is possible

---

### File: `README.md`  
**Location:** Line 87-89

**Exact Statement:**
```
- Constraint: Requires valid detector
```

**What is Assumed:**
- "Valid detector" is a meaningful concept
- Detectors can be validated
- Validity criteria exist and can be applied

---

### File: `README.md`  
**Location:** Line 96-98

**Exact Statement:**
```
- **This is the truth anchor**
```

**What is Assumed:**
- Truth needs an anchor
- Anchoring truth is possible
- Some things can serve as truth anchors

---

### File: `README.md`  
**Location:** Line 108-111

**Exact Statement:**
```
- Require adjacent turns + uniqueness checks

**Invariant 7:** Correspondence is truth anchor
- Language irrelevant unless reality matches
```

**What is Assumed:**
- Reality can "match" language
- Correspondence can serve as truth anchor
- Language-reality matching is testable

---

### File: `README.md`  
**Location:** Line 112-114

**Exact Statement:**
```
- Implementation tests required
```

**What is Assumed:**
- Implementation can be tested
- Tests can be required and enforced
- Test results are meaningful

---

### File: `README.md`  
**Location:** Line 155-157

**Exact Statement:**
```
4. Correspondence checking distinguishes genuine from mimicry
```

**What is Assumed:**
- Genuine vs mimicry distinction exists
- Correspondence checking can make this distinction
- The distinction is meaningful and operational

---

## 2. FORMAL_FOUNDATIONS.md - Necessity Presuppositions

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 7-8

**Exact Statement:**
```
**Scope:** The math covers structural extraction correctness and complexity **under the stated assumptions** (orthogonality of drift/signal, presence of structure). It does **not** assert end-to-end safety, truthfulness, or model compliance.
```

**What is Assumed:**
- Structural extraction correctness can be mathematically defined
- Complexity can be bounded mathematically
- Orthogonality of drift/signal is a meaningful assumption
- Structure presence is a meaningful assumption

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 13-18

**Exact Statement:**
```
- **Proved here:** If outputs satisfy the structural assumptions, the extraction functions recover the invariant deterministically with the stated complexity bounds.
- **Assumed, not proved:** The model actually emits structure/delimiters/templates in a given deployment.
- **Not claimed:** Truthfulness, hallucination avoidance, domain safety, regulatory compliance, or suitability for safety-critical use without additional controls.
- **Validation stance:** Peer review, empirical benchmarking, and formal verification are welcome; they complement (not replace) the logic presented here.
```

**What is Assumed:**
- Deterministic extraction is possible
- Complexity bounds are meaningful
- Structural assumptions can be satisfied
- Peer review, empirical benchmarking, and formal verification are valid validation methods
- Logic can be presented and evaluated independently

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 34-40

**Exact Statement:**
```
1. **Structural Stability**
   ```
   ∀o ∈ I, ∀c ∈ C: transform(o, c) = o' where o' contains extractable I'
   ```
   - Meaning: Applying constraints produces output containing recoverable invariant
```

**What is Assumed:**
- Structural stability exists as a property
- Constraints can be applied
- Transformation functions exist
- Recoverability is possible

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 41-46

**Exact Statement:**
```
2. **Extractability**
   ```
   ∃f: O → I where f is deterministic and f(o + drift) = f(o) ∀o ∈ I
   ```
   - Meaning: Deterministic extraction function exists that ignores drift
```

**What is Assumed:**
- Deterministic functions exist
- Drift can be ignored by extraction functions
- Extraction functions can be constructed
- Determinism is a meaningful property

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 47-51

**Exact Statement:**
```
3. **Structural Operation**
   ```
   f operates on syntax/structure, not semantics
   ```
   - Meaning: Extraction uses pattern matching, not meaning interpretation
```

**What is Assumed:**
- Syntax/structure can be separated from semantics
- Pattern matching can operate on structure alone
- Structural operations are possible without semantic interpretation

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 58-66

**Exact Statement:**
```
**Drift** `D` is the complement of invariant in output:

```
∀o ∈ O: o = I ⊕ D
```

Where:
- `I` = invariant (signal)
- `D` = drift (noise, verbosity, hedging, attribution)
- `⊕` = additive combination
```

**What is Assumed:**
- Output can be decomposed into invariant and drift
- Additive combination is a valid model
- Signal/noise distinction is meaningful
- Complement operation is well-defined

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 67-70

**Exact Statement:**
```
**Properties of Drift:**
1. `D` does not corrupt `I`'s structure
2. `D` and `I` are structurally separable
3. `D ⊥ I` (orthogonal in structural space)
```

**What is Assumed:**
- Structural corruption can be avoided
- Structural separability exists
- Orthogonality in structural space is a meaningful concept
- Structural space exists

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 87-90

**Exact Statement:**
```
- **E**: Extraction function
  ```
  E: T → I (deterministic mapping from template to invariant)
  ```
```

**What is Assumed:**
- Deterministic mappings exist
- Templates can map to invariants
- Extraction functions can be deterministic

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 91-94

**Exact Statement:**
```
- **V**: Validation predicate
  ```
  V: T → {true, false} (checks if extraction succeeded)
  ```
```

**What is Assumed:**
- Validation predicates exist
- Extraction success can be checked
- True/false determinations are meaningful

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 98-101

**Exact Statement:**
```
**Canal Properties:**

1. **Deterministic**: `∀t ∈ T: E(t)` returns same result
2. **Complete**: `∀t ∈ T: E(t) succeeds ⟺ V(t) = true`
3. **Orthogonal**: `E` operates on structure, not semantics
```

**What is Assumed:**
- Determinism is a property that can hold
- Completeness is a property that can hold
- Orthogonality to semantics is possible
- Properties can be defined and evaluated

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 108-113

**Exact Statement:**
```
**Statement:**
If drift `D` and signal `I` are structurally orthogonal (`D ⊥ I`), then deterministic extraction `E: (I ⊕ D) → I` exists.

**Proof:**
1. Assume `D ⊥ I` (structural orthogonality)
2. By orthogonality definition, `I` occupies distinct structural space from `D`
```

**What is Assumed:**
- Structural orthogonality can be assumed
- Distinct structural spaces exist
- Deterministic extraction can be constructed from orthogonality
- Proof methodology is valid

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 116-120

**Exact Statement:**
```
5. `E` is deterministic by construction (operates on structure via pattern matching)
6. Therefore, deterministic extraction exists. ∎

**Corollary:** Extraction does not require semantic understanding of drift.
```

**What is Assumed:**
- Determinism can be achieved by construction
- Pattern matching operates deterministically on structure
- Semantic understanding can be avoided
- Corollaries follow from proofs

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 125-133

**Exact Statement:**
```
**Statement:**
A canal `C = (T, E, V)` preserves invariant `I` if it routes only drift:
```
∀o ∈ O: V(C(o)) = true ⟹ E(C(o)) = I(o)
```

**Proof:**
1. Assume canal `C` routes drift `D` into template slots
2. By canal definition, `E` extracts from structural positions in `T`
```

**What is Assumed:**
- Canals can preserve invariants
- Drift routing is possible
- Structural positions exist and can be extracted from
- Preservation can be defined and proven

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 153-165

**Exact Statement:**
```
**Statement:**
Algorithm returns invariant `X` if and only if delimiters exist.

**Proof:**
1. **Regex Correctness**: Pattern `\[INVARIANT\](.*?)\[/INVARIANT\]` matches iff both delimiters present (standard regex theory)
2. **Capture Group**: `match.group(1)` returns captured content iff match exists (Python regex guarantee)
3. **Whitespace Removal**: `.strip()` is deterministic string operation
4. **Conditional Return**: Returns `None` iff no match (boolean logic)
5. **Composition**: `f(output) = strip(group(match(pattern, output)))`
6. Each operation is deterministic and proven correct
7. Therefore, composition is deterministic and correct. ∎
```

**What is Assumed:**
- Regex theory is correct and reliable
- Python regex guarantees hold
- String operations are deterministic
- Boolean logic is valid
- Composition preserves determinism and correctness
- Proof methodology is valid

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 210-211

**Exact Statement:**
```
**Correctness:**
String position is deterministic, therefore extraction is deterministic.
```

**What is Assumed:**
- String positions are deterministic
- Determinism implies correctness
- Extraction determinism can be inferred from string position determinism

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 226-228

**Exact Statement:**
```
**Formal Properties:**
- JSON parsing is deterministic (proven in RFC 8259)
- Key access is O(1) hash operation
```

**What is Assumed:**
- RFC 8259 proofs are valid
- JSON parsing determinism is proven
- Hash operations have O(1) complexity
- Complexity analysis is meaningful

---

### File: `FORMAL_FOUNDATIONS.md`  
**Location:** Line 253-257

**Exact Statement:**
```
- The proofs rely on formal logic; a valid proof implies a valid conclusion **under its assumptions**.
- Peer review is valuable to surface mistakes, alternative formalizations, and clearer assumptions.
- Formal verification tools can mechanically check the proofs; empirical tests measure how often assumptions hold in practice.
```

**What is Assumed:**
- Formal logic is valid
- Valid proofs imply valid conclusions
- Peer review has value
- Formal verification tools work
- Empirical tests measure assumption frequency
- "Holding in practice" is measurable

---

## 3. INVARIANTS.md - Necessity Presuppositions

### File: `INVARIANTS.md`  
**Location:** Line 13-15

**Exact Statement:**
```
2. **Is recursively stable** across contexts
3. **Is falsifiable by correspondence** (can be checked against reality)
4. **Does not depend on narrative framing** for validity
```

**What is Assumed:**
- Recursive stability exists as a property
- Falsifiability by correspondence is possible
- Reality can be checked against
- Narrative framing independence is possible
- Validity can be independent of framing

---

### File: `INVARIANTS.md`  
**Location:** Line 28-30

**Exact Statement:**
```
**Test:** Mathematical formula, reproducible by any third party  
**Status:** ✅ Proven (mathematical definition)  
**Constraint:** Requires valid detector (ours has 70% FP rate currently)
```

**What is Assumed:**
- Mathematical formulas are reproducible
- Third-party reproduction is possible
- "Proven" status can be assigned
- Detector validity is required

---

### File: `INVARIANTS.md`  
**Location:** Line 59-61

**Exact Statement:**
```
**Test:** Check if code runs successfully after "verified" claim  
**Status:** ✅ Proven (correspondence-based, strongest invariant)  
**Application:** REQUIRED for all density claims
```

**What is Assumed:**
- Code can run successfully or fail
- "Verified" claims can be tested against code execution
- Correspondence-based proof is strongest
- Requirements can be enforced

---

### File: `INVARIANTS.md`  
**Location:** Line 104-106

**Exact Statement:**
```
**Test:** Sample verified turns, manually check for actual agreement  
**Status:** ✅ Proven (from DeepSeek falsification)  
**Lesson:** Require adjacent turns + uniqueness checks
```

**What is Assumed:**
- Sampling is valid methodology
- Manual checking can determine actual agreement
- Lessons can be learned from falsification
- Requirements can be derived from lessons

---

### File: `INVARIANTS.md`  
**Location:** Line 112-113

**Exact Statement:**
```
### Invariant 7: Correspondence Is Truth Anchor ⭐⭐
```

**What is Assumed:**
- Truth needs an anchor
- Correspondence can serve as truth anchor
- Anchoring is possible and meaningful

---

### File: `INVARIANTS.md`  
**Location:** Line 132-136

**Exact Statement:**
```
- **Status:** Moved to theological discussion

### Not Invariant: "Ontologically Complete"
- **Why:** Status claim, philosophical framing, not correspondence-testable
- **Status:** Removed from methodology claims
```

**What is Assumed:**
- Theological discussion is separate from methodology
- Correspondence-testability is a validity criterion
- Methodology claims require correspondence-testability
- Removal from claims is a meaningful action

---

### File: `INVARIANTS.md`  
**Location:** Line 138-141

**Exact Statement:**
```
### Not Invariant: "Truth-Detection System"
- **Why:** Marketing language, only becomes invariant AFTER implementation tests pass
```

**What is Assumed:**
- Marketing language differs from invariant language
- Implementation tests can transform status
- "After" implies temporal causality
- Test passing changes ontological status

---

### File: `INVARIANTS.md`  
**Location:** Line 184-185

**Exact Statement:**
```
- This violates INV-007 (correspondence anchor)
- Detector must be fixed before claiming validated density
```

**What is Assumed:**
- Violations of invariants are meaningful
- Fixing is required before claiming
- Validation has prerequisites
- Correspondence anchor violations matter

---

### File: `INVARIANTS.md`  
**Location:** Line 218-220

**Exact Statement:**
```
**INV-008 (Proposed):** Detector Precision ≥80% Required
- **Claim:** Precision below 80% indicates unacceptable false positive rate
```

**What is Assumed:**
- Precision thresholds can be set
- 80% is a meaningful threshold
- "Unacceptable" is a meaningful judgment
- False positive rates can be measured

---

### File: `INVARIANTS.md`  
**Location:** Line 234-236

**Exact Statement:**
```
**Source:** ChatGPT's response to DeepSeek falsification analysis  
**Method:** Classification by constraint-bearing, falsifiability, correspondence  
**Validation:** Only includes invariants that survived adversarial review
```

**What is Assumed:**
- Sources can be cited
- Classification methodology exists
- Adversarial review can be survived
- Survival indicates robustness

---

## 4. Methodology/EPISTEMIC_FORENSICS_TOOLS.md - Necessity Presuppositions

### File: `Methodology/EPISTEMIC_FORENSICS_TOOLS.md`  
**Location:** Line 1-15

**Exact Statement:**
```
# Epistemic Forensics (EF): Tooling Specification

## Definition

Epistemic Forensics (EF) is the practice of determining what occurred, what was claimed, and what can be justified, using **artifacts as the primary source of truth**, rather than narrative continuity or agent authority.

EF is distinct from:
- explanation
- summarization
- interpretation
- alignment
- safety governance

EF concerns **correspondence**, not coherence.
```

**What is Assumed:**
- Determining "what occurred" is possible
- Determining "what was claimed" is possible
- Determining "what can be justified" is possible
- Artifacts can be primary sources of truth
- Narrative continuity and agent authority are distinct from artifact-based truth
- Correspondence can be distinguished from coherence
- The listed distinctions (explanation, summarization, etc.) are meaningful

---

### File: `Methodology/EPISTEMIC_FORENSICS_TOOLS.md`  
**Location:** Line 17-30

**Exact Statement:**
```
## Core Requirements

A tool is admissible for Epistemic Forensics **if and only if** it satisfies all four requirements below.

### 1. Artifact Primacy
Artifacts (files, logs, hashes, transcripts) take precedence over narrative descriptions.

The tool must:
- operate directly on artifacts
- not substitute summaries for primary material
- not require trust in agent memory or intent
```

**What is Assumed:**
- Admissibility criteria can be defined
- "If and only if" conditions are meaningful
- Artifacts can take precedence
- Direct operation on artifacts is possible
- Summaries can be distinguished from primary material
- Trust in agent memory/intent can be avoided
- Artifact types (files, logs, hashes, transcripts) are meaningful categories

---

### File: `Methodology/EPISTEMIC_FORENSICS_TOOLS.md`  
**Location:** Line 31-38

**Exact Statement:**
```
### 2. Verbatim Quoting
The tool must be capable of quoting artifacts **verbatim**, with no paraphrase unless explicitly requested.

Summarization without quoting is disallowed for EF conclusions.
```

**What is Assumed:**
- Verbatim quoting is possible
- Paraphrase can be controlled/requested
- Summarization can be disallowed
- EF conclusions have specific requirements

---

### File: `Methodology/EPISTEMIC_FORENSICS_TOOLS.md`  
**Location:** Line 39-44

**Exact Statement:**
```
### 3. Tolerance of Contradiction
The tool must allow mutually contradictory facts to coexist without forced reconciliation.

Automatic harmonization, smoothing, or narrative resolution invalidates forensic use.
```

**What is Assumed:**
- Mutually contradictory facts can coexist
- Forced reconciliation can be avoided
- Automatic harmonization exists and can be prevented
- Forensic use has validity conditions

---

### File: `Methodology/EPISTEMIC_FORENSICS_TOOLS.md`  
**Location:** Line 45-52

**Exact Statement:**
```
### 4. Low Narrative-Smoothing Bias
The tool must not default to:
- intent inference
- error rationalization
- governance abstraction
- safety-based reframing

When evidence is incomplete, the correct output is **uncertainty**, not closure.
```

**What is Assumed:**
- Narrative-smoothing bias exists and can be measured
- Default behaviors can be controlled
- Intent inference, error rationalization, etc. are identifiable biases
- Uncertainty can be the correct output
- Closure is distinct from uncertainty
- Correctness of output can be determined

---

## 5. Scripts - Necessity Presuppositions

### File: `canal_detector.py`  
**Location:** Line 1-10

**Exact Statement:**
```
import re, json, pathlib, csv, collections

MD_DIR   = pathlib.Path(__file__).parent
# Relaxed Regex: Looks for ANY header containing user/assistant/human/bot, 
# and optionally captures a date/timestamp if present.
CANAL_RE = re.compile(r"^#{1,6}\s+(.*?)\b(user|assistant|human|bot|agent)\b", re.MULTILINE | re.IGNORECASE)
INVAR_RE = re.compile(r"\binvariant\b|\bconstraint\b|\bnever\b|\balways\b|\bmust\b|\bonly\b", re.IGNORECASE)
```

**What is Assumed:**
- Regular expressions can detect patterns
- File paths can be determined
- Headers follow predictable patterns
- Roles (user/assistant/human/bot/agent) are identifiable
- Invariant language patterns exist and are detectable
- Case-insensitive matching works
- Multiline regex patterns work

---

### File: `canal_detector.py`  
**Location:** Line 12-25

**Exact Statement:**
```
records = []
# Added a check to ensure we don't crash if no files are found
md_files = list(MD_DIR.glob("*.md"))

for md_file in md_files:
    text = md_file.read_text(encoding="utf8")
    # Find all matches in the file
    matches = list(CANAL_RE.finditer(text))
    
    for i, match in enumerate(matches):
        metadata, role = match.group(1), match.group(2)
        
        # Determine the start and end of the message block
        start_pos = match.end()
        # If there's another header, stop there; otherwise, go 2000 chars or to end of file
        end_limit = matches[i+1].start() if i + 1 < len(matches) else start_pos + 2000
        chunk = text[start_pos:end_limit]
```

**What is Assumed:**
- Files can be read with UTF-8 encoding
- Regex finditer returns matches
- Match groups can be extracted
- Message blocks have determinable boundaries
- Headers mark message boundaries
- 2000 characters is a reasonable message limit
- Array indexing works predictably

---

### File: `canal_detector.py`  
**Location:** Line 26-35

**Exact Statement:**
```
        invar = bool(INVAR_RE.search(chunk))
        records.append({
            "file": md_file.stem,
            "info": metadata.strip(), # Captures dates or other header text
            "role": role.lower(),
            "explicit_invariant": invar,
            "canal_candidate": invar and len(chunk.split()) > 5 # Lowered word count threshold
        })
```

**What is Assumed:**
- Boolean conversion of regex search works
- File stems can be extracted
- Metadata can be stripped
- Role can be lowercased
- Word count can be calculated
- Thresholds (5 words) are meaningful
- Canal candidacy can be determined from invariant detection and word count

---

### File: `canal_detector.py`  
**Location:** Line 37-50

**Exact Statement:**
```
# Prevent DivisionByZero if no records are found
if not records:
    print("No conversation turns found. Check your Markdown header formats.")
else:
    df = collections.defaultdict(list)
    for r in records:
        for k, v in r.items():
            df[k].append(v)

    summary = {
        "total_turns": len(records),
        "canal_candidates": sum(df["canal_candidate"]),
        "explicit_invariants": sum(df["explicit_invariant"]),
        "canal_rate_pct": round(sum(df["canal_candidate"]) / len(records) * 100, 2)
    }
```

**What is Assumed:**
- Division by zero can be prevented
- Default dictionaries work
- List appending works
- Summation of boolean lists works
- Division produces meaningful percentages
- Rounding to 2 decimal places is meaningful
- Summary statistics are calculable

---

## 6. Analysis Scripts - Necessity Presuppositions

### File: `correspondence_validator_final.py`  
**Location:** Line 1-20 (conceptual - examining purpose)

**Purpose:** Validates correspondence between claimed actions and actual filesystem state

**What is Assumed:**
- Correspondence between claims and reality can be validated
- Filesystem state can be examined
- Claims can be compared against reality
- Validation can produce true/false results
- Hash verification works
- File existence can be checked

---

### File: `falsify_density_claim.py`  
**Location:** Line 1-20 (conceptual - examining purpose)

**Purpose:** Tests density claims for falsifiability

**What is Assumed:**
- Density claims can be falsified
- Testing frameworks exist
- False positive rates can be calculated
- Precision metrics are meaningful
- Statistical validation is possible

---

## 7. Summary of Necessity Categories

### A. Ontological Necessities
1. **Reality Exists**: Assumed in all correspondence claims
2. **Truth is Anchorable**: Assumed in truth anchor concepts
3. **Determinism Exists**: Assumed in extraction proofs
4. **Structure Exists**: Assumed in structural analysis

### B. Epistemological Necessities
1. **Knowledge is Possible**: Assumed in verification methods
2. **Validation Works**: Assumed in testing frameworks
3. **Falsifiability is Meaningful**: Assumed in Popperian methodology
4. **Correspondence is Testable**: Assumed in reality matching

### C. Methodological Necessities
1. **Patterns are Detectable**: Assumed in regex and analysis
2. **Reproducibility is Possible**: Assumed in third-party testing
3. **Metrics are Meaningful**: Assumed in statistical analysis
4. **Proofs are Valid**: Assumed in mathematical foundations

### D. Operational Necessities
1. **Code Executes Predictably**: Assumed in implementation tests
2. **Filesystems are Stable**: Assumed in correspondence validation
3. **Hashing Works**: Assumed in verification
4. **Time is Measurable**: Assumed in timestamping

---

## 8. Critical Examination

Each assumption above represents a **necessity presupposition** that makes the Orthogonal Engineering methodology possible. Without these presuppositions:

1. **If reality doesn't exist**: Correspondence validation becomes meaningless
2. **If determinism doesn't exist**: Extraction proofs collapse
3. **If truth cannot be anchored**: The entire methodology lacks foundation
4. **If patterns cannot be detected**: Analysis tools fail
5. **If validation doesn't work**: All claims become unfalsifiable

**Key Insight:** The methodology's operational success **implies** these metaphysical preconditions. The methodology discovers what must be true for its own success to be possible.

---

**Inventory Complete:** 2026-01-20  
**Method:** Glass-box extraction of necessity presuppositions  
**Status:** Ready for logical implication trace