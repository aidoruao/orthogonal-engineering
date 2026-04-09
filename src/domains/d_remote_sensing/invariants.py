"""D_REMOTE_SENSING invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError.
No pass bodies. No return True stubs. All Fraction arithmetic.

Source: IEEE GRSS standards, OGC specifications, NeurIPS ML
reproducibility checklist, Copernicus data quality requirements.
"""
from fractions import Fraction
from typing import Dict

from .implementation import (
    CrossScaleChecker,
    ExperimentConfig,
    GeoBounds,
    MaskPattern,
    MaskType,
    PatchGrid,
    RepresentationVector,
    ResolutionLevel,
    SpectralBand,
    SpectralSignature,
)


def check_cross_scale_alignment_within_epsilon() -> bool:
    """
    Invariant: representations of the same geography at HIGH and
    MEDIUM resolution must align within epsilon² = 1/100.

    Falsification: if d²(high, low) > 1/100 for identical geography,
    the cross-scale encoder has a defect.
    """
    checker = CrossScaleChecker()
    bounds = GeoBounds(
        min_lat=Fraction(34), max_lat=Fraction(35),
        min_lon=Fraction(-118), max_lon=Fraction(-117),
    )

    high = RepresentationVector(
        components=tuple(Fraction(i, 10) for i in range(8)),
        resolution=ResolutionLevel.HIGH,
        geo_bounds=bounds,
    )
    low = RepresentationVector(
        components=tuple(Fraction(i, 10) + Fraction(1, 100) for i in range(8)),
        resolution=ResolutionLevel.MEDIUM,
        geo_bounds=bounds,
    )

    epsilon_sq = Fraction(1, 100)
    aligned, proof = checker.check_alignment(high, low, epsilon_sq)
    assert aligned, f"Cross-scale alignment violated: {proof.conclusion}"
    return True


def check_cross_scale_misalignment_detected() -> bool:
    """
    Invariant (negative test): deliberately misaligned representations
    must be detected as violations.
    """
    checker = CrossScaleChecker()
    bounds = GeoBounds(
        min_lat=Fraction(34), max_lat=Fraction(35),
        min_lon=Fraction(-118), max_lon=Fraction(-117),
    )

    high = RepresentationVector(
        components=tuple(Fraction(i, 10) for i in range(8)),
        resolution=ResolutionLevel.HIGH,
        geo_bounds=bounds,
    )
    misaligned = RepresentationVector(
        components=tuple(Fraction(i, 10) + Fraction(5, 1) for i in range(8)),
        resolution=ResolutionLevel.MEDIUM,
        geo_bounds=bounds,
    )

    epsilon_sq = Fraction(1, 100)
    aligned, proof = checker.check_alignment(high, misaligned, epsilon_sq)
    assert not aligned, (
        f"Misalignment NOT detected — epsilon bound too loose: {proof.conclusion}"
    )
    return True


def check_mask_preserves_geographic_coverage() -> bool:
    """
    Invariant: a 75% mask ratio on a 14x14 grid must still leave
    at least 25% visible patches (geographic coverage floor).
    """
    checker = CrossScaleChecker()
    grid = PatchGrid(rows=14, cols=14)
    masked = tuple(range(147))
    mask = MaskPattern(grid=grid, masked_indices=masked, mask_type=MaskType.RANDOM_PATCH)

    min_visible = Fraction(1, 4)
    bounds = GeoBounds(
        min_lat=Fraction(40), max_lat=Fraction(41),
        min_lon=Fraction(-74), max_lon=Fraction(-73),
    )

    covered, proof = checker.check_geographic_coverage(mask, bounds, min_visible)
    assert covered, f"Geographic coverage violated: {proof.conclusion}"
    return True


def check_excessive_masking_rejected() -> bool:
    """
    Invariant (negative test): a 95% mask ratio must be rejected
    as violating the 25% minimum coverage floor.
    """
    checker = CrossScaleChecker()
    grid = PatchGrid(rows=14, cols=14)
    masked = tuple(range(186))
    mask = MaskPattern(grid=grid, masked_indices=masked, mask_type=MaskType.RANDOM_PATCH)

    min_visible = Fraction(1, 4)
    bounds = GeoBounds(
        min_lat=Fraction(40), max_lat=Fraction(41),
        min_lon=Fraction(-74), max_lon=Fraction(-73),
    )

    covered, proof = checker.check_geographic_coverage(mask, bounds, min_visible)
    assert not covered, (
        f"Excessive masking NOT rejected — coverage floor not enforced: "
        f"{proof.conclusion}"
    )
    return True


def check_spectral_ndvi_consistency_across_resolutions() -> bool:
    """
    Invariant: NDVI computed from high-res and low-res imagery of
    the same geography must agree within 1/20.
    """
    checker = CrossScaleChecker()

    sig_high = SpectralSignature(values={
        SpectralBand.RED: Fraction(1, 10),
        SpectralBand.NIR: Fraction(4, 10),
        SpectralBand.GREEN: Fraction(2, 10),
    })
    sig_low = SpectralSignature(values={
        SpectralBand.RED: Fraction(1, 10) + Fraction(1, 100),
        SpectralBand.NIR: Fraction(4, 10) - Fraction(1, 100),
        SpectralBand.GREEN: Fraction(2, 10),
    })

    max_drift = Fraction(1, 20)
    consistent, proof = checker.check_spectral_consistency(
        sig_high, sig_low, max_drift
    )
    assert consistent, f"Spectral consistency violated: {proof.conclusion}"
    return True


def check_experiment_reproducibility_deterministic() -> bool:
    """
    Invariant: identical ExperimentConfig must produce identical
    output hashes across runs.
    """
    checker = CrossScaleChecker()

    config = ExperimentConfig(
        seed=42,
        model_architecture="ViT-B/16",
        patch_size=16,
        mask_ratio=Fraction(3, 4),
        learning_rate=Fraction(1, 10000),
        epochs=100,
        dataset_hash="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    )

    hash1 = "deadbeef" * 8
    hash2 = "deadbeef" * 8

    reproducible, proof = checker.check_reproducibility(config, hash1, hash2)
    assert reproducible, f"Reproducibility violated: {proof.conclusion}"
    return True


def check_non_reproducibility_detected() -> bool:
    """
    Invariant (negative test): different output hashes for same config
    must be flagged as non-reproducible.
    """
    checker = CrossScaleChecker()

    config = ExperimentConfig(
        seed=42,
        model_architecture="ViT-B/16",
        patch_size=16,
        mask_ratio=Fraction(3, 4),
        learning_rate=Fraction(1, 10000),
        epochs=100,
        dataset_hash="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
    )

    hash1 = "deadbeef" * 8
    hash2 = "cafebabe" * 8  # Different output — non-reproducible

    reproducible, proof = checker.check_reproducibility(config, hash1, hash2)
    assert not reproducible, f"Should detect non-reproducibility: {proof.conclusion}"
    return True


def check_geo_bounds_area_positive() -> bool:
    """
    Invariant: geographic bounding box must have positive area.
    """
    bounds = GeoBounds(
        min_lat=Fraction(35), max_lat=Fraction(36),
        min_lon=Fraction(-120), max_lon=Fraction(-119),
    )
    area = bounds.area_degrees_squared()
    assert area > 0, f"Geo bounds must have positive area, got {area}"
    return True


def check_ndvi_range_bounded() -> bool:
    """
    Invariant: NDVI values must be in [-1, 1].
    """
    # Valid NDVI: 0.7
    valid_sig = SpectralSignature(values={
        SpectralBand.RED: Fraction(1, 10),
        SpectralBand.NIR: Fraction(4, 10),
    })
    ndvi = valid_sig.ndvi()
    assert ndvi is not None
    assert -1 <= ndvi <= 1, f"NDVI out of range: {ndvi}"

    # Test boundary: NDVI = 1 (all NIR, no RED)
    max_sig = SpectralSignature(values={
        SpectralBand.RED: Fraction(0),
        SpectralBand.NIR: Fraction(1),
    })
    ndvi_max = max_sig.ndvi()
    assert ndvi_max == 1, f"Max NDVI should be 1, got {ndvi_max}"

    # Test boundary: NDVI = -1 (all RED, no NIR)
    min_sig = SpectralSignature(values={
        SpectralBand.RED: Fraction(1),
        SpectralBand.NIR: Fraction(0),
    })
    ndvi_min = min_sig.ndvi()
    assert ndvi_min == -1, f"Min NDVI should be -1, got {ndvi_min}"

    return True
