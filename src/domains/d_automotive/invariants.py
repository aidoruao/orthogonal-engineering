#!/usr/bin/env python3
"""D_AUTOMOTIVE Invariants — ISO 26262, AUTOSAR, OTA security, CAN bus timing

Automotive functional safety per ISO 26262 requires deterministic safety mechanisms.
All invariants use Fraction arithmetic for exact timing and diagnostic coverage.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    SafetyComponent, OTAUpdate, CANMessage, ADASSystem,
    ASILLevel, ota_signature_required, can_critical_latency_threshold,
    asil_d_diagnostic_threshold, adas_sync_threshold
)


def check_ota_signature(update: OTAUpdate) -> Tuple[bool, ProofObject]:
    """
    ISO/SAE 21434: OTA updates must have valid cryptographic signatures.

    Falsifies if: signature_valid is False
    falsifies_if: signature_valid is False
    """
    required = ota_signature_required()

    if not update.signature_valid:
        return False, ProofObject(
            conclusion=f"VIOLATION: OTA update {update.version} has invalid signature",
            premises=[f"Signature valid: {update.signature_valid}", f"Required: 100%"],
            rule="iso_sae_21434_ota_signature"
        )

    return True, ProofObject(
        conclusion=f"OTA update {update.version} signature valid",
        premises=[f"Signature: {update.signature[:16]}..."],
        rule="iso_sae_21434_ota_signature"
    )


def check_can_latency(message: CANMessage, measured_latency_ms: Fraction) -> Tuple[bool, ProofObject]:
    """
    CAN bus critical messages must have <10ms latency per automotive standards.

    Falsifies if: measured_latency_ms >= 10ms for critical messages
    falsifies_if: measured_latency_ms >= 10ms for critical messages
    """
    if not message.is_critical:
        return True, ProofObject(
            conclusion=f"Non-critical CAN message {message.message_id}",
            premises=[],
            rule="can_latency_non_critical"
        )

    threshold = can_critical_latency_threshold()

    if measured_latency_ms >= threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: CAN message {message.message_id} latency {measured_latency_ms}ms exceeds {threshold}ms",
            premises=[f"Measured: {measured_latency_ms}ms", f"Threshold: {threshold}ms"],
            rule="can_critical_latency"
        )

    return True, ProofObject(
        conclusion=f"CAN message {message.message_id} latency {measured_latency_ms}ms within spec",
        premises=[f"Latency: {measured_latency_ms}ms < {threshold}ms"],
        rule="can_critical_latency"
    )


def check_asil_d_coverage(component: SafetyComponent) -> Tuple[bool, ProofObject]:
    """
    ISO 26262 ASIL-D: Single-Point Fault Metric (SPFM) must exceed 99%.

    Falsifies if: component.asil_level == ASIL-D and spfm < 99%
    falsifies_if: component.asil_level == ASIL-D and spfm < 99%
    """
    if component.asil_level != ASILLevel.D:
        return True, ProofObject(
            conclusion=f"Component {component.component_id} is {component.asil_level.name}, not ASIL-D",
            premises=[],
            rule="asil_d_not_applicable"
        )

    threshold = asil_d_diagnostic_threshold()
    coverage_fraction = component.spfm / Fraction(100)

    if coverage_fraction < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: ASIL-D component {component.component_id} SPFM {component.spfm}% < 99.9%",
            premises=[
                f"SPFM: {component.spfm}%",
                f"Required: {threshold * 100}%"
            ],
            rule="iso_26262_asil_d_spfm"
        )

    return True, ProofObject(
        conclusion=f"ASIL-D component {component.component_id} SPFM {component.spfm}% adequate",
        premises=[f"SPFM: {component.spfm}% >= 99.9%"],
        rule="iso_26262_asil_d_spfm"
    )


def check_adas_sensor_sync(adas: ADASSystem) -> Tuple[bool, ProofObject]:
    """
    ADAS sensor fusion requires synchronized timestamps within 1ms.

    Falsifies if: sensor_fusion_latency_ms > 1ms
    falsifies_if: sensor_fusion_latency_ms > 1ms
    """
    threshold = adas_sync_threshold()

    if adas.sensor_fusion_latency_ms > threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: ADAS {adas.system_name} sensor sync {adas.sensor_fusion_latency_ms}ms exceeds {threshold}ms",
            premises=[
                f"Latency: {adas.sensor_fusion_latency_ms}ms",
                f"Threshold: {threshold}ms"
            ],
            rule="adas_sensor_synchronization"
        )

    return True, ProofObject(
        conclusion=f"ADAS {adas.system_name} sensor sync {adas.sensor_fusion_latency_ms}ms within spec",
        premises=[f"Sync latency: {adas.sensor_fusion_latency_ms}ms <= {threshold}ms"],
        rule="adas_sensor_synchronization"
    )


def check_autosar_determinism(component: SafetyComponent) -> Tuple[bool, ProofObject]:
    """
    AUTOSAR Adaptive Platform requires deterministic WCET for safety components.

    Falsifies if: latency_ms varies or exceeds design budget
    falsifies_if: latency_ms varies or exceeds design budget
    """
    # For ASIL-C and above, latency must be strictly bounded
    if component.asil_level.value >= ASILLevel.C.value:
        # Check if latency is within deterministic bound (assume 50ms design budget)
        design_budget = Fraction(50, 1)

        if component.latency_ms > design_budget:
            return False, ProofObject(
                conclusion=f"VIOLATION: Component {component.component_id} latency {component.latency_ms}ms exceeds WCET budget {design_budget}ms",
                premises=[
                    f"Measured latency: {component.latency_ms}ms",
                    f"WCET budget: {design_budget}ms",
                    f"ASIL level: {component.asil_level.name}"
                ],
                rule="autosar_wcet_determinism"
            )

    return True, ProofObject(
        conclusion=f"Component {component.component_id} meets AUTOSAR determinism requirements",
        premises=[f"Latency: {component.latency_ms}ms", f"ASIL: {component.asil_level.name}"],
        rule="autosar_wcet_determinism"
    )


def run_all_invariants() -> dict:
    """Run all D_AUTOMOTIVE invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    adas_system = ADASSystem(
        system_name=None,
        sensor_fusion_latency_ms=Fraction(1),
        lidar_points=None,
        radar_targets=None,
        camera_frames_per_sec=Fraction(1),
    )
    safety_component = SafetyComponent(
        component_id=None,
        asil_level=ASILLevel.QM,
        diagnostic_coverage=Fraction(100),
        spfm=Fraction(1),
        latency_ms=Fraction(1),
    )
    can_message = CANMessage(
        message_id=None,
        data=None,
        timestamp_us=None,
        is_critical=None,
    )
    ota_update = OTAUpdate(
        version=None,
        signature=None,
        signature_valid=None,
        rollback_supported=None,
    )

    checks = [
        ("check_adas_sensor_sync", lambda: check_adas_sensor_sync(adas_system)),
        ("check_asil_d_coverage", lambda: check_asil_d_coverage(safety_component)),
        ("check_autosar_determinism", lambda: check_autosar_determinism(safety_component)),
        ("check_can_latency", lambda: check_can_latency(can_message, Fraction(1))),
        ("check_ota_signature", lambda: check_ota_signature(ota_update)),
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
    print("All D_AUTOMOTIVE invariants: PASS")
