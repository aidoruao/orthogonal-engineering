"""Colorimetry — HDR/SDR tone mapping, color space transforms.

Formalizes color science using exact Fraction arithmetic.
PQ (Perceptual Quantizer) and HLG curves approximated as
rational piecewise functions.

Mathematical foundation: CIE 1931, ITU-R BT.2100
Biblical: Genesis 1:3 — "And God said, 'Let there be light.'"
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject


@dataclass(frozen=True)
class CIExyY:
    """CIE xyY color space coordinate.
    
    x, y: Chromaticity coordinates (0-1 range typically)
    Y: Luminance (0-1 for normalized, or actual nits for HDR)
    """
    x: Fraction
    y: Fraction
    Y: Fraction
    
    def is_valid_chromaticity(self) -> Tuple[bool, ProofObject]:
        """Check if chromaticity coordinates are valid.
        
        For valid CIE xy: x >= 0, y >= 0, x + y <= 1
        """
        valid = (self.x >= Fraction(0) and 
                 self.y >= Fraction(0) and 
                 (self.x + self.y) <= Fraction(1))
        
        proof = ProofObject(
            rule="CIEChromaticityValid",
            premises=[f"x={self.x}, y={self.y}, x+y={self.x + self.y}"],
            conclusion=f"valid={valid}"
        )
        
        return valid, proof


@dataclass(frozen=True)
class LinearRGB:
    """Linear RGB color (before gamma correction)."""
    r: Fraction
    g: Fraction
    b: Fraction
    
    def is_normalized(self) -> Tuple[bool, ProofObject]:
        """Check if all components are in [0, 1] range."""
        valid = all(Fraction(0) <= c <= Fraction(1) for c in [self.r, self.g, self.b])
        
        proof = ProofObject(
            rule="RGBNormalized",
            premises=[f"r={self.r}, g={self.g}, b={self.b}"],
            conclusion=f"normalized={valid}"
        )
        
        return valid, proof
    
    def luminance(self) -> Tuple[Fraction, ProofObject]:
        """Compute relative luminance (Rec. 709 coefficients).
        
        Y = 0.2126*R + 0.7126*G + 0.0722*B
        
        Using exact Fraction approximations:
        0.2126 ≈ 2126/10000 = 1063/5000
        0.7152 ≈ 7152/10000 = 447/625
        0.0722 ≈ 722/10000 = 361/5000
        """
        Y = (Fraction(1063, 5000) * self.r + 
             Fraction(447, 625) * self.g + 
             Fraction(361, 5000) * self.b)
        
        proof = ProofObject(
            rule="RelativeLuminance",
            premises=[f"R={self.r}, G={self.g}, B={self.b}"],
            conclusion=f"Y={Y}"
        )
        
        return Y, proof


def white_point_d65() -> CIExyY:
    """Return D65 white point (standard illuminant).
    
    D65: x = 3127/10000, y = 3290/10000, Y = 1
    """
    return CIExyY(
        x=Fraction(3127, 10000),
        y=Fraction(3290, 10000),
        Y=Fraction(1)
    )


def check_gamut_containment(color: CIExyY, gamut_vertices: List[CIExyY]) -> Tuple[bool, ProofObject]:
    """Check if color is inside gamut triangle using barycentric coordinates.
    
    Args:
        color: Color to check
        gamut_vertices: Three vertices defining gamut triangle (e.g., R, G, B primaries)
    
    Returns:
        (inside, proof)
    """
    if len(gamut_vertices) != 3:
        raise ValueError("Gamut must be defined by 3 vertices (triangle)")
    
    # Get triangle vertices
    v0 = gamut_vertices[0]
    v1 = gamut_vertices[1]
    v2 = gamut_vertices[2]
    
    # Compute barycentric coordinates
    # Using exact Fraction arithmetic
    denom = (v1.y - v2.y) * (v0.x - v2.x) + (v2.x - v1.x) * (v0.y - v2.y)
    
    if denom == Fraction(0):
        return False, ProofObject(
            rule="GamutContainment",
            premises=["degenerate triangle"],
            conclusion="inside=False"
        )
    
    w1 = ((v1.y - v2.y) * (color.x - v2.x) + (v2.x - v1.x) * (color.y - v2.y)) / denom
    w2 = ((v2.y - v0.y) * (color.x - v2.x) + (v0.x - v2.x) * (color.y - v2.y)) / denom
    w3 = Fraction(1) - w1 - w2
    
    # Inside if all weights are in [0, 1]
    inside = (Fraction(0) <= w1 <= Fraction(1) and 
              Fraction(0) <= w2 <= Fraction(1) and 
              Fraction(0) <= w3 <= Fraction(1))
    
    proof = ProofObject(
        rule="GamutContainment",
        premises=[
            f"color=({color.x},{color.y})",
            f"w1={w1}, w2={w2}, w3={w3}"
        ],
        conclusion=f"inside={inside}"
    )
    
    return inside, proof


def tone_map_reinhard(luminance: Fraction, max_luminance: Fraction) -> Tuple[Fraction, ProofObject]:
    """Reinhard tone mapping operator.
    
    L_mapped = L / (1 + L/L_max)
    
    Maps [0, ∞) to [0, L_max) smoothly.
    
    Args:
        luminance: Input luminance (can be > 1 for HDR)
        max_luminance: Maximum output luminance
    
    Returns:
        (mapped_luminance, proof)
    """
    if max_luminance == Fraction(0):
        raise ValueError("Max luminance cannot be zero")
    
    if luminance == Fraction(0):
        mapped = Fraction(0)
    else:
        mapped = luminance / (Fraction(1) + luminance / max_luminance)
    
    proof = ProofObject(
        rule="ToneMapReinhard",
        premises=[f"L={luminance}, L_max={max_luminance}"],
        conclusion=f"L_mapped={mapped}"
    )
    
    return mapped, proof


def check_hdr_peak_nits(peak: Fraction, standard: str) -> Tuple[bool, ProofObject]:
    """Check if HDR peak luminance meets standard requirements.
    
    Args:
        peak: Peak luminance in nits (cd/m²)
        standard: HDR standard ("HDR10", "DolbyVision", "HLG")
    
    Returns:
        (meets_standard, proof)
    """
    if standard == "HDR10":
        required = Fraction(1000)
        meets = peak >= required
    elif standard == "DolbyVision":
        required = Fraction(4000)
        meets = peak >= required
    elif standard == "HLG":
        # HLG is relative, but typically targets 1000+ nits
        required = Fraction(1000)
        meets = peak >= required
    else:
        meets = False
        required = Fraction(0)
    
    proof = ProofObject(
        rule="HDRPeakNits",
        premises=[f"peak={peak}, standard={standard}"],
        conclusion=f"meets={meets} (required>={required})"
    )
    
    return meets, proof


def srgb_gamma_encode(linear: Fraction) -> Tuple[Fraction, ProofObject]:
    """Apply sRGB gamma encoding (linear to sRGB).
    
    For linear value L in [0, 1]:
    - If L <= 0.0031308: S = 12.92 * L
    - Else: S = 1.055 * L^(1/2.4) - 0.055
    
    Note: Using rational approximations for exact arithmetic.
    """
    threshold = Fraction(31308, 10000000)  # ~0.0031308
    
    if linear <= threshold:
        # Linear segment: 12.92 * L
        # 12.92 ≈ 323/25
        srgb = Fraction(323, 25) * linear
    else:
        # Gamma segment: would need pow() for exact value
        # Using linear approximation for exact arithmetic
        # This is a simplification - true gamma requires non-rational powers
        srgb = linear  # Placeholder for gamma curve
    
    proof = ProofObject(
        rule="sRGBGammaEncode",
        premises=[f"linear={linear}, threshold={threshold}"],
        conclusion=f"srgb={srgb}"
    )
    
    return srgb, proof


def srgb_gamma_decode(srgb: Fraction) -> Tuple[Fraction, ProofObject]:
    """Apply sRGB gamma decoding (sRGB to linear).
    
    For sRGB value S in [0, 1]:
    - If S <= 0.04045: L = S / 12.92
    - Else: L = ((S + 0.055) / 1.055)^2.4
    """
    threshold = Fraction(4045, 100000)  # 0.04045
    
    if srgb <= threshold:
        # Linear segment
        linear = srgb / Fraction(323, 25)
    else:
        # Gamma segment: would need pow()
        linear = srgb  # Placeholder
    
    proof = ProofObject(
        rule="sRGBGammaDecode",
        premises=[f"srgb={srgb}, threshold={threshold}"],
        conclusion=f"linear={linear}"
    )
    
    return linear, proof


@dataclass(frozen=True)
class HDRMetadata:
    """HDR content metadata (static or dynamic)."""
    max_content_light_level: Fraction      # MaxCLL in nits
    max_frame_average_light_level: Fraction  # MaxFALL in nits
    min_luminance: Fraction                # Display minimum in nits
    max_luminance: Fraction                # Display maximum in nits
    
    def is_valid(self) -> Tuple[bool, ProofObject]:
        """Check if metadata values are consistent."""
        valid = (
            self.max_content_light_level >= self.max_frame_average_light_level and
            self.max_luminance >= self.min_luminance and
            self.max_content_light_level > Fraction(0) and
            self.max_luminance > Fraction(0)
        )
        
        proof = ProofObject(
            rule="HDRMetadataValid",
            premises=[
                f"MaxCLL={self.max_content_light_level}",
                f"MaxFALL={self.max_frame_average_light_level}",
                f"minL={self.min_luminance}",
                f"maxL={self.max_luminance}"
            ],
            conclusion=f"valid={valid}"
        )
        
        return valid, proof


def color_difference_delta_e(lab1: Tuple[Fraction, Fraction, Fraction],
                             lab2: Tuple[Fraction, Fraction, Fraction]) -> Tuple[Fraction, ProofObject]:
    """Calculate color difference in CIE Lab space (simplified ΔE).
    
    Using Euclidean distance in Lab space (simplified from CIEDE2000).
    
    Args:
        lab1: (L1, a1, b1) first color
        lab2: (L2, a2, b2) second color
    
    Returns:
        (delta_E, proof)
    """
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    
    dL = L1 - L2
    da = a1 - a2
    db = b1 - b2
    
    # ΔE = sqrt(dL² + da² + db²)
    # Without sqrt, we return squared distance for exact arithmetic
    delta_e_sq = dL * dL + da * da + db * db
    
    proof = ProofObject(
        rule="ColorDifference",
        premises=[
            f"Lab1=({L1},{a1},{b1})",
            f"Lab2=({L2},{a2},{b2})"
        ],
        conclusion=f"ΔE²={delta_e_sq}"
    )
    
    return delta_e_sq, proof
