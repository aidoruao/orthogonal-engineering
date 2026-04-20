---
tags: [src, domains, d-intellectual-property, readme]
register: technical
---

# D_INTELLECTUAL_PROPERTY — Intellectual Property

**Layer:** 2 (Statutory)  
**Domain:** Intellectual Property — Patent, Copyright, Trademark  
**CardinalStrength:** PREDICATIVE

## Overview

Implements intellectual property law including:

- **Patent (35 U.S.C.):** Novelty, non-obviousness, infringement (all elements rule)
- **Copyright (17 U.S.C.):** Originality, substantial similarity, fair use (four factors)
- **Trademark (15 U.S.C.):** Distinctiveness, likelihood of confusion, dilution

## Key Components

### Patent Requirements
- **Novelty:** No identical prior art (35 U.S.C. §102)
- **Non-Obviousness:** Not obvious to person skilled in the art (35 U.S.C. §103)
- **Utility:** Must have specific, substantial, credible utility
- **Term:** 20 years from filing date
- **Infringement:** All elements of at least one claim must be present

### Copyright Protection
- **Originality:** Independently created + minimal creativity
- **Fixed:** Tangible medium of expression
- **Term:** Life + 70 years (individual) / 95-120 years (work for hire)
- **Infringement:** Copying + substantial similarity
- **Fair Use:** Purpose, nature, amount, market effect (17 U.S.C. §107)

### Trademark Requirements
- **Distinctiveness:** Arbitrary > suggestive > descriptive (secondary meaning) > generic (unprotectable)
- **Use in Commerce:** Interstate commerce requirement
- **No Likelihood of Confusion:** Polaroid factors
- **No Dilution:** For famous marks only

## Usage

```python
from src.domains.d_intellectual_property import (
    PatentAnalyzer,
    Invention,
    PatentClaim,
)

# Create invention
invention = Invention(
    invention_id="I001",
    title="New Device",
    inventor="Alice",
    filing_date=datetime(2024, 1, 1),
    claims=[PatentClaim(1, PatentClaimType.APPARATUS, "A device", ["A", "B", "C"])],
)

# Check novelty
analyzer = PatentAnalyzer()
result = analyzer.check_novelty(invention)
```

## Biblical Foundation

> "You shall not steal."  
> — Exodus 20:15

Intellectual property law extends the biblical prohibition against theft
to intangible creations. Just as physical property represents the fruits
of labor, creative works and inventions represent mental labor that
belongs to their creators.

## Files

- `implementation.py` — Core IP logic
- `invariants.py` — Executable invariant checks (5+ checks)
- `__init__.py` — Public exports
- `README.md` — This documentation

## See Also

- Layer 2: `D_ANTITRUST` — IP licensing and antitrust
- Layer 1: `D_TAKINGS_CLAUSE` — IP as property
- Layer 0: `D_UDHR` — Right to property (Article 17)
