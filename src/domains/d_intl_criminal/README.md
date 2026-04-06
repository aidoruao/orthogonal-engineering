# D_INTERNATIONAL_CRIMINAL: International Criminal Law

**Layer:** 0 (Supranational)  
**CardinalStrength:** MAHLO  
**Authority:** Rome Statute of the International Criminal Court (1998)

## Description

Domain implementing universal jurisdiction for core crimes and ICC complementarity
principle checking.

## Invariants

1. **Universal Jurisdiction**: Core crimes (genocide, crimes against humanity,
war crimes, aggression) are subject to universal jurisdiction when evidence is present.

2. **No Prosecution Without Evidence**: Cases without evidence cannot be prosecuted
under universal jurisdiction.

3. **ICC Complementarity**: ICC can only prosecute if domestic court is unwilling
or unable to genuinely prosecute.

## Key Classes

- `InternationalCriminalLaw`: Universal jurisdiction and complementarity checker
- `UniversalJurisdictionCase`: Case subject to universal jurisdiction
- `CoreCrime`: Enum of genocide, crimes against humanity, war crimes, aggression

## Usage

```python
from src.domains.d_intl_criminal import (
    InternationalCriminalLaw,
    UniversalJurisdictionCase,
    CoreCrime,
)

icl = InternationalCriminalLaw()

# Check complementarity
icc_can_prosecute = icl.check_complementarity(
    domestic_proceedings=False,
    domestic_willing=False,
    domestic_able=False,
)

# Create a universal jurisdiction case
case = UniversalJurisdictionCase(
    case_id="CASE-001",
    crime=CoreCrime.GENOCIDE,
    suspect="Suspect Name",
    location="Jurisdiction",
    evidence_present=True,
)

if case.can_prosecute():
    print("Case can be prosecuted under universal jurisdiction")
```

## Biblical Inspiration

Genesis 9:6 — "Whoever sheds human blood, by humans shall their blood be shed;
for in the image of God has God made mankind."

The principle of universal jurisdiction for core crimes reflects the transcendent
value of human life and the duty of all nations to protect it.

## Falsification Tests

- `F_INTL_CRIMINAL_001`: Verify core crimes with evidence are prosecutable
- `F_INTL_CRIMINAL_002`: Verify cases without evidence cannot be prosecuted
- `F_INTL_CRIMINAL_003`: Verify ICC complementarity principle enforcement
- `F_INTL_CRIMINAL_004`: Verify all four Rome Statute crimes are defined
