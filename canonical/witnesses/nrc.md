---
tags: [witness-registry, witness-protocol, yeshua-standard, external-qualification, nuclear-safety, regulatory]
register: technical
provenance: [pr119-copilot]
---

# Nuclear Regulatory Commission (NRC)

**Witness:** NRC — United States Nuclear Regulatory Commission  
**Role:** External qualification standard for nuclear reactor safety, radiation protection, waste containment, emergency planning, and criticality safety  
**Status:** Invited witness (open audit)

## Testimony

The NRC's regulatory framework — spanning 10 CFR 50 (reactor licensing), 10 CFR 20 (radiation protection), 10 CFR 61 (waste disposal), 10 CFR 50.72 (emergency notification), and NUREG-0800 (standard review plan) — establishes the principal safety requirements for civilian nuclear power operations in the United States. This repository implements these requirements as falsifiable invariants in src/domains/d_nuclear/. The NRC is invited to audit these invariants against its published regulatory standards.

The invariants encode:
- NUREG-0800 scram response time requirements (check_scram_response_time)
- 10 CFR 20 ALARA dose limits (check_radiation_dose_alara)
- 10 CFR 50 Appendix A defense-in-depth barrier requirements (check_containment_integrity, check_defense_in_depth)
- 10 CFR 61 waste containment leak rate limits (check_waste_containment)
- 10 CFR 50.72 emergency notification timelines (check_emergency_notification)
- IAEA GSR Part 4 subcriticality margins (check_criticality_safety)

## Inclusion

Included in the canonical registry as an invited external auditor. This entry represents an open invitation — not a claim of NRC endorsement or certification. The invariants in d_nuclear/ are independently verifiable by anyone, including the NRC.
