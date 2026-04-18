"""Implementation models for Mechatronics."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MechatronicsClaim:
    """Structured claim parameters for Mechatronics domain invariants."""

    control_loop_closed: bool
    pid_tuning_stable: bool
    encoder_resolution_sufficient: bool
    power_regulated: bool
    pwm_duty_cycle: Fraction


def create_nominal_claim() -> MechatronicsClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return MechatronicsClaim(
        control_loop_closed=True,
        pid_tuning_stable=True,
        encoder_resolution_sufficient=True,
        power_regulated=True,
        pwm_duty_cycle=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "MECHATRONICS",
    "claim_model": "MechatronicsClaim",
    "check_functions": [
        "check_sensor_actuator_loop_closed",
        "check_pid_tuning_stable",
        "check_encoder_resolution_sufficient",
        "check_power_supply_regulation",
        "check_pwm_duty_cycle_fraction",
    ],
}
