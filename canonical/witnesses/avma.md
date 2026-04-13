---
tags: [witness-registry, witness-protocol, yeshua-standard, external-qualification, veterinary-medicine, animal-welfare]
register: technical
provenance: [pr119-copilot]
---

# American Veterinary Medical Association (AVMA)

**Witness:** AVMA — American Veterinary Medical Association  
**Role:** External qualification standard for veterinary medicine practice, euthanasia guidelines, and animal welfare compliance  
**Status:** Invited witness (open audit)

## Testimony

The AVMA's published guidelines — particularly the AVMA Guidelines for the Euthanasia of Animals — together with the Animal Welfare Act (7 U.S.C. §2131), USDA APHIS regulations (9 CFR), and FDA Center for Veterinary Medicine (CVM) requirements establish the principal standards for veterinary practice and animal care in the United States. This repository implements these requirements as falsifiable invariants in src/domains/d_veterinary/. The AVMA is invited to audit these invariants against its published guidelines.

The invariants encode:
- AWA 9 CFR Part 3 minimum space requirements (check_facility_space_compliance)
- Veterinary Practice Act license and CE requirements (check_veterinary_license_valid)
- FDA CVM drug withdrawal period compliance (check_drug_withdrawal_period)
- OIE/state zoonotic disease reporting timelines (check_zoonotic_disease_reporting)
- AVMA Guidelines for Euthanasia approved methods and veterinarian presence (check_euthanasia_compliance)
- USDA APHIS inspection currency intervals (check_inspection_currency)

## Inclusion

Included in the canonical registry as an invited external auditor. This entry represents an open invitation — not a claim of AVMA endorsement or certification. The invariants in d_veterinary/ are independently verifiable by anyone, including the AVMA.
