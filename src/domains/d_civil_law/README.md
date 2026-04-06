# D_CIVIL_LAW: Civil Law / Torts

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** Common Law, State Statutes

## Description

Domain implementing tort law with functorial duty → breach → causation →
damages chain. Enforces statute of limitations with documented filing dates.

## Invariants

1. **Functorial Chain**: Duty → Breach → Causation → Damages must all be
proven for liability (chain is functorial—break any link, no liability).

2. **Statute of Limitations**: Claims filed beyond statutory period are
dismissed.

3. **Damages Required**: Liability requires actual damages.

4. **Different Limitations Periods**: Intentional torts typically have
shorter limitations periods than negligence.

## Key Classes

- `CivilLaw`: Civil law / torts system
- `TortClaim`: A tort claim with all elements
- `DutyBreachCausationDamages`: Functorial chain of tort elements
- `StatuteOfLimitations`: Limitations period enforcement

## Usage

```python
from datetime import datetime, timedelta
from fractions import Fraction
from src.domains.d_civil_law import CivilLaw, TortType

law = CivilLaw()

# File tort claim
claim = law.file_claim(
    claim_id="C001",
    plaintiff="Plaintiff",
    defendant="Defendant",
    tort_type=TortType.NEGLIGENCE,
    incident_date=datetime.now() - timedelta(days=100),
    filing_date=datetime.now(),
    duty_description="Duty to drive safely",
    breach_description="Ran red light",
    causation_description="Caused collision",
    damages_amount=Fraction(25000),
)

# Adjudicate
result = law.adjudicate_claim("C001")
```

## Biblical Inspiration

Exodus 21:33-34 — "If anyone uncovers a pit or digs one and fails to cover
it and an ox or a donkey falls into it, the one who opened the pit must pay
the owner for the loss and take the dead animal in exchange."

Ancient tort law established duty, breach, and damages—modern tort law's
functorial chain has biblical roots.

## Falsification Tests

- `F_CIVIL_001`: Verify duty-breach-causation-damages chain
- `F_CIVIL_002`: Verify statute of limitations enforced
- `F_CIVIL_003`: Verify timely claims allowed
- `F_CIVIL_004`: Verify damages required for liability
- `F_CIVIL_005`: Verify functorial chain completeness
- `F_CIVIL_006`: Verify intentional vs negligence limitations
- `F_CIVIL_007`: Verify statute function accuracy
