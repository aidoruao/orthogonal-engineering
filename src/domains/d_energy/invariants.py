"""D_ENERGY invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes FERC licensing,
renewable portfolio standards, and grid interconnection requirements.

Standards:
- FERC Order 1000 (Transmission Planning)
- PURPA (16 U.S.C. §824a-3)
- State Renewable Portfolio Standards (RPS)
- IEEE 1547-2018 (Interconnection Standards)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import EnergyFacility


def check_ferc_licensing(facility: EnergyFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: Hydroelectric facilities require a valid FERC license (16 U.S.C. §797).

    falsifies_if: facility_type is "hydro" AND ferc_license_valid is False.
    """
    if facility.facility_type == "hydro":
        success = facility.ferc_license_valid
    else:
        success = True

    if not success:
        return False, ProofObject(
            rule="FERCLicensingRequired",
            premises=[
                f"facility_id={facility.facility_id}",
                f"facility_type={facility.facility_type}",
                f"ferc_license_valid={facility.ferc_license_valid}",
            ],
            conclusion="VIOLATION: 16 U.S.C. §797 — hydroelectric facility operating without valid FERC license",
        )

    return True, ProofObject(
        rule="FERCLicensingRequired",
        premises=[
            f"facility_id={facility.facility_id}",
            f"facility_type={facility.facility_type}",
            f"ferc_license_valid={facility.ferc_license_valid}",
        ],
        conclusion="FERC licensing requirement satisfied per 16 U.S.C. §797",
    )


def check_renewable_portfolio_standard(facility: EnergyFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: Renewable energy fraction must meet or exceed the required portfolio standard.

    falsifies_if: renewable_portfolio_fraction < required_renewable_fraction.
    """
    success = facility.renewable_portfolio_fraction >= facility.required_renewable_fraction

    if not success:
        return False, ProofObject(
            rule="RenewablePortfolioStandard",
            premises=[
                f"facility_id={facility.facility_id}",
                f"renewable_portfolio_fraction={facility.renewable_portfolio_fraction}",
                f"required_renewable_fraction={facility.required_renewable_fraction}",
            ],
            conclusion="VIOLATION: RPS — renewable portfolio fraction below required minimum",
        )

    return True, ProofObject(
        rule="RenewablePortfolioStandard",
        premises=[
            f"facility_id={facility.facility_id}",
            f"renewable_portfolio_fraction={facility.renewable_portfolio_fraction}",
            f"required_renewable_fraction={facility.required_renewable_fraction}",
        ],
        conclusion="Renewable Portfolio Standard satisfied",
    )


def check_grid_interconnection(facility: EnergyFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: Grid-connected generation requires an interconnection agreement per FERC Order 2003.

    falsifies_if: interconnection_agreement is False.
    """
    success = facility.interconnection_agreement

    if not success:
        return False, ProofObject(
            rule="GridInterconnectionAgreement",
            premises=[
                f"facility_id={facility.facility_id}",
                f"interconnection_agreement={facility.interconnection_agreement}",
                f"capacity_mw={facility.capacity_mw}",
            ],
            conclusion="VIOLATION: FERC Order 2003 — facility connected without interconnection agreement",
        )

    return True, ProofObject(
        rule="GridInterconnectionAgreement",
        premises=[
            f"facility_id={facility.facility_id}",
            f"interconnection_agreement={facility.interconnection_agreement}",
        ],
        conclusion="FERC Order 2003 grid interconnection agreement satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_ENERGY invariants with nominal passing data.

    falsifies_if: any energy invariant check fails or raises an exception.
    """
    facility = EnergyFacility(
        facility_id="FAC-001",
        ferc_license_valid=True,
        facility_type="hydro",
        interconnection_agreement=True,
        net_metering_eligible=True,
        capacity_mw=Fraction(50),
        reported_capacity_mw=Fraction(50),
        renewable_portfolio_fraction=Fraction(3, 10),
        required_renewable_fraction=Fraction(1, 5),
    )

    checks = [
        ("check_ferc_licensing", lambda: check_ferc_licensing(facility)),
        ("check_renewable_portfolio_standard", lambda: check_renewable_portfolio_standard(facility)),
        ("check_grid_interconnection", lambda: check_grid_interconnection(facility)),
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
    print("All D_ENERGY invariants: PASS")
