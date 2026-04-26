"""D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS domain metadata and claim model.

Paper: arXiv 2604.07782v1 (quant-ph)
Title: "Ghost imaging with zero photons"
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class GhostImagingClaim:
    """Structured claim parameters for the Yeshua Inversion.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    source_name: str
    is_thermal_light: bool
    has_photon_number_resolution: bool
    has_post_selection: bool
    uses_intensity_correlation: bool
    uses_zero_photon_bins: bool
    object_transmissivity: Fraction
    image_reconstruction_quality: Fraction
    quality_threshold: Fraction


@dataclass(frozen=True)
class GhostImagingEvidence:
    """Evidence bundle for the inversion verification.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: GhostImagingClaim
    empirical_validation_result: str
    formal_proof_reference: str


DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS",
    "claim_model": "GhostImagingClaim",
    "evidence_model": "GhostImagingEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "paper_id": "2604.07782v1",
    "paper_title": "Ghost imaging with zero photons",
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
