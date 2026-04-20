---
tags: [src, domains, d-bill-of-rights, readme]
register: technical
---

# D_BILL_OF_RIGHTS: Bill of Rights & Fundamental Rights

**Layer:** 1 (Constitutional)  
**CardinalStrength:** INACCESSIBLE  
**Authority:** US Constitution Amendments 1-10

## Description

Domain implementing First Amendment (speech, religion, press, assembly, petition),
Fourth Amendment (search/seizure), and Fifth/Fourteenth Amendment (due process)
compliance checking.

## Invariants

1. **Political Speech Protected**: Political speech is protected under First Amendment;
restrictions must be content-neutral and narrowly tailored.

2. **Home Searches Require Warrant**: Fourth Amendment requires warrant for home searches
absent consent or exigent circumstances.

3. **Due Process Requirements**: Notice and opportunity to be heard required before
deprivation of life, liberty, or property.

4. **Unprotected Speech**: Incitement, true threats, and fraud are not protected speech.

## Key Classes

- `BillOfRightsChecker`: Comprehensive Bill of Rights compliance checker
- `FirstAmendmentRights`: First Amendment speech and religion rights
- `FourthAmendmentRights`: Search and seizure protections
- `DueProcessRights`: Fifth and Fourteenth Amendment due process
- `RightsViolation`: Enum of possible rights violations

## Usage

```python
from src.domains.d_bill_of_rights import BillOfRightsChecker

checker = BillOfRightsChecker()

# Check First Amendment
result = checker.check_first_amendment(
    speech_content="Political criticism",
    law_name="Speech Restriction Act",
    restricts_speech=True,
)

# Check Fourth Amendment
result = checker.check_fourth_amendment(
    search_location="home",
    has_warrant=False,
    probable_cause=False,
    law_name="Warrantless Search Act",
)

# Check Due Process
result = checker.check_due_process(
    deprivation_type="liberty",
    notice_given=False,
    hearing_held=False,
    law_name="Administrative Detention Act",
)
```

## Biblical Inspiration

Proverbs 31:8-9 — "Speak up for those who cannot speak for themselves, for the
rights of all who are destitute. Speak up and judge fairly; defend the rights
of the poor and needy."

The Bill of Rights embodies the protection of the vulnerable against government
overreach—an institutionalization of the call to defend the rights of all.

## Falsification Tests

- `F_BOR_001`: Verify political speech protection
- `F_BOR_002`: Verify unprotected speech detection (incitement)
- `F_BOR_003`: Verify home search warrant requirement
- `F_BOR_004`: Verify consent validates search
- `F_BOR_005`: Verify due process requires notice/hearing
- `F_BOR_006`: Verify exigent circumstances exception
