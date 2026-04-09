#!/usr/bin/env python3
"""D_BIOTECH Invariants — NGS quality, CRISPR precision, lab automation, biosafety

Biotechnology requires deterministic reproducibility for clinical diagnostics.
All invariants use Fraction arithmetic for exact quality metrics.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    SequencingRun, CRISPREdit, LabAutomation, BiosafetyCabinet,
    BiosafetLevel, phred_q30_threshold, crispr_on_target_threshold,
    crispr_off_target_max, sample_swap_max, hepa_filtration_min
)


def check_ngs_quality(run: SequencingRun) -> Tuple[bool, ProofObject]:
    """
    NGS base-calling must achieve >90% Q30 (Phred quality score >30, <0.1% error).

    Falsifies if: phred_q30_percent < 90%
    """
    threshold = phred_q30_threshold()

    if run.phred_q30_percent < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: NGS run {run.run_id} Q30 rate {run.phred_q30_percent}% < {threshold}%",
            premises=[f"Q30: {run.phred_q30_percent}%", f"Required: {threshold}%"],
            rule="ngs_phred_q30_quality"
        )

    return True, ProofObject(
        conclusion=f"NGS run {run.run_id} Q30 rate {run.phred_q30_percent}% adequate",
        premises=[f"Q30: {run.phred_q30_percent}% >= {threshold}%"],
        rule="ngs_phred_q30_quality"
    )


def check_crispr_precision(edit: CRISPREdit) -> Tuple[bool, ProofObject]:
    """
    CRISPR guide RNAs must achieve >80% on-target efficiency with <1% off-target.

    Falsifies if: on_target < 80% OR off_target >= 1%
    """
    on_target_min = crispr_on_target_threshold()
    off_target_max_val = crispr_off_target_max()

    if edit.on_target_efficiency < on_target_min:
        return False, ProofObject(
            conclusion=f"VIOLATION: CRISPR guide {edit.guide_rna_id} on-target {edit.on_target_efficiency}% < {on_target_min}%",
            premises=[
                f"On-target: {edit.on_target_efficiency}%",
                f"Required: {on_target_min}%"
            ],
            rule="crispr_on_target_efficiency"
        )

    if edit.off_target_rate >= off_target_max_val:
        return False, ProofObject(
            conclusion=f"VIOLATION: CRISPR guide {edit.guide_rna_id} off-target {edit.off_target_rate}% >= {off_target_max_val}%",
            premises=[
                f"Off-target: {edit.off_target_rate}%",
                f"Max allowed: {off_target_max_val}%"
            ],
            rule="crispr_off_target_limit"
        )

    return True, ProofObject(
        conclusion=f"CRISPR guide {edit.guide_rna_id} precision adequate",
        premises=[
            f"On-target: {edit.on_target_efficiency}%",
            f"Off-target: {edit.off_target_rate}%"
        ],
        rule="crispr_editing_precision"
    )


def check_lab_automation_fidelity(automation: LabAutomation) -> Tuple[bool, ProofObject]:
    """
    Automated liquid handling must maintain <0.0001% sample swap rate.

    Falsifies if: sample_swap_rate >= 0.0001%
    """
    max_swap = sample_swap_max()

    if automation.sample_swap_rate >= max_swap:
        return False, ProofObject(
            conclusion=f"VIOLATION: Plate {automation.plate_id} sample swap rate {automation.sample_swap_rate}% >= {max_swap}%",
            premises=[
                f"Swap rate: {automation.sample_swap_rate}%",
                f"Max: {max_swap}%"
            ],
            rule="lab_automation_sample_identity"
        )

    return True, ProofObject(
        conclusion=f"Plate {automation.plate_id} sample identity maintained",
        premises=[f"Swap rate: {automation.sample_swap_rate}% < {max_swap}%"],
        rule="lab_automation_sample_identity"
    )


def check_biosafety_containment(cabinet: BiosafetyCabinet) -> Tuple[bool, ProofObject]:
    """
    BSC HEPA filtration must achieve >99.97% particle capture efficiency.

    Falsifies if: hepa_efficiency < 99.97%
    """
    min_efficiency = hepa_filtration_min()

    if cabinet.hepa_efficiency < min_efficiency:
        return False, ProofObject(
            conclusion=f"VIOLATION: BSC {cabinet.cabinet_id} HEPA efficiency {cabinet.hepa_efficiency * 100}% < {min_efficiency * 100}%",
            premises=[
                f"HEPA: {cabinet.hepa_efficiency * 100}%",
                f"Required: {min_efficiency * 100}%"
            ],
            rule="biosafety_hepa_filtration"
        )

    return True, ProofObject(
        conclusion=f"BSC {cabinet.cabinet_id} HEPA filtration adequate",
        premises=[f"HEPA: {cabinet.hepa_efficiency * 100}%"],
        rule="biosafety_hepa_filtration"
    )


def check_biosafety_pressure(cabinet: BiosafetyCabinet) -> Tuple[bool, ProofObject]:
    """
    BSL-3 cabinets require negative pressure for containment.

    Falsifies if: biosafety_level >= BSL3 AND negative_pressure_pa <= 0
    """
    if cabinet.biosafety_level.value >= BiosafetLevel.BSL3.value:
        if cabinet.negative_pressure_pa <= Fraction(0):
            return False, ProofObject(
                conclusion=f"VIOLATION: {cabinet.biosafety_level.name} cabinet {cabinet.cabinet_id} lacks negative pressure",
                premises=[
                    f"Pressure: {cabinet.negative_pressure_pa} Pa",
                    f"Level: {cabinet.biosafety_level.name}"
                ],
                rule="biosafety_negative_pressure"
            )

    return True, ProofObject(
        conclusion=f"BSC {cabinet.cabinet_id} pressure containment adequate",
        premises=[
            f"Level: {cabinet.biosafety_level.name}",
            f"Pressure: {cabinet.negative_pressure_pa} Pa"
        ],
        rule="biosafety_negative_pressure"
    )
