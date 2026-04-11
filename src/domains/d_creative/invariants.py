#!/usr/bin/env python3
"""D_CREATIVE Invariants — Copyright, DMCA, generative AI reproducibility, style transfer

Creative works per Copyright Act (17 USC), DMCA (1998), and fair use doctrine.
All invariants use Fraction arithmetic for exact measurements.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    CreativeWork, GenerativeOutput, StyleTransfer, DMCACompliance,
    LicenseType, GenerationMode,
    style_transfer_content_min, perceptual_similarity_threshold
)


def check_cc_by_attribution(work: CreativeWork) -> Tuple[bool, ProofObject]:
    """
    Creative Commons BY license requires author attribution.

    Falsifies if: license_type == CC_BY AND NOT author_attributed
    
    
    if work.license_type == LicenseType.CC_BY and not work.author_attributed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Work {work.work_id} uses CC-BY license but lacks author attribution",
            premises=[
                f"License: {work.license_type.name}",
                f"Author attributed: {work.author_attributed}"
            ],
            rule="creative_commons_by_attribution"
        )

    return True, ProofObject(
        conclusion=f"Work {work.work_id} meets licensing requirements",
        premises=[
            f"License: {work.license_type.name}",
            f"Attribution: {work.author_attributed}"
        ],
        rule="creative_commons_by_attribution"
    )


def check_generative_reproducibility(gen: GenerativeOutput) -> Tuple[bool, ProofObject]:
    """
    Generative AI: fixed seed in deterministic mode must produce reproducible output.

    Falsifies if: mode == DETERMINISTIC AND seed is not None AND NOT reproducible
    
    
    if gen.mode == GenerationMode.DETERMINISTIC and gen.seed is not None and not gen.reproducible:
        return False, ProofObject(
            conclusion=f"VIOLATION: Generative output {gen.output_id} is deterministic with seed {gen.seed} but not reproducible",
            premises=[
                f"Mode: {gen.mode.name}",
                f"Seed: {gen.seed}",
                f"Reproducible: {gen.reproducible}"
            ],
            rule="generative_deterministic_reproducibility"
        )

    return True, ProofObject(
        conclusion=f"Generative output {gen.output_id} meets reproducibility requirements",
        premises=[
            f"Mode: {gen.mode.name}",
            f"Seed: {gen.seed}",
            f"Reproducible: {gen.reproducible}"
        ],
        rule="generative_deterministic_reproducibility"
    )


def check_style_transfer_content_preservation(transfer: StyleTransfer) -> Tuple[bool, ProofObject]:
    """
    Style transfer must preserve >= 70% of content features.

    Falsifies if: content_preserved_percent < 0.70
    
    
    min_content = style_transfer_content_min()

    if transfer.content_preserved_percent < min_content:
        return False, ProofObject(
            conclusion=f"VIOLATION: Style transfer {transfer.transfer_id} preserves {transfer.content_preserved_percent * 100}% content < {min_content * 100}%",
            premises=[
                f"Content preserved: {transfer.content_preserved_percent * 100}%",
                f"Minimum: {min_content * 100}%"
            ],
            rule="style_transfer_content_preservation"
        )

    return True, ProofObject(
        conclusion=f"Style transfer {transfer.transfer_id} preserves adequate content",
        premises=[f"Content preserved: {transfer.content_preserved_percent * 100}% >= {min_content * 100}%"],
        rule="style_transfer_content_preservation"
    )


def check_dmca_copyright_infringement(dmca: DMCACompliance) -> Tuple[bool, ProofObject]:
    """
    DMCA: perceptually identical content to copyrighted source is infringement unless fair use.

    Falsifies if: perceptually_identical AND copyrighted_source AND NOT fair_use_exception
    
    
    if dmca.perceptually_identical and dmca.copyrighted_source and not dmca.fair_use_exception:
        return False, ProofObject(
            conclusion=f"VIOLATION: Content {dmca.content_id} is perceptually identical to copyrighted source {dmca.copyrighted_source} without fair use",
            premises=[
                f"Perceptually identical: {dmca.perceptually_identical}",
                f"Copyrighted source: {dmca.copyrighted_source}",
                f"Fair use exception: {dmca.fair_use_exception}"
            ],
            rule="dmca_copyright_infringement"
        )

    return True, ProofObject(
        conclusion=f"Content {dmca.content_id} complies with DMCA",
        premises=[
            f"Perceptually identical: {dmca.perceptually_identical}",
            f"Fair use: {dmca.fair_use_exception}"
        ],
        rule="dmca_copyright_infringement"
    )


def check_cc_by_sa_share_alike(work: CreativeWork) -> Tuple[bool, ProofObject]:
    """
    Creative Commons BY-SA (ShareAlike): derivative works must use same license.

    Falsifies if: license_type != CC_BY_SA AND derivative_of points to CC_BY_SA work
    (This check requires access to parent work license, simplified here)
    
    
    if work.license_type == LicenseType.CC_BY_SA and work.derivative_of:
        return True, ProofObject(
            conclusion=f"Work {work.work_id} is CC-BY-SA derivative (ShareAlike compliant)",
            premises=[
                f"License: {work.license_type.name}",
                f"Derivative of: {work.derivative_of}"
            ],
            rule="creative_commons_share_alike"
        )

    return True, ProofObject(
        conclusion=f"Work {work.work_id} license check (no ShareAlike conflict detected)",
        premises=[f"License: {work.license_type.name}"],
        rule="creative_commons_share_alike"
    )
