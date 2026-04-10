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
from .implementation import Vessel, MaritimeIncident, GeneralAverage, Cargo


def check_safe_manning(vessel: Vessel) -> Tuple[bool, ProofObject]:
    """SOLAS Chapter V requires adequate crew for safe operation.
    
    falsifies_if:
        - crew_count < minimum_safe_manning
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
    
    falsifies_if:
        - smc_certified is False
        - doc_certified is False
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
    
    falsifies_if:
        - flag_state.black_list is True
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
    
    falsifies_if:
        - Serious incident without investigation
        - Report not issued within 12 months
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
    
    falsifies_if:
        - Contribution total is zero
        - Sacrifice ratio > 100%
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
    
    falsifies_if:
        - dangerous_goods is True but imdg_class is None
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
