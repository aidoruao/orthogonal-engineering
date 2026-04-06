# D_HOUSING_LAW — Housing Law

**Layer:** 2 (Statutory)  
**Domain:** Housing Law — Fair Housing Act, Tenant Rights, Eviction Process  
**CardinalStrength:** PREDICATIVE

## Overview

Implements housing law protections including:

- **Fair Housing Act (42 U.S.C. §3601):** Prohibits discrimination in housing based on race, color, religion, national origin, sex, familial status, and disability
- **Tenant Rights:** Implied warranty of habitability, protection from retaliation
- **Eviction Process:** Proper notice requirements, defenses, procedural protections
- **Reasonable Accommodations:** Requirements for persons with disabilities

## Key Components

### Protected Classes
- `RACE`, `COLOR`, `RELIGION`, `NATIONAL_ORIGIN`
- `SEX` (including sexual orientation and gender identity under current interpretation)
- `FAMILIAL_STATUS` (presence of children under 18)
- `DISABILITY` (physical and mental)

### Eviction Notices
- `PAY_OR_QUIT`: For nonpayment of rent (typically 3-5 days)
- `CURE_OR_QUIT`: For curable lease violations (typically 7-10 days)
- `UNCONDITIONAL_QUIT`: For serious violations (immediate or 3-5 days)
- `NOTICE_TO_QUIT`: No-cause termination (typically 30-60 days)

### Habitability Requirements
- Structural integrity
- Weather protection (roof, windows)
- Plumbing and sanitation
- Heating and electrical
- Clean water
- Extermination

## Usage

```python
from src.domains.d_housing_law import FairHousingAnalyzer, HousingDiscriminationComplaint

# Analyze potential discrimination
complaint = HousingDiscriminationComplaint(
    complaint_id="C001",
    complainant_name="Jane Doe",
    respondent_name="ABC Properties",
    protected_class=ProtectedClass.DISABILITY,
    discrimination_type=HousingDiscriminationType.REFUSAL_TO_RENT,
    description="Denied rental after requesting accommodation",
)

analyzer = FairHousingAnalyzer()
result = analyzer.analyze_discrimination_complaint(complaint)
```

## Biblical Foundation

> "Give back to them immediately their fields, vineyards, olive groves and houses..."  
> — Nehemiah 5:11

The biblical narrative of Nehemiah opposing housing oppression establishes that housing is essential to human dignity. Unjust eviction and housing discrimination violate this principle.

## Files

- `implementation.py` — Core housing law logic
- `invariants.py` — Executable invariant checks (5+ checks)
- `__init__.py` — Public exports
- `README.md` — This documentation

## See Also

- Layer 1: `D_DUE_PROCESS` — Eviction requires due process
- Layer 1: `D_EQUAL_PROTECTION` — Anti-discrimination foundations
- Layer 0: `D_UDHR` — Universal right to housing (Article 25)
