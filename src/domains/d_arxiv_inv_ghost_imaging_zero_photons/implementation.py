"""D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS implementation — Yeshua Inversion.

Paper: arXiv 2604.07782v1 (quant-ph)
Title: "Ghost imaging with zero photons"

IMPOSSIBLE_CLAIM:
  Ghost imaging requires photon interaction with the object. Either the signal
  beam illuminates the object or the reference beam correlates with it. Image
  reconstruction without any photon-object interaction is impossible.

YESHUA_INVERSION:
  Restrict the domain to thermal light sources with photon-number projection
  measurement and post-selection on zero-photon time bins. Under this
  restriction, the image can be reconstructed from the statistics of the
  zero-photon bins because the photon-number correlation between signal and
  reference beams encodes the object information even when no photon interacts
  with the object. The impossibility is inverted by changing the measurement
  protocol from intensity-based to photon-number-resolved post-selection.

Mathematical Standards:
- Original claim: intensity correlation requires photon detection.
- Inversion: photon-number projection measurement + thermal statistics enable
  reconstruction from absence-of-detection events (zero-photon bins).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class LightSource:
    """A model of the light source.

    Falsifies if: source properties are inconsistent.
    falsifies_if: source properties are inconsistent.
    """
    source_name: str
    is_thermal_light: bool
    has_photon_number_resolution: bool
    has_post_selection: bool


@dataclass(frozen=True)
class ImagingSetup:
    """A model of the imaging setup.

    Falsifies if: setup properties are inconsistent.
    falsifies_if: setup properties are inconsistent.
    """
    uses_intensity_correlation: bool
    uses_zero_photon_bins: bool
    object_transmissivity: Fraction


@dataclass(frozen=True)
class GhostImagingClaim:
    """Structured claim for the Yeshua Inversion of ghost imaging with zero photons.

    Falsifies if: any field violates its stated constraint.
    falsifies_if: any field violates its stated constraint.
    """
    source: LightSource
    setup: ImagingSetup
    image_reconstruction_quality: Fraction
    quality_threshold: Fraction


@dataclass(frozen=True)
class GhostImagingEvidence:
    """Evidence bundle for the inversion.

    Falsifies if: evidence contradicts claim.
    falsifies_if: evidence contradicts claim.
    """
    evidence_id: str
    claim: GhostImagingClaim
    empirical_validation_result: str
    formal_proof_reference: str


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

IMPOSSIBLE_CLAIM = (
    "Ghost imaging requires photon interaction with the object. Either the signal "
    "beam illuminates the object or the reference beam correlates with it. Image "
    "reconstruction without any photon-object interaction is impossible."
)

YESHUA_INVERSION = (
    "Restrict the domain to thermal light sources with photon-number projection "
    "measurement and post-selection on zero-photon time bins. Under this "
    "restriction, the image can be reconstructed from the statistics of the "
    "zero-photon bins because the photon-number correlation between signal and "
    "reference beams encodes the object information even when no photon interacts "
    "with the object. The impossibility is inverted by changing the measurement "
    "protocol from intensity-based to photon-number-resolved post-selection."
)

DOMAIN_METADATA = {
    "id": "D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS",
    "paper_id": "2604.07782v1",
    "claim_model": "GhostImagingClaim",
    "evidence_model": "GhostImagingEvidence",
    "check_functions": [
        "check_inversion_holds",
        "check_domain_restriction_satisfied",
        "check_original_impossibility_holds_without_restriction",
    ],
    "layer": 4,
    "cardinal_strength": "PREDICATIVE",
}
