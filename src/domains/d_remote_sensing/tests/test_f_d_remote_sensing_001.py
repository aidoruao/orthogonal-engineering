"""Tests for D_REMOTE_SENSING domain invariants."""
from src.domains.d_remote_sensing.invariants import (
    check_cross_scale_alignment_within_epsilon,
    check_cross_scale_misalignment_detected,
    check_mask_preserves_geographic_coverage,
    check_excessive_masking_rejected,
    check_spectral_ndvi_consistency_across_resolutions,
    check_experiment_reproducibility_deterministic,
    check_non_reproducibility_detected,
    check_geo_bounds_area_positive,
    check_ndvi_range_bounded,
)

def test_cross_scale_alignment():
    assert check_cross_scale_alignment_within_epsilon()

def test_cross_scale_misalignment_detected():
    assert check_cross_scale_misalignment_detected()

def test_mask_geographic_coverage():
    assert check_mask_preserves_geographic_coverage()

def test_excessive_masking_rejected():
    assert check_excessive_masking_rejected()

def test_spectral_ndvi_consistency():
    assert check_spectral_ndvi_consistency_across_resolutions()

def test_reproducibility():
    assert check_experiment_reproducibility_deterministic()

def test_non_reproducibility_detected():
    assert check_non_reproducibility_detected()

def test_geo_bounds_positive():
    assert check_geo_bounds_area_positive()

def test_ndvi_range():
    assert check_ndvi_range_bounded()
