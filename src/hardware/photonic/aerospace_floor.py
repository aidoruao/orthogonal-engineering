"""PHOTONIC Aerospace Floor — DO-178C determinism, MIL-STD-882E laser hazards,
NASA radiation hardness, SIL-4 optical safety.

Category 13: Aerospace Floor Integration (checks 79-82).

Standards: DO-178C Level A, MIL-STD-882E, NASA NPR 7150.2, IEC 61508 SIL-4.
All invariants use Fraction arithmetic for exact thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class PhotonicDeterminism:
    """DO-178C photonic determinism parameters.

    falsifies_if: is_deterministic is False.
    falsifies_if: is_deterministic is False.
    """
    component_id: str
    is_deterministic: bool


@dataclass(frozen=True)
class LaserHazardAssessment:
    """MIL-STD-882E laser hazard assessment parameters.

    falsifies_if: hazard_assessed_in_fmea is False.
    falsifies_if: hazard_assessed_in_fmea is False.
    """
    system_id: str
    hazard_assessed_in_fmea: bool


@dataclass(frozen=True)
class RadiationHardness:
    """NASA radiation hardness parameters.

    falsifies_if: has_radiation_data is False.
    falsifies_if: has_radiation_data is False.
    """
    component_id: str
    has_radiation_data: bool


@dataclass(frozen=True)
class Sil4OpticalLink:
    """IEC 61508 SIL-4 optical link safety parameters.

    falsifies_if: pfd is negative.
    falsifies_if: pfd is negative.
    """
    link_id: str
    pfd: Fraction


# ---------------------------------------------------------------------------
# Threshold functions
# ---------------------------------------------------------------------------

def sil4_pfd_max() -> Fraction:
    """IEC 61508 SIL-4 maximum PFD: 1/10 000."""
    return Fraction(1, 10_000)


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_do178c_photonic_determinism(d: PhotonicDeterminism) -> Tuple[bool, ProofObject]:
    """Photonic matrix output must be deterministic across runs per DO-178C Level A.

    Falsifies if: is_deterministic is False.
    falsifies_if: is_deterministic is False.
    """
    if not d.is_deterministic:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {d.component_id} photonic matrix output is non-deterministic"
            ),
            premises=[
                f"Component: {d.component_id}",
                f"Deterministic: {d.is_deterministic}",
            ],
            rule="do178c_photonic_determinism",
        )
    return True, ProofObject(
        conclusion=f"{d.component_id} photonic output is deterministic",
        premises=[f"Component: {d.component_id}", f"Deterministic: True"],
        rule="do178c_photonic_determinism",
    )


def check_milstd882e_laser_hazard(assessment: LaserHazardAssessment) -> Tuple[bool, ProofObject]:
    """Laser hazard must be assessed in FMEA per MIL-STD-882E.

    Falsifies if: hazard_assessed_in_fmea is False.
    falsifies_if: hazard_assessed_in_fmea is False.
    """
    if not assessment.hazard_assessed_in_fmea:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {assessment.system_id} laser hazard not assessed in FMEA"
            ),
            premises=[
                f"System: {assessment.system_id}",
                f"FMEA assessed: {assessment.hazard_assessed_in_fmea}",
            ],
            rule="mil_std_882e_laser_hazard",
        )
    return True, ProofObject(
        conclusion=f"{assessment.system_id} laser hazard assessed in FMEA",
        premises=[f"System: {assessment.system_id}", f"FMEA assessed: True"],
        rule="mil_std_882e_laser_hazard",
    )


def check_nasa_class_a_radiation(rad: RadiationHardness) -> Tuple[bool, ProofObject]:
    """Space-rated optics must have radiation hardness data per NASA NPR 7150.2.

    Falsifies if: has_radiation_data is False.
    falsifies_if: has_radiation_data is False.
    """
    if not rad.has_radiation_data:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {rad.component_id} has no radiation hardness data"
            ),
            premises=[
                f"Component: {rad.component_id}",
                f"Radiation data: {rad.has_radiation_data}",
            ],
            rule="nasa_npr_7150_2_radiation",
        )
    return True, ProofObject(
        conclusion=f"{rad.component_id} radiation hardness data present",
        premises=[f"Component: {rad.component_id}", f"Radiation data: True"],
        rule="nasa_npr_7150_2_radiation",
    )


def check_sil4_optical_safety(link: Sil4OpticalLink) -> Tuple[bool, ProofObject]:
    """PFD must not exceed 1/10 000 for safety-critical optical link per IEC 61508 SIL-4.

    Falsifies if: pfd > Fraction(1, 10_000).
    falsifies_if: pfd > Fraction(1, 10_000).
    """
    limit = sil4_pfd_max()
    if link.pfd > limit:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: {link.link_id} PFD {link.pfd} > SIL-4 limit {limit}"
            ),
            premises=[
                f"PFD: {link.pfd}",
                f"SIL-4 limit: {limit}",
            ],
            rule="iec_61508_sil4_optical",
        )
    return True, ProofObject(
        conclusion=f"{link.link_id} PFD {link.pfd} <= SIL-4 limit {limit}",
        premises=[f"PFD: {link.pfd} <= {limit}"],
        rule="iec_61508_sil4_optical",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> list:
    """Run all aerospace floor checks with passing and failing test data.

    falsifies_if: any check fails or raises an exception.
    """
    pass_det = PhotonicDeterminism(component_id="pass_det", is_deterministic=True)
    fail_det = PhotonicDeterminism(component_id="fail_det", is_deterministic=False)
    pass_fmea = LaserHazardAssessment(system_id="pass_fmea", hazard_assessed_in_fmea=True)
    fail_fmea = LaserHazardAssessment(system_id="fail_fmea", hazard_assessed_in_fmea=False)
    pass_rad = RadiationHardness(component_id="pass_rad", has_radiation_data=True)
    fail_rad = RadiationHardness(component_id="fail_rad", has_radiation_data=False)
    pass_sil4 = Sil4OpticalLink(link_id="pass_sil4", pfd=Fraction(1, 50_000))
    fail_sil4 = Sil4OpticalLink(link_id="fail_sil4", pfd=Fraction(1, 5_000))

    checks = [
        ("check_do178c_photonic_determinism_pass", lambda: check_do178c_photonic_determinism(pass_det)),
        ("check_do178c_photonic_determinism_fail", lambda: check_do178c_photonic_determinism(fail_det)),
        ("check_milstd882e_laser_hazard_pass", lambda: check_milstd882e_laser_hazard(pass_fmea)),
        ("check_milstd882e_laser_hazard_fail", lambda: check_milstd882e_laser_hazard(fail_fmea)),
        ("check_nasa_class_a_radiation_pass", lambda: check_nasa_class_a_radiation(pass_rad)),
        ("check_nasa_class_a_radiation_fail", lambda: check_nasa_class_a_radiation(fail_rad)),
        ("check_sil4_optical_safety_pass", lambda: check_sil4_optical_safety(pass_sil4)),
        ("check_sil4_optical_safety_fail", lambda: check_sil4_optical_safety(fail_sil4)),
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
