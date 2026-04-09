"""D_REMOTE_SENSING implementation — dataclasses and verification logic.

All arithmetic uses Fraction. No floats. No randomness.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from axioms.logic import ProofObject


class ResolutionLevel(Enum):
    """Satellite imagery resolution tiers."""
    VERY_HIGH = auto()   # <1m GSD (WorldView, Pleiades)
    HIGH = auto()        # 1-5m GSD (SPOT, PlanetScope)
    MEDIUM = auto()      # 5-30m GSD (Sentinel-2, Landsat)
    LOW = auto()         # 30-250m GSD (MODIS)
    VERY_LOW = auto()    # >250m GSD (geostationary)


class SpectralBand(Enum):
    """Common spectral bands in earth observation."""
    COASTAL = auto()
    BLUE = auto()
    GREEN = auto()
    RED = auto()
    RED_EDGE = auto()
    NIR = auto()         # Near-infrared
    SWIR1 = auto()       # Short-wave infrared 1
    SWIR2 = auto()       # Short-wave infrared 2
    THERMAL = auto()
    PAN = auto()         # Panchromatic


class MaskType(Enum):
    """Types of masking strategies for self-supervised learning."""
    RANDOM_PATCH = auto()
    STRUCTURED_GRID = auto()
    SPECTRAL_BAND = auto()
    GEOGRAPHIC_AWARE = auto()
    ATTENTION_GUIDED = auto()


@dataclass(frozen=True)
class GeoBounds:
    """Geographic bounding box in decimal degrees (as Fraction)."""
    min_lat: Fraction
    max_lat: Fraction
    min_lon: Fraction
    max_lon: Fraction

    def area_degrees_squared(self) -> Fraction:
        """Area in degrees squared (approximate, not geodetic)."""
        return (self.max_lat - self.min_lat) * (self.max_lon - self.min_lon)

    def contains(self, lat: Fraction, lon: Fraction) -> bool:
        return (self.min_lat <= lat <= self.max_lat and
                self.min_lon <= lon <= self.max_lon)


@dataclass(frozen=True)
class PatchGrid:
    """Grid of image patches for masked autoencoder."""
    rows: int
    cols: int
    total_patches: int = 0

    def __post_init__(self):
        object.__setattr__(self, 'total_patches', self.rows * self.cols)


@dataclass(frozen=True)
class MaskPattern:
    """A specific masking pattern applied to a patch grid."""
    grid: PatchGrid
    masked_indices: Tuple[int, ...]
    mask_type: MaskType

    @property
    def mask_ratio(self) -> Fraction:
        if self.grid.total_patches == 0:
            return Fraction(0)
        return Fraction(len(self.masked_indices), self.grid.total_patches)

    @property
    def visible_ratio(self) -> Fraction:
        return Fraction(1) - self.mask_ratio

    @property
    def visible_indices(self) -> Tuple[int, ...]:
        all_idx = set(range(self.grid.total_patches))
        return tuple(sorted(all_idx - set(self.masked_indices)))


@dataclass(frozen=True)
class RepresentationVector:
    """A representation vector with Fraction components."""
    components: Tuple[Fraction, ...]
    resolution: ResolutionLevel
    geo_bounds: GeoBounds

    def l2_distance_squared(self, other: 'RepresentationVector') -> Fraction:
        """Squared L2 distance (avoids sqrt/float)."""
        if len(self.components) != len(other.components):
            raise ValueError(
                f"Dimension mismatch: {len(self.components)} vs "
                f"{len(other.components)}"
            )
        return sum(
            (a - b) * (a - b)
            for a, b in zip(self.components, other.components)
        )


@dataclass(frozen=True)
class SpectralSignature:
    """Spectral reflectance values per band (as Fraction)."""
    values: Dict[SpectralBand, Fraction]

    def ndvi(self) -> Optional[Fraction]:
        """Normalized Difference Vegetation Index = (NIR - RED) / (NIR + RED)."""
        nir = self.values.get(SpectralBand.NIR)
        red = self.values.get(SpectralBand.RED)
        if nir is None or red is None:
            return None
        denom = nir + red
        if denom == 0:
            return Fraction(0)
        return (nir - red) / denom

    def ndwi(self) -> Optional[Fraction]:
        """Normalized Difference Water Index = (GREEN - NIR) / (GREEN + NIR)."""
        green = self.values.get(SpectralBand.GREEN)
        nir = self.values.get(SpectralBand.NIR)
        if green is None or nir is None:
            return None
        denom = green + nir
        if denom == 0:
            return Fraction(0)
        return (green - nir) / denom


@dataclass(frozen=True)
class ExperimentConfig:
    """Deterministic experiment configuration."""
    seed: int
    model_architecture: str
    patch_size: int
    mask_ratio: Fraction
    learning_rate: Fraction
    epochs: int
    dataset_hash: str  # SHA-256 of dataset manifest

    def config_hash(self) -> str:
        """Deterministic hash of this config."""
        import hashlib
        content = (
            f"{self.seed}|{self.model_architecture}|{self.patch_size}|"
            f"{self.mask_ratio}|{self.learning_rate}|{self.epochs}|"
            f"{self.dataset_hash}"
        )
        return hashlib.sha256(content.encode()).hexdigest()


class CrossScaleChecker:
    """Verifies cross-scale representation consistency."""

    def check_alignment(
        self,
        high_res: RepresentationVector,
        low_res: RepresentationVector,
        epsilon_squared: Fraction,
    ) -> Tuple[bool, ProofObject]:
        """
        Invariant: representations of the same geography at different
        resolutions must align within epsilon (squared L2 distance).

        This is a formal bound, not a loss to minimize.
        """
        dist_sq = high_res.l2_distance_squared(low_res)
        aligned = dist_sq <= epsilon_squared

        proof = ProofObject(
            conclusion=(
                f"Cross-scale alignment {'HOLDS' if aligned else 'VIOLATED'}: "
                f"d²={dist_sq}, ε²={epsilon_squared}"
            ),
            premises=[
                f"high_res resolution: {high_res.resolution.name}",
                f"low_res resolution: {low_res.resolution.name}",
                f"dimension: {len(high_res.components)}",
                f"squared_distance: {dist_sq}",
                f"epsilon_squared: {epsilon_squared}",
                "Representations of identical geography at different "
                "resolutions must be within provable epsilon bound.",
            ],
            rule="cross_scale_alignment",
        )
        return aligned, proof

    def check_geographic_coverage(
        self,
        mask: MaskPattern,
        geo_bounds: GeoBounds,
        min_visible_ratio: Fraction,
    ) -> Tuple[bool, ProofObject]:
        """
        Invariant: masking must preserve minimum geographic coverage.
        A mask that hides too much of a geographic region loses
        semantic information irrecoverably.
        """
        covered = mask.visible_ratio >= min_visible_ratio

        proof = ProofObject(
            conclusion=(
                f"Geographic coverage {'HOLDS' if covered else 'VIOLATED'}: "
                f"visible={mask.visible_ratio}, min={min_visible_ratio}"
            ),
            premises=[
                f"grid: {mask.grid.rows}x{mask.grid.cols} = {mask.grid.total_patches} patches",
                f"masked: {len(mask.masked_indices)} patches",
                f"visible_ratio: {mask.visible_ratio}",
                f"min_visible_ratio: {min_visible_ratio}",
                f"mask_type: {mask.mask_type.name}",
                "Masking strategy must preserve minimum semantic coverage "
                "to ensure geographic features remain recoverable.",
            ],
            rule="geographic_coverage_preservation",
        )
        return covered, proof

    def check_spectral_consistency(
        self,
        sig_high: SpectralSignature,
        sig_low: SpectralSignature,
        max_ndvi_drift: Fraction,
    ) -> Tuple[bool, ProofObject]:
        """
        Invariant: spectral indices (NDVI, NDWI) must remain consistent
        across resolution levels. Drift beyond threshold indicates
        information loss in the downsampling pipeline.
        """
        ndvi_high = sig_high.ndvi()
        ndvi_low = sig_low.ndvi()

        if ndvi_high is None or ndvi_low is None:
            proof = ProofObject(
                conclusion="Spectral consistency SKIPPED: missing NIR or RED band",
                premises=["Required bands not present in one or both signatures",
                          "Cannot compute NDVI without NIR and RED bands"],
                rule="spectral_consistency",
            )
            return True, proof  # Vacuously true if bands missing

        drift = abs(ndvi_high - ndvi_low)
        consistent = drift <= max_ndvi_drift

        proof = ProofObject(
            conclusion=(
                f"Spectral consistency {'HOLDS' if consistent else 'VIOLATED'}: "
                f"NDVI drift={drift}, max={max_ndvi_drift}"
            ),
            premises=[
                f"NDVI (high-res): {ndvi_high}",
                f"NDVI (low-res): {ndvi_low}",
                f"drift: {drift}",
                f"max_allowed_drift: {max_ndvi_drift}",
                "Spectral indices must remain stable across resolution "
                "levels. Excessive drift indicates pipeline error.",
            ],
            rule="spectral_consistency",
        )
        return consistent, proof

    def check_reproducibility(
        self,
        config: ExperimentConfig,
        output_hash_run1: str,
        output_hash_run2: str,
    ) -> Tuple[bool, ProofObject]:
        """
        Invariant: identical experiment config must produce identical
        output hash. This is deterministic reproducibility, not
        statistical reproducibility.
        """
        reproducible = output_hash_run1 == output_hash_run2

        proof = ProofObject(
            conclusion=(
                f"Reproducibility {'HOLDS' if reproducible else 'VIOLATED'}: "
                f"{'hashes match' if reproducible else 'hashes differ'}"
            ),
            premises=[
                f"config_hash: {config.config_hash()[:16]}...",
                f"run1_output_hash: {output_hash_run1[:16]}...",
                f"run2_output_hash: {output_hash_run2[:16]}...",
                f"seed: {config.seed}",
                "Identical configuration must yield identical output. "
                "Non-determinism in ML pipelines is a defect, not a feature.",
            ],
            rule="deterministic_reproducibility",
        )
        return reproducible, proof
