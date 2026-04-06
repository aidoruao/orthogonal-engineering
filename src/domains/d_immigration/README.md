# D_IMMIGRATION: Immigration Law

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** Immigration and Nationality Act (INA) 8 U.S.C. §1101 et seq.,
8 CFR (Code of Federal Regulations)

## Description

Domain implementing immigration law including visa preference categories,
asylum and refugee analysis, removal defense, and due process protections.
Immigration law balances sovereign control over borders with humanitarian
obligations and family unity.

**Layer 1 Link**: Due process protections in removal proceedings connect to
constitutional due process guarantees (Fifth Amendment).

## Invariants

1. **Protected Nexus Requirement**: Asylum requires nexus to race, religion,
   nationality, political opinion, or particular social group.

2. **One-Year Filing Deadline**: Asylum applications must be filed within
   one year of arrival (with exceptions for changed circumstances).

3. **Visa Allocations**: Family-sponsored (226,000/year) and employment-based
   (140,000/year) visas have statutory limits.

4. **Per-Country Limit**: No country may receive more than 7% of total visas
   in a category (preventing monopolization).

5. **Cancellation Requirements**: Non-LPR cancellation requires 10 years
   continuous physical presence, good moral character, and exceptional hardship.

6. **Due Process in Removal**: Aliens in removal proceedings have right to
   hearing, counsel (at own expense), and appeal.

7. **Family-Based Categories**: Immediate relatives and family preference
   categories recognized as family-based.

## Key Classes

- `VisaPreferenceSystem`: Manages visa allocations and priority dates
- `AsylumAnalyzer`: Evaluates asylum claim eligibility
- `RemovalDefenseAnalyzer`: Analyzes cancellation and other defenses
- `ImmigrationComplianceChecker`: Comprehensive compliance validator
- `Alien`: Non-citizen with admission status
- `VisaApplication`: Application for immigration benefit
- `AsylumClaim`: Asylum or withholding claim

## Usage

```python
from datetime import date
from src.domains.d_immigration import (
    AsylumAnalyzer,
    Alien,
    AsylumClaim,
    AdmissionClass,
)

# Create asylum claimant
alien = Alien(
    name="Asylum Seeker",
    alien_id="A001",
    nationality="Oppressia",
    date_of_birth=date(1990, 1, 1),
    date_of_entry=date(2023, 3, 15),
)

# Create asylum claim
claim = AsylumClaim(
    claimant=alien,
    claim_date=date(2023, 8, 1),  # Within 1 year
    feared_country="Oppressia",
)

claim.add_persecution_claim(
    harm="Imprisonment and torture",
    nexus="political opinion",
    government_involvement=True,
)

analyzer = AsylumAnalyzer()
result = analyzer.analyze_asylum_eligibility(claim)

print(f"Eligible: {result['eligible']}")
print(f"Protected nexus: {claim.has_protected_nexus()}")
```

## Biblical Inspiration

Leviticus 19:34 — "The foreigner residing among you must be treated as
your native-born. Love them as yourself, for you were foreigners in Egypt."

Immigration law reflects this command to welcome the stranger, balanced with
legitimate sovereign interests. The asylum system specifically embodies the
obligation to protect those fleeing persecution—modern implementation of
ancient cities of refuge.

## Falsification Tests

- `F_IMMIGRATION_001`: Verify asylum requires protected nexus
- `F_IMMIGRATION_002`: Verify one-year filing deadline enforced
- `F_IMMIGRATION_003`: Verify per-country limit calculation
- `F_IMMIGRATION_004`: Verify cancellation presence requirements
- `F_IMMIGRATION_005`: Verify due process rights in removal
