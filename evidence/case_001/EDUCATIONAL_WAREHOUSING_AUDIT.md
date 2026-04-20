---
tags: [evidence, case-001, educational-warehousing-audit]
register: audit
---

# EDUCATIONAL WAREHOUSING AUDIT — CASE_001

**Case ID:** CASE_001_SELECTIVE_MUTISM_WAREHOUSING
**Pipeline:** IA-CYPHER-0003
**Patterns:** S-26 EDUCATIONAL_WAREHOUSING · S-27 EDUCATIONAL_NEGLECT · S-28 ADAPTIVE_INVISIBILITY · S-29 INSTITUTIONAL_ERASURE (compound)

---

## Pattern Analysis

### S-26 EDUCATIONAL_WAREHOUSING

| Field | Value |
|---|---|
| Actor | School District / CPS / DCF |
| Severity | SYSTEMIC |
| Predicate | WAREHOUSED(child) — see formal spec below |

**Formal detection predicate:**

```
Let E = enrollment_start_date
Let C = condition_documentation_date
Let I = {IEP, 504, speech_referral, behavioral_plan}

WAREHOUSED(child) :=
    (E is defined) ∧
    (C ≤ E ∨ C is documented during enrollment) ∧
    (∀ i ∈ I : i = NULL ∨ i.start_date - E > 30 days) ∧
    (district.enrollment_metric(child) = COMPLIANT)

falsifies_if: ∃ i ∈ I : (i ≠ NULL) ∧ (i.start_date - E ≤ 30) ∧ (i.progress_met = TRUE)
```

**Applied to Case_001:**
- Enrollment: Okaloosa County school district (multiple semesters)
- Condition documentation: CPS case 2013-278708 (selective mutism observable)
- IEP/504/speech referral: absent from record
- District enrollment metric: COMPLIANT
- **Result: WAREHOUSED(child) = TRUE**

---

### S-27 EDUCATIONAL_NEGLECT

| Field | Value |
|---|---|
| Actor | School District / Teacher / Administration |
| Severity | CRITICAL |
| Predicate | NEGLECTED(child) — see formal spec below |

**Formal detection predicate:**

```
Let D = condition_known_date (min of CPS_report_date, teacher_observation_date, parent_disclosure_date)
Let R = referral_initiation_date
Let T_statutory = 60 days (IDEA) or district policy timeline

NEGLECTED(child) :=
    (D is defined) ∧
    (R = NULL ∨ R - D > T_statutory) ∧
    (child.condition ∈ {selective_mutism, speech_disorder, anxiety_disorder, ...})

falsifies_if: (R ≠ NULL) ∧ (R - D ≤ T_statutory) ∧ (service_plan.delivered = TRUE)
```

**Applied to Case_001:**
- Condition known: CPS case 2013-278708 open date (teacher observable non-verbal behavior)
- IDEA referral: no record of initiation
- Statutory deadline: 60 days from condition_known_date
- **Result: NEGLECTED(child) = TRUE**

---

### S-28 ADAPTIVE_INVISIBILITY

| Field | Value |
|---|---|
| Actor | Multi-Agency (School + CPS + Family) |
| Severity | SYSTEMIC |
| Predicate | INVISIBLE(child) — see formal spec below |

**Formal detection predicate:**

```
Let B = behavioral_incident_count
Let A = academic_flag_count
Let G = social_engagement_metric
Let S = service_record

INVISIBLE(child) :=
    (B = 0) ∧ (A = 0) ∧ (G < engagement_threshold) ∧ (S = NULL) ∧
    (child.condition ∈ ADAPTIVE_CONDITIONS)

# Standard institutional filter:
#   NEEDS_HELP(child) := (B > 0) ∨ (A > 0)
# Therefore: INVISIBLE(child) → ¬NEEDS_HELP(child) under standard filter.
# S-28 := the institution's detection function is structurally blind to the condition.

falsifies_if: institution.screening_protocol includes
    SILENT_FLAG(child) := (B = 0) ∧ (A = 0) ∧ (G < threshold) → REFER(child)
```

**Applied to Case_001:**
- Behavioral incidents: zero (selectively mute child does not disrupt)
- Academic flags: zero (passes via non-verbal compliance)
- Social engagement: below threshold (non-verbal, withdrawn)
- Service record: NULL
- Institutional conclusion: no intervention needed
- **Result: INVISIBLE(child) = TRUE**

---

### S-29 INSTITUTIONAL_ERASURE (Compound)

```
S-29 := S-26 ∧ S-27 ∧ S-28

ERASED(child) :=
    WAREHOUSED(child) ∧ NEGLECTED(child) ∧ INVISIBLE(child)
```

**Applied to Case_001:**
- WAREHOUSED(child) = TRUE (S-26 above)
- NEGLECTED(child) = TRUE (S-27 above)
- INVISIBLE(child) = TRUE (S-28 above)
- **Result: ERASED(child) = TRUE**

The institution's own records show a compliant, enrolled child while the actual child received no services. This is the educational analogue of S-19 EPISTEMIC_FATIGUE in the law-enforcement domain.

---

## Cross-Reference to Bowers/McNeil (PR #81)

| PR #82 Pattern | PR #81 Analogue | Structural Mapping |
|---|---|---|
| S-26 EDUCATIONAL_WAREHOUSING | S-12 LOSSY_COMPRESSION | Both preserve a compliance signal while dropping material facts |
| S-27 EDUCATIONAL_NEGLECT | S-11 STRATEGIC_IGNORANCE | Both avoid intake that would trigger institutional duties |
| S-28 ADAPTIVE_INVISIBILITY | S-13 PERFORMED_IMPUNITY | Both produce self-concealing failure modes |
| S-29 INSTITUTIONAL_ERASURE | S-19 EPISTEMIC_FATIGUE | Both are compound effects where architecture defeats truth-seeking |
| CPS case 2013-278708 | SAO memo (Bowers/McNeil) | Both are institutional records whose correspondence to reality is falsifiable |
