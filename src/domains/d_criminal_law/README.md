# D_CRIMINAL_LAW: Criminal Law

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** State/Federal Penal Codes

## Description

Domain implementing statutory criminal law with nullum crimen sine lege
(no crime without law), burden of proof on prosecution, guilt beyond
reasonable doubt, and sentencing within statutory ranges.

## Invariants

1. **Nullum Crimen Sine Lege**: No punishment without prior law defining
the offense (statute citation required).

2. **Burden of Proof**: Prosecution bears burden of proof; defendant is
presumed innocent.

3. **Beyond Reasonable Doubt**: Conviction requires guilt proven beyond
reasonable doubt (high certainty threshold).

4. **Statutory Sentencing**: Sentence must be within statutory range for
the offense class.

5. **Sentencing Factors**: Mitigating factors reduce sentence; aggravating
factors increase it.

## Key Classes

- `CriminalLaw`: Criminal law system
- `CriminalOffense`: A defined criminal offense
- `BurdenOfProof`: Prosecution burden of proof
- `Sentencing`: Criminal sentencing with factors

## Usage

```python
from fractions import Fraction
from src.domains.d_criminal_law import CriminalLaw, OffenseClass

law = CriminalLaw()

# Define offense (nullum crimen sine lege)
law.define_offense(
    offense_name="Theft",
    statute_citation="Penal Code § 484",
    offense_class=OffenseClass.MISDEMEANOR,
    elements=["taking", "property of another", "intent"],
    max_penalty_years=1,
    max_fine=Fraction(1000),
)

# Prosecute (burden of proof on prosecution)
result = law.prosecute(
    defendant="Defendant",
    offense_name="Theft",
    evidence=["video", "witness", "physical evidence"],
)

# Sentence (within statutory range)
sentence = law.sentence(
    defendant="Defendant",
    offense_name="Theft",
    base_sentence_years=6,
    fine=Fraction(500),
    mitigating=["first offense"],
    aggravating=["vulnerable victim"],
)
```

## Biblical Inspiration

Deuteronomy 19:15 — "One witness is not enough to convict anyone accused of
any crime or offense they may have committed. A matter must be established
by the testimony of two or three witnesses."

The biblical standard of multiple witnesses reflects the high burden of
proof required in criminal proceedings.

## Falsification Tests

- `F_CRIMINAL_001`: Verify nullum crimen sine lege
- `F_CRIMINAL_002`: Verify burden of proof on prosecution
- `F_CRIMINAL_003`: Verify proof beyond reasonable doubt required
- `F_CRIMINAL_004`: Verify sentencing within statutory range
- `F_CRIMINAL_005`: Verify mitigating factors reduce sentence
- `F_CRIMINAL_006`: Verify aggravating factors increase sentence
- `F_CRIMINAL_007`: Verify offense definition requirements
