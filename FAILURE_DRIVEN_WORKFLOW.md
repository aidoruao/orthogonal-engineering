---
tags: [failure-driven-workflow]
register: documentation
---

# FAILURE-DRIVEN DEVELOPMENT WORKFLOW
# Orthogonal Engineering - Glass Box Methodology
# Version: 1.0.0
# Date: 2026-01-20
# Methodology: Orthogonal Engineering with Popperian Falsification

## 🎯 EXECUTIVE SUMMARY

**Core Principle:** Development is driven by systematic failure discovery, documentation, and resolution rather than feature completion.

**Workflow Goal:** Create a self-correcting system where each failure improves both the implementation AND the methodology.

**Key Innovation:** Failures are not bugs to fix and forget—they are evidence of methodological integrity and opportunities for ontological refinement.

## 🔄 WORKFLOW OVERVIEW

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLAIM MAKING  │───▶│ FAILURE HUNTING │───▶│  FAILURE DOC    │
│  (Make explicit,│    │ (Actively try   │    │ (Timestamp,     │
│  falsifiable    │    │ to falsify)     │    │ hash, analyze)  │
│  claims)        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
         │                                               │
         │                                               │
         ▼                                               ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ METHODOLOGY     │◀───│  FAILURE FIX    │◀───│ ONTOLOGICAL     │
│  UPDATE         │    │ (Address root   │    │  ANALYSIS       │
│ (Refine premises│    │ causes with     │    │ (Which premises │
│ based on        │    │ audit trail)    │    │ violated?)      │
│ failures)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 PHASE 1: CLAIM MAKING (Week 1)

### Step 1.1: Explicit Claim Formulation
**Goal:** Create claims that are maximally falsifiable.

**Template:**
```
CLAIM-[ID]: [Specific, measurable claim]
FALSIFICATION TEST: [How to test if claim is false]
FALSIFICATION CONDITION: [What would constitute falsification]
CONFIDENCE: [0.0-1.0 based on evidence]
EVIDENCE: [What supports this claim]
CORRESPONDENCE: [How claim maps to reality]
```

**Example:**
```
CLAIM-DET-001: canal_refiner.py detects canals with ≥80% precision
FALSIFICATION TEST: Manual review of 100 "verified" turns
FALSIFICATION CONDITION: If precision <80% in manual review
CONFIDENCE: 0.3 (based on previous 30% precision finding)
EVIDENCE: Previous analysis showed 30% precision
CORRESPONDENCE: Precision measured against manual human labeling
```

### Step 1.2: Claim Categorization
**Categories:**
1. **Tool Performance Claims:** "Tool X works with Y accuracy"
2. **Methodological Claims:** "Methodology can detect Z type of failure"
3. **Ontological Claims:** "Premise P holds under conditions C"
4. **Implementation Claims:** "System implements specification S"

### Step 1.3: Claim Dependency Mapping
**Create dependency graph:**
- Which tools depend on which claims?
- Which methodological principles depend on which ontological premises?
- What breaks if this claim is falsified?

### Step 1.4: Git Integration
**For each claim:**
```bash
# Create claim file
echo "[Claim content]" > claims/CLAIM-[ID].md

# Commit with audit trail
git add claims/CLAIM-[ID].md
git commit -m "CLAIM-[ID]: [Brief description] - [Timestamp]"
```

## 🔍 PHASE 2: FAILURE HUNTING (Week 2)

### Step 2.1: Systematic Falsification Attempts
**Goal:** Actively try to falsify every claim.

**Methods:**
1. **Independent Verification:** Have different people/teams test same claim
2. **Boundary Testing:** Test at edge cases and extreme conditions
3. **Stress Testing:** Test under high load or adversarial conditions
4. **Correspondence Testing:** Verify outputs match real-world expectations

### Step 2.2: Failure Discovery Protocols
**Protocol A: Tool Testing**
```python
def test_tool_claim(tool_name, claim_id, test_cases):
    """
    Test if tool performs as claimed
    """
    failures = []
    for test_case in test_cases:
        try:
            result = run_tool(tool_name, test_case)
            if not claim_holds(result, claim_id):
                failures.append({
                    'test_case': test_case,
                    'result': result,
                    'expected': claim_expectation(claim_id)
                })
        except Exception as e:
            failures.append({
                'test_case': test_case,
                'error': str(e),
                'type': 'exception'
            })
    return failures
```

**Protocol B: Methodological Testing**
```python
def test_methodology_claim(claim_id, scenarios):
    """
    Test if methodology works as claimed
    """
    failures = []
    for scenario in scenarios:
        # Can methodology detect known problems?
        detection_result = methodology.apply(scenario)
        if not detection_matches_claim(detection_result, claim_id):
            failures.append({
                'scenario': scenario,
                'detection': detection_result,
                'expected': claim_expectation(claim_id)
            })
    return failures
```

### Step 2.3: Failure Prioritization
**Scoring System:**
- **Severity (1-5):** How bad is the failure?
- **Impact (1-5):** How many claims/tools affected?
- **Reproducibility (1-5):** How easy to reproduce?
- **Urgency (1-5):** How soon must it be fixed?

**Priority = (Severity × Impact × Urgency) / Reproducibility**

### Step 2.4: Failure Evidence Collection
**Required Evidence:**
1. **Inputs:** Exactly what was tested
2. **Outputs:** Exactly what happened
3. **Environment:** System state during test
4. **Expected vs Actual:** Clear comparison
5. **Reproduction Steps:** Step-by-step instructions

## 📝 PHASE 3: FAILURE DOCUMENTATION (Week 3)

### Step 3.1: Failure Entry Creation
**Template:**
```yaml
failure_id: FAILURE-[YYYYMMDD]-[SEQ]
title: [Descriptive title]
claim_affected: CLAIM-[ID]
discovered_at: [ISO timestamp]
discovered_by: [Person/team]
severity: [critical|high|medium|low|info]
category: [detector|correspondence|statistical|reproducibility|methodology]

description: |
  [Detailed description of what failed]

evidence:
  - type: [test_result|exception|log|screenshot]
    content: [Actual evidence]
    hash: [SHA256 of content]
    timestamp: [When collected]

reproduction_steps:
  - [Step 1]
  - [Step 2]
  - [Step 3]

ontological_analysis:
  premises_violated:
    - [Premise 1]
    - [Premise 2]
  violation_types:
    - [direct|indirect|potential]
  methodology_implications:
    - [Implication 1]
    - [Implication 2]

impact_analysis:
  affected_claims:
    - [Claim 1]
    - [Claim 2]
  affected_tools:
    - [Tool 1]
    - [Tool 2]
  user_impact: [How this affects users]
  timeline_impact: [How this affects schedule]

resolution:
  status: [open|in_progress|resolved|wont_fix]
  required_actions:
    - [Action 1]
    - [Action 2]
  priority: [immediate|high|medium|low]
  assigned_to: [Person/team]
  target_date: [YYYY-MM-DD]
  verification_method: [How to verify fix]

falsifiable_claims_generated:
  - [New claim about the failure]
  - [New claim about the fix]

metadata:
  created_at: [ISO timestamp]
  updated_at: [ISO timestamp]
  hash: [SHA256 of entire entry]
  git_commit: [Commit hash where documented]
```

### Step 3.2: Ontological Premise Analysis
**For each failure, analyze:**
1. **Which premises violated?** (falsifiability, correspondence, transparency, etc.)
2. **How violated?** (direct contradiction, indirect implication, potential risk)
3. **Methodological implications:** What does this mean for the methodology?
4. **Premise refinement needed?** Do premises need updating based on this failure?

### Step 3.3: Failure Hash Chain
**Create verifiable audit trail:**
```python
def create_failure_hash_chain(failure_entry, previous_hash):
    """
    Create cryptographic hash chain for failures
    """
    current_hash = sha256(failure_entry)
    chain_entry = {
        'failure_id': failure_entry['failure_id'],
        'timestamp': failure_entry['created_at'],
        'hash': current_hash,
        'previous_hash': previous_hash,
        'next_hash': None  # Will be filled by next failure
    }
    return chain_entry, current_hash
```

### Step 3.4: Git Integration for Failures
```bash
# Create failure file
echo "[Failure entry]" > failures/FAILURE-[ID].yaml

# Add to failure index
echo "- FAILURE-[ID]: [Brief description]" >> failures/INDEX.md

# Commit with audit trail
git add failures/FAILURE-[ID].yaml failures/INDEX.md
git commit -m "FAILURE-[ID]: [Brief description] - [Timestamp] - [Hash prefix]"
```

## 🛠️ PHASE 4: FAILURE RESOLUTION (Week 4)

### Step 4.1: Root Cause Analysis
**Five Whys Technique:**
1. Why did the failure occur? [First reason]
2. Why did that happen? [Deeper reason]
3. Why did that happen? [Systemic reason]
4. Why did that happen? [Methodological reason]
5. Why did that happen? [Ontological reason]

**Fishbone Diagram Categories:**
- Tools
- Methodology
- People
- Environment
- Data
- Process

### Step 4.2: Fix Design with Audit Trail
**Template for fix design:**
```yaml
fix_id: FIX-[FAILURE-ID]-[SEQ]
failure_id: FAILURE-[ID]
designed_at: [ISO timestamp]
designed_by: [Person/team]

root_cause: [Identified root cause]
fix_strategy: [How fix addresses root cause]

changes_required:
  code_changes:
    - [File 1: Change description]
    - [File 2: Change description]
  documentation_changes:
    - [Document 1: Update description]
    - [Document 2: Update description]
  methodological_changes:
    - [Methodology update 1]
    - [Methodology update 2]

audit_trail_requirements:
  - [What to log before change]
  - [What to log during change]
  - [What to log after change]

verification_plan:
  - [Test 1 to verify fix]
  - [Test 2 to verify fix]
  - [Regression test to ensure no new issues]

rollback_plan:
  - [How to revert if fix causes problems]
  - [Checkpoint to roll back to]
```

### Step 4.3: Implementation with Glass Box Principles
**Implementation Protocol:**
1. **Pre-implementation snapshot:** Hash all affected files
2. **Change documentation:** Document each change with reason
3. **Intermediate verification:** Test after each significant change
4. **Post-implementation snapshot:** Hash all changed files
5. **Audit trail creation:** Log entire implementation process

### Step 4.4: Verification and Validation
**Verification Protocol:**
```python
def verify_fix(failure_id, fix_id):
    """
    Verify that fix actually resolves the failure
    """
    # 1. Reproduce original failure
    original_failure = reproduce_failure(failure_id)
    
    # 2. Apply fix
    apply_fix(fix_id)
    
    # 3. Test if failure still occurs
    test_result = run_original_test(original_failure['test_case'])
    
    # 4. Check for regressions
    regression_results = run_regression_tests()
    
    # 5. Verify audit trail
    audit_trail_valid = verify_audit_trail(fix_id)
    
    return {
        'failure_resolved': not test_result['failed'],
        'regressions_found': regression_results['failures'],
        'audit_trail_valid': audit_trail_valid,
        'verification_hash': sha256_all_results()
    }
```

### Step 4.5: Fix Documentation
**Update failure entry:**
```yaml
resolution:
  status: resolved
  resolved_at: [ISO timestamp]
  resolved_by: [Person/team]
  fix_applied: FIX-[ID]
  verification_results:
    failure_resolved: true/false
    regressions_found: [list or none]
    audit_trail_valid: true/false
    verification_hash: [SHA256]
  lessons_learned:
    - [Lesson 1]
    - [Lesson 2]
```

## 🔄 PHASE 5: METHODOLOGY UPDATE (Week 5)

### Step 5.1: Failure Pattern Analysis
**Analyze failure patterns:**
- **Temporal patterns:** When do failures occur?
- **Categorical patterns:** What types of failures are most common?
- **Root cause patterns:** What are the most common root causes?
- **Resolution patterns:** What fixes work best?

### Step 5.2: Ontological Premise Refinement
**For each premise violated by failures:**
1. **Is premise still valid?** Does evidence support it?
2. **Does premise need refinement?** More precise wording needed?
3. **Does premise need additional evidence?** More support needed?
4. **Should premise be removed?** No longer supported?

**Premise update template:**
```yaml
premise_id: PREMISE-[ID]
version: [New version number]
previous_version: [Old version number]
updated_at: [ISO timestamp]
updated_by: [Person/team]

change_reason: |
  [Why premise needed updating]
  [Reference to failures that prompted update]

old_statement: [Previous premise statement]
new_statement: [Updated premise statement]

changes_made:
  - [Change 1]
  - [Change 2]

evidence_supporting_change:
  - [Failure 1 that prompted change]
  - [Failure 2 that prompted change]
  - [New evidence supporting change]

falsification_tests_updated:
  - [Test 1 updated]
  - [Test 2 updated]
```

### Step 5.3: Tool Improvement Based on Failures
**For each tool with failures:**
1. **Failure analysis:** What patterns in tool failures?
2. **Redesign requirements:** What needs to change?
3. **Validation requirements:** How to prove redesign works?
4. **Documentation updates:** What needs to be documented?

### Step 5.4: Workflow Refinement
**Based on failure resolution experience:**
1. **What worked well?** Keep these practices
2. **What didn't work?** Improve or remove these
3. **What was missing?** Add to workflow
4. **What was inefficient?** Streamline

### Step 5.5: Knowledge Base Update
**Create/update:**
1. **Failure database:** All failures with searchable metadata
2. **Solution patterns:** Common fixes for common failures
3. **Prevention guidelines:** How to avoid similar failures
4. **Verification templates:** Reusable verification protocols

## 📊 PHASE 6: METRICS AND REPORTING (Continuous)

### Step 6.1: Failure Metrics Dashboard
**Key Metrics:**
- **Failure Discovery Rate:** Failures found per week
- **Time to Document:** Average time from discovery to documentation
- **Resolution Rate:** Percentage of failures resolved
- **Resolution Time:** Average time to resolve failures
- **Reopened Rate:** Percentage of resolved failures that reopen
- **Premise Violation Rate:** Failures per ontological premise

### Step 6.2: Methodology Health Score
**Calculation:**
```
Health Score = 
  (Falsifiability Score × 0.3) +
  (Correspondence Score × 0.25) +
  (Transparency Score × 0.2) +
  (Reproducibility Score × 0.15) +
  (Tool Validation Score × 0.1)
```

**Where each score (0.0-1.0) is based on:**
- Number of successful falsifications
- Correspondence validation results
- Transparency audit results
- Reproduction success rate
- Tool validation results

### Step 6.3: Regular Reporting
**Weekly Report Template:**
```markdown
# Failure-Driven Development Report - Week [X]

## Executive Summary
- Total failures: [X]
- Critical failures: [X]
- Resolved this week: [X]
- Methodology health score: [X]/1.0

## Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

## Critical Issues
- [Issue 1]
- [Issue 2]

## Methodology Updates
- [Update 1]
- [Update 2]

## Next Week Focus
1. [Focus area 1]
2. [Focus area 2]
```

### Step 6.4: Stakeholder Communication
**Different reports for different stakeholders:**
- **Technical team:** Detailed failure analysis and fixes
- **Methodology team:** Ontological premise updates
- **Management:** High-level metrics and trends
- **Community:** Public failure documentation (transparency)

## 🚀 IMPLEMENTATION CHECKLIST

### Setup Phase:
- [ ] Create claims directory structure
- [ ] Create failures directory structure
- [ ] Set up failure hash chain
- [ ] Configure git hooks for audit trail
- [ ] Set up metrics dashboard

### First Cycle:
- [ ] Make 10 explicit, falsifiable claims
- [ ] Attempt to falsify all 10 claims
- [ ] Document all failures found
- [ ] Resolve at least 3 failures
- [ ] Update methodology based on findings

### Ongoing