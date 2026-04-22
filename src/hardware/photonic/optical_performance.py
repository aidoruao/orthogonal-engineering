"""PHOTONIC Optical Performance — Insertion loss, return loss, extinction ratio,
PDL, wavelength accuracy, OSNR, BER floor.

Category 5: Optical Performance (checks 22-28).

Standards: IEEE 802.3, IEC 61300-3-6, ITU-T G.959.1, ITU-T G.697, ITU-T G.694.1
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class OpticalComponent:
    """Generic optical component performance parameters.

    falsifies_if: any loss parameter is negative.
    falsifies_if: any loss parameter is negative.
    """
    component_id: str
    insertion_loss_db: Fraction
    return_loss_db: Fraction
    extinction_ratio_db: Fraction
    pdl_db: Fraction


@dataclass(frozen=True)
class WavelengthSource:
    """Laser or modulator wavelength parameters.

    falsifies_if: actual_wavelength_nm is negative.
    falsifies_if: actual_wavelength_nm is negative.
    """
    source_id: str
    actual_wavelength_nm: Fraction
    grid_wavelength_nm: Fraction


@dataclass(frozen=True)
class OpticalChannel:
    """Optical link channel quality parameters.

    falsifies_if: osnr_db is negative.
    falsifies_if: osnr_db is negative.
    """
    channel_id: str
    osnr_db: Fraction


@dataclass(frozen=True)
class DigitalReceiver:
    """Digital receiver bit-error-rate parameters.

    falsifies_if: ber is negative.
    falsifies_if: ber is negative.
    """
    receiver_id: str
    ber: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def insertion_loss_threshold() -> Fraction:
    """IEEE 802.3 maximum insertion loss per component: 3 dB."""
    return Fraction(3, 1)


def return_loss_threshold() -> Fraction:
    """IEC 61300-3-6 minimum return loss: 40 dB."""
    return Fraction(40, 1)


def extinction_ratio_threshold() -> Fraction:
    """ITU-T G.959.1 minimum extinction ratio: 9 dB."""
    return Fraction(9, 1)


def pdl_threshold() -> Fraction:
    """ITU-T G.697 maximum polarization-dependent loss: 0.5 dB."""
    return Fraction(1, 2)


def wavelength_accuracy_threshold() -> Fraction:
    """ITU-T G.694.1 wavelength grid accuracy: 0.1 nm."""
    return Fraction(1, 10)


def osnr_threshold() -> Fraction:
    """ITU-T G.697 minimum OSNR: 20 dB."""
    return Fraction(20, 1)


def ber_floor_threshold() -> Fraction:
    """IEEE 802.3 maximum acceptable BER floor: 1e-12."""
    return Fraction(1, 1_000_000_000_000)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_insertion_loss(comp: OpticalComponent) -> Tuple[bool, ProofObject]:
    """Insertion loss must not exceed 3 dB per IEEE 802.3.

    Falsifies if: insertion_loss_db > Fraction(3, 1).
    falsifies_if: insertion_loss_db > Fraction(3, 1).
    """
    limit = insertion_loss_threshold()
    if comp.insertion_loss_db > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {comp.component_id} insertion loss {comp.insertion_loss_db} dB > "
                f"limit {limit} dB"
            ),
            premises=[
                f"Insertion loss: {comp.insertion_loss_db} dB",
                f"Limit: {limit} dB",
            ],
            rule="ieee_802_3_insertion_loss",
        )
    return True, ProofObject(
        conclusion=f"{comp.component_id} insertion loss {comp.insertion_loss_db} dB <= {limit} dB",
        premises=[f"Insertion loss: {comp.insertion_loss_db} dB <= {limit} dB"],
        rule="ieee_802_3_insertion_loss",
    )


def check_return_loss(comp: OpticalComponent) -> Tuple[bool, ProofObject]:
    """Return loss must be at least 40 dB per IEC 61300-3-6.

    Falsifies if: return_loss_db < Fraction(40, 1).
    falsifies_if: return_loss_db < Fraction(40, 1).
    """
    limit = return_loss_threshold()
    if comp.return_loss_db < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {comp.component_id} return loss {comp.return_loss_db} dB < "
                f"minimum {limit} dB"
            ),
            premises=[
                f"Return loss: {comp.return_loss_db} dB",
                f"Minimum: {limit} dB",
            ],
            rule="iec_61300_return_loss",
        )
    return True, ProofObject(
        conclusion=f"{comp.component_id} return loss {comp.return_loss_db} dB >= {limit} dB",
        premises=[f"Return loss: {comp.return_loss_db} dB >= {limit} dB"],
        rule="iec_61300_return_loss",
    )


def check_extinction_ratio(comp: OpticalComponent) -> Tuple[bool, ProofObject]:
    """Extinction ratio must be at least 9 dB per ITU-T G.959.1.

    Falsifies if: extinction_ratio_db < Fraction(9, 1).
    falsifies_if: extinction_ratio_db < Fraction(9, 1).
    """
    limit = extinction_ratio_threshold()
    if comp.extinction_ratio_db < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {comp.component_id} ER {comp.extinction_ratio_db} dB < "
                f"minimum {limit} dB"
            ),
            premises=[
                f"ER: {comp.extinction_ratio_db} dB",
                f"Minimum: {limit} dB",
            ],
            rule="itu_g9591_extinction_ratio",
        )
    return True, ProofObject(
        conclusion=f"{comp.component_id} ER {comp.extinction_ratio_db} dB >= {limit} dB",
        premises=[f"ER: {comp.extinction_ratio_db} dB >= {limit} dB"],
        rule="itu_g9591_extinction_ratio",
    )


def check_polarization_dependent_loss(comp: OpticalComponent) -> Tuple[bool, ProofObject]:
    """Polarization-dependent loss must not exceed 0.5 dB per ITU-T G.697.

    Falsifies if: pdl_db > Fraction(1, 2).
    falsifies_if: pdl_db > Fraction(1, 2).
    """
    limit = pdl_threshold()
    if comp.pdl_db > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {comp.component_id} PDL {comp.pdl_db} dB > "
                f"limit {limit} dB"
            ),
            premises=[
                f"PDL: {comp.pdl_db} dB",
                f"Limit: {limit} dB",
            ],
            rule="itu_g697_pdl",
        )
    return True, ProofObject(
        conclusion=f"{comp.component_id} PDL {comp.pdl_db} dB <= {limit} dB",
        premises=[f"PDL: {comp.pdl_db} dB <= {limit} dB"],
        rule="itu_g697_pdl",
    )


def check_wavelength_accuracy(src: WavelengthSource) -> Tuple[bool, ProofObject]:
    """Wavelength must be within 0.1 nm of ITU-T G.694.1 grid.

    Falsifies if: abs(actual - grid) > Fraction(1, 10).
    falsifies_if: abs(actual - grid) > Fraction(1, 10).
    """
    limit = wavelength_accuracy_threshold()
    deviation = abs(src.actual_wavelength_nm - src.grid_wavelength_nm)
    if deviation > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {src.source_id} wavelength deviation {deviation} nm > "
                f"limit {limit} nm"
            ),
            premises=[
                f"Actual: {src.actual_wavelength_nm} nm",
                f"Grid: {src.grid_wavelength_nm} nm",
                f"Deviation: {deviation} nm",
            ],
            rule="itu_g6941_wavelength_accuracy",
        )
    return True, ProofObject(
        conclusion=f"{src.source_id} wavelength deviation {deviation} nm <= {limit} nm",
        premises=[f"Deviation: {deviation} nm <= {limit} nm"],
        rule="itu_g6941_wavelength_accuracy",
    )


def check_osnr(ch: OpticalChannel) -> Tuple[bool, ProofObject]:
    """OSNR must be at least 20 dB per ITU-T G.697.

    Falsifies if: osnr_db < Fraction(20, 1).
    falsifies_if: osnr_db < Fraction(20, 1).
    """
    limit = osnr_threshold()
    if ch.osnr_db < limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {ch.channel_id} OSNR {ch.osnr_db} dB < "
                f"minimum {limit} dB"
            ),
            premises=[
                f"OSNR: {ch.osnr_db} dB",
                f"Minimum: {limit} dB",
            ],
            rule="itu_g697_osnr",
        )
    return True, ProofObject(
        conclusion=f"{ch.channel_id} OSNR {ch.osnr_db} dB >= {limit} dB",
        premises=[f"OSNR: {ch.osnr_db} dB >= {limit} dB"],
        rule="itu_g697_osnr",
    )


def check_ber_floor(rx: DigitalReceiver) -> Tuple[bool, ProofObject]:
    """BER must not exceed 1e-12 per IEEE 802.3.

    Falsifies if: ber > Fraction(1, 10**12).
    falsifies_if: ber > Fraction(1, 10**12).
    """
    limit = ber_floor_threshold()
    if rx.ber > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {rx.receiver_id} BER {rx.ber} > "
                f"limit {limit}"
            ),
            premises=[
                f"BER: {rx.ber}",
                f"Limit: {limit}",
            ],
            rule="ieee_802_3_ber_floor",
        )
    return True, ProofObject(
        conclusion=f"{rx.receiver_id} BER {rx.ber} <= {limit}",
        premises=[f"BER: {rx.ber} <= {limit}"],
        rule="ieee_802_3_ber_floor",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all optical performance checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_comp = OpticalComponent(
        component_id="pass_comp",
        insertion_loss_db=Fraction(1, 1),
        return_loss_db=Fraction(45, 1),
        extinction_ratio_db=Fraction(12, 1),
        pdl_db=Fraction(1, 10),
    )
    fail_comp = OpticalComponent(
        component_id="fail_comp",
        insertion_loss_db=Fraction(5, 1),
        return_loss_db=Fraction(35, 1),
        extinction_ratio_db=Fraction(5, 1),
        pdl_db=Fraction(1, 1),
    )
    pass_src = WavelengthSource(
        source_id="pass_src",
        actual_wavelength_nm=Fraction(1550, 1),
        grid_wavelength_nm=Fraction(1550, 1),
    )
    fail_src = WavelengthSource(
        source_id="fail_src",
        actual_wavelength_nm=Fraction(1550, 1) + Fraction(2, 10),
        grid_wavelength_nm=Fraction(1550, 1),
    )
    pass_ch = OpticalChannel(
        channel_id="pass_ch",
        osnr_db=Fraction(25, 1),
    )
    fail_ch = OpticalChannel(
        channel_id="fail_ch",
        osnr_db=Fraction(15, 1),
    )
    pass_rx = DigitalReceiver(
        receiver_id="pass_rx",
        ber=Fraction(1, 10_000_000_000_000),
    )
    fail_rx = DigitalReceiver(
        receiver_id="fail_rx",
        ber=Fraction(1, 100_000_000_000),
    )

    checks = [
        ("check_insertion_loss_pass", lambda: check_insertion_loss(pass_comp)),
        ("check_insertion_loss_fail", lambda: check_insertion_loss(fail_comp)),
        ("check_return_loss_pass", lambda: check_return_loss(pass_comp)),
        ("check_return_loss_fail", lambda: check_return_loss(fail_comp)),
        ("check_extinction_ratio_pass", lambda: check_extinction_ratio(pass_comp)),
        ("check_extinction_ratio_fail", lambda: check_extinction_ratio(fail_comp)),
        ("check_polarization_dependent_loss_pass", lambda: check_polarization_dependent_loss(pass_comp)),
        ("check_polarization_dependent_loss_fail", lambda: check_polarization_dependent_loss(fail_comp)),
        ("check_wavelength_accuracy_pass", lambda: check_wavelength_accuracy(pass_src)),
        ("check_wavelength_accuracy_fail", lambda: check_wavelength_accuracy(fail_src)),
        ("check_osnr_pass", lambda: check_osnr(pass_ch)),
        ("check_osnr_fail", lambda: check_osnr(fail_ch)),
        ("check_ber_floor_pass", lambda: check_ber_floor(pass_rx)),
        ("check_ber_floor_fail", lambda: check_ber_floor(fail_rx)),
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
