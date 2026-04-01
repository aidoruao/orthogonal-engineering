# TIMELINE — CASE_001 SELECTIVE MUTISM WAREHOUSING

**Case ID:** CASE_001_SELECTIVE_MUTISM_WAREHOUSING
**Pipeline:** IA-CYPHER-0003
**Primary Source:** CPS_2013_278708.pdf (SHA-256: `50b3f2fb5a52c2d52e674a99d865213a90f3ebc92418f294697ef66912b6133d`)

---

## Temporal Sequence

| Event | Date/Period | Source | Pattern Triggered |
|---|---|---|---|
| CPS case 2013-278708 opened | 2013 | CPS_2013_278708.pdf | INV-001 |
| Child enrolled in Okaloosa County school | On or before CPS open date | Enrollment record | S-26 |
| Selective mutism observable / condition known | On or before CPS open date | CPS_2013_278708.pdf; teacher observation | S-27 (D defined) |
| IDEA statutory referral window opens | = condition_known_date | IDEA (60-day window) | S-27 clock starts |
| IDEA referral deadline | condition_known_date + 60 days | IDEA | S-27 clock expires |
| Actual IDEA referral | NULL — no record | Absence of service record | NEGLECTED(child) = TRUE |
| IEP / 504 / speech-language plan | NULL — no record | Absence of service record | WAREHOUSED(child) = TRUE |
| Continued enrollment (multiple semesters) | 2013 onward | Enrollment record | S-26 persists |
| Institution concludes no intervention needed | Implicit in zero-incident record | Behavioral incident log = 0 | INVISIBLE(child) = TRUE |
| CPS PDF uploaded to repository | 2026-04-01 | CFNetworkDownload_E8DLNc.pdf → CPS_2013_278708.pdf | Hash anchor established |

---

## Hash Anchors

| Document | SHA-256 | Anchors |
|---|---|---|
| CPS_2013_278708.pdf | `50b3f2fb5a52c2d52e674a99d865213a90f3ebc92418f294697ef66912b6133d` | INV-001, INV-002, INV-003, INV-004 |

---

## Warehousing Gap Metric

```
warehousing_gap := first_service_date - enrollment_start_date

# Applied to Case_001:
# first_service_date = NULL (no service record)
# warehousing_gap = ∞ (unbounded)
# Threshold: > 30 days → flag
# Result: FLAGGED (warehousing_gap = NULL → treated as > 30 days)
```
