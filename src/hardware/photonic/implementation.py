"""PHOTONIC implementation — GDSII & TRL 9 photonic chip domain

Category 1: Domain foundation
Layer: 3
CardinalStrength: PREDICATIVE
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class PhotonicWaveguide:
    """Optical waveguide parameters.

    Falsifies if: core_width <= 0 or wavelength_nm <= 0.
    falsifies_if: core_width <= 0 or wavelength_nm <= 0.
    """
    core_width: Fraction  # nm
    cladding_index: Fraction
    core_index: Fraction
    wavelength_nm: Fraction
    propagation_loss_db_per_cm: Fraction


@dataclass(frozen=True)
class MachZehnderInterferometer:
    """MZI optical switch/modulator.

    Falsifies if: splitting_ratio not in [0, 1].
    falsifies_if: splitting_ratio not in [0, 1].
    """
    arm_length_1: Fraction  # um
    arm_length_2: Fraction  # um
    phase_shift: Fraction  # radians
    splitting_ratio: Fraction  # 0..1


@dataclass(frozen=True)
class PhotonicChip:
    """Integrated photonic chip.

    Falsifies if: total_insertion_loss_db < 0.
    falsifies_if: total_insertion_loss_db < 0.
    """
    waveguides: Tuple[PhotonicWaveguide, ...]
    mzis: Tuple[MachZehnderInterferometer, ...]
    total_insertion_loss_db: Fraction
    chip_area_mm2: Fraction


def effective_index(wg: PhotonicWaveguide) -> Fraction:
    """Effective refractive index approximation (average of core and cladding).

    Falsifies if: result is not a positive Fraction.
    falsifies_if: result is not a positive Fraction.
    """
    return (wg.core_index + wg.cladding_index) / Fraction(2, 1)


def group_velocity(wg: PhotonicWaveguide) -> Fraction:
    """Normalized group velocity c / n_eff (c approximated as 3).

    Falsifies if: n_eff is zero.
    falsifies_if: n_eff is zero.
    """
    return Fraction(3, 1) / effective_index(wg)


def coupling_efficiency(power_in: Fraction, power_out: Fraction) -> Fraction:
    """Coupling efficiency η = P_out / P_in.

    Falsifies if: power_in is zero.
    falsifies_if: power_in is zero.
    """
    return power_out / power_in


def extinction_ratio_db(mzi: MachZehnderInterferometer) -> Fraction:
    """Extinction ratio proxy in dB.

    For a balanced MZI (splitting_ratio = 0.5), ER is effectively infinite.
    For unbalanced, proxy = 10 / |splitting_ratio - 0.5|.

    Falsifies if: deviation is zero and proxy is mishandled.
    falsifies_if: deviation is zero and proxy is mishandled.
    """
    deviation = abs(mzi.splitting_ratio - Fraction(1, 2))
    if deviation == Fraction(0, 1):
        return Fraction(10000, 1)
    return Fraction(10, 1) / deviation


def v_number(wg: PhotonicWaveguide) -> Fraction:
    """Normalized frequency (V-number) proxy using linear NA approximation.

    V ≈ (2πa / λ) * (n_core - n_clad)

    Falsifies if: wavelength_nm is zero.
    falsifies_if: wavelength_nm is zero.
    """
    pi = Fraction(355, 113)
    na = wg.core_index - wg.cladding_index
    return Fraction(2, 1) * pi * wg.core_width / wg.wavelength_nm * na


def minimum_bend_radius(wavelength_nm: Fraction) -> Fraction:
    """Minimum bend radius rule of thumb: 10 × wavelength.

    Falsifies if: wavelength_nm is negative.
    falsifies_if: wavelength_nm is negative.
    """
    return wavelength_nm * Fraction(10, 1)
