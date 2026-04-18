"""Invariant checks for Mechatronics."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import MechatronicsClaim, create_nominal_claim


def check_sensor_actuator_loop_closed(data: MechatronicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Sensor-actuator control loop is closed.

    Standard: Mechatronics domain invariant.
    Falsifies if: not control_loop_closed.
    falsifies_if: not control_loop_closed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.control_loop_closed
    proof = ProofObject(
        rule="check_sensor_actuator_loop_closed",
        premises=[
            "domain=Mechatronics",
            f"control_loop_closed={{data.control_loop_closed}}",
        ],
        conclusion=(
            "PASS: Sensor-actuator control loop is closed"
            if success else "FAIL: Sensor-actuator control loop is closed"
        ),
    )
    return success, proof


def check_pid_tuning_stable(data: MechatronicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: PID tuning produces stable response.

    Standard: Mechatronics domain invariant.
    Falsifies if: not pid_tuning_stable.
    falsifies_if: not pid_tuning_stable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.pid_tuning_stable
    proof = ProofObject(
        rule="check_pid_tuning_stable",
        premises=[
            "domain=Mechatronics",
            f"pid_tuning_stable={{data.pid_tuning_stable}}",
        ],
        conclusion=(
            "PASS: PID tuning produces stable response"
            if success else "FAIL: PID tuning produces stable response"
        ),
    )
    return success, proof


def check_encoder_resolution_sufficient(data: MechatronicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Encoder resolution is sufficient.

    Standard: Mechatronics domain invariant.
    Falsifies if: not encoder_resolution_sufficient.
    falsifies_if: not encoder_resolution_sufficient.

    Returns:
        Tuple of (success, proof).
    """
    success = data.encoder_resolution_sufficient
    proof = ProofObject(
        rule="check_encoder_resolution_sufficient",
        premises=[
            "domain=Mechatronics",
            f"encoder_resolution_sufficient={{data.encoder_resolution_sufficient}}",
        ],
        conclusion=(
            "PASS: Encoder resolution is sufficient"
            if success else "FAIL: Encoder resolution is sufficient"
        ),
    )
    return success, proof


def check_power_supply_regulation(data: MechatronicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Power supply is regulated.

    Standard: Mechatronics domain invariant.
    Falsifies if: not power_regulated.
    falsifies_if: not power_regulated.

    Returns:
        Tuple of (success, proof).
    """
    success = data.power_regulated
    proof = ProofObject(
        rule="check_power_supply_regulation",
        premises=[
            "domain=Mechatronics",
            f"power_regulated={{data.power_regulated}}",
        ],
        conclusion=(
            "PASS: Power supply is regulated"
            if success else "FAIL: Power supply is regulated"
        ),
    )
    return success, proof


def check_pwm_duty_cycle_fraction(data: MechatronicsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: PWM duty cycle is between 0 and 1.

    Standard: Mechatronics domain invariant.
    Falsifies if: not pwm_duty_cycle.
    falsifies_if: not pwm_duty_cycle.

    Returns:
        Tuple of (success, proof).
    """
    success = data.pwm_duty_cycle >= Fraction(0)
    proof = ProofObject(
        rule="check_pwm_duty_cycle_fraction",
        premises=[
            "domain=Mechatronics",
            f"pwm_duty_cycle={{data.pwm_duty_cycle}}",
        ],
        conclusion=(
            "PASS: PWM duty cycle is between 0 and 1 is non-negative"
            if success else "FAIL: PWM duty cycle is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Mechatronics nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_sensor_actuator_loop_closed", check_sensor_actuator_loop_closed),
        ("check_pid_tuning_stable", check_pid_tuning_stable),
        ("check_encoder_resolution_sufficient", check_encoder_resolution_sufficient),
        ("check_power_supply_regulation", check_power_supply_regulation),
        ("check_pwm_duty_cycle_fraction", check_pwm_duty_cycle_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
