"""PHOTONIC EMC — EMI radiated/conducted, ESD immunity, power supply ripple,
jitter, optical crosstalk.

Category 10: EMC & Signal Integrity (checks 61-66).

Standards: FCC Part 15, CISPR 32, IEC 61000-4-2, IEEE 802.3, ITU-T G.694.1, Custom OE.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class EmissionProfile:
    """Radiated EMI parameters per FCC Part 15 / CISPR 32.

    falsifies_if: emission_dbm is positive (above 0 dBm is physically implausible for emission limit).
    falsifies_if: emission_dbm is positive.
    """
    component_id: str
    emission_dbm: Fraction


@dataclass(frozen=True)
class ConductedEmission:
    """Conducted EMI parameters per CISPR 32.

    falsifies_if: conducted_dbm is positive.
    falsifies_if: conducted_dbm is positive.
    """
    component_id: str
    conducted_dbm: Fraction


@dataclass(frozen=True)
class EsdImmunity:
    """ESD immunity parameters per IEC 61000-4-2.

    falsifies_if: withstand_kv is negative.
    falsifies_if: withstand_kv is negative.
    """
    component_id: str
    withstand_kv: Fraction


@dataclass(frozen=True)
class PowerSupply:
    """Power supply ripple parameters.

    falsifies_if: ripple_mv is negative.
    falsifies_if: ripple_mv is negative.
    """
    supply_id: str
    ripple_mv: Fraction


@dataclass(frozen=True)
class JitterProfile:
    """Jitter parameters per IEEE 802.3.

    falsifies_if: total_jitter_ps is negative.
    falsifies_if: total_jitter_ps is negative.
    """
    component_id: str
    total_jitter_ps: Fraction


@dataclass(frozen=True)
class OpticalCrosstalk:
    """Optical crosstalk parameters per ITU-T G.694.1.

    falsifies_if: adjacent_channel_isolation_db is negative.
    falsifies_if: adjacent_channel_isolation_db is negative.
    """
    channel_id: str
    adjacent_channel_isolation_db: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def radiated_emission_limit() -> Fraction:
    """FCC Part 15 / CISPR 32 radiated emission limit at 3m: -47 dBm."""
    # TODO: Expand radiated_emission_limit() - stub detected by Yeshua Agent
    return Fraction(-47, 1)


def conducted_emission_limit() -> Fraction:
    """CISPR 32 conducted emission limit: -40 dBm."""
    # TODO: Expand conducted_emission_limit() - stub detected by Yeshua Agent
    return Fraction(-40, 1)


def esd_immunity_threshold() -> Fraction:
    """IEC 61000-4-2 minimum ESD withstand: 8 kV contact discharge."""
    # TODO: Expand esd_immunity_threshold() - stub detected by Yeshua Agent
    return Fraction(8, 1)


def ripple_threshold_mv() -> Fraction:
    """Custom OE maximum power supply ripple: 50 mV pk-pk."""
    # TODO: Expand ripple_threshold_mv() - stub detected by Yeshua Agent
    return Fraction(50, 1)


def jitter_threshold_ps() -> Fraction:
    """IEEE 802.3 total jitter at BER 10^-12: 28 ps."""
    # TODO: Expand jitter_threshold_ps() - stub detected by Yeshua Agent
    return Fraction(28, 1)


def crosstalk_isolation_threshold() -> Fraction:
    """ITU-T G.694.1 minimum adjacent channel isolation: 25 dB."""
    # TODO: Expand crosstalk_isolation_threshold() - stub detected by Yeshua Agent
    return Fraction(25, 1)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_emi_radiated(profile: EmissionProfile) -> Tuple[bool, ProofObject]:
    """Radiated emission must not exceed -47 dBm at 3m per FCC Part 15 / CISPR 32.

    Falsifies if: emission_dbm > Fraction(-47, 1).
    falsifies_if: emission_dbm > Fraction(-47, 1).
    """
    limit = radiated_emission_limit()
    if profile.emission_dbm > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.component_id} radiated emission {profile.emission_dbm} dBm > "
                f"limit {limit} dBm"
            ),
            premises=[
                f"Emission: {profile.emission_dbm} dBm",
                f"Limit: {limit} dBm",
            ],
            rule="fcc_cispr_radiated_emi",
        )
    return True, ProofObject(
        conclusion=f"{profile.component_id} radiated emission {profile.emission_dbm} dBm <= {limit} dBm",
        premises=[f"Emission: {profile.emission_dbm} dBm <= {limit} dBm"],
        rule="fcc_cispr_radiated_emi",
    )


def check_emi_conducted(emission: ConductedEmission) -> Tuple[bool, ProofObject]:
    """Conducted emission must not exceed -40 dBm per CISPR 32.

    Falsifies if: conducted_dbm > Fraction(-40, 1).
    falsifies_if: conducted_dbm > Fraction(-40, 1).
    """
    limit = conducted_emission_limit()
    if emission.conducted_dbm > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {emission.component_id} conducted emission {emission.conducted_dbm} dBm > "
                f"limit {limit} dBm"
            ),
            premises=[
                f"Conducted: {emission.conducted_dbm} dBm",
                f"Limit: {limit} dBm",
            ],
            rule="cispr_conducted_emi",
        )
    return True, ProofObject(
        conclusion=f"{emission.component_id} conducted emission {emission.conducted_dbm} dBm <= {limit} dBm",
        premises=[f"Conducted: {emission.conducted_dbm} dBm <= {limit} dBm"],
        rule="cispr_conducted_emi",
    )


def check_esd_immunity(immunity: EsdImmunity) -> Tuple[bool, ProofObject]:
    """ESD immunity must withstand at least 8 kV contact discharge per IEC 61000-4-2.

    Falsifies if: withstand_kv < Fraction(8, 1).
    falsifies_if: withstand_kv < Fraction(8, 1).
    """
    limit = esd_immunity_threshold()
    if immunity.withstand_kv < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {immunity.component_id} ESD withstand {immunity.withstand_kv} kV < "
                f"minimum {limit} kV"
            ),
            premises=[
                f"Withstand: {immunity.withstand_kv} kV",
                f"Minimum: {limit} kV",
            ],
            rule="iec_61000_4_2_esd",
        )
    return True, ProofObject(
        conclusion=f"{immunity.component_id} ESD withstand {immunity.withstand_kv} kV >= {limit} kV",
        premises=[f"Withstand: {immunity.withstand_kv} kV >= {limit} kV"],
        rule="iec_61000_4_2_esd",
    )


def check_power_supply_ripple(supply: PowerSupply) -> Tuple[bool, ProofObject]:
    """Power supply ripple must not exceed 50 mV pk-pk (Custom OE).

    Falsifies if: ripple_mv > Fraction(50, 1).
    falsifies_if: ripple_mv > Fraction(50, 1).
    """
    limit = ripple_threshold_mv()
    if supply.ripple_mv > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {supply.supply_id} ripple {supply.ripple_mv} mV > "
                f"limit {limit} mV"
            ),
            premises=[
                f"Ripple: {supply.ripple_mv} mV",
                f"Limit: {limit} mV",
            ],
            rule="oe_supply_ripple",
        )
    return True, ProofObject(
        conclusion=f"{supply.supply_id} ripple {supply.ripple_mv} mV <= {limit} mV",
        premises=[f"Ripple: {supply.ripple_mv} mV <= {limit} mV"],
        rule="oe_supply_ripple",
    )


def check_jitter(profile: JitterProfile) -> Tuple[bool, ProofObject]:
    """Total jitter must not exceed 28 ps at BER 10^-12 per IEEE 802.3.

    Falsifies if: total_jitter_ps > Fraction(28, 1).
    falsifies_if: total_jitter_ps > Fraction(28, 1).
    """
    limit = jitter_threshold_ps()
    if profile.total_jitter_ps > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {profile.component_id} jitter {profile.total_jitter_ps} ps > "
                f"limit {limit} ps"
            ),
            premises=[
                f"Jitter: {profile.total_jitter_ps} ps",
                f"Limit: {limit} ps",
            ],
            rule="ieee_802_3_jitter",
        )
    return True, ProofObject(
        conclusion=f"{profile.component_id} jitter {profile.total_jitter_ps} ps <= {limit} ps",
        premises=[f"Jitter: {profile.total_jitter_ps} ps <= {limit} ps"],
        rule="ieee_802_3_jitter",
    )


def check_optical_crosstalk(ct: OpticalCrosstalk) -> Tuple[bool, ProofObject]:
    """Adjacent channel isolation must be at least 25 dB per ITU-T G.694.1.

    Falsifies if: adjacent_channel_isolation_db < Fraction(25, 1).
    falsifies_if: adjacent_channel_isolation_db < Fraction(25, 1).
    """
    limit = crosstalk_isolation_threshold()
    if ct.adjacent_channel_isolation_db < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {ct.channel_id} isolation {ct.adjacent_channel_isolation_db} dB < "
                f"minimum {limit} dB"
            ),
            premises=[
                f"Isolation: {ct.adjacent_channel_isolation_db} dB",
                f"Minimum: {limit} dB",
            ],
            rule="itu_g6941_crosstalk",
        )
    return True, ProofObject(
        conclusion=f"{ct.channel_id} isolation {ct.adjacent_channel_isolation_db} dB >= {limit} dB",
        premises=[f"Isolation: {ct.adjacent_channel_isolation_db} dB >= {limit} dB"],
        rule="itu_g6941_crosstalk",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all EMC checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_rad = EmissionProfile(component_id="pass_rad", emission_dbm=Fraction(-55, 1))
    fail_rad = EmissionProfile(component_id="fail_rad", emission_dbm=Fraction(-40, 1))
    pass_cond = ConductedEmission(component_id="pass_cond", conducted_dbm=Fraction(-50, 1))
    fail_cond = ConductedEmission(component_id="fail_cond", conducted_dbm=Fraction(-35, 1))
    pass_esd = EsdImmunity(component_id="pass_esd", withstand_kv=Fraction(10, 1))
    fail_esd = EsdImmunity(component_id="fail_esd", withstand_kv=Fraction(4, 1))
    pass_ripple = PowerSupply(supply_id="pass_ripple", ripple_mv=Fraction(30, 1))
    fail_ripple = PowerSupply(supply_id="fail_ripple", ripple_mv=Fraction(70, 1))
    pass_jit = JitterProfile(component_id="pass_jit", total_jitter_ps=Fraction(20, 1))
    fail_jit = JitterProfile(component_id="fail_jit", total_jitter_ps=Fraction(35, 1))
    pass_xt = OpticalCrosstalk(channel_id="pass_xt", adjacent_channel_isolation_db=Fraction(30, 1))
    fail_xt = OpticalCrosstalk(channel_id="fail_xt", adjacent_channel_isolation_db=Fraction(20, 1))

    checks = [
        ("check_emi_radiated_pass", lambda: check_emi_radiated(pass_rad)),
        ("check_emi_radiated_fail", lambda: check_emi_radiated(fail_rad)),
        ("check_emi_conducted_pass", lambda: check_emi_conducted(pass_cond)),
        ("check_emi_conducted_fail", lambda: check_emi_conducted(fail_cond)),
        ("check_esd_immunity_pass", lambda: check_esd_immunity(pass_esd)),
        ("check_esd_immunity_fail", lambda: check_esd_immunity(fail_esd)),
        ("check_power_supply_ripple_pass", lambda: check_power_supply_ripple(pass_ripple)),
        ("check_power_supply_ripple_fail", lambda: check_power_supply_ripple(fail_ripple)),
        ("check_jitter_pass", lambda: check_jitter(pass_jit)),
        ("check_jitter_fail", lambda: check_jitter(fail_jit)),
        ("check_optical_crosstalk_pass", lambda: check_optical_crosstalk(pass_xt)),
        ("check_optical_crosstalk_fail", lambda: check_optical_crosstalk(fail_xt)),
    ]

    results = []
    for name, func in checks:
        try:
            ok, proof = func()
            results.append((name, ok, proof))
        except Exception as exc:
            fake_proof = ProofObject(
                conclusion=f"ERROR in {name}: {exc}",
                premises=[],
                rule=name,
            )
            results.append((name, False, fake_proof))

    return results
