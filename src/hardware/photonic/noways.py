"""src/hardware/photonic/noways — Photonic Impossibility Proofs (Noways)

Category 3: Noways — Fundamental limits that cannot be inverted by any
domain restriction. Each entry documents why a physical law is a hard wall
for photonic computation and what OE consequences follow.

Standard: Yeshua Standard — every claim has a certainty Fraction and a falsifies_if.

falsifies_if: a noway entry appears with certainty != Fraction(1, 1) or without
a falsifies_if statement.
"""

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from src.noways.impossibility_proofs import Noway


PHOTONIC_NOWAYS: Tuple[Noway, ...] = (
    Noway(
        key="no_cloning",
        statement=(
            "An unknown quantum state cannot be perfectly copied (Wootters-Zurek 1982)."
        ),
        proof_summary=(
            "Linearity of quantum mechanics — cloning operator contradicts superposition."
        ),
        falsifies_if=(
            "a device duplicates an arbitrary unknown quantum state with fidelity = 1"
        ),
        oe_consequences=(
            "Photonic signal amplification must use classical regeneration "
            "(measure-and-remodulate), not quantum cloning. Amplifier invariants must "
            "budget noise figure > 3 dB (quantum limit)."
        ),
        domain="quantum_information",
        certainty=Fraction(1, 1),
    ),
    Noway(
        key="diffraction_limit",
        statement=(
            "Minimum resolvable feature size in optical lithography is bounded by "
            "λ/(2·NA) (Abbe 1873)."
        ),
        proof_summary=(
            "Fourier optics — spatial frequencies above 2·NA/λ are evanescent and do not "
            "propagate to far field."
        ),
        falsifies_if=(
            "a far-field optical system resolves features below λ/(2·NA) without near-field "
            "or computational post-processing"
        ),
        oe_consequences=(
            "Photonic waveguide minimum width is bounded by fabrication wavelength. "
            "check_single_mode_condition() threshold derives from this limit."
        ),
        domain="optics",
        certainty=Fraction(1, 1),
    ),
    Noway(
        key="detector_dark_count",
        statement=(
            "Photodetectors have a nonzero dark count rate from thermal carrier generation "
            "(Planck statistics)."
        ),
        proof_summary=(
            "At T > 0, thermal energy excites carriers across bandgap with probability "
            "proportional to exp(-E_g / k_B T). Dark counts are thermodynamically inevitable "
            "above absolute zero."
        ),
        falsifies_if=(
            "a photodetector at T > 0 K exhibits exactly zero dark counts over infinite "
            "observation time"
        ),
        oe_consequences=(
            "Photonic receiver sensitivity has a noise floor. BER calculations must include "
            "dark count rate as irreducible term. check_optical_power_budget() must account "
            "for detector noise."
        ),
        domain="photonics",
        certainty=Fraction(1, 1),
    ),
    Noway(
        key="nonlinear_efficiency_wall",
        statement=(
            "Second-order nonlinear conversion efficiency is bounded by phase-matching "
            "bandwidth and interaction length (Boyd, Nonlinear Optics)."
        ),
        proof_summary=(
            "Coupled-wave equations — conversion efficiency scales as sinc²(ΔkL/2). "
            "Perfect phase matching (Δk=0) gives η proportional to L², but material dispersion "
            "makes Δk=0 achievable only over finite bandwidth."
        ),
        falsifies_if=(
            "a χ² nonlinear process achieves unity conversion efficiency over arbitrary "
            "bandwidth without phase matching"
        ),
        oe_consequences=(
            "On-chip wavelength conversion and photon-pair generation have bounded efficiency. "
            "Photonic interconnect designs must budget for conversion loss in nonlinear elements."
        ),
        domain="nonlinear_optics",
        certainty=Fraction(1, 1),
    ),
)


def run_all_invariants() -> List[Tuple[str, str]]:
    """Iterate PHOTONIC_NOWAYS and print each key + statement.

    falsifies_if: any noway entry is missing a key or statement.
    """
    results: List[Tuple[str, str]] = []
    for noway in PHOTONIC_NOWAYS:
        print(f"{noway.key}: {noway.statement}")
        results.append((noway.key, noway.statement))
    return results
