"""D_TRADE_AGREEMENTS invariants — Yeshua Standard. 0 floats.

Standards:
- GATT 1994 (WTO General Agreement on Tariffs and Trade)
- WTO Agreement on Safeguards (Article XIX GATT)
- USMCA / NAFTA successor — tariff schedules
- 19 U.S.C. §2462 — GSP (Generalized System of Preferences)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import TariffSchedule, TradeAgreement


def check_mfn_tariff_nonneg(schedule: TariffSchedule) -> Tuple[bool, ProofObject]:
    """Most-Favored-Nation (MFN) tariff rate must be >= 0.

    Standard: GATT Article I — MFN obligation; WTO Tariff Schedule commitments
    falsifies_if: schedule.mfn_rate < 0.
    """
    ok = schedule.mfn_rate >= Fraction(0)
    premises = [
        f"product_code={schedule.product_code}",
        f"mfn_rate={schedule.mfn_rate}",
    ]
    return ok, ProofObject(
        rule="MFNTariffNonNeg",
        premises=premises,
        conclusion=f"PASS: MFN rate {schedule.mfn_rate} >= 0" if ok else "VIOLATION: negative MFN tariff rate",
    )


def check_preferential_le_mfn(schedule: TariffSchedule) -> Tuple[bool, ProofObject]:
    """Preferential tariff rate must be <= MFN rate (FTA preference).

    Standard: GATT Article XXIV — preferential arrangements must reduce barriers
    falsifies_if: schedule.preferential_rate > schedule.mfn_rate.
    """
    ok = schedule.preferential_rate <= schedule.mfn_rate
    premises = [
        f"product_code={schedule.product_code}",
        f"mfn_rate={schedule.mfn_rate}",
        f"preferential_rate={schedule.preferential_rate}",
    ]
    return ok, ProofObject(
        rule="PreferentialLeMFN",
        premises=premises,
        conclusion=f"PASS: preferential {schedule.preferential_rate} <= MFN {schedule.mfn_rate}" if ok else f"VIOLATION: preferential {schedule.preferential_rate} > MFN {schedule.mfn_rate}",
    )


def check_preferential_tariff_nonneg(schedule: TariffSchedule) -> Tuple[bool, ProofObject]:
    """Preferential tariff rate must be >= 0.

    Standard: WTO Agreement on Safeguards — no negative tariffs unless agreed
    falsifies_if: schedule.preferential_rate < 0.
    """
    ok = schedule.preferential_rate >= Fraction(0)
    premises = [
        f"product_code={schedule.product_code}",
        f"preferential_rate={schedule.preferential_rate}",
    ]
    return ok, ProofObject(
        rule="PreferentialTariffNonNeg",
        premises=premises,
        conclusion=f"PASS: preferential rate {schedule.preferential_rate} >= 0" if ok else "VIOLATION: negative preferential tariff",
    )


def check_product_code_nonempty(schedule: TariffSchedule) -> Tuple[bool, ProofObject]:
    """Product code (HS code) must be non-empty.

    Standard: WTO Harmonized System (HS) nomenclature requirement
    falsifies_if: schedule.product_code is empty.
    """
    ok = bool(schedule.product_code.strip())
    premises = [f"product_code={schedule.product_code!r}"]
    return ok, ProofObject(
        rule="ProductCodeNonEmpty",
        premises=premises,
        conclusion="PASS: product code set" if ok else "VIOLATION: product code empty",
    )


def check_agreement_has_parties(agreement: TradeAgreement) -> Tuple[bool, ProofObject]:
    """Trade agreement must have at least 2 parties.

    Standard: GATT Article XXIV(5)(a) — at least two contracting parties
    falsifies_if: len(agreement.parties) < 2.
    """
    parties = getattr(agreement, "parties", []) or []
    ok = len(parties) >= 2
    premises = [
        f"agreement_name={getattr(agreement, 'name', 'unknown')}",
        f"party_count={len(parties)}",
    ]
    return ok, ProofObject(
        rule="AgreementHasParties",
        premises=premises,
        conclusion=f"PASS: {len(parties)} parties" if ok else "VIOLATION: trade agreement needs >= 2 parties",
    )


def check_mfn_rate_bound(schedule: TariffSchedule) -> Tuple[bool, ProofObject]:
    """MFN rate must not exceed 100% (Fraction(1)).

    Standard: WTO bound tariff commitments — rates above 100% are anomalous
    falsifies_if: schedule.mfn_rate > Fraction(1).
    """
    ok = schedule.mfn_rate <= Fraction(1)
    premises = [
        f"product_code={schedule.product_code}",
        f"mfn_rate={schedule.mfn_rate}",
    ]
    return ok, ProofObject(
        rule="MFNRateBound",
        premises=premises,
        conclusion=f"PASS: MFN rate {schedule.mfn_rate} <= 1" if ok else f"VIOLATION: MFN rate {schedule.mfn_rate} > 1",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    schedule = TariffSchedule(
        product_code="8471.30",
        mfn_rate=Fraction(0),
        preferential_rate=Fraction(0),
    )
    agreement = TradeAgreement(agreement_name="USMCA")
    agreement.parties = ["USA", "Canada", "Mexico"]
    results = {}
    for fn, args in [
        (check_mfn_tariff_nonneg, (schedule,)),
        (check_preferential_le_mfn, (schedule,)),
        (check_preferential_tariff_nonneg, (schedule,)),
        (check_product_code_nonempty, (schedule,)),
        (check_agreement_has_parties, (agreement,)),
        (check_mfn_rate_bound, (schedule,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
