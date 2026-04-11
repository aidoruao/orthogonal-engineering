"""D_EMERGENCY Invariants — 911 Response, EMS, NFPA Standards

Verifies emergency response times, EMS system performance,
cardiac arrest survival rates, resource availability.

Standards: NFPA 1710, NEMSIS, FEMA National Response Framework
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import EmergencyIncident, EMSAgency, EmergencyType, ems_response_target, cardiac_survival_target


def check_ems_response_time(agency: EMSAgency) -> Tuple[bool, ProofObject]:
    """
    NFPA 1710 requires timely EMS response.
    
    NFPA 1710 Standard:
    - 90% of EMS calls within 9 minutes
    - Average response time targets
    - Urban vs rural adjustments
    
    Falsifies if: 90th percentile > 9 minutes
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_90th = Fraction(9)  # 9 minutes
    
    if agency.response_time_90th_minutes > max_90th:
        return False, ProofObject(
            conclusion=f"VIOLATION: Agency {agency.name} 90th percentile response {agency.response_time_90th_minutes} min exceeds {max_90th} min",
            premises=[
                f"90th percentile: {agency.response_time_90th_minutes} min",
                f"Average: {agency.response_time_avg_minutes} min",
                "NFPA 1710 — EMS response time"
            ],
            rule="ems_response_time"
        )
    
    return True, ProofObject(
        conclusion=f"Agency {agency.name} EMS response time compliant",
        premises=[f"90th percentile: {agency.response_time_90th_minutes} min"],
        rule="ems_response_time"
    )


def check_cardiac_arrest_survival(agency: EMSAgency) -> Tuple[bool, ProofObject]:
    """
    Cardiac arrest survival rate indicates system effectiveness.
    
    Utstein standards:
    - Survival to discharge measured
    - Bystander CPR rates
    - AED deployment
    
    Falsifies if: survival rate < 10%
    
    
    falsifies_if: condition_evaluated_to_false"""
    target = cardiac_survival_target()
    rate = agency.get_cardiac_survival_rate()
    
    if agency.cardiac_arrest_calls > 10 and rate < target:
        return False, ProofObject(
            conclusion=f"VIOLATION: Agency {agency.name} cardiac survival {rate} below target {target}",
            premises=[
                f"Survivals: {agency.cardiac_arrest_survivals}",
                f"Calls: {agency.cardiac_arrest_calls}",
                f"Rate: {rate}",
                "Utstein standards — Cardiac arrest survival"
            ],
            rule="cardiac_arrest_survival"
        )
    
    return True, ProofObject(
        conclusion=f"Agency {agency.name} cardiac arrest survival rate acceptable",
        premises=[f"Rate: {rate}"],
        rule="cardiac_arrest_survival"
    )


def check_ambulance_availability(agency: EMSAgency) -> Tuple[bool, ProofObject]:
    """
    Ambulance availability required for system reliability.
    
    System reliability:
    - Units available for dispatch
    - Redundancy required
    - Peak demand coverage
    
    Falsifies if: availability < 20%
    
    
    falsifies_if: condition_evaluated_to_false"""
    min_availability = Fraction(1, 5)  # 20%
    avail = agency.get_ambulance_availability()
    
    if avail < min_availability:
        return False, ProofObject(
            conclusion=f"VIOLATION: Agency {agency.name} ambulance availability {avail} below {min_availability}",
            premises=[
                f"Available: {agency.ambulances_available}",
                f"Total: {agency.ambulances_total}",
                f"Availability: {avail}",
                "EMS system — Resource availability"
            ],
            rule="ambulance_availability"
        )
    
    return True, ProofObject(
        conclusion=f"Agency {agency.name} ambulance availability adequate",
        premises=[f"Availability: {avail}"],
        rule="ambulance_availability"
    )


def check_emergency_response_priority(incident: EmergencyIncident) -> Tuple[bool, ProofObject]:
    """
    Priority 1 emergencies require immediate response.
    
    Dispatch prioritization:
    - Priority 1: Life threatening
    - Priority 2: Emergency
    - Priority 3-5: Urgent/non-urgent
    
    Falsifies if: Priority 1 response time excessive
    
    
    falsifies_if: condition_evaluated_to_false"""
    response_time = incident.get_response_time_minutes()
    
    if response_time is None:
        return True, ProofObject(
            conclusion=f"Incident {incident.incident_id} response time not available",
            premises=["Response: pending"],
            rule="response_priority_pending"
        )
    
    if incident.priority == 1 and response_time > Fraction(8):  # 8 minutes for Priority 1
        return False, ProofObject(
            conclusion=f"VIOLATION: Priority 1 incident {incident.incident_id} response time {response_time} min excessive",
            premises=[
                f"Priority: {incident.priority}",
                f"Response time: {response_time} min",
                "911 dispatch — Priority response standards"
            ],
            rule="emergency_response_priority"
        )
    
    return True, ProofObject(
        conclusion=f"Incident {incident.incident_id} response time acceptable",
        premises=[f"Priority: {incident.priority}", f"Response: {response_time} min"],
        rule="emergency_response_priority"
    )


def check_ems_coverage_density(agency: EMSAgency) -> Tuple[bool, ProofObject]:
    """
    EMS coverage density sufficient for population served.
    
    Coverage standards:
    - Units per capita
    - Geographic coverage
    - Response time feasibility
    
    Falsifies if: insufficient units for population
    
    
    falsifies_if: condition_evaluated_to_false"""
    if agency.service_area_population == 0:
        return True, ProofObject(
            conclusion=f"Agency {agency.name} no population data",
            premises=["Population: 0"],
            rule="ems_coverage_exemption"
        )
    
    # Minimum: 1 ambulance per 50,000 population
    min_ratio = Fraction(1, 50000)
    actual_ratio = Fraction(agency.ambulances_total) / agency.service_area_population
    
    if actual_ratio < min_ratio:
        return False, ProofObject(
            conclusion=f"VIOLATION: Agency {agency.name} ambulance ratio {actual_ratio} below {min_ratio}",
            premises=[
                f"Ambulances: {agency.ambulances_total}",
                f"Population: {agency.service_area_population}",
                f"Ratio: {actual_ratio}",
                "EMS coverage standards"
            ],
            rule="ems_coverage_density"
        )
    
    return True, ProofObject(
        conclusion=f"Agency {agency.name} EMS coverage adequate",
        premises=[f"Ratio: {actual_ratio}"],
        rule="ems_coverage_density"
    )
