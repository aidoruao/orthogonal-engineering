"""PHOTONIC Manufacturing — Wafer uniformity, etch depth, lithography overlay,
waveguide width, coupling efficiency, yield rate.

Category 9: Manufacturing & Process Control (checks 55-60).

Standards: SEMI M1, SEMI E10, SEMI P38, Custom OE.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class WaferProfile:
    """Wafer uniformity parameters per SEMI M1.

    falsifies_if: thickness_variation is negative.
    falsifies_if: thickness_variation is negative.
    """
    wafer_id: str
    thickness_variation: Fraction


@dataclass(frozen=True)
class EtchProcess:
    """Etch depth parameters per SEMI E10.

    falsifies_if: actual_depth_nm or target_depth_nm is negative.
    falsifies_if: actual_depth_nm or target_depth_nm is negative.
    """
    process_id: str
    actual_depth_nm: Fraction
    target_depth_nm: Fraction


@dataclass(frozen=True)
class LithographyStep:
    """Lithography overlay parameters per SEMI P38.

    falsifies_if: overlay_error_nm is negative.
    falsifies_if: overlay_error_nm is negative.
    """
    step_id: str
    overlay_error_nm: Fraction


@dataclass(frozen=True)
class WaveguideFabrication:
    """Waveguide width tolerance parameters.

    falsifies_if: actual_width_nm or target_width_nm is negative.
    falsifies_if: actual_width_nm or target_width_nm is negative.
    """
    wg_id: str
    actual_width_nm: Fraction
    target_width_nm: Fraction


@dataclass(frozen=True)
class FiberCoupling:
    """Fiber-to-chip coupling efficiency parameters.

    falsifies_if: fiber_to_chip_loss_db is negative.
    falsifies_if: fiber_to_chip_loss_db is negative.
    """
    coupling_id: str
    fiber_to_chip_loss_db: Fraction


@dataclass(frozen=True)
class YieldData:
    """Die yield parameters.

    falsifies_if: die_yield is negative.
    falsifies_if: die_yield is negative.
    """
    lot_id: str
    die_yield: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def wafer_uniformity_threshold() -> Fraction:
    """SEMI M1 maximum thickness variation: 5%."""
    return Fraction(5, 100)


def etch_depth_tolerance_nm() -> Fraction:
    """SEMI E10 etch depth tolerance: 10 nm."""
    return Fraction(10, 1)


def lithography_overlay_threshold_nm() -> Fraction:
    """SEMI P38 maximum overlay error: 50 nm."""
    return Fraction(50, 1)


def waveguide_width_tolerance_nm() -> Fraction:
    """Custom OE waveguide width tolerance: 20 nm."""
    return Fraction(20, 1)


def coupling_loss_threshold_db() -> Fraction:
    """Custom OE maximum fiber-to-chip coupling loss: 3 dB."""
    return Fraction(3, 1)


def yield_threshold() -> Fraction:
    """Custom OE minimum die yield: 70%."""
    return Fraction(7, 10)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_wafer_uniformity(wafer: WaferProfile) -> Tuple[bool, ProofObject]:
    """Wafer thickness variation must not exceed 5% per SEMI M1.

    Falsifies if: thickness_variation > Fraction(5, 100).
    falsifies_if: thickness_variation > Fraction(5, 100).
    """
    limit = wafer_uniformity_threshold()
    if wafer.thickness_variation > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {wafer.wafer_id} thickness variation {wafer.thickness_variation} "
                f"> limit {limit}"
            ),
            premises=[
                f"Variation: {wafer.thickness_variation}",
                f"Limit: {limit}",
            ],
            rule="semi_m1_uniformity",
        )
    return True, ProofObject(
        conclusion=(
            f"{wafer.wafer_id} thickness variation {wafer.thickness_variation} <= {limit}"
        ),
        premises=[f"Variation: {wafer.thickness_variation} <= {limit}"],
        rule="semi_m1_uniformity",
    )


def check_etch_depth_tolerance(proc: EtchProcess) -> Tuple[bool, ProofObject]:
    """Etch depth must be within 10 nm of target per SEMI E10.

    Falsifies if: abs(actual - target) > Fraction(10, 1).
    falsifies_if: abs(actual - target) > Fraction(10, 1).
    """
    limit = etch_depth_tolerance_nm()
    deviation = abs(proc.actual_depth_nm - proc.target_depth_nm)
    if deviation > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {proc.process_id} etch deviation {deviation} nm > "
                f"limit {limit} nm"
            ),
            premises=[
                f"Actual: {proc.actual_depth_nm} nm",
                f"Target: {proc.target_depth_nm} nm",
                f"Deviation: {deviation} nm",
            ],
            rule="semi_e10_etch_depth",
        )
    return True, ProofObject(
        conclusion=f"{proc.process_id} etch deviation {deviation} nm <= {limit} nm",
        premises=[f"Deviation: {deviation} nm <= {limit} nm"],
        rule="semi_e10_etch_depth",
    )


def check_lithography_overlay(step: LithographyStep) -> Tuple[bool, ProofObject]:
    """Lithography overlay error must not exceed 50 nm per SEMI P38.

    Falsifies if: overlay_error_nm > Fraction(50, 1).
    falsifies_if: overlay_error_nm > Fraction(50, 1).
    """
    limit = lithography_overlay_threshold_nm()
    if step.overlay_error_nm > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {step.step_id} overlay error {step.overlay_error_nm} nm > "
                f"limit {limit} nm"
            ),
            premises=[
                f"Overlay error: {step.overlay_error_nm} nm",
                f"Limit: {limit} nm",
            ],
            rule="semi_p38_overlay",
        )
    return True, ProofObject(
        conclusion=f"{step.step_id} overlay error {step.overlay_error_nm} nm <= {limit} nm",
        premises=[f"Overlay error: {step.overlay_error_nm} nm <= {limit} nm"],
        rule="semi_p38_overlay",
    )


def check_waveguide_width_tolerance(wg: WaveguideFabrication) -> Tuple[bool, ProofObject]:
    """Waveguide width must be within 20 nm of target (Custom OE).

    Falsifies if: abs(actual - target) > Fraction(20, 1).
    falsifies_if: abs(actual - target) > Fraction(20, 1).
    """
    limit = waveguide_width_tolerance_nm()
    deviation = abs(wg.actual_width_nm - wg.target_width_nm)
    if deviation > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {wg.wg_id} width deviation {deviation} nm > "
                f"limit {limit} nm"
            ),
            premises=[
                f"Actual: {wg.actual_width_nm} nm",
                f"Target: {wg.target_width_nm} nm",
                f"Deviation: {deviation} nm",
            ],
            rule="oe_waveguide_width",
        )
    return True, ProofObject(
        conclusion=f"{wg.wg_id} width deviation {deviation} nm <= {limit} nm",
        premises=[f"Deviation: {deviation} nm <= {limit} nm"],
        rule="oe_waveguide_width",
    )


def check_coupling_efficiency(coup: FiberCoupling) -> Tuple[bool, ProofObject]:
    """Fiber-to-chip coupling loss must not exceed 3 dB (Custom OE).

    Falsifies if: fiber_to_chip_loss_db > Fraction(3, 1).
    falsifies_if: fiber_to_chip_loss_db > Fraction(3, 1).
    """
    limit = coupling_loss_threshold_db()
    if coup.fiber_to_chip_loss_db > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {coup.coupling_id} coupling loss {coup.fiber_to_chip_loss_db} dB > "
                f"limit {limit} dB"
            ),
            premises=[
                f"Coupling loss: {coup.fiber_to_chip_loss_db} dB",
                f"Limit: {limit} dB",
            ],
            rule="oe_coupling_efficiency",
        )
    return True, ProofObject(
        conclusion=f"{coup.coupling_id} coupling loss {coup.fiber_to_chip_loss_db} dB <= {limit} dB",
        premises=[f"Coupling loss: {coup.fiber_to_chip_loss_db} dB <= {limit} dB"],
        rule="oe_coupling_efficiency",
    )


def check_yield_rate(yield_data: YieldData) -> Tuple[bool, ProofObject]:
        """Die yield must be at least 70% (Custom OE).

        Falsifies if: die_yield < Fraction(7, 10).
        falsifies_if: die_yield < Fraction(7, 10).
        """
        limit = yield_threshold()
        if yield_data.die_yield < limit:
            return False, ProofObject(
                conclusion=(
                    f"VIOLATION: {yield_data.lot_id} yield {yield_data.die_yield} < "
                    f"floor {limit}"
                ),
                premises=[
                    f"Die yield: {yield_data.die_yield}",
                    f"Floor: {limit}",
                ],
                rule="oe_yield_rate",
            )
        return True, ProofObject(
            conclusion=f"{yield_data.lot_id} yield {yield_data.die_yield} >= {limit}",
            premises=[f"Die yield: {yield_data.die_yield} >= {limit}"],
            rule="oe_yield_rate",
        )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all manufacturing checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_wafer = WaferProfile(wafer_id="pass_wafer", thickness_variation=Fraction(2, 100))
    fail_wafer = WaferProfile(wafer_id="fail_wafer", thickness_variation=Fraction(8, 100))
    pass_etch = EtchProcess(
        process_id="pass_etch",
        actual_depth_nm=Fraction(220, 1),
        target_depth_nm=Fraction(220, 1),
    )
    fail_etch = EtchProcess(
        process_id="fail_etch",
        actual_depth_nm=Fraction(240, 1),
        target_depth_nm=Fraction(220, 1),
    )
    pass_litho = LithographyStep(step_id="pass_litho", overlay_error_nm=Fraction(30, 1))
    fail_litho = LithographyStep(step_id="fail_litho", overlay_error_nm=Fraction(70, 1))
    pass_wg = WaveguideFabrication(
        wg_id="pass_wg",
        actual_width_nm=Fraction(500, 1),
        target_width_nm=Fraction(500, 1),
    )
    fail_wg = WaveguideFabrication(
        wg_id="fail_wg",
        actual_width_nm=Fraction(540, 1),
        target_width_nm=Fraction(500, 1),
    )
    pass_coup = FiberCoupling(
        coupling_id="pass_coup",
        fiber_to_chip_loss_db=Fraction(2, 1),
    )
    fail_coup = FiberCoupling(
        coupling_id="fail_coup",
        fiber_to_chip_loss_db=Fraction(5, 1),
    )
    pass_yield = YieldData(lot_id="pass_yield", die_yield=Fraction(8, 10))
    fail_yield = YieldData(lot_id="fail_yield", die_yield=Fraction(5, 10))

    checks = [
        ("check_wafer_uniformity_pass", lambda: check_wafer_uniformity(pass_wafer)),
        ("check_wafer_uniformity_fail", lambda: check_wafer_uniformity(fail_wafer)),
        ("check_etch_depth_tolerance_pass", lambda: check_etch_depth_tolerance(pass_etch)),
        ("check_etch_depth_tolerance_fail", lambda: check_etch_depth_tolerance(fail_etch)),
        ("check_lithography_overlay_pass", lambda: check_lithography_overlay(pass_litho)),
        ("check_lithography_overlay_fail", lambda: check_lithography_overlay(fail_litho)),
        ("check_waveguide_width_tolerance_pass", lambda: check_waveguide_width_tolerance(pass_wg)),
        ("check_waveguide_width_tolerance_fail", lambda: check_waveguide_width_tolerance(fail_wg)),
        ("check_coupling_efficiency_pass", lambda: check_coupling_efficiency(pass_coup)),
        ("check_coupling_efficiency_fail", lambda: check_coupling_efficiency(fail_coup)),
        ("check_yield_rate_pass", lambda: check_yield_rate(pass_yield)),
        ("check_yield_rate_fail", lambda: check_yield_rate(fail_yield)),
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
