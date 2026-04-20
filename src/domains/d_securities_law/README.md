---
tags: [src, domains, d-securities-law, readme]
register: technical
---

# D_SECURITIES_LAW — Securities Law

**Layer:** 2 (Statutory)  
**Domain:** Securities Law — Securities Act 1933, Exchange Act 1934  
**CardinalStrength:** PREDICATIVE

## Overview

Implements securities regulation including:

- **Securities Act of 1933:** Registration requirements for public offerings
- **Securities Exchange Act of 1934:** Anti-fraud, insider trading, reporting
- **Rule 10b-5:** Prohibition on material misstatements and omissions
- **Section 16:** Insider short-swing profit rules
- **Regulation D:** Private placement exemptions

## Key Components

### Registration Requirements
- **Public Offerings:** Must register with SEC (Form S-1)
- **Exemptions:** Reg D (private placements), Rule 147 (intrastate)
- **Accredited Investors:** Can participate in unregistered offerings

### Insider Trading (Rule 10b-5)
- **Material Information:** Would affect investment decision
- **Nonpublic:** Not disseminated to public
- **Duty:** Breach of fiduciary duty or misappropriation
- **Scienter:** Intent to deceive

### Anti-Fraud Provisions
- **Section 10(b) and Rule 10b-5:** Broad anti-fraud authority
- **Material Misstatements:** False statements of material fact
- **Material Omissions:** Failure to disclose material facts
- **Ponzi Schemes:** Unusually consistent returns, payouts > revenue

## Usage

```python
from src.domains.d_securities_law import (
    InsiderTradingAnalyzer,
    Transaction,
    Security,
)

# Analyze potential insider trading
transaction = Transaction(
    transaction_id="T001",
    security=security,
    transaction_type=TransactionType.SALE,
    buyer="Buyer",
    seller="CEO",
    seller_is_insider=True,
    material_nonpublic_info_known=True,
)

analyzer = InsiderTradingAnalyzer()
result = analyzer.analyze_transaction(transaction)
```

## Biblical Foundation

> "The LORD detests dishonest scales, but accurate weights find favor with him."  
> — Proverbs 11:1

Securities law enforces honest dealing in capital markets, reflecting the
biblical command for honest weights and measures. Fraudulent schemes like
Ponzi schemes violate this principle.

## Files

- `implementation.py` — Core securities law logic
- `invariants.py` — Executable invariant checks (5+ checks)
- `__init__.py` — Public exports
- `README.md` — This documentation

## See Also

- Layer 2: `D_BANKING_REGULATION` — Banking/securities intersection
- Layer 1: `D_DUE_PROCESS` — Enforcement procedures
- Layer 0: `D_UDHR` — Property rights
