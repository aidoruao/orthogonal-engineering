# REFACTOR RULE: SUBTRACTIVE CLARITY
## Design Rule 1.0

**Authority:** Subtractive Clarity Canon (SC-CANON-1.0)  
**Schema ID:** SC-REFACTOR-1.0  
**Generated:** 2026-01-24  
**Status:** ACTIVE - Mandatory refactor preference rule

---

## 🎯 RULE DEFINITION

> **Refactors that reduce ambiguity, duplicate meaning, or implicit rules are ALWAYS preferred over feature additions.**

This is a **mathematical preference rule** that governs all refactoring decisions in the Orthogonal Engineering repository.

---

## 📜 THE RULE

### **Core Principle:**
When faced with multiple refactoring options, choose the one that:

1. **Removes the most ambiguity**
2. **Eliminates the most duplication**
3. **Makes the most implicit rules explicit**
4. **Reduces the most cognitive load**

### **Priority Order:**
```
Ambiguity Reduction > Duplication Elimination > Explicitization > Feature Addition
```

### **Non-negotiable Application:**
This rule applies to:
- ✅ All code refactors
- ✅ All documentation updates
- ✅ All interface changes
- ✅ All configuration modifications
- ✅ All workflow adjustments

---

## 🏗️ RATIONALE

### **Why This Rule Exists:**
Software entropy naturally increases over time. Without this rule:
- Systems become more complex with each change
- Implicit knowledge accumulates
- Maintenance costs grow exponentially
- New contributors face steeper learning curves

### **What This Rule Prevents:**
- **Feature creep** (adding without clarifying)
- **Implicit complexity** (hidden assumptions)
- **Knowledge silos** (undocumented expertise)
- **Ambiguity accumulation** (unclear behavior)

### **What This Rule Enables:**
- **Progressive simplification** (system gets clearer)
- **Knowledge preservation** (explicit documentation)
- **Scalable maintenance** (clear boundaries)
- **Deterministic evolution** (predictable changes)

---

## 🔧 CONCRETE EXAMPLES

### **Example 1: Code Refactor**
```python
# BEFORE (ambiguous, implicit):
def process(data):
    # Magic happens here
    result = transform(data)
    return result

# OPTION A (add feature):
def process(data, new_feature=False):
    # Still magic, but with new feature
    result = transform(data)
    if new_feature:
        result = enhance(result)
    return result

# OPTION B (subtractive clarity - PREFERRED):
@glass_box_boundary(
    input_validator=validate_data,
    output_validator=validate_result
)
def process(data: ValidatedData) -> ValidatedResult:
    """
    Process data using documented transformation algorithm.
    
    Algorithm:
    1. Validate input against schema
    2. Apply linear transformation
    3. Validate output against schema
    4. Return result
    
    Complexity: O(n)
    """
    # Transparent implementation
    validated_data = validate_data(data)
    result = linear_transform(validated_data)
    validated_result = validate_result(result)
    return validated_result
```

**Rule Applied:** Option B is preferred because it removes ambiguity about what the function does, how it works, and what it expects/returns.

### **Example 2: Documentation Refactor**
```markdown
# BEFORE (implicit, scattered):
- File A: "See File B for details"
- File B: "Refer to File C"
- File C: "Check the code"

# OPTION A (add more documentation):
- File A: "See File B for details"
- File B: "Refer to File C"  
- File C: "Check the code"
- File D: "New documentation here"

# OPTION B (subtractive clarity - PREFERRED):
# SINGLE_SOURCE_OF_TRUTH.md
## Complete System Documentation

### Component A
- Purpose: Data processing
- Interface: process(data) -> result
- Dependencies: None
- Usage: import from module_a

### Component B
- Purpose: Data validation
- Interface: validate(data) -> bool
- Dependencies: schema.json
- Usage: import from module_b

### Component C
- Purpose: Result formatting
- Interface: format(result) -> string
- Dependencies: template.txt
- Usage: import from module_c
```

**Rule Applied:** Option B is preferred because it eliminates duplication, removes implicit references, and creates a single source of truth.

### **Example 3: Configuration Refactor**
```yaml
# BEFORE (ambiguous, implicit defaults):
app:
  settings: "default"
  # timeout is somewhere in code
  # retry logic is hardcoded

# OPTION A (add more settings):
app:
  settings: "default"
  new_feature: true
  experimental_mode: false
  # timeout still implicit
  # retry logic still hardcoded

# OPTION B (subtractive clarity - PREFERRED):
app:
  # EXPLICIT CONFIGURATION
  settings: 
    mode: "production"
    debug: false
    
  timeout:
    connection: 30s
    read: 60s
    write: 60s
    
  retry:
    max_attempts: 3
    backoff: exponential
    base_delay: 1s
    max_delay: 30s
    
  validation:
    input_schema: "schemas/input.json"
    output_schema: "schemas/output.json"
    
  logging:
    level: "info"
    format: "json"
    destination: "logs/app.log"
```

**Rule Applied:** Option B is preferred because it makes all implicit defaults explicit, removes ambiguity about behavior, and provides complete configuration visibility.

---

## ⚖️ DECISION FRAMEWORK

### **Decision Matrix:**
When choosing between refactor options, score each option (0-10) on:

1. **Ambiguity Reduction:** How much unclear behavior is made explicit?
2. **Duplication Elimination:** How much repeated logic/info is removed?
3. **Explicitization:** How many implicit rules are made explicit?
4. **Cognitive Load Reduction:** How much easier is it to understand?

**Formula:** `Total Score = (A×3) + (D×2) + (E×2) + (C×1)`

**Choose the option with the highest score.**

### **Tie-Breaking Rules:**
1. If scores are equal, choose the option that removes the most **systemic ambiguity**
2. If still equal, choose the option that benefits **new contributors** the most
3. If still equal, choose the option that enables **AI understanding** the most

---

## 🛠️ PRACTICAL GUIDELINES

### **When to Apply This Rule:**
1. **During code review** - Assess all proposed changes
2. **When fixing bugs** - Consider clarity improvements
3. **When adding features** - First clarify existing code
4. **When documenting** - Eliminate duplication first
5. **When refactoring** - Always prefer clarity gains

### **How to Apply This Rule:**
1. **Identify ambiguity** - What's unclear or implicit?
2. **Measure current state** - Score existing code (0-10)
3. **Propose alternatives** - Create multiple refactor options
4. **Score each option** - Use decision matrix
5. **Implement highest score** - Choose subtractive clarity
6. **Verify improvement** - Re-score after implementation

### **Red Flags (Violate This Rule):**
- ❌ "We'll document it later"
- ❌ "It's obvious from context"
- ❌ "Experts will understand"
- ❌ "The code is self-explanatory"
- ❌ "We don't have time for clarity"

### **Green Flags (Follow This Rule):**
- ✅ "Let me make this explicit"
- ✅ "I'll remove this duplication"
- ✅ "This assumption should be documented"
- ✅ "The implicit rule needs to be explicit"
- ✅ "Clarity first, features second"

---

## 🔍 DETECTION MECHANISMS

### **Static Analysis Checks:**
1. **Ambiguity Detection:** Find unclear variable/function names
2. **Duplication Detection:** Identify repeated logic/configuration
3. **Implicit Rule Detection:** Find undocumented assumptions
4. **Cognitive Load Measurement:** Estimate understanding difficulty

### **Dynamic Analysis Checks:**
1. **Runtime Ambiguity:** Monitor unclear error messages
2. **Implicit Behavior:** Detect undocumented side effects
3. **Assumption Violation:** Catch broken implicit rules
4. **Understanding Gaps:** Measure contributor confusion

### **Human Review Checks:**
1. **New Contributor Test:** Can someone new understand this?
2. **AI Comprehension Test:** Can an AI operate this correctly?
3. **Maintenance Cost Estimate:** How hard will this be to maintain?
4. **Evolution Predictability:** How will this change over time?

---

## 📊 SUCCESS METRICS

### **Quantitative Measures:**
- **Ambiguity Score Reduction:** Pre-refactor vs post-refactor
- **Duplication Percentage:** Repeated lines / total lines
- **Explicitization Rate:** Documented rules / total rules
- **Cognitive Load Index:** Estimated understanding time

### **Qualitative Measures:**
- Can a new contributor understand this in <15 minutes?
- Can an AI correctly use this without human clarification?
- Are all failure modes predictable and documented?
- Is the evolution path clear and predictable?

### **Progress Tracking:**
- Weekly ambiguity reduction reports
- Monthly duplication elimination metrics
- Quarterly explicitization progress
- Annual cognitive load improvements

---

## 🚨 VIOLATION HANDLING

### **Violation Types:**
1. **CLARITY_VIOLATION:** Chose features over clarity
2. **DUPLICATION_VIOLATION:** Added duplication instead of removing
3. **IMPLICIT_RULE_VIOLATION:** Left rules implicit
4. **COGNITIVE_LOAD_VIOLATION:** Increased understanding difficulty

### **Correction Actions:**
1. **Immediate:** Reject violating changes
2. **Short-term:** Require clarity improvements
3. **Medium-term:** Add clarity training
4. **Long-term:** Improve detection systems

### **Severity Levels:**
- **Critical:** Introduces systemic ambiguity
- **High:** Significantly increases maintenance cost
- **Medium:** Makes important behavior unclear
- **Low:** Minor clarity regression

---

## 🔗 INTEGRATION POINTS

### **With Subtractive Clarity Canon:**
This rule operationalizes the canon's principle:
- **Canon:** "Remove ambiguity, not add capability"
- **This Rule:** "Prefer refactors that remove ambiguity"

### **With Glass-Box Boundary:**
- Refactors must maintain/increase boundary clarity
- New boundaries should reduce systemic ambiguity
- Boundary violations indicate needed refactors

### **With Forgiveness System:**
- Clarity violations trigger forgiveness actions
- Refactor improvements reduce violation counts
- Clear systems need less forgiveness

### **With AI-Human Collaboration:**
- Clear systems enable better AI operation
- AI can help identify ambiguity for refactoring
- Refactors improve AI comprehension

---

## 📈 EVOLUTION PATH

### **Versioning:**
- **Major versions:** Fundamental rule changes
- **Minor versions:** New refactor patterns or examples
- **Patch versions:** Clarifications or corrections

### **Amendment Process:**
1. Demonstrate current rule fails to optimize clarity
2. Propose new rule with clarity improvement proof
3. Test against historical refactor decisions
4. Update if clarity improvement is proven

### **Sunset Conditions:**
This rule may be retired when:
1. All systems achieve maximum clarity scores
2. Zero clarity violations for 1 year
3. New contributors achieve instant understanding
4. AI operates with perfect comprehension

---

## 🏁 CONCLUSION

### **The Bottom Line:**
Every refactor should leave the system **clearer** than it found it.

### **The Contract:**
By refactoring in this repository, you agree:
1. To measure clarity impact of all changes
2. To prefer ambiguity reduction over feature addition
3. To eliminate duplication whenever possible
4. To make implicit rules explicit
5. To reduce cognitive load for all users

### **The Promise:**
A system that gets progressively clearer, simpler, and more maintainable with each change.

---

**Subtractive Clarity Compliance:** ✅ This rule itself follows subtractive clarity principles  
**Enforcement Status:** 🔄 Active - All refactors assessed against this rule  
**Mathematical Preference:** 🧮 Clarity > Features (always)

*"We don't add features to clarify—we clarify to enable features."*