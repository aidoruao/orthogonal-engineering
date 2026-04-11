"""D_OILGAS Invariants — Pipeline Safety, BSEE, Oil Pollution Prevention

Verifies PHMSA pipeline safety standards, BSEE offshore regulations,
EPA Spill Prevention Control and Countermeasure (SPCC) requirements.

Standards: 49 CFR Parts 190-199 (PHMSA), 30 CFR Part 250 (BSEE), 40 CFR 112 (EPA)
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import Pipeline, OffshorePlatform, SpillResponsePlan, PipelineClass, phmsa_max_hoop_stress, bsee_bop_test_interval


def check_phmsa_hoop_stress(pipeline: Pipeline) -> Tuple[bool, ProofObject]:
    """
    PHMSA limits maximum allowable operating pressure (hoop stress).
    
    49 CFR § 195.106:
    - Hoop stress shall not exceed 72% of SMYS (Specified Minimum Yield Strength)
    - Class 3 and 4 locations: max 60% SMYS
    - Safety margin required for pressure fluctuations
    
    Falsifies if: hoop_stress > max_allowed
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_stress = phmsa_max_hoop_stress(pipeline.pipeline_class)
    
    if pipeline.hoop_stress_percent > max_stress:
        return False, ProofObject(
            conclusion=f"VIOLATION: Pipeline {pipeline.pipeline_id} hoop stress {pipeline.hoop_stress_percent} exceeds {max_stress} for {pipeline.pipeline_class.name}",
            premises=[
                f"Hoop stress: {pipeline.hoop_stress_percent}",
                f"Max allowed: {max_stress}",
                f"Pipeline class: {pipeline.pipeline_class.name}",
                "49 CFR § 195.106 — Design requirements"
            ],
            rule="phmsa_hoop_stress"
        )
    
    return True, ProofObject(
        conclusion=f"Pipeline {pipeline.pipeline_id} hoop stress within limits",
        premises=[f"Hoop stress: {pipeline.hoop_stress_percent}", f"Max: {max_stress}"],
        rule="phmsa_hoop_stress"
    )


def check_phmsa_leak_detection(pipeline: Pipeline) -> Tuple[bool, ProofObject]:
    """
    PHMSA requires leak detection for hazardous liquid pipelines.
    
    49 CFR § 195.134:
    - Leak detection systems required for pipelines in HCAs
    - Must be capable of detecting leaks
    - Prompt notification required
    
    Falsifies if: HCA pipeline without leak detection
    
    
    falsifies_if: condition_evaluated_to_false"""
    if pipeline.pipeline_class == PipelineClass.CLASS_1:
        return True, ProofObject(
            conclusion=f"Pipeline {pipeline.pipeline_id} in rural area — leak detection recommended but not mandatory",
            premises=[f"Class: {pipeline.pipeline_class.name}"],
            rule="phmsa_leak_detection_rural"
        )
    
    if not pipeline.leak_detection_system:
        return False, ProofObject(
            conclusion=f"VIOLATION: Pipeline {pipeline.pipeline_id} in {pipeline.pipeline_class.name} lacks required leak detection",
            premises=[
                f"Pipeline class: {pipeline.pipeline_class.name}",
                "Leak detection: NO",
                "49 CFR § 195.134 — Leak detection"
            ],
            rule="phmsa_leak_detection"
        )
    
    return True, ProofObject(
        conclusion=f"Pipeline {pipeline.pipeline_id} leak detection system verified",
        premises=["Leak detection: YES"],
        rule="phmsa_leak_detection"
    )


def check_bsee_bop_testing(platform: OffshorePlatform) -> Tuple[bool, ProofObject]:
    """
    BSEE requires regular blowout preventer (BOP) testing.
    
    30 CFR § 250.446:
    - BOP must be tested every 14 days (surface stack)
    - Pressure tests required after repairs
    - Documentation required
    
    Falsifies if: BOP test interval > 14 days
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_interval = bsee_bop_test_interval()
    
    if platform.bop_test_frequency_days > max_interval:
        return False, ProofObject(
            conclusion=f"VIOLATION: Platform {platform.platform_id} BOP test interval {platform.bop_test_frequency_days} days exceeds {max_interval} day limit",
            premises=[
                f"Test frequency: {platform.bop_test_frequency_days} days",
                f"Required: ≤ {max_interval} days",
                "30 CFR § 250.446 — BOP testing"
            ],
            rule="bsee_bop_testing"
        )
    
    return True, ProofObject(
        conclusion=f"Platform {platform.platform_id} BOP testing compliant",
        premises=[f"Test interval: {platform.bop_test_frequency_days} days"],
        rule="bsee_bop_testing"
    )


def check_spill_response_capacity(plan: SpillResponsePlan) -> Tuple[bool, ProofObject]:
    """
    EPA requires adequate spill response equipment.
    
    40 CFR § 112.20:
    - Worst case discharge scenario planning required
    - Response resources must be sufficient
    - Contractual agreements for equipment
    
    Falsifies if: response capacity < worst case discharge
    
    
    falsifies_if: condition_evaluated_to_false"""
    # Response must be able to recover worst case in reasonable time
    # Assuming 24-hour response capability check
    required_skimmer_bpd = plan.worst_case_discharge_barrels * Fraction(1, 10)  # 10% per day recovery
    
    if plan.skimmer_capacity_bpd < required_skimmer_bpd:
        return False, ProofObject(
            conclusion=f"VIOLATION: Facility {plan.facility_id} skimmer capacity {plan.skimmer_capacity_bpd} BPD insufficient for worst case {plan.worst_case_discharge_barrels} barrels",
            premises=[
                f"Skimmer capacity: {plan.skimmer_capacity_bpd} BPD",
                f"Required: {required_skimmer_bpd} BPD minimum",
                f"Worst case: {plan.worst_case_discharge_barrels} barrels",
                "40 CFR § 112.20 — Response plan requirements"
            ],
            rule="epa_spill_response_capacity"
        )
    
    return True, ProofObject(
        conclusion=f"Facility {plan.facility_id} spill response capacity adequate",
        premises=[
            f"Skimmer: {plan.skimmer_capacity_bpd} BPD",
            f"Storage: {plan.storage_capacity_barrels} barrels"
        ],
        rule="epa_spill_response_capacity"
    )


def check_pipeline_incident_rate(pipeline: Pipeline) -> Tuple[bool, ProofObject]:
    """
    PHMSA tracks pipeline incident rates as safety indicator.
    
    Industry average ~0.5 incidents per 1000 miles annually
    Significantly elevated rates trigger investigation
    
    Falsifies if: incident rate > 5 per 1000 miles (10x average)
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_acceptable_rate = Fraction(5)  # 5 per 1000 miles
    
    rate = pipeline.get_incident_rate()
    
    if rate > max_acceptable_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Pipeline {pipeline.pipeline_id} incident rate {rate} per 1000 miles exceeds threshold",
            premises=[
                f"Incidents: {pipeline.incidents_annual}",
                f"Length: {pipeline.length_miles} miles",
                f"Rate: {rate} per 1000 miles",
                f"Fatalities: {pipeline.fatalities_annual}",
                "PHMSA safety performance standards"
            ],
            rule="phmsa_incident_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Pipeline {pipeline.pipeline_id} incident rate within acceptable range",
        premises=[f"Rate: {rate} per 1000 miles"],
        rule="phmsa_incident_rate"
    )


def check_offshore_violation_rate(platform: OffshorePlatform) -> Tuple[bool, ProofObject]:
    """
    BSEE monitors violation rates for offshore platforms.
    
    High violation rates indicate safety culture issues
    Pattern of violations may trigger enforcement
    
    Falsifies if: >2 violations per inspection (pattern of non-compliance)
    
    
    falsifies_if: condition_evaluated_to_false"""
    max_violation_rate = Fraction(2)  # 2 violations per inspection
    
    rate = platform.get_violation_rate()
    
    if platform.bsee_inspections_annual > 0 and rate > max_violation_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Platform {platform.platform_id} violation rate {rate} per inspection indicates systemic issues",
            premises=[
                f"Violations: {platform.violations_issued}",
                f"Inspections: {platform.bsee_inspections_annual}",
                f"Rate: {rate}",
                "30 CFR Part 250 — BSEE enforcement"
            ],
            rule="bsee_violation_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Platform {platform.platform_id} violation rate acceptable",
        premises=[f"Rate: {rate} per inspection"],
        rule="bsee_violation_rate"
    )
