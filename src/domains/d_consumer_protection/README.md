# D_CONSUMER_PROTECTION — Consumer Protection

**Layer:** 2 (Statutory)  
**Domain:** Consumer Protection — FTC Act, TILA, Magnuson-Moss  
**CardinalStrength:** PREDICATIVE

## Overview

Implements consumer protection law including:

- **FTC Act §5:** Prohibition on unfair or deceptive acts or practices
- **TILA (Truth in Lending Act):** Credit disclosure requirements
- **Magnuson-Moss Warranty Act:** Warranty standards and enforcement
- **Cooling-Off Rule:** 3-day right to cancel door-to-door sales

## Key Components

### Deceptive Practices (FTC Act §5)
Deceptive: Material representation, omission, or practice likely to mislead reasonable consumer

**Common Violations:**
- False advertising claims
- Bait-and-switch tactics
- Hidden fees and terms
- Fake testimonials
- Sale of recalled products

### TILA Disclosures (15 U.S.C. §1601)
Required for credit transactions:
- Annual Percentage Rate (APR)
- Finance charge
- Amount financed
- Total of payments
- Payment schedule

### Warranty Types (Magnuson-Moss)
- **Full Warranty:** Meets federal minimum standards
- **Limited Warranty:** Specified coverage limitations
- **Implied Warranty of Merchantability:** UCC §2-314 (unless disclaimed)
- **Implied Warranty of Fitness:** UCC §2-315

## Usage

```python
from src.domains.d_consumer_protection import (
    DeceptivePracticeAnalyzer,
    ConsumerTransaction,
    Product,
)

# Create transaction
product = Product(
    product_id="P001",
    name="Electronics",
    manufacturer="TechCorp",
    category="electronics",
    msrp=Fraction(999),
)

transaction = ConsumerTransaction(
    transaction_id="T001",
    consumer_name="Jane Doe",
    product=product,
    agreed_price=Fraction(999),
    final_price=Fraction(1099),  # Hidden fees!
)

# Analyze for deceptive practices
analyzer = DeceptivePracticeAnalyzer()
result = analyzer.analyze_transaction(transaction)
```

## Biblical Foundation

> "Do not use dishonest standards when measuring length, weight or quantity.
> Use honest scales and honest weights... I am the LORD your God."  
> — Leviticus 19:35-36

Consumer protection law reflects the biblical command for honest dealing
in commerce. Deceptive practices violate this principle by using "dishonest
scales" in modern forms—hidden fees, false claims, and misleading terms.

## Files

- `implementation.py` — Core consumer protection logic
- `invariants.py` — Executable invariant checks (5+ checks)
- `__init__.py` — Public exports
- `README.md` — This documentation

## See Also

- Layer 2: `D_BANKING_REGULATION` — Lending protections
- Layer 1: `D_DUE_PROCESS` — Consumer hearing rights
- Layer 0: `D_UDHR` — Consumer rights (Article 25)
