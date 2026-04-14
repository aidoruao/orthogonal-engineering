#!/usr/bin/env python3
"""Maritime Domain Invariants — SOLAS compliance, UNCLOS, safety at sea.

Standards:
- UNCLOS (Law of the Sea)
- SOLAS (Safety of Life at Sea)
- ISM Code (International Safety Management)
- York-Antwerp Rules (General Average)

Falsifies if:
- Vessel undermanned
- Substandard flag state
- SOLAS violations
- General average calculation error
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Cargo,
    FlagState,
    GeneralAverage,
    MaritimeIncident,
    Vessel,
    MaritimeZone,
    VesselType,
)


def check_safe_manning(vessel: Vessel) -> Tuple[bool, ProofObject]:
    """SOLAS Chapter V requires adequate crew for safe operation.
    
    Falsifies if: crew_count is below minimum_safe_manning.
    falsifies_if: crew_count is below minimum_safe_manning.
    """
    if not vessel.adequately_manned():
        deficit = vessel.minimum_safe_manning - vessel.crew_count
        return False, ProofObject(
            conclusion=f"VIOLATION: Vessel undermanned by {deficit} crew",
            premises=[
                f"Vessel: {vessel.vessel_name}",
                f"Crew: {vessel.crew_count}",
                f"Required: {vessel.minimum_safe_manning}",
                f"Deficit: {deficit}"
            ],
            rule="solas_chapter_v_safe_manning"
        )
    
    return True, ProofObject(
        conclusion="Vessel adequately manned",
        premises=[f"Crew: {vessel.crew_count}", f"Minimum: {vessel.minimum_safe_manning}"],
        rule="safe_manning_compliant"
    )


def check_ism_compliance(vessel: Vessel) -> Tuple[bool, ProofObject]:
    """ISM Code requires Safety Management Certificate and Document of Compliance.
    
    Falsifies if: smc_certified or doc_certified is False.
    falsifies_if: smc_certified or doc_certified is False.
    """
    if not vessel.smc_certified:
        return False, ProofObject(
            conclusion="VIOLATION: Vessel lacks Safety Management Certificate",
            premises=[
                f"Vessel: {vessel.vessel_name}",
                "SMC: Not certified"
            ],
            rule="ism_code_smc_required"
        )
    
    if not vessel.doc_certified:
        return False, ProofObject(
            conclusion="VIOLATION: Vessel lacks Document of Compliance",
            premises=[
                f"Vessel: {vessel.vessel_name}",
                "DOC: Not certified"
            ],
            rule="ism_code_doc_required"
        )
    
    return True, ProofObject(
        conclusion="Vessel ISM compliant",
        premises=["SMC: Certified", "DOC: Certified"],
        rule="ism_compliant"
    )


def check_flag_state_quality(vessel: Vessel) -> Tuple[bool, ProofObject]:
    """Paris MoU/Tokyo MoU target substandard flag states.
    
    Falsifies if: flag_state.black_list is True.
    falsifies_if: flag_state.black_list is True.
    """
    if vessel.flag_state.black_list:
        return False, ProofObject(
            conclusion="VIOLATION: Vessel registered under black-list flag state",
            premises=[
                f"Vessel: {vessel.vessel_name}",
                f"Flag: {vessel.flag_state.country_name}",
                "Status: Black list (high detention rate)"
            ],
            rule="port_state_control_flag_quality"
        )
    
    return True, ProofObject(
        conclusion="Flag state acceptable",
        premises=[
            f"Flag: {vessel.flag_state.country_name}",
            f"White list: {vessel.flag_state.white_list}"
        ],
        rule="flag_state_compliant"
    )


def check_serious_incident_reporting(incident: MaritimeIncident) -> Tuple[bool, ProofObject]:
    """Casualties must be investigated per IMO requirements.
    
    Falsifies if: serious incident lacks flag state investigation or reporting.
    falsifies_if: serious incident lacks flag state investigation or reporting.
    """
    is_serious = incident.fatalities > 0 or incident.vessel_damage > Fraction(1, 2)
    
    if is_serious and not incident.flag_state_investigation:
        return False, ProofObject(
            conclusion="VIOLATION: Serious maritime incident without flag state investigation",
            premises=[
                f"Incident: {incident.incident_id}",
                f"Fatalities: {incident.fatalities}",
                f"Damage: {incident.vessel_damage}",
                "Investigation: None"
            ],
            rule="imo_casualty_investigation"
        )
    
    return True, ProofObject(
        conclusion="Incident properly investigated or not serious",
        premises=[
            f"Fatalities: {incident.fatalities}",
            f"Investigated: {incident.flag_state_investigation}"
        ],
        rule="incident_reporting_compliant"
    )


def check_general_average_calculation(ga: GeneralAverage) -> Tuple[bool, ProofObject]:
    """York-Antwerp Rules require proportional contribution.
    
    Falsifies if: contribution total is zero or sacrifice ratio exceeds 100%.
    falsifies_if: contribution total is zero or sacrifice ratio exceeds 100%.
    """
    total = ga.total_contribution()
    
    if total == 0:
        return False, ProofObject(
            conclusion="VIOLATION: General Average has no contributing interests",
            premises=[
                f"GA: {ga.ga_id}",
                "Vessel value: 0",
                f"Cargo count: {len(ga.cargo_values)}"
            ],
            rule="york_antwerp_contribution_required"
        )
    
    ratio = ga.sacrifice_ratio()
    if ratio > Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: GA sacrifice ratio {ratio} exceeds 100%",
            premises=[
                f"Sacrifice: {ga.cargo_sacrificed_value + ga.vessel_damage_value}",
                f"Contribution: {total}",
                f"Ratio: {ratio}"
            ],
            rule="york_antwerp_proportionality"
        )
    
    return True, ProofObject(
        conclusion="General Average calculation valid",
        premises=[f"Contribution total: {total}", f"Sacrifice ratio: {ratio}"],
        rule="general_average_valid"
    )


def check_hazmat_declaration(cargo: Cargo) -> Tuple[bool, ProofObject]:
    """IMDG Code requires dangerous goods to be declared.
    
    Falsifies if: cargo.dangerous_goods is True while imdg_class is missing.
    falsifies_if: cargo.dangerous_goods is True while imdg_class is missing.
    """
    if cargo.dangerous_goods and cargo.imdg_class is None:
        return False, ProofObject(
            conclusion="VIOLATION: Dangerous goods without IMDG classification",
            premises=[
                f"Cargo: {cargo.cargo_id}",
                "Dangerous: True",
                "IMDG class: Not declared"
            ],
            rule="imdg_code_declaration_required"
        )
    
    return True, ProofObject(
        conclusion="Hazmat properly declared or not dangerous",
        premises=[
            f"Dangerous: {cargo.dangerous_goods}",
            f"Class: {cargo.imdg_class}"
        ],
        rule="hazmat_compliant"
    )


def run_all_invariants() -> dict:
    """Run all D_MARITIME invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    vessel = Vessel(
        imo_number=None,
        vessel_name=None,
        vessel_type=VesselType.CONTAINER,
        flag_state=FlagState(
        country_code=None,
        country_name=None,
        white_list=None,
        grey_list=None,
        black_list=None,
    ),
        gross_tonnage=None,
        crew_count=None,
        minimum_safe_manning=None,
        smc_certified=None,
        doc_certified=None,
        p_and_i_insurance=None,
        hull_insurance=None,
    )
    general_average = GeneralAverage(
        ga_id=None,
        voyage_number=None,
        declaration_date=None,
        cargo_sacrificed_value=Fraction(1),
        vessel_damage_value=Fraction(1),
        vessel_value=Fraction(1),
        cargo_values=None,
        freight_at_risk=Fraction(1),
    )
    cargo = Cargo(
        cargo_id=None,
        bill_of_lading=None,
        description=None,
        weight_kg=None,
        value=Fraction(1),
        shipper=None,
        consignee=None,
        dangerous_goods=None,
        imdg_class=None,
        loaded=None,
        delivered=None,
    )
    maritime_incident = MaritimeIncident(
        incident_id=None,
        vessel_imo=None,
        incident_date=None,
        location=None,
        incident_type=None,
        maritime_zone=MaritimeZone.INTERNAL_WATERS,
        injuries=None,
        fatalities=None,
        pollution_released=None,
        vessel_damage=Fraction(1),
        flag_state_investigation=None,
        maib_involved=None,
        report_issued=None,
    )

    checks = [
        ("check_flag_state_quality", lambda: check_flag_state_quality(vessel)),
        ("check_general_average_calculation", lambda: check_general_average_calculation(general_average)),
        ("check_hazmat_declaration", lambda: check_hazmat_declaration(cargo)),
        ("check_ism_compliance", lambda: check_ism_compliance(vessel)),
        ("check_safe_manning", lambda: check_safe_manning(vessel)),
        ("check_serious_incident_reporting", lambda: check_serious_incident_reporting(maritime_incident)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_MARITIME invariants: PASS")
