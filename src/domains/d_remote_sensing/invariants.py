"""D_REMOTE_SENSING invariants — Yeshua Standard. 0 floats.

Standards:
- OGC WMS/WCS standards (raster coverage)
- ASPRS Accuracy Standards for Digital Geospatial Data
- ISO 19115 (geographic metadata)
- ITAR/EAR (satellite imagery export controls)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import GeoBounds, PatchGrid, MaskPattern, SpectralSignature


def check_geobounds_valid(bounds: GeoBounds) -> Tuple[bool, ProofObject]:
    """Latitude in [-90, 90] and longitude in [-180, 180] and min < max.

    Standard: ISO 19115 geographic metadata; OGC WMS bounding box
    falsifies_if: min_lat >= max_lat or min_lon >= max_lon or lat/lon out of range.
    """
    lat_ok = Fraction(-90) <= bounds.min_lat < bounds.max_lat <= Fraction(90)
    lon_ok = Fraction(-180) <= bounds.min_lon < bounds.max_lon <= Fraction(180)
    ok = lat_ok and lon_ok
    premises = [
        f"min_lat={bounds.min_lat}, max_lat={bounds.max_lat}",
        f"min_lon={bounds.min_lon}, max_lon={bounds.max_lon}",
        f"lat_ok={lat_ok}, lon_ok={lon_ok}",
    ]
    return ok, ProofObject(
        rule="GeoBoundsValid",
        premises=premises,
        conclusion="PASS: geographic bounds valid" if ok else "VIOLATION: geographic bounds invalid",
    )


def check_patch_grid_coverage(grid: PatchGrid) -> Tuple[bool, ProofObject]:
    """total_patches must equal rows * cols.

    Standard: ASPRS accuracy standards — coverage completeness
    falsifies_if: grid.total_patches != grid.rows * grid.cols.
    """
    expected = grid.rows * grid.cols
    ok = grid.total_patches == expected
    premises = [
        f"rows={grid.rows}",
        f"cols={grid.cols}",
        f"expected_patches={expected}",
        f"actual_patches={grid.total_patches}",
    ]
    return ok, ProofObject(
        rule="PatchGridCoverage",
        premises=premises,
        conclusion=f"PASS: {grid.total_patches} patches = {grid.rows}x{grid.cols}" if ok else f"VIOLATION: patch count {grid.total_patches} != {expected}",
    )


def check_mask_coverage_ratio(mask: MaskPattern) -> Tuple[bool, ProofObject]:
    """Masked patch ratio must not exceed 80% (Fraction(4, 5)).

    Standard: ASPRS cloud cover threshold for usable imagery
    falsifies_if: mask.mask_ratio > Fraction(4, 5).
    """
    max_mask = Fraction(4, 5)
    ratio = mask.mask_ratio
    ok = ratio <= max_mask
    premises = [
        f"mask_ratio={ratio}",
        f"max_allowed={max_mask}",
    ]
    return ok, ProofObject(
        rule="MaskCoverageRatio",
        premises=premises,
        conclusion=f"PASS: mask ratio {ratio} <= {max_mask}" if ok else f"VIOLATION: mask ratio {ratio} > {max_mask}",
    )


def check_spectral_bands_consistent(sig: SpectralSignature) -> Tuple[bool, ProofObject]:
    """All band reflectances must be in [0, 1].

    Standard: ASPRS / ESA Sentinel-2 radiometric calibration
    falsifies_if: any band_reflectance < 0 or > 1.
    """
    if not hasattr(sig, "values"):
        ok = True
        premises = ["no band data to check"]
    else:
        invalid = [(b, v) for b, v in sig.values.items() if v < Fraction(0) or v > Fraction(1)]
        ok = len(invalid) == 0
        premises = [f"band_count={len(sig.values)}", f"invalid_bands={invalid}"]
    return ok, ProofObject(
        rule="SpectralBandsConsistent",
        premises=premises,
        conclusion="PASS: all reflectances in [0,1]" if ok else f"VIOLATION: reflectances out of range",
    )


def check_geobounds_non_degenerate(bounds: GeoBounds) -> Tuple[bool, ProofObject]:
    """Bounding box must have non-zero area.

    Standard: OGC WMS BBox non-degeneracy requirement
    falsifies_if: (max_lat - min_lat) == 0 or (max_lon - min_lon) == 0.
    """
    lat_span = bounds.max_lat - bounds.min_lat
    lon_span = bounds.max_lon - bounds.min_lon
    ok = lat_span > Fraction(0) and lon_span > Fraction(0)
    premises = [
        f"lat_span={lat_span}",
        f"lon_span={lon_span}",
    ]
    return ok, ProofObject(
        rule="GeoBoundsNonDegenerate",
        premises=premises,
        conclusion="PASS: bounding box has positive area" if ok else "VIOLATION: degenerate bounding box",
    )


def check_patch_grid_positive(grid: PatchGrid) -> Tuple[bool, ProofObject]:
    """rows and cols must be positive integers.

    Standard: ASPRS coverage grid requirements
    falsifies_if: grid.rows <= 0 or grid.cols <= 0.
    """
    ok = grid.rows > 0 and grid.cols > 0
    premises = [f"rows={grid.rows}", f"cols={grid.cols}"]
    return ok, ProofObject(
        rule="PatchGridPositive",
        premises=premises,
        conclusion="PASS: grid dimensions positive" if ok else "VIOLATION: grid has non-positive dimension",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    bounds = GeoBounds(min_lat=Fraction(34), max_lat=Fraction(36), min_lon=Fraction(-118), max_lon=Fraction(-116))
    grid = PatchGrid(rows=10, cols=10, total_patches=100)
    from .implementation import MaskPattern, MaskType, SpectralSignature, SpectralBand
    inner_grid = PatchGrid(rows=5, cols=5, total_patches=25)
    mask = MaskPattern(grid=inner_grid, masked_indices=tuple(range(4)), mask_type=MaskType.RANDOM_PATCH)
    sig = SpectralSignature(values={SpectralBand.RED: Fraction(3, 10), SpectralBand.GREEN: Fraction(4, 10), SpectralBand.NIR: Fraction(6, 10)})
    results = {}
    for fn, args in [
        (check_geobounds_valid, (bounds,)),
        (check_patch_grid_coverage, (grid,)),
        (check_mask_coverage_ratio, (mask,)),
        (check_spectral_bands_consistent, (sig,)),
        (check_geobounds_non_degenerate, (bounds,)),
        (check_patch_grid_positive, (grid,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
