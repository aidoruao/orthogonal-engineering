---
tags: [src, domains, d-un-charter, readme]
register: technical
---

# D_UN_CHARTER: UN Charter & International Law

**Layer:** 0 (Supranational)  
**CardinalStrength:** MAHLO  
**Authority:** UN Charter (1945), Universal Declaration of Human Rights (1948)

## Description

Domain implementing jus cogens norms (peremptory norms of general international law)
from which no derogation is permitted. These norms bind all states regardless of
treaty ratification.

## Invariants

1. **Jus Cogens Non-Derogable**: No state may violate jus cogens norms (genocide,
   slavery, torture, aggression, crimes against humanity, piracy).

2. **UDHR Universal**: UDHR rights are non-derogable in all circumstances.

## Key Classes

- `JusCogensNorms`: Registry and checker for jus cogens norms
- `UNCharterChecker`: Comprehensive compliance checker
- `ComplianceResult`: Result of compliance check

## Usage

```python
from src.domains.d_un_charter import check_jus_cogens_compliance

result = check_jus_cogens_compliance(
    law_text="The state prohibits torture in all circumstances",
    law_name="Anti-Torture Act",
)

if result.compliant:
    print("Compliant with UN Charter")
else:
    print(f"Violations: {result.violated_norms}")
```

## Biblical Inspiration

Isaiah 2:4 — "They shall beat their swords into plowshares, and their spears
into pruning hooks; nation shall not lift up sword against nation, neither
shall they learn war anymore."

The UN Charter's prohibition of aggression reflects this eschatological hope
for peace between nations.

## Falsification Tests

- `F_UN_CHARTER_001`: Verify torture authorization is flagged as violation
- `F_UN_CHARTER_002`: Verify genocide authorization is flagged as violation
- `F_UN_CHARTER_003`: Verify compliant laws pass without false positives
