---
tags: [src, domains, d-banking-regulation, readme]
register: technical
---

# D_BANKING_REGULATION — Banking Regulation

**Layer:** 2 (Statutory)  
**Domain:** Banking Regulation — Dodd-Frank, FDIC, Capital Requirements  
**CardinalStrength:** PREDICATIVE

## Overview

Implements banking regulation including:

- **Capital Adequacy:** Basel III Tier 1 and Total Capital ratios
- **FDIC Insurance:** Deposit insurance coverage limits
- **Reserve Requirements:** Federal Reserve requirements
- **Usury Limits:** State interest rate caps
- **Ability-to-Repay:** TILA/Reg Z compliance

## Key Components

### Capital Ratios (Basel III)
- **Tier 1 Ratio:** Minimum 6% of risk-weighted assets
- **Total Capital Ratio:** Minimum 8% of risk-weighted assets
- **Leverage Ratio:** Minimum 4% of total assets
- **Conservation Buffer:** Additional 2.5%

### FDIC Insurance
- **Standard Coverage:** $250,000 per depositor, per institution
- **Joint Accounts:** $250,000 per co-owner
- **Revocable Trusts:** $250,000 per beneficiary (up to 5)

### Reserve Requirements
- **Requirement:** Varies by institution type (0-10%)
- **Vault Cash + Fed Reserves:** Count toward requirement

## Usage

```python
from src.domains.d_banking_regulation import Bank, CapitalAdequacyCalculator

# Create bank
bank = Bank(
    bank_id="B001",
    bank_name="Community Bank",
    charter_type="national",
    tier1_capital=Fraction(10_000_000),
    tier2_capital=Fraction(2_000_000),
    total_assets=Fraction(100_000_000),
    total_deposits=Fraction(80_000_000),
    insured_deposits=Fraction(75_000_000),
    vault_cash=Fraction(5_000_000),
    reserves_at_fed=Fraction(5_000_000),
)

# Check capital adequacy
calc = CapitalAdequacyCalculator()
result = calc.check_capital_adequacy(bank)
```

## Biblical Foundation

> "If you lend money to one of my people among you who is needy,
> do not treat it like a business deal; charge no interest."  
> — Exodus 22:25

The biblical prohibition on usury (charging interest to the needy)
establishes limits on banking practices that exploit vulnerability.
Modern banking regulation reflects this principle through usury caps
and consumer lending protections.

## Files

- `implementation.py` — Core banking regulation logic
- `invariants.py` — Executable invariant checks (5+ checks)
- `__init__.py` — Public exports
- `README.md` — This documentation

## See Also

- Layer 1: `D_DUE_PROCESS` — Banking exam procedures
- Layer 1: `D_TAKINGS_CLAUSE` — Regulatory takings analysis
- Layer 2: `D_CONSUMER_PROTECTION` — Lending protections
