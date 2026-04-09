"""D_GRAPHICS_REALITY implementation — Vendor-Agnostic Super Resolution.

Abstractions for DLSS, FSR, XeSS, PSSR with unified interfaces.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional, List
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class Vendor(Enum):
    """GPU vendors."""
    NVIDIA = "NVIDIA"
    AMD = "AMD"
    INTEL = "Intel"
    SONY = "Sony"
    GENERIC = "Generic"


class SRMethod(Enum):
    """Super-resolution methods."""
    DLSS = "DLSS"
    FSR = "FSR"
    XeSS = "XeSS"
    PSSR = "PSSR"
    BILINEAR = "bilinear"
    NEAREST = "nearest"


@dataclass(frozen=True)
class SuperResolutionPass:
    """Super-resolution pass configuration (vendor-agnostic).
    
    Abstracts DLSS Quality/Balanced/Performance, FSR UltraQuality/Quality/Balanced/Performance, etc.
    """
    input_width: int
    input_height: int
    output_width: int
    output_height: int
    method: SRMethod
    quality_preset: str  # "ultra", "quality", "balanced", "performance"
    temporal_samples: int  # Number of temporal samples for accumulation
    motion_vector_precision: Fraction  # Precision of motion vectors (0-1)
    sharpness: Fraction  # Sharpening amount (0-1)
    
    def upscale_ratio(self) -> Fraction:
        """Calculate upscale ratio."""
        return Fraction(self.output_width) / Fraction(self.input_width)
    
    def estimated_quality_score(self) -> Tuple[Fraction, ProofObject]:
        """Estimate quality score based on configuration.
        
        Higher temporal samples and motion vector precision increase quality.
        Performance presets reduce quality.
        """
        base_score = Fraction(1)
        
        # Quality preset factor
        preset_factor = {
            "ultra": Fraction(10, 10),
            "quality": Fraction(9, 10),
            "balanced": Fraction(8, 10),
            "performance": Fraction(7, 10),
        }.get(self.quality_preset, Fraction(8, 10))
        
        # Motion vector precision factor
        mv_factor = self.motion_vector_precision
        
        # Temporal samples factor (saturates around 8 samples)
        temporal_factor = Fraction(min(self.temporal_samples, 8), 8)
        
        score = base_score * preset_factor * mv_factor * temporal_factor
        
        proof = ProofObject(
            rule="SRQualityScore",
            premises=[
                f"preset={self.quality_preset}",
                f"preset_factor={preset_factor}",
                f"mv_precision={self.motion_vector_precision}",
                f"temporal_samples={self.temporal_samples}"
            ],
            conclusion=f"quality_score={score}"
        )
        
        return score, proof


@dataclass(frozen=True)
class FrameGenerationPass:
    """Frame generation (temporal interpolation) pass.
    
    e.g., DLSS 3 Frame Generation, FSR 3 FrameGen
    """
    frame_n_hash: str       # Hash of frame N
    frame_n1_hash: str      # Hash of frame N+1
    interpolated_hash: str  # Hash of generated frame
    motion_vector_error: Fraction  # Estimated motion vector error
    optical_flow_confidence: Fraction  # Confidence in optical flow (0-1)
    
    def generation_valid(self, threshold: Fraction) -> Tuple[bool, ProofObject]:
        """Check if frame generation is valid (error below threshold)."""
        valid = self.motion_vector_error <= threshold
        
        proof = ProofObject(
            rule="FrameGenValid",
            premises=[
                f"motion_error={self.motion_vector_error}",
                f"threshold={threshold}",
                f"flow_confidence={self.optical_flow_confidence}"
            ],
            conclusion=f"valid={valid}"
        )
        
        return valid, proof


@dataclass(frozen=True)
class RayReconstructionPass:
    """Ray reconstruction / denoising pass.
    
    e.g., DLSS 3.5 Ray Reconstruction, Intel Denoiser
    """
    samples_per_pixel: int  # Input sample count
    denoiser_method: str    # "neural", "SVGF", "NRD", etc.
    bias: Fraction          # Estimated bias introduced by denoiser
    variance: Fraction      # Remaining variance after denoising
    
    def bias_variance_tradeoff(self) -> Tuple[Fraction, ProofObject]:
        """Evaluate bias-variance tradeoff.
        
        Lower is better. Ideally both bias and variance approach 0.
        """
        # Simple sum of bias and variance as tradeoff metric
        tradeoff = self.bias + self.variance
        
        proof = ProofObject(
            rule="BiasVarianceTradeoff",
            premises=[
                f"bias={self.bias}",
                f"variance={self.variance}",
                f"method={self.denoiser_method}"
            ],
            conclusion=f"tradeoff={tradeoff}"
        )
        
        return tradeoff, proof
    
    def is_acceptable(self, max_bias: Fraction, max_variance: Fraction) -> Tuple[bool, ProofObject]:
        """Check if denoising result is within acceptable bounds."""
        acceptable = (self.bias <= max_bias) and (self.variance <= max_variance)
        
        proof = ProofObject(
            rule="DenoiseAcceptable",
            premises=[
                f"bias={self.bias} (max={max_bias})",
                f"variance={self.variance} (max={max_variance})"
            ],
            conclusion=f"acceptable={acceptable}"
        )
        
        return acceptable, proof


@dataclass(frozen=True)
class VendorCapability:
    """Represents a vendor-specific graphics capability."""
    vendor: Vendor
    feature: str            # e.g., "DLSS", "FSR", "XeSS", "frame_generation"
    api_version: str        # API version required
    fallback_available: bool  # Whether fallback exists
    fallback_method: Optional[str] = None  # What fallback method to use
    
    def can_run_on(self, target_vendor: Vendor) -> Tuple[bool, ProofObject]:
        """Check if this capability can run on target vendor (directly or via fallback)."""
        direct = (self.vendor == target_vendor)
        via_fallback = self.fallback_available and target_vendor == Vendor.GENERIC
        can_run = direct or via_fallback
        
        proof = ProofObject(
            rule="VendorCompatibility",
            premises=[
                f"capability_vendor={self.vendor}",
                f"target_vendor={target_vendor}",
                f"fallback_available={self.fallback_available}"
            ],
            conclusion=f"can_run={can_run}"
        )
        
        return can_run, proof


@dataclass(frozen=True)
class TemporalFrame:
    """A frame with temporal metadata."""
    frame_hash: str
    timestamp: Fraction
    motion_vectors_valid: bool


def temporal_stability_metric(frame_a: TemporalFrame, frame_b: TemporalFrame,
                              motion_magnitude: Fraction) -> Tuple[Fraction, ProofObject]:
    """Calculate temporal stability metric between two frames.
    
    Lower is better (0 = identical, higher = more change).
    """
    # Base metric: hash difference indicates change
    hash_diff = Fraction(0) if frame_a.frame_hash == frame_b.frame_hash else Fraction(1)
    
    # Weight by motion magnitude
    stability = hash_diff * motion_magnitude
    
    proof = ProofObject(
        rule="TemporalStability",
        premises=[
            f"hash_diff={hash_diff}",
            f"motion_magnitude={motion_magnitude}"
        ],
        conclusion=f"stability={stability}"
    )
    
    return stability, proof
