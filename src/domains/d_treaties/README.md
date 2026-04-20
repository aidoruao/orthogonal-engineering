---
tags: [src, domains, d-treaties, readme]
register: technical
---

# D_TREATIES: Treaty Obligations

**Layer:** 0 (Supranational)  
**CardinalStrength:** MAHLO  
**Authority:** Vienna Convention on the Law of Treaties (1969)

## Description

Domain implementing treaty registry, supremacy clause resolution, and
withdrawal procedures per international law.

## Invariants

1. **Supremacy**: Ratified treaty provisions override conflicting domestic statute.
2. **Notice Period**: Treaty withdrawal requires documented notice period.

## Key Classes

- `TreatyRegistry`: Registry of treaties and their status
- `RatificationRecord`: Record of treaty ratification
- `WithdrawalNotice`: Notice of treaty withdrawal

## Usage

```python
from src.domains.d_treaties import TreatyRegistry

registry = TreatyRegistry()
registry.register_treaty("Geneva Conventions", signed_date, "PL 116-1")
registry.ratify_treaty("Geneva Conventions", ratified_date)

result = registry.check_supremacy(
    treaty_name="Geneva Conventions",
    domestic_law_name="Military Act",
    conflict_description="Conflict description",
)
```

## Biblical Inspiration

2 Kings 23:3 — King Josiah made a covenant "to keep his commandments...
with all his heart and all his soul." Treaties bind the nation.
