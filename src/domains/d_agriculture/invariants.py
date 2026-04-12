"""D_AGRICULTURE invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes agricultural
regulatory requirements for organic certification, water rights, and pesticide safety.

Standards:
- Organic Foods Production Act (7 U.S.C. §6501)
- Reclamation Act of 1902 (43 U.S.C. §431)
- Federal Insecticide, Fungicide, and Rodenticide Act (FIFRA, 7 U.S.C. §136)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import Farm


def check_organic_certification(farm: Farm) -> Tuple[bool, ProofObject]:
    """
    Rule: A farm making organic claims must hold organic certification (OFPA 7 U.S.C. §6505).

    falsifies_if: is_organic_claim is True AND organic_certified is False.
    """
    success = not (farm.is_organic_claim and not farm.organic_certified)

    if not success:
        return False, ProofObject(
            rule="OrganicCertificationRequired",
            premises=[
                f"farm_id={farm.farm_id}",
                f"is_organic_claim={farm.is_organic_claim}",
                f"organic_certified={farm.organic_certified}",
            ],
            conclusion="VIOLATION: OFPA §6505 — organic claim without certification",
        )

    return True, ProofObject(
        rule="OrganicCertificationRequired",
        premises=[
            f"farm_id={farm.farm_id}",
            f"is_organic_claim={farm.is_organic_claim}",
            f"organic_certified={farm.organic_certified}",
        ],
        conclusion="OFPA §6505 organic certification requirement satisfied",
    )


def check_water_rights(farm: Farm) -> Tuple[bool, ProofObject]:
    """
    Rule: Farms must hold a valid water permit; Reclamation Act limits acreage to 160 acres (43 U.S.C. §431).

    falsifies_if: water_permit_valid is False OR acres > max_acreage_reclamation.
    """
    permit_ok = farm.water_permit_valid
    acreage_ok = farm.acres <= farm.max_acreage_reclamation
    success = permit_ok and acreage_ok

    if not success:
        return False, ProofObject(
            rule="WaterRightsCompliance",
            premises=[
                f"farm_id={farm.farm_id}",
                f"water_permit_valid={farm.water_permit_valid}",
                f"acres={farm.acres}",
                f"max_acreage_reclamation={farm.max_acreage_reclamation}",
            ],
            conclusion=(
                "VIOLATION: Reclamation Act §431 — no water permit or acreage exceeds 160-acre limit"
                if not acreage_ok
                else "VIOLATION: water permit not valid"
            ),
        )

    return True, ProofObject(
        rule="WaterRightsCompliance",
        premises=[
            f"farm_id={farm.farm_id}",
            f"water_permit_valid={farm.water_permit_valid}",
            f"acres={farm.acres}",
        ],
        conclusion="Water rights and acreage limit satisfied per Reclamation Act §431",
    )


def check_pesticide_withdrawal(farm: Farm) -> Tuple[bool, ProofObject]:
    """
    Rule: Harvest must not occur before the pesticide pre-harvest interval elapses (FIFRA 7 U.S.C. §136).

    falsifies_if: harvest_days_after_last_application < pesticide_withdrawal_days.
    """
    success = farm.harvest_days_after_last_application >= farm.pesticide_withdrawal_days

    if not success:
        return False, ProofObject(
            rule="PesticideWithdrawalPeriod",
            premises=[
                f"farm_id={farm.farm_id}",
                f"harvest_days_after_last_application={farm.harvest_days_after_last_application}",
                f"pesticide_withdrawal_days={farm.pesticide_withdrawal_days}",
            ],
            conclusion="VIOLATION: FIFRA §136 — harvest before pesticide withdrawal period elapsed",
        )

    return True, ProofObject(
        rule="PesticideWithdrawalPeriod",
        premises=[
            f"farm_id={farm.farm_id}",
            f"harvest_days_after_last_application={farm.harvest_days_after_last_application}",
            f"pesticide_withdrawal_days={farm.pesticide_withdrawal_days}",
        ],
        conclusion="FIFRA §136 pesticide withdrawal period satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_AGRICULTURE invariants with nominal passing data.

    falsifies_if: any agricultural invariant check fails or raises an exception.
    """
    farm = Farm(
        farm_id="FARM-001",
        organic_certified=True,
        is_organic_claim=True,
        acres=Fraction(150),
        max_acreage_reclamation=Fraction(160),
        water_permit_valid=True,
        pesticide_withdrawal_days=Fraction(14),
        harvest_days_after_last_application=Fraction(21),
    )

    checks = [
        ("check_organic_certification", lambda: check_organic_certification(farm)),
        ("check_water_rights", lambda: check_water_rights(farm)),
        ("check_pesticide_withdrawal", lambda: check_pesticide_withdrawal(farm)),
    ]

    results: Dict[str, str] = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_AGRICULTURE invariants: PASS")
