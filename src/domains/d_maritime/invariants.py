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

from datetime import datetime
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


def check_ism_completeness_score(vessel: Vessel) -> Tuple[bool, ProofObject]:
    """ISM Code requires Safety Management Certificate and Document of Compliance.
    
    Falsifies if: smc_compliance_score or doc_compliance_score is below 3/4.
    falsifies_if: smc_compliance_score or doc_compliance_score is below 3/4.
    """
    threshold = Fraction(3, 4)
    
    if vessel.smc_compliance_score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: SMC compliance score {vessel.smc_compliance_score} below threshold {threshold}",
            premises=[
                f"Vessel: {vessel.vessel_name}",
                f"SMC score: {vessel.smc_compliance_score}",
                f"Threshold: {threshold}"
            ],
            rule="ism_code_smc_required"
        )
    
    if vessel.doc_compliance_score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: DOC compliance score {vessel.doc_compliance_score} below threshold {threshold}",
            premises=[
                f"Vessel: {vessel.vessel_name}",
                f"DOC score: {vessel.doc_compliance_score}",
                f"Threshold: {threshold}"
            ],
            rule="ism_code_doc_required"
        )
    
    composite = (vessel.smc_compliance_score + vessel.doc_compliance_score) / 2
    return True, ProofObject(
        conclusion=f"Vessel ISM compliant with composite score {composite}",
        premises=[
            f"SMC score: {vessel.smc_compliance_score}",
            f"DOC score: {vessel.doc_compliance_score}",
            f"Composite: {composite}"
        ],
        rule="ism_compliant"
    )


def check_flag_state_score(vessel: Vessel) -> Tuple[bool, ProofObject]:
    """Paris MoU/Tokyo MoU target substandard flag states.
    
    Falsifies if: flag_state_quality_score is below 1/2.
    falsifies_if: flag_state_quality_score is below 1/2.
    """
    threshold = Fraction(1, 2)
    
    if vessel.flag_state.flag_state_quality_score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Flag state quality score {vessel.flag_state.flag_state_quality_score} below threshold {threshold}",
            premises=[
                f"Vessel: {vessel.vessel_name}",
                f"Flag: {vessel.flag_state.country_name}",
                f"Quality score: {vessel.flag_state.flag_state_quality_score}",
                f"Threshold: {threshold}"
            ],
            rule="port_state_control_flag_quality"
        )
    
    return True, ProofObject(
        conclusion="Flag state acceptable",
        premises=[
            f"Flag: {vessel.flag_state.country_name}",
            f"Quality score: {vessel.flag_state.flag_state_quality_score}"
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
        imo_number="1234567",
        vessel_name="Nominal Vessel",
        vessel_type=VesselType.CONTAINER,
        flag_state=FlagState(
            country_code="GB",
            country_name="United Kingdom",
            white_list=True,
            grey_list=False,
            black_list=False,
            flag_state_quality_score=Fraction(3, 4),
        ),
        gross_tonnage=50000,
        crew_count=20,
        minimum_safe_manning=10,
        smc_certified=True,
        doc_certified=True,
        smc_compliance_score=Fraction(1, 1),
        doc_compliance_score=Fraction(1, 1),
        p_and_i_insurance=True,
        hull_insurance=True,
    )
    general_average = GeneralAverage(
        ga_id="GA-001",
        voyage_number="V001",
        declaration_date=datetime(2024, 1, 1, 12, 0),
        cargo_sacrificed_value=Fraction(1),
        vessel_damage_value=Fraction(1),
        vessel_value=Fraction(10),
        cargo_values=[Fraction(5)],
        freight_at_risk=Fraction(5),
    )
    cargo = Cargo(
        cargo_id="C-001",
        bill_of_lading="BL-001",
        description="Test cargo",
        weight_kg=1000,
        value=Fraction(100),
        shipper="Shipper A",
        consignee="Consignee B",
        dangerous_goods=False,
        imdg_class=None,
        loaded=True,
        delivered=False,
    )
    maritime_incident = MaritimeIncident(
        incident_id="I-001",
        vessel_imo="1234567",
        incident_date=datetime(2024, 1, 1, 12, 0),
        location="Test location",
        incident_type="collision",
        maritime_zone=MaritimeZone.INTERNAL_WATERS,
        injuries=0,
        fatalities=0,
        pollution_released=False,
        vessel_damage=Fraction(1, 10),
        flag_state_investigation=False,
        maib_involved=False,
        report_issued=False,
    )

    checks = [
        ("check_flag_state_score", lambda: check_flag_state_score(vessel)),
        ("check_general_average_calculation", lambda: check_general_average_calculation(general_average)),
        ("check_hazmat_declaration", lambda: check_hazmat_declaration(cargo)),
        ("check_ism_completeness_score", lambda: check_ism_completeness_score(vessel)),
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
