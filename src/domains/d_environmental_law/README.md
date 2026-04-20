---
tags: [src, domains, d-environmental-law, readme]
register: technical
---

# D_ENVIRONMENTAL_LAW: Environmental Law

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** Clean Air Act (42 U.S.C. §7401), NEPA (42 U.S.C. §4321),
Clean Water Act (33 U.S.C. §1251), RCRA (42 U.S.C. §6901)

## Description

Domain implementing environmental law including Clean Air Act compliance
(NAAQS, PSD, Title V permits), NEPA environmental review, and permitting
analysis. Environmental law balances economic development with protection
of public health and natural resources.

## Invariants

1. **NAAQS Compliance**: Air quality measurements exceeding National Ambient
   Air Quality Standards constitute violations.

2. **Major Source Threshold**: Sources emitting ≥100 tons/year of regulated
   pollutants are classified as "major sources."

3. **PSD in Attainment**: Major new sources in attainment areas require
   Prevention of Significant Deterioration permits.

4. **NEPA Significance**: Federal actions with significant environmental
   impacts require Environmental Impact Statements (EIS).

5. **Emission Summation**: Total emissions equal the sum of all pollutant
   emissions from a source.

6. **Public Participation**: Major permits require minimum public comment
   periods (typically 30+ days for PSD).

7. **Nonattainment Stricter Standards**: Nonattainment areas have more
   stringent New Source Review requirements (LAER vs. BACT).

## Key Classes

- `CleanAirActAnalyzer`: Analyzes CAA compliance and permitting
- `NEPAAnalyzer`: Classifies federal actions for NEPA purposes
- `PermittingSystem`: Manages permit applications and public participation
- `EnvironmentalComplianceChecker`: Comprehensive compliance validator
- `EmissionSource`: Air pollution source with emissions data
- `AirQualityMonitor`: Station measuring air quality vs. standards
- `FederalAction`: Federal action subject to NEPA review

## Usage

```python
from fractions import Fraction
from src.domains.d_environmental_law import (
    CleanAirActAnalyzer,
    EmissionSource,
    AirQualityClass,
    PollutantType,
)

# Define emission source
source = EmissionSource(
    source_id="S001",
    source_name="Power Plant Stack",
    facility_name="PowerGen Facility",
    emissions={
        PollutantType.SO2: Fraction(150),
        PollutantType.NO2: Fraction(120),
        PollutantType.PM25: Fraction(45),
    },
)

print(f"Total emissions: {source.total_emissions} tpy")
print(f"Is major source: {source.is_major_source}")

# Analyze permitting requirements
analyzer = CleanAirActAnalyzer()
result = analyzer.analyze_source_permitting(
    source=source,
    air_quality_class=AirQualityClass.ATTAINMENT,
    is_new_source=True,
)

print(f"Permits required: {result['num_requirements']}")
for req in result['permit_requirements']:
    print(f"  - {req.get('permit_type', req.get('requirement'))}")
```

## Biblical Inspiration

Genesis 2:15 — "The LORD God took the man and put him in the Garden of Eden
to work it and take care of it."

Environmental law embodies this "creation care" mandate—humanity's responsibility
to steward the earth, not merely exploit it. The NEPA requirement to consider
environmental consequences before acting reflects the wisdom of counting the
cost before building (Luke 14:28).

## Falsification Tests

- `F_ENV_001`: Verify NAAQS violation detection
- `F_ENV_002`: Verify major source 100 tpy threshold
- `F_ENV_003`: Verify PSD requirement in attainment areas
- `F_ENV_004`: Verify NEPA EIS requirement for significant actions
- `F_ENV_005`: Verify public comment period minimums
