"""D_GRAPHICS_REALITY invariant checks."""

from typing import Tuple
from fractions import Fraction

from axioms.logic import ProofObject
from src.domains.d_graphics_reality.implementation import (
    FrameGenerationPass,
    RayReconstructionPass,
    SuperResolutionPass,
    TemporalFrame,
    Vendor,
    VendorCapability,
    temporal_stability_metric,
)


def check_temporal_stability(frame_a: TemporalFrame, frame_b: TemporalFrame,
                             motion_magnitude: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: Temporal stability metric within acceptable bounds.
    
    Large motion should correlate with expected frame differences.
    
    Falsifies if: temporal_stability_metric reports instability beyond threshold
    falsifies_if: temporal_stability_metric reports instability beyond threshold
    or raises during evaluation.
    """
    stability, proof = temporal_stability_metric(frame_a, frame_b, motion_magnitude)
    
    # Threshold for stability (arbitrary, would be tuned)
    acceptable = stability < Fraction(1)
    
    proof_with_threshold = ProofObject(
        rule="TemporalStability",
        premises=proof.premises,
        conclusion=f"acceptable={acceptable} (stability={stability})"
    )
    
    return acceptable, proof_with_threshold


def check_upscale_spectral_preservation(input_bandwidth: Fraction, 
                                        output_bandwidth: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: Upscaling preserves spectral content within Nyquist limits.
    
    Output bandwidth should not exceed what can be properly represented
    given the upscale ratio.
    
    Falsifies if: output_bandwidth exceeds twice the input_bandwidth (ratio > 2).
    falsifies_if: output_bandwidth exceeds twice the input_bandwidth (ratio > 2).
    """
    if input_bandwidth == Fraction(0):
        return True, ProofObject(
            rule="SpectralPreservation",
            premises=["input_bandwidth is zero"],
            conclusion="n/a"
        )
    
    # Output bandwidth should not exceed 2x input (conservative)
    ratio = output_bandwidth / input_bandwidth
    preserved = ratio <= Fraction(2)
    
    proof = ProofObject(
        rule="SpectralPreservation",
        premises=[
            f"input_bw={input_bandwidth}",
            f"output_bw={output_bandwidth}",
            f"ratio={ratio}"
        ],
        conclusion=f"preserved={preserved}"
    )
    
    return preserved, proof


def check_frame_gen_motion_error(pass_: FrameGenerationPass, 
                                 threshold: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: Frame generation motion error below threshold.
    
    High motion vector error leads to visual artifacts.
    
    Falsifies if: generation_valid returns False for the provided threshold.
    falsifies_if: generation_valid returns False for the provided threshold.
    """
    return pass_.generation_valid(threshold)


def check_vendor_fallback_exists(capability: VendorCapability) -> Tuple[bool, ProofObject]:
    """Invariant: Vendor-specific features have fallback paths.
    
    Ensures portability across GPU vendors.
    
    Falsifies if: fallback_available is False for the capability.
    falsifies_if: fallback_available is False for the capability.
    """
    has_fallback = capability.fallback_available
    
    proof = ProofObject(
        rule="VendorFallback",
        premises=[
            f"vendor={capability.vendor}",
            f"feature={capability.feature}",
            f"fallback_available={capability.fallback_available}"
        ],
        conclusion=f"has_fallback={has_fallback}"
    )
    
    return has_fallback, proof


def check_ray_reconstruction_bias_variance(pass_: RayReconstructionPass,
                                           max_bias: Fraction,
                                           max_variance: Fraction) -> Tuple[bool, ProofObject]:
    """Invariant: Ray reconstruction within bias-variance bounds.
    
    Denoising must not introduce excessive bias or leave excessive variance.
    
    Falsifies if: is_acceptable returns False for the provided bias/variance bounds.
    falsifies_if: is_acceptable returns False for the provided bias/variance bounds.
    """
    return pass_.is_acceptable(max_bias, max_variance)


def run_all_invariants() -> dict:
    """Run all invariant checks against deterministic reference fixtures.

    Each invariant is evaluated on a pinned Fraction-only fixture so the dict
    returned is deterministic and covers every contract exposed by the module.
    Fixtures are chosen to be well inside the acceptable region; each check
    is expected to pass. Values are ``"PASS"`` on success or
    ``"FAIL: <conclusion>"`` on failure so that generic callers (see
    ``src/layers/inter_layer_morphism.py``) that compare against the
    sentinel ``"PASS"`` continue to work.

    Falsifies if: any invariant check returns False on its reference fixture,
    raises an exception, or produces a non-string status value.
    falsifies_if: any invariant check returns False on its reference fixture,
    raises an exception, or produces a non-string status value.
    """
    frame_a = TemporalFrame(
        frame_hash="a" * 64, timestamp=Fraction(0), motion_vectors_valid=True
    )
    frame_b = TemporalFrame(
        frame_hash="a" * 64, timestamp=Fraction(1, 60), motion_vectors_valid=True
    )
    stability_ok, stability_proof = check_temporal_stability(
        frame_a, frame_b, motion_magnitude=Fraction(1, 2)
    )

    spectral_ok, spectral_proof = check_upscale_spectral_preservation(
        input_bandwidth=Fraction(1), output_bandwidth=Fraction(3, 2)
    )

    frame_gen_pass = FrameGenerationPass(
        frame_n_hash="b" * 64,
        frame_n1_hash="c" * 64,
        interpolated_hash="d" * 64,
        motion_vector_error=Fraction(1, 100),
        optical_flow_confidence=Fraction(9, 10),
    )
    frame_gen_ok, frame_gen_proof = check_frame_gen_motion_error(
        frame_gen_pass, threshold=Fraction(1, 10)
    )

    capability = VendorCapability(
        vendor=Vendor.NVIDIA,
        feature="DLSS",
        api_version="3.5",
        fallback_available=True,
        fallback_method="FSR",
    )
    vendor_ok, vendor_proof = check_vendor_fallback_exists(capability)

    ray_pass = RayReconstructionPass(
        samples_per_pixel=4,
        denoiser_method="neural",
        bias=Fraction(1, 100),
        variance=Fraction(1, 50),
    )
    ray_ok, ray_proof = check_ray_reconstruction_bias_variance(
        ray_pass, max_bias=Fraction(1, 20), max_variance=Fraction(1, 10)
    )

    def _status(ok: bool, proof: ProofObject) -> str:
        return "PASS" if ok else f"FAIL: {proof.conclusion}"

    return {
        "temporal_stability": _status(stability_ok, stability_proof),
        "spectral_preservation": _status(spectral_ok, spectral_proof),
        "frame_gen_motion_error": _status(frame_gen_ok, frame_gen_proof),
        "vendor_fallback": _status(vendor_ok, vendor_proof),
        "ray_reconstruction_bias_variance": _status(ray_ok, ray_proof),
    }
