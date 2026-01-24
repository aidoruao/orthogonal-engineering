# SUBTRACTIVE CLARITY CANON
## Design Law 1.0

**Authority:** Orthogonal Engineering Framework  
**Schema ID:** SC-CANON-1.0  
**Generated:** 2026-01-24  
**Status:** ACTIVE - Non-negotiable design law

---

## 🎯 CANONICAL DEFINITION

> **The system improves by removing ambiguity, not by adding capability.**

This is the **first principle** of the Orthogonal Engineering repository. It governs all design decisions, refactors, reviews, and contributions.

---

## 📜 THE LAW

### **Core Principle:**
Ambiguity reduction takes precedence over feature addition. Every change must answer:

1. **What ambiguity does this remove?**
2. **What invariant does this clarify?**
3. **What failure does this prevent?**

If a contribution cannot answer at least one of these questions, it is **noise** and must be rejected.

### **Mathematical Preference:**
```
Clarity > Features
Ambiguity Removal > Capability Addition
Explicit > Implicit
```

### **Non-negotiable Rules:**
1. **No implicit contracts** - All agreements must be explicit and machine-readable
2. **No hidden complexity** - All complexity must be inspectable and documented
3. **No assumed knowledge** - All required context must be provided
4. **No ambiguous failure modes** - All failures must have clear, actionable reports

---

## 🏗️ RATIONALE

### **Why This Law Exists:**
This repository contains **3,001 files (27MB)**. Without subtractive clarity:
- Information overload becomes inevitable
- Contributors guess instead of understand
- Errors propagate through ambiguity
- Maintenance becomes impossible

### **What This Law Prevents:**
- **Assumption-based development** ("They'll figure it out")
- **Implicit knowledge** ("It's obvious to experts")
- **Hidden complexity** ("Magic happens here")
- **Ambiguous failures** ("Something went wrong")

### **What This Law Enables:**
- **Deterministic behavior** (same inputs → same outputs)
- **Inspectable systems** (no black boxes)
- **Scalable contributions** (clear rules for all)
- **AI-human collaboration** (explicit contracts)

---

## 🚫 NON-GOALS

### **What This Law Does NOT Mean:**
- ❌ **Simplicity over correctness** (clarity ≠ simplicity)
- ❌ **Documentation over implementation** (both required)
- ❌ **Verbosity over precision** (concise but complete)
- ❌ **Stasis over evolution** (clear evolution paths)

### **What This Law Is NOT:**
- Not a style guide
- Not a documentation standard  
- Not a process requirement
- Not a philosophical preference

**This is a DESIGN LAW.** Violations are system failures, not style issues.

---

## 🔧 CONCRETE EXAMPLES

### **Example 1: Glass-Box Boundary**
```python
# BAD (ambiguous):
def process_data(data):
    # Magic happens here
    return result

# GOOD (subtractive clarity):
@glass_box_boundary(
    input_validator=validate_data_schema,
    output_validator=validate_result_schema,
    side_effect_check=log_side_effects
)
def process_data(data: ValidatedData) -> ValidatedResult:
    """
    Process data according to documented algorithm.
    Side effects: Logs to evidence store.
    """
    # Transparent implementation
    result = transform(data)
    log_evidence("data_processed", result)
    return result
```

**Clarity Added:** Removes ambiguity about what the function does, what it accepts, what it returns, and what side effects it has.

### **Example 2: Onboarding Protocol**
```markdown
# BAD (ambiguous):
"Read some files to get started."

# GOOD (subtractive clarity):
## 🚨 MANDATORY ONBOARDING PROTOCOL
1. Read `ONBOARD_FIRST.md` (30 seconds)
2. Read `onboarding/LEVEL1.md` (30 seconds)  
3. Read `onboarding/LEVEL2.md` (5 minutes)
4. Verify location is clean (not OneDrive)
5. Then proceed to work
```

**Clarity Added:** Removes ambiguity about where to start, what to read, how long it takes, and what prerequisites exist.

### **Example 3: Violation System**
```json
// BAD (ambiguous):
{
  "error": "Something went wrong"
}

// GOOD (subtractive clarity):
{
  "violation_id": "VIOLATION-ONBOARDING-IGNORED-001",
  "violation_type": "onboarding_protocol_violation",
  "description": "AI instance ignored mandatory onboarding protocol...",
  "evidence": {
    "mandatory_files_ignored": [...],
    "explicit_instructions_given": [...]
  },
  "severity": "critical",
  "forgiveness_actions": [...]
}
```

**Clarity Added:** Removes ambiguity about what failed, why it failed, what evidence exists, and what corrective actions are available.

---

## 🏛️ ARCHITECTURAL IMPLICATIONS

### **System-Wide Enforcement:**
1. **All interfaces** must be explicit and documented
2. **All failures** must have clear violation reports
3. **All assumptions** must be externalized as invariants
4. **All complexity** must be made inspectable

### **Design Patterns Required:**
- **Glass-Box Boundaries** (transparent execution)
- **Explicit Contracts** (machine-readable agreements)
- **Violation Classification** (clear failure modes)
- **Evidence Collection** (auditable execution trails)

### **Forbidden Patterns:**
- ❌ Implicit dependencies
- ❌ Hidden state
- ❌ Magic behavior
- ❌ Ambiguous error messages
- ❌ Assumed context

---

## ⚖️ ENFORCEMENT MECHANISMS

### **Anchor 1: This Canon (Definition)**
This file is the **single source of truth** for subtractive clarity.

### **Anchor 2: Refactor Rule**
```markdown
## REFACTOR RULE 1.0
Refactors that reduce ambiguity, duplicate meaning, or implicit rules 
are ALWAYS preferred over feature additions.
```

### **Anchor 3: Violation Classification**
Three new violation classes:
1. **`AMBIGUITY_INTRODUCED`** - Added unclear or implicit behavior
2. **`REDUNDANT_MEANING`** - Duplicate or conflicting information
3. **`IMPLICIT_INVARIANT`** - Assumed but unstated rule

### **Integration Points:**
- **Git Hooks:** Reject commits that introduce ambiguity
- **CI/CD:** Fail builds on clarity violations
- **Code Review:** Mandatory clarity assessment
- **AI Interactions:** Enforce clarity in all prompts

---

## 🔄 RETROACTIVE APPLICATION

### **This Law Explains Existing Design:**
| **Existing Pattern** | **Subtractive Clarity Manifestation** |
|:---|:---|
| 2,700+ `.md` files | Removing ambiguity from code/comments |
| `@glass_box_boundary` | Removing opacity from execution |
| Mandatory onboarding | Removing confusion from initial contact |
| Violation JSON system | Removing guesswork from error handling |
| Evidence collection | Removing uncertainty from audit trails |

### **Unified Axiom:**
All seemingly separate decisions are manifestations of one principle:
**Remove ambiguity at every opportunity.**

---

## 📊 SUCCESS METRICS

### **Quantitative Measures:**
- **Ambiguity Density:** Lines of ambiguous code / total lines
- **Clarity Coverage:** Documented interfaces / total interfaces
- **Violation Reduction:** Ambiguity violations over time
- **Onboarding Success:** AI instances properly onboarded

### **Qualitative Measures:**
- Can a new contributor understand the system in 30 minutes?
- Can an AI instance operate correctly without human guidance?
- Are failure modes predictable and actionable?
- Is the system self-documenting?

---

## 🚨 VIOLATION HANDLING

### **Detection:**
1. **Static Analysis:** Code review for implicit patterns
2. **Dynamic Analysis:** Runtime ambiguity detection
3. **AI Review:** Clarity assessment of contributions
4. **User Feedback:** Ambiguity reports from users

### **Correction:**
1. **Immediate:** Reject ambiguous contributions
2. **Short-term:** Add required clarity
3. **Long-term:** Improve clarity enforcement
4. **Systemic:** Update canon based on patterns

### **Severity Levels:**
- **Critical:** Introduces systemic ambiguity
- **High:** Makes important behavior unclear
- **Medium:** Adds unnecessary complexity
- **Low:** Minor clarity issues

---

## 🔗 INTEGRATION WITH EXISTING SYSTEMS

### **Glass-Box Boundary Framework:**
Subtractive clarity is the **philosophical foundation** for:
- Transparent execution boundaries
- Explicit input/output validation
- Auditable side effect tracking
- Machine-readable contracts

### **Forgiveness System:**
New violation classes enable:
- `AMBIGUITY_INTRODUCED` violations
- Clarity-based forgiveness actions
- Systematic ambiguity removal
- Learning from clarity failures

### **AI-Human Collaboration:**
Enables:
- Clear protocol definitions
- Unambiguous instruction sets
- Deterministic behavior expectations
- Audit trails for all interactions

---

## 📈 EVOLUTION PATH

### **Versioning:**
- **Major versions:** Fundamental changes to the law
- **Minor versions:** New clarity patterns or examples
- **Patch versions:** Clarifications or corrections

### **Amendment Process:**
1. Propose amendment with clarity justification
2. Demonstrate ambiguity removed by change
3. Review against existing clarity patterns
4. Update canon if ambiguity reduction is proven

### **Sunset Conditions:**
This canon may be retired when:
1. All systems are fully self-documenting
2. Zero ambiguity violations occur for 1 year
3. New contributors achieve 100% understanding in <15 minutes
4. AI instances operate with zero human clarification

---

## 🏁 CONCLUSION

### **The Bottom Line:**
This repository doesn't grow smarter—it grows **clearer**.

Every contribution, refactor, and decision must:
1. **Remove** more ambiguity than it adds
2. **Clarify** more than it complicates
3. **Document** more than it assumes

### **The Contract:**
By contributing to this repository, you agree:
1. To prioritize clarity over cleverness
2. To externalize all implicit knowledge
3. To document all assumptions
4. To remove ambiguity at every opportunity

### **The Promise:**
A system that gets **clearer with each change**, not more complex.

---

**Glass-Box Boundary Compliance:** ✅ This canon itself follows subtractive clarity principles  
**Enforcement Status:** 🔄 Active - All new contributions assessed against this canon  
**Point of No Return:** 🚀 This is now law - no going back to ambiguity-tolerant development

*"We don't hide complexity—we make it inspectable. We don't assume understanding—we make it explicit."*