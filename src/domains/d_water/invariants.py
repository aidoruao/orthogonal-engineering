"""D_WATER Invariants — Safe Drinking Water Act (SDWA), Clean Water Act

Verifies EPA drinking water standards, lead/copper rule compliance,
Consumer Confidence Report delivery, NPDES wastewater discharge limits.

Standards: 42 U.S.C. § 300f (SDWA), 33 U.S.C. § 1251 (CWA)
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    WaterQualitySample, WaterUtility, WastewaterDischarge,
    WaterSourceType, epa_lead_action_level, epa_copper_action_level, epa_ph_range
)


def check_lead_copper_rule(sample: WaterQualitySample) -> Tuple[bool, ProofObject]:
    """
    EPA Lead and Copper Rule requires action if levels exceed thresholds.
    
    40 CFR § 141.80:
    - Lead action level: 0.015 mg/L (15 ppb)
    - Copper action level: 1.3 mg/L (1300 ppb)
    - 90th percentile of samples must be below action level
    
    Falsifies if: lead > 0.015 mg/L or copper > 1.3 mg/L
    falsifies_if: lead > 0.015 mg/L or copper > 1.3 mg/L
    """
    lead_limit = epa_lead_action_level()
    copper_limit = epa_copper_action_level()
    
    violations = []
    
    if sample.lead_level > lead_limit:
        violations.append(f"Lead {sample.lead_level} mg/L exceeds {lead_limit} mg/L")
    
    if sample.copper_level > copper_limit:
        violations.append(f"Copper {sample.copper_level} mg/L exceeds {copper_limit} mg/L")
    
    if violations:
        return False, ProofObject(
            conclusion=f"VIOLATION: Sample {sample.sample_id} Lead and Copper Rule violations: {'; '.join(violations)}",
            premises=[
                f"Sample ID: {sample.sample_id}",
                f"Lead: {sample.lead_level} mg/L",
                f"Copper: {sample.copper_level} mg/L",
                "40 CFR § 141.80 — Lead and Copper Rule"
            ],
            rule="sdwa_lead_copper_rule"
        )
    
    return True, ProofObject(
        conclusion=f"Sample {sample.sample_id} meets Lead and Copper Rule requirements",
        premises=[f"Lead: {sample.lead_level}", f"Copper: {sample.copper_level}"],
        rule="sdwa_lead_copper_rule"
    )


def check_ph_compliance(sample: WaterQualitySample) -> Tuple[bool, ProofObject]:
    """
    EPA National Secondary Drinking Water Regulations specify pH range.
    
    40 CFR § 143.3:
    - Recommended pH range: 6.5 - 8.5
    - Outside this range may cause taste/odor issues, corrosion
    
    Falsifies if: pH < 6.5 or pH > 8.5
    falsifies_if: pH < 6.5 or pH > 8.5
    """
    ph_min, ph_max = epa_ph_range()
    
    if sample.ph_level < ph_min or sample.ph_level > ph_max:
        return False, ProofObject(
            conclusion=f"VIOLATION: Sample {sample.sample_id} pH {sample.ph_level} outside acceptable range {ph_min}-{ph_max}",
            premises=[
                f"pH: {sample.ph_level}",
                f"Acceptable range: {ph_min} to {ph_max}",
                "40 CFR § 143.3 — Secondary drinking water standards"
            ],
            rule="sdwa_ph_range"
        )
    
    return True, ProofObject(
        conclusion=f"Sample {sample.sample_id} pH within acceptable range",
        premises=[f"pH: {sample.ph_level}", f"Range: {ph_min}-{ph_max}"],
        rule="sdwa_ph_range"
    )


def check_microbial_compliance(sample: WaterQualitySample) -> Tuple[bool, ProofObject]:
    """
    EPA Total Coliform Rule and E. coli standards.
    
    40 CFR § 141.21:
    - E. coli: MCL (Maximum Contaminant Level) = 0
    - Total coliform: Presence/absence-based detection
    - Repeat sampling required after positive results
    
    Falsifies if: E. coli detected
    falsifies_if: E. coli detected
    """
    if sample.e_coli_detected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Sample {sample.sample_id} E. coli detected — acute health risk",
            premises=[
                f"E. coli: DETECTED",
                f"Total coliform count: {sample.total_coliform_count}",
                "40 CFR § 141.21 — Total Coliform Rule"
            ],
            rule="sdwa_microbial_standards"
        )
    
    # Warning for high total coliform
    if sample.total_coliform_count > 0:
        return True, ProofObject(
            conclusion=f"Sample {sample.sample_id} total coliform detected but E. coli negative — monitoring required",
            premises=[
                f"Total coliform: {sample.total_coliform_count}",
                f"E. coli: NOT DETECTED"
            ],
            rule="sdwa_microbial_standards"
        )
    
    return True, ProofObject(
        conclusion=f"Sample {sample.sample_id} microbial compliance verified",
        premises=["E. coli: NOT DETECTED", f"Total coliform: {sample.total_coliform_count}"],
        rule="sdwa_microbial_standards"
    )


def check_consumer_confidence_report(utility: WaterUtility) -> Tuple[bool, ProofObject]:
    """
    SDWA requires annual Consumer Confidence Report (CCR) delivery.
    
    40 CFR § 141.152:
    - CCR must be delivered annually by July 1
    - Must include detected contaminants, compliance status
    - Required for all community water systems
    
    Falsifies if: CCR not delivered for systems serving >1000 people
    falsifies_if: CCR not delivered for systems serving >1000 people
    """
    min_population_for_ccr = Fraction(1000)
    
    if utility.population_served < min_population_for_ccr:
        return True, ProofObject(
            conclusion=f"Utility {utility.system_name} exempt from CCR (population {utility.population_served} < {min_population_for_ccr})",
            premises=[f"Population: {utility.population_served}"],
            rule="sdwa_ccr_exemption"
        )
    
    if not utility.ccr_delivered:
        return False, ProofObject(
            conclusion=f"VIOLATION: Utility {utility.system_name} failed to deliver Consumer Confidence Report",
            premises=[
                f"System: {utility.utility_id}",
                f"Population: {utility.population_served}",
                "CCR delivered: NO",
                "40 CFR § 141.152 — Consumer Confidence Report"
            ],
            rule="sdwa_ccr_requirement"
        )
    
    return True, ProofObject(
        conclusion=f"Utility {utility.system_name} CCR delivery verified",
        premises=[f"Delivery date: {utility.ccr_delivery_date}"],
        rule="sdwa_ccr_requirement"
    )


def check_npdes_discharge_limits(discharge: WastewaterDischarge) -> Tuple[bool, ProofObject]:
    """
    Clean Water Act NPDES permit requires meeting discharge limits.
    
    33 U.S.C. § 1342:
    - NPDES permit specifies effluent limitations
    - Technology-based and water quality-based limits
    - Discharge Monitoring Reports (DMRs) required
    
    Falsifies if: actual > limit for any parameter
    falsifies_if: actual > limit for any parameter
    """
    violations = []
    
    if discharge.bod_actual > discharge.bod_limit:
        violations.append(f"BOD {discharge.bod_actual} > {discharge.bod_limit}")
    
    if discharge.tss_actual > discharge.tss_limit:
        violations.append(f"TSS {discharge.tss_actual} > {discharge.tss_limit}")
    
    if violations:
        return False, ProofObject(
            conclusion=f"VIOLATION: Discharge {discharge.permit_id} exceeds NPDES limits: {'; '.join(violations)}",
            premises=[
                f"Permit: {discharge.permit_id}",
                f"Violations: {discharge.permit_violations_annual}",
                "33 U.S.C. § 1342 — NPDES permits"
            ],
            rule="cwa_npdes_limits"
        )
    
    return True, ProofObject(
        conclusion=f"Discharge {discharge.permit_id} meets NPDES permit limits",
        premises=[
            f"BOD: {discharge.bod_actual} <= {discharge.bod_limit}",
            f"TSS: {discharge.tss_actual} <= {discharge.tss_limit}"
        ],
        rule="cwa_npdes_limits"
    )


def check_lead_service_line_replacement(utility: WaterUtility) -> Tuple[bool, ProofObject]:
    """
    EPA Lead and Copper Rule requires lead service line replacement at action level.
    
    40 CFR § 141.84:
    - If lead action level exceeded, replacement required
    - Must replace 7% per year until compliance
    - Full inventory of lead service lines required
    
    Falsifies if: lead lines exist but replacement rate < 7% annually
    falsifies_if: lead lines exist but replacement rate < 7% annually
    """
    required_annual_rate = Fraction(7, 100)  # 7% per year
    
    if utility.estimated_lead_service_lines == 0:
        return True, ProofObject(
            conclusion=f"Utility {utility.system_name} has no lead service lines",
            premises=["Lead service lines: 0"],
            rule="sdwa_lead_service_line_exemption"
        )
    
    replacement_rate = utility.get_lead_replacement_rate()
    
    # Check if at least 7% annual replacement rate maintained
    if replacement_rate < required_annual_rate and utility.estimated_lead_service_lines > 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: Utility {utility.system_name} lead service line replacement rate {replacement_rate} below required {required_annual_rate}",
            premises=[
                f"Lead lines: {utility.estimated_lead_service_lines}",
                f"Replaced: {utility.lead_service_lines_replaced}",
                f"Rate: {replacement_rate}",
                "40 CFR § 141.84 — Lead service line replacement"
            ],
            rule="sdwa_lead_service_line_replacement"
        )
    
    return True, ProofObject(
        conclusion=f"Utility {utility.system_name} lead service line replacement on track",
        premises=[
            f"Lead lines: {utility.estimated_lead_service_lines}",
            f"Replaced: {utility.lead_service_lines_replaced}",
            f"Rate: {replacement_rate}"
        ],
        rule="sdwa_lead_service_line_replacement"
    )


def run_all_invariants() -> dict:
    """Run all D_WATER invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    water_utility = WaterUtility(
        utility_id=None,
        system_name=None,
        population_served=Fraction(1),
        source_type=WaterSourceType.SURFACE_WATER,
        annual_compliance_violations=None,
        health_based_violations=None,
        monitoring_violations=None,
        reporting_violations=None,
        ccr_delivered=None,
        ccr_delivery_date=None,
        estimated_lead_service_lines=Fraction(1),
        lead_service_lines_replaced=Fraction(1),
    )
    water_quality_sample = WaterQualitySample(
        sample_id=None,
        facility_id=None,
        source_type=WaterSourceType.SURFACE_WATER,
        sample_date=None,
        lead_level=Fraction(1),
        copper_level=Fraction(1),
        chlorine_residual=Fraction(1),
        ph_level=Fraction(1),
        turbidity=Fraction(1),
        e_coli_detected=None,
        total_coliform_count=None,
    )
    wastewater_discharge = WastewaterDischarge(
        permit_id=None,
        facility_id=None,
        flow_rate_mgd=Fraction(1),
        bod_limit=Fraction(1000),
        bod_actual=Fraction(1),
        tss_limit=Fraction(1000),
        tss_actual=Fraction(1),
        permit_violations_annual=None,
        enforcement_actions=None,
    )

    checks = [
        ("check_consumer_confidence_report", lambda: check_consumer_confidence_report(water_utility)),
        ("check_lead_copper_rule", lambda: check_lead_copper_rule(water_quality_sample)),
        ("check_lead_service_line_replacement", lambda: check_lead_service_line_replacement(water_utility)),
        ("check_microbial_compliance", lambda: check_microbial_compliance(water_quality_sample)),
        ("check_npdes_discharge_limits", lambda: check_npdes_discharge_limits(wastewater_discharge)),
        ("check_ph_compliance", lambda: check_ph_compliance(water_quality_sample)),
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
    print("All D_WATER invariants: PASS")
