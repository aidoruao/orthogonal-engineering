"""Sampling Theory — Nyquist-Shannon for signal reconstruction.

Formalizes sampling requirements for upscaling, anti-aliasing,
and signal reconstruction using exact Fraction arithmetic.

Mathematical foundation: Shannon, "A Mathematical Theory of Communication"
Biblical: Job 38:4 — "Where were you when I laid the earth's foundation?"
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class SamplingConfig:
    """Sampling configuration for a signal."""
    sample_rate: Fraction       # Samples per unit time/space
    max_signal_freq: Fraction   # Maximum frequency in signal
    
    def nyquist_rate(self) -> Tuple[Fraction, ProofObject]:
        """Calculate Nyquist rate: 2 * f_max
        
        The Nyquist-Shannon sampling theorem states that to perfectly
        reconstruct a signal, the sample rate must be at least twice
        the maximum frequency present in the signal.
        """
        rate = Fraction(2) * self.max_signal_freq
        
        proof = ProofObject(
            rule="NyquistRate",
            premises=[f"f_max={self.max_signal_freq}"],
            conclusion=f"f_Nyquist={rate}"
        )
        
        return rate, proof
    
    def is_sufficient(self) -> Tuple[bool, ProofObject]:
        """Check if current sample rate satisfies Nyquist criterion."""
        nyquist, _ = self.nyquist_rate()
        sufficient = self.sample_rate >= nyquist
        
        proof = ProofObject(
            rule="NyquistSufficient",
            premises=[
                f"sample_rate={self.sample_rate}",
                f"nyquist_rate={nyquist}"
            ],
            conclusion=f"sufficient={sufficient}"
        )
        
        return sufficient, proof


def nyquist_rate(max_frequency: Fraction) -> Tuple[Fraction, ProofObject]:
    """Calculate Nyquist rate: 2 * max_frequency
    
    Args:
        max_frequency: Maximum frequency present in signal
    
    Returns:
        (nyquist_rate, proof)
    """
    rate = Fraction(2) * max_frequency
    
    proof = ProofObject(
        rule="NyquistRate",
        premises=[f"f_max={max_frequency}"],
        conclusion=f"f_Nyquist={rate}"
    )
    
    return rate, proof


def check_aliasing(sample_rate: Fraction, signal_freq: Fraction) -> Tuple[bool, ProofObject]:
    """Check if aliasing will occur.
    
    Aliasing occurs when sample_rate < 2 * signal_freq.
    Returns True if aliasing WILL occur.
    
    Args:
        sample_rate: Actual sampling rate
        signal_freq: Frequency component in signal
    
    Returns:
        (will_alias, proof)
    """
    will_alias = sample_rate < (Fraction(2) * signal_freq)
    
    proof = ProofObject(
        rule="AliasingCheck",
        premises=[
            f"sample_rate={sample_rate}",
            f"signal_freq={signal_freq}",
            f"nyquist_threshold={Fraction(2) * signal_freq}"
        ],
        conclusion=f"will_alias={will_alias}"
    )
    
    return will_alias, proof


def reconstruction_error_bound(sample_rate: Fraction, bandwidth: Fraction) -> Tuple[Fraction, ProofObject]:
    """Compute error bound for signal reconstruction.
    
    If sample_rate >= 2*bandwidth: perfect reconstruction possible (error = 0)
    If sample_rate < 2*bandwidth: error proportional to unrepresented frequencies
    
    Args:
        sample_rate: Actual sampling rate
        bandwidth: Signal bandwidth (highest frequency)
    
    Returns:
        (error_bound, proof)
    """
    nyquist = Fraction(2) * bandwidth
    
    if sample_rate >= nyquist:
        error = Fraction(0)
        proof = ProofObject(
            rule="ReconstructionError",
            premises=[
                f"sample_rate={sample_rate}",
                f"bandwidth={bandwidth}",
                f"nyquist={nyquist}"
            ],
            conclusion="error=0 (perfect reconstruction possible)"
        )
    else:
        # Error proportional to missing bandwidth
        error = bandwidth - sample_rate / Fraction(2)
        proof = ProofObject(
            rule="ReconstructionError",
            premises=[
                f"sample_rate={sample_rate}",
                f"bandwidth={bandwidth}",
                "sample_rate < nyquist"
            ],
            conclusion=f"error={error} (aliasing distortion)"
        )
    
    return error, proof


def upscale_factor_valid(input_res: Fraction, output_res: Fraction,
                         nyquist_limit: Fraction) -> Tuple[bool, ProofObject]:
    """Check if upscale ratio respects information-theoretic limits.
    
    For image upscaling, we cannot create information that wasn't present.
    This checks if the upscale factor is within theoretically justifiable bounds.
    
    Args:
        input_res: Input resolution (pixels per unit)
        output_res: Output resolution (pixels per unit)
        nyquist_limit: Maximum justifiable output resolution
    
    Returns:
        (valid, proof)
    """
    if input_res == Fraction(0):
        raise ValueError("Input resolution cannot be zero")
    
    upscale_factor = output_res / input_res
    
    # Upscale factor shouldn't exceed what's theoretically recoverable
    # Conservative bound: output shouldn't exceed nyquist_limit
    valid = output_res <= nyquist_limit and upscale_factor <= Fraction(4)
    
    proof = ProofObject(
        rule="UpscaleFactorValid",
        premises=[
            f"input_res={input_res}",
            f"output_res={output_res}",
            f"upscale_factor={upscale_factor}",
            f"nyquist_limit={nyquist_limit}"
        ],
        conclusion=f"valid={valid}"
    )
    
    return valid, proof


@dataclass(frozen=True)
class ImageUpscale:
    """Image upscaling operation parameters."""
    input_width: int
    input_height: int
    output_width: int
    output_height: int
    method: str  # "DLSS", "FSR", "XeSS", "PSSR", "native", "bilinear", etc.
    
    def upscale_ratio(self) -> Tuple[Fraction, ProofObject]:
        """Calculate upscale ratio as Fraction."""
        ratio_w = Fraction(self.output_width) / Fraction(self.input_width)
        ratio_h = Fraction(self.output_height) / Fraction(self.input_height)
        
        # Assume uniform scaling (aspect ratio preserved)
        ratio = ratio_w  # Could also verify ratio_w == ratio_h
        
        proof = ProofObject(
            rule="UpscaleRatio",
            premises=[
                f"input=({self.input_width},{self.input_height})",
                f"output=({self.output_width},{self.output_height})"
            ],
            conclusion=f"ratio={ratio}"
        )
        
        return ratio, proof
    
    def information_limited(self) -> Tuple[bool, ProofObject]:
        """Check if upscaling is information-theoretically limited.
        
        Returns True if the upscale creates pixels beyond Nyquist limit.
        """
        ratio, _ = self.upscale_ratio()
        
        # Beyond 4x upscale, information is purely hallucinated
        limited = ratio > Fraction(4)
        
        proof = ProofObject(
            rule="InformationLimited",
            premises=[
                f"ratio={ratio}",
                f"method={self.method}"
            ],
            conclusion=f"information_limited={limited}"
        )
        
        return limited, proof


def temporal_upsampling_valid(base_fps: Fraction, target_fps: Fraction,
                              motion_complexity: Fraction) -> Tuple[bool, ProofObject]:
    """Check if temporal upsampling (frame generation) is valid.
    
    Frame generation creates intermediate frames. Validity depends on:
    - Base fps must be sufficient for motion (Nyquist for temporal frequency)
    - Motion complexity limits how much interpolation is valid
    
    Args:
        base_fps: Original frame rate
        target_fps: Target frame rate after generation
        motion_complexity: 0-1 scale of motion complexity
    
    Returns:
        (valid, proof)
    """
    if base_fps == Fraction(0):
        raise ValueError("Base FPS cannot be zero")
    
    generation_ratio = target_fps / base_fps
    
    # Conservative: frame generation shouldn't exceed 4x
    # And motion complexity reduces valid generation
    max_valid_ratio = Fraction(4) * (Fraction(1) - motion_complexity / Fraction(2))
    
    valid = generation_ratio <= max_valid_ratio
    
    proof = ProofObject(
        rule="TemporalUpsampling",
        premises=[
            f"base_fps={base_fps}",
            f"target_fps={target_fps}",
            f"generation_ratio={generation_ratio}",
            f"motion_complexity={motion_complexity}",
            f"max_valid_ratio={max_valid_ratio}"
        ],
        conclusion=f"valid={valid}"
    )
    
    return valid, proof
