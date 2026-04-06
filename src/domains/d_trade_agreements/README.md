# D_TRADE_AGREEMENTS: Trade & Commerce Agreements

**Layer:** 0 (Supranational)  
**CardinalStrength:** MAHLO  
**Authority:** WTO Agreements, GATT 1994

## Description

Domain implementing trade agreement tariff schedules, Most-Favored-Nation (MFN)
clause enforcement, and deterministic rate calculations using exact fractions.

## Invariants

1. **MFN Rate Application**: Tariffs are calculated correctly using MFN or
preferential rates.

2. **MFN Clause Enforcement**: When a lower rate is offered to one party, the
MFN clause applies that rate to all parties.

3. **No Rate Increase**: MFN clause never increases tariff rates, only decreases them.

4. **Exact Fraction Arithmetic**: All tariff calculations use `fractions.Fraction`
for precise representation.

## Key Classes

- `TradeAgreement`: Trade agreement with tariff schedules and MFN enforcement
- `TariffSchedule`: Deterministic tariff schedule with MFN and preferential rates

## Usage

```python
from fractions import Fraction
from src.domains.d_trade_agreements import TradeAgreement, TariffSchedule

agreement = TradeAgreement("Regional FTA")

# Add tariff schedule
schedule = TariffSchedule(
    product_code="WIDGET-001",
    mfn_rate=Fraction(5, 100),  # 5%
    preferential_rate=Fraction(2, 100),  # 2%
)
agreement.add_tariff_schedule(schedule)

# Apply MFN clause (lower rate offered)
agreement.apply_mfn_clause("WIDGET-001", Fraction(3, 100))

# Calculate tariff
value = Fraction(1000, 1)  # $1000
tariff = schedule.calculate_tariff(value, preferential=False)
# Result: $30 (3% of $1000 due to MFN clause)
```

## Biblical Inspiration

Leviticus 19:35-36 — "Do not use dishonest standards when measuring length,
weight or quantity. Use honest scales and honest weights..."

Fair trade requires honest, consistent measures—reflected in the MFN principle
that equal treatment must be given to all trading partners.

## Falsification Tests

- `F_TRADE_AGREEMENTS_001`: Verify MFN and preferential rate calculations
- `F_TRADE_AGREEMENTS_002`: Verify MFN clause reduces rates when lower offered
- `F_TRADE_AGREEMENTS_003`: Verify MFN clause never increases rates
- `F_TRADE_AGREEMENTS_004`: Verify exact fraction arithmetic in calculations
