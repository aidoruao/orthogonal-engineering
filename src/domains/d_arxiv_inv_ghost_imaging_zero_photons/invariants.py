"""Invariant checks for D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS — Yeshua Inversion.

Paper: arXiv 2604.07782v1 (quant-ph)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    LightSource,
    ImagingSetup,
    GhostImagingClaim,
    GhostImagingEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    # TODO: Expand check_inversion_holds() - stub detected by Yeshua Agent
    claim: GhostImagingClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: image quality meets threshold under restriction.

    Standard: arXiv 2604.07782v1 Yeshua Inversion operationalization.
    Falsifies if: image_reconstruction_quality < quality_threshold.
    falsifies_if: image_reconstruction_quality is below quality_threshold after restriction.
    """
    if claim.image_reconstruction_quality < claim.quality_threshold:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"image_reconstruction_quality={claim.image_reconstruction_quality}",
                f"quality_threshold={claim.quality_threshold}",
            ],
            conclusion="VIOLATION: Image quality below threshold — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"image_reconstruction_quality={claim.image_reconstruction_quality}",
            f"quality_threshold={claim.quality_threshold}",
        ],
        conclusion="Inversion holds: image reconstructable from zero-photon bins",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    # TODO: Expand check_domain_restriction_satisfied() - stub detected by Yeshua Agent
    claim: GhostImagingClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2604.07782v1 domain restriction operationalization.
    Falsifies if: source is not thermal, lacks photon-number resolution, or lacks post-selection.
    falsifies_if: source is not thermal, lacks photon-number resolution, or lacks post-selection.
    """
    src = claim.source
    setup = claim.setup
    violations = []

    if not src.is_thermal_light:
        violations.append("is_thermal_light=False")
    if not src.has_photon_number_resolution:
        violations.append("has_photon_number_resolution=False")
    if not src.has_post_selection:
        violations.append("has_post_selection=False")
    if not setup.uses_zero_photon_bins:
        violations.append("uses_zero_photon_bins=False")

    if violations:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=violations,
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"source={src.source_name}",
            "is_thermal_light=True",
            "has_photon_number_resolution=True",
            "has_post_selection=True",
            "uses_zero_photon_bins=True",
        ],
        conclusion="Domain restriction satisfied: thermal light with photon-number-resolved post-selection",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    # TODO: Expand check_original_impossibility_holds_without_restriction() - stub detected by Yeshua Agent
    claim: GhostImagingClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for unrestricted setups.

    Standard: arXiv 2604.07782v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for intensity-correlation setups.
    falsifies_if: the original theorem is contradicted for intensity-correlation setups.
    """
    src = claim.source
    setup = claim.setup

    unrestricted = setup.uses_intensity_correlation and not setup.uses_zero_photon_bins

    if unrestricted:
        if claim.image_reconstruction_quality >= claim.quality_threshold:
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "setup=intensity_correlation_only",
                    f"image_reconstruction_quality={claim.image_reconstruction_quality}",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — intensity-only setup reconstructs image",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "setup=intensity_correlation_only",
                "original_theorem=preserves_impossibility",
            ],
            conclusion="Original impossibility holds for intensity-correlation setups",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["setup=photon_number_resolved", "check=vacuous"],
        conclusion="Original impossibility check vacuous for photon-number-resolved setups",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: thermal light with photon-number resolution and post-selection
    src_thermal = LightSource(
        source_name="thermal_pnr",
        is_thermal_light=True,
        has_photon_number_resolution=True,
        has_post_selection=True,
    )
    setup_zero_photon = ImagingSetup(
        uses_intensity_correlation=False,
        uses_zero_photon_bins=True,
        object_transmissivity=Fraction(1, 2),
    )
    claim_safe = GhostImagingClaim(
        source=src_thermal,
        setup=setup_zero_photon,
        image_reconstruction_quality=Fraction(8, 10),
        quality_threshold=Fraction(6, 10),
    )

    # FAIL case: intensity-correlation-only setup
    setup_intensity = ImagingSetup(
        uses_intensity_correlation=True,
        uses_zero_photon_bins=False,
        object_transmissivity=Fraction(1, 2),
    )
    claim_bad = GhostImagingClaim(
        source=src_thermal,
        setup=setup_intensity,
        image_reconstruction_quality=Fraction(8, 10),
        quality_threshold=Fraction(6, 10),
    )

    # FAIL case 2: thermal light but image quality too low
    claim_low_quality = GhostImagingClaim(
        source=src_thermal,
        setup=setup_zero_photon,
        image_reconstruction_quality=Fraction(3, 10),
        quality_threshold=Fraction(6, 10),
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_original_impossibility_holds_without_restriction_fail", lambda: check_original_impossibility_holds_without_restriction(claim_bad)),
        ("check_inversion_holds_fail_low_quality", lambda: check_inversion_holds(claim_low_quality)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail") and not k.endswith("_vacuous")
    ]
    unexpected = [
        k for k, v in results.items()
        if k.endswith("_fail") and not v.startswith("FAIL")
    ]
    failures.extend(unexpected)
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARXIV_INV_GHOST_IMAGING_ZERO_PHOTONS invariants: PASS")
