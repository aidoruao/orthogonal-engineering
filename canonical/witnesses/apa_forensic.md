---
tags: [witness-registry, witness-protocol, yeshua-standard, external-qualification, forensic-psychology, expert-testimony]
register: technical
provenance: [pr119-copilot]
---

# APA Division 41 — American Psychology-Law Society (Forensic Psychology)

**Witness:** APA — American Psychological Association, Division 41 (American Psychology-Law Society)  
**Role:** External qualification standard for forensic psychology evaluations, expert testimony admissibility, and civil commitment review  
**Status:** Invited witness (open audit)

## Testimony

The APA Specialty Guidelines for Forensic Psychology (2013), combined with landmark U.S. Supreme Court standards — Daubert v. Merrell Dow Pharmaceuticals (509 U.S. 579, 1993), Dusky v. United States (362 U.S. 402, 1960), Jackson v. Indiana (406 U.S. 715, 1972), and O'Connor v. Donaldson (422 U.S. 563, 1975) — establish the principal requirements for forensic psychological evaluation, expert testimony admissibility, and civil commitment due process. This repository implements these requirements as falsifiable invariants in src/domains/d_forensic_psychology/. The APA is invited to audit these invariants against its published specialty guidelines.

The invariants encode:
- Dusky competency-to-stand-trial standard: factual and rational understanding + ability to assist counsel (check_competency_to_stand_trial)
- Daubert four-factor admissibility test for expert psychological testimony (check_daubert_admissibility)
- APA Specialty Guidelines evaluator licensing and board-certification requirements (check_evaluator_qualifications)
- Jackson v. Indiana periodic review requirements for civil commitment (check_civil_commitment_review)
- Actuarial risk assessment instrument validation standards (AUC, inter-rater reliability, population match) (check_risk_assessment_validity)
- O'Connor v. Donaldson least-restrictive-alternative due process requirement (check_least_restrictive_alternative)

## Inclusion

Included in the canonical registry as an invited external auditor. This entry represents an open invitation — not a claim of APA endorsement or certification. The invariants in d_forensic_psychology/ are independently verifiable by anyone, including the APA.
