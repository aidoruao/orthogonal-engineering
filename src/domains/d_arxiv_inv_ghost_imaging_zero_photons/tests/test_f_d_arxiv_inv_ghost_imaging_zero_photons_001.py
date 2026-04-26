"""Tests for D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_ghost_imaging_zero_photons.implementation import (
    LightSource,
    ImagingSetup,
    GhostImagingClaim,
)
from domains.d_arxiv_inv_ghost_imaging_zero_photons.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_thermal_source():
    return LightSource(
        source_name="thermal_pnr",
        is_thermal_light=True,
        has_photon_number_resolution=True,
        has_post_selection=True,
    )


def make_zero_photon_setup():
    return ImagingSetup(
        uses_intensity_correlation=False,
        uses_zero_photon_bins=True,
        object_transmissivity=Fraction(1, 2),
    )


def make_intensity_setup():
    return ImagingSetup(
        uses_intensity_correlation=True,
        uses_zero_photon_bins=False,
        object_transmissivity=Fraction(1, 2),
    )


def make_safe_claim():
    return GhostImagingClaim(
        source=make_thermal_source(),
        setup=make_zero_photon_setup(),
        image_reconstruction_quality=Fraction(8, 10),
        quality_threshold=Fraction(6, 10),
    )


def make_bad_claim():
    return GhostImagingClaim(
        source=make_thermal_source(),
        setup=make_intensity_setup(),
        image_reconstruction_quality=Fraction(8, 10),
        quality_threshold=Fraction(6, 10),
    )


def make_low_quality_claim():
    return GhostImagingClaim(
        source=make_thermal_source(),
        setup=make_zero_photon_setup(),
        image_reconstruction_quality=Fraction(3, 10),
        quality_threshold=Fraction(6, 10),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_low_quality():
    claim = make_low_quality_claim()
    success, proof = check_inversion_holds(claim)
    assert success is False
    assert "Image quality below threshold" in proof.conclusion


def test_check_domain_restriction_satisfied_pass():
    claim = make_safe_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is True
    assert "Domain restriction satisfied" in proof.conclusion


def test_check_domain_restriction_satisfied_fail():
    claim = make_bad_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is False
    assert "Domain restriction not satisfied" in proof.conclusion


def test_check_original_impossibility_holds_without_restriction_vacuous():
    claim = make_safe_claim()
    success, proof = check_original_impossibility_holds_without_restriction(claim)
    assert success is True
    assert "vacuous" in proof.conclusion


def test_check_original_impossibility_holds_without_restriction_fail():
    claim = make_bad_claim()
    success, proof = check_original_impossibility_holds_without_restriction(claim)
    assert success is False
    assert "Original impossibility contradicted" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass") or name.endswith("_vacuous"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
