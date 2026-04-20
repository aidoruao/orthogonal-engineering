---
tags: [src, domains, d-diplomatic, readme]
register: technical
---

# D_DIPLOMATIC: Diplomatic Law

**Layer:** 0 (Supranational)  
**CardinalStrength:** MAHLO  
**Authority:** Vienna Convention on Diplomatic Relations (1961)

## Description

Domain implementing diplomatic immunity, persona non grata declarations, and
Vienna Convention compliance checking.

## Invariants

1. **Diplomatic Immunity**: Registered diplomats have immunity for actions within
their declared immunity scope.

2. **Persona Non Grata Validity**: PNG declarations require a valid reason and
departure deadline must be after declaration date.

3. **Immunity Scope Lookup**: Law can accurately check immunity by diplomat name
and action type.

## Key Classes

- `DiplomaticLaw`: Main registry and checker for diplomatic relations
- `Diplomat`: Represents a diplomat with immunity scope
- `PersonaNonGrata`: Persona non grata declaration record

## Usage

```python
from src.domains.d_diplomatic import DiplomaticLaw, Diplomat

law = DiplomaticLaw()

# Register a diplomat
diplomat = Diplomat(
    name="Ambassador Smith",
    country="Exampleland",
    rank="Ambassador",
    immunity_scope=["official_acts", "diplomatic_communications"],
)
law.register_diplomat(diplomat)

# Check immunity
has_immunity = law.check_immunity_scope("Ambassador Smith", "official_acts")

# Declare persona non grata
png = law.declare_persona_non_grata(
    diplomat_name="Offending Agent",
    declaring_country="Host Country",
    reason="Engaged in activities incompatible with diplomatic status",
    departure_days=48,
)
```

## Biblical Inspiration

2 Corinthians 5:20 — "We are therefore Christ's ambassadors, as though God were
making his appeal through us."

The concept of diplomatic immunity reflects the sacred status of ambassadors as
representatives of their sovereign.

## Falsification Tests

- `F_DIPLOMATIC_001`: Verify diplomats have immunity for actions in scope
- `F_DIPLOMATIC_002`: Verify PNG declarations require valid reason and deadline
- `F_DIPLOMATIC_003`: Verify immunity lookup works for registered diplomats
