# D_CORPORATE_LAW: Corporate Law

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** Delaware General Corporation Law (DGCL), Model Business
Corporation Act (MBCA), Restatement (Second) of Agency

## Description

Domain implementing corporate governance principles including fiduciary duties
(duty of care, duty of loyalty), self-dealing analysis under DGCL §144, and
corporate veil piercing (alter ego doctrine). Corporate law creates a framework
for responsible stewardship of assets entrusted to directors and officers.

## Invariants

1. **Self-Dealing Disclosure**: Related-party transactions require full disclosure
   to be valid.

2. **Disinterested Director Safe Harbor**: Approval by disinterested directors
   after full disclosure creates DGCL §144 safe harbor.

3. **Duty of Loyalty**: Directors must prioritize corporation's interests over
   personal interests.

4. **Duty of Care**: Directors must be informed before making decisions.

5. **Veil Piercing Factors**: Courts consider commingling, inadequate capitalization,
   failure to follow formalities, and other factors when determining whether to
   pierce the corporate veil.

6. **Controlling Interest**: Ownership of 50%+ shares creates controlling interest.

## Key Classes

- `FiduciaryDutyAnalyzer`: Analyzes duty of care and loyalty compliance
- `CorporateVeilAnalyzer`: Assesses veil piercing risk
- `Director`: Corporate director with potential conflicts
- `CorporateTransaction`: Transaction subject to fiduciary analysis
- `Shareholder`: Corporate shareholder with ownership percentage
- `CorporateComplianceChecker`: Comprehensive compliance validator

## Usage

```python
from fractions import Fraction
from src.domains.d_corporate_law import (
    FiduciaryDutyAnalyzer,
    Director,
    CorporateTransaction,
)

# Create conflicted director
director = Director(
    name="John Smith",
    director_id="D001",
    financial_interests={"Target Corp": Fraction(100)},
)

# Create self-dealing transaction
transaction = CorporateTransaction(
    transaction_id="T001",
    description="Acquisition of Target Corp",
    counterparty="Target Corp",
    value=Fraction(5_000_000),
    directors_involved=[director],
    disclosure_complete=True,
    approved_by_disinterested=True,
)

analyzer = FiduciaryDutyAnalyzer()
result = analyzer.check_self_dealing_compliance(transaction)

if result.get("safe_harbor"):
    print("Transaction qualifies for DGCL §144 safe harbor")
```

## Biblical Inspiration

Luke 16:10 — "Whoever can be trusted with very little can also be trusted
with much, and whoever is dishonest with very little will also be dishonest
with much."

Corporate fiduciary duty institutionalizes this principle of stewardship—
directors hold others' assets in trust and must account for their management.
The corporate form creates a structure for trustworthy aggregation of capital.

## Falsification Tests

- `F_CORP_001`: Verify undisclosed self-dealing violates duty of loyalty
- `F_CORP_002`: Verify disinterested approval creates safe harbor
- `F_CORP_003`: Verify veil piercing factors cumulative effect
- `F_CORP_004`: Verify duty of care requires informed decision
- `F_CORP_005`: Verify controlling interest at 50% threshold
