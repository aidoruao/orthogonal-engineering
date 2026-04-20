---
tags: [evidence, case-001, invariant-registry]
register: audit
---

# INVARIANT REGISTRY — CASE_001 SELECTIVE MUTISM WAREHOUSING

**Case ID:** CASE_001_SELECTIVE_MUTISM_WAREHOUSING
**Pipeline:** IA-CYPHER-0003
**Primary Source SHA-256:** `50b3f2fb5a52c2d52e674a99d865213a90f3ebc92418f294697ef66912b6133d`
**Source File:** CPS_2013_278708.pdf (original: CFNetworkDownload_E8DLNc.pdf)

---

## Notation

An invariant is a fact extracted from a primary source whose truth value is determined by the source document itself, not by subsequent interpretation. Each invariant is falsifiable: a stated condition is given under which the invariant would be false.

---

## INV-001

**Fact:** A CPS case numbered 2013-278708 was opened in Okaloosa County, Florida.
**Source:** CPS_2013_278708.pdf (SHA-256: `50b3f2fb5a52c2d52e674a99d865213a90f3ebc92418f294697ef66912b6133d`)
**Falsifies_if:** No CPS case with this number exists in Okaloosa County DCF records.

---

## INV-002

**Fact:** The case involves a child with selective mutism enrolled in the Okaloosa County school district.
**Source:** CPS_2013_278708.pdf
**Falsifies_if:** The CPS record contains no reference to selective mutism or observable non-verbal behavior.

---

## INV-003

**Fact:** The CPS record predates or coincides with any IEP, 504 plan, or speech-language referral in the child's school record.
**Source:** CPS_2013_278708.pdf
**Falsifies_if:** School records show an IEP, 504, or speech-language referral initiated within 30 days of enrollment and prior to or concurrent with the CPS case open date.

---

## INV-004

**Fact:** The school district reported 100% enrollment compliance for the child while no individualized educational services matched to selective mutism were delivered.
**Source:** CPS_2013_278708.pdf; absence of IEP/504 in case record
**Falsifies_if:** School enrollment record is accompanied by an active IEP or 504 plan with documented selective mutism interventions.

---

## INV-005 (Compound — S-29)

**Fact:** The conjunction of INV-001 through INV-004 satisfies the ERASED(child) predicate: the child was enrolled (S-26), received no mandated services (S-27), and the adaptive behavior prevented detection (S-28).
**Source:** CPS_2013_278708.pdf; Okaloosa County enrollment records (absence of service record)
**Falsifies_if:** Any one of INV-003 or INV-004 is falsified.
