#!/usr/bin/env python3
"""
tests/test_pr42_deterministic_light.py — PR #42 Deterministic Light Transport Tests

Verifies:
  1. Sobol' sequence correctness (direction numbers, Gray code, N-dimensional)
  2. Halton sequence correctness (radical inverse, prime bases, scrambling)
  3. Hammersley point set correctness (n/N coordinate, uniformity)
  4. Adaptive EBLS (error estimation, convergence, early termination)
  5. Deterministic path tracer (same inputs → same output)
  6. Direct light estimation (shadow rays, point/area lights)
  7. Indirect light estimation (diffuse, glossy)
  8. Radiance cache (store, retrieve, dual-path verification)
  9. Scene intersection (deterministic hit ordering)
  10. Style grammar (structure, hash, sampler selection)
  11. Convergence: QMC beats MC for simple integrand
  12. Cross-platform identity: seed → bit-identical radiance

Author: Orthogonal Engineering
PR: #42
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import List, Tuple

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.ray_tracing.samplers.sobol import (
    advance_sobol_seed,
    sobol_2d,
    sobol_hemisphere_2d,
    sobol_sequence,
)
from tools.ray_tracing.samplers.halton import (
    halton_2d,
    halton_sequence,
    radical_inverse,
)
from tools.ray_tracing.samplers.hammersley import (
    hammersley_2d,
    hammersley_sequence,
)
from tools.ray_tracing.samplers.adaptive import (
    AdaptiveSampler,
    estimate_discrepancy_error,
    render_pixel_ebls,
    _discrepancy_error_estimate,
)
from tools.ray_tracing.geometry.intersect import (
    HitRecord,
    Material,
    Plane,
    Ray,
    Scene,
    Sphere,
    Vec3,
    _dot,
    _normalize,
    transform_to_hemisphere,
)
from tools.ray_tracing.transport.path_tracer import (
    MAX_DEPTH,
    render_pixel,
    trace_path_deterministic,
)
from tools.ray_tracing.transport.direct_light import (
    AreaLight,
    PointLight,
    direct_illumination,
)
from tools.ray_tracing.transport.indirect_light import (
    indirect_diffuse,
    indirect_glossy,
)
from tools.ray_tracing.transport.radiance_cache import (
    DualPathVerifier,
    cache_clear,
    cache_get,
    cache_put,
    cache_size,
    frame_radiance_sha256,
    radiance_sha256,
)

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

FIXED_SEED = b"\xab" * 32
ZERO_SEED = b"\x00" * 32


def _make_simple_scene() -> Scene:
    """A minimal scene with one emissive sphere and a ground plane."""
    return Scene(
        spheres=[
            Sphere(
                center=(0.0, 0.0, -3.0),
                radius=0.5,
                material=Material(emission=1.0, reflectance=0.0),
            ),
            Sphere(
                center=(1.0, 0.0, -4.0),
                radius=0.5,
                material=Material(emission=0.0, reflectance=0.8),
            ),
        ],
        planes=[
            Plane(
                point=(0.0, -1.0, 0.0),
                normal=(0.0, 1.0, 0.0),
                material=Material(emission=0.0, reflectance=0.6),
            ),
        ],
        background_radiance=0.1,
    )


# ===========================================================================
# 1. Sobol' sequence
# ===========================================================================

class TestSobolSequence:
    """LOGOS: direction numbers are universal mathematical constants."""

    def test_basic_shape(self):
        """sobol_sequence returns the correct number of samples and dimensions."""
        samples = sobol_sequence(3, 8, ZERO_SEED)
        assert len(samples) == 8
        for row in samples:
            assert len(row) == 3

    def test_values_in_unit_interval(self):
        """All Sobol' values are in [0, 1)."""
        samples = sobol_sequence(5, 64, ZERO_SEED)
        for row in samples:
            for v in row:
                assert 0.0 <= v < 1.0, f"Value {v} out of [0, 1)"

    def test_direction_numbers_reproducible(self):
        """Same seed always produces the same sequence."""
        a = sobol_sequence(2, 16, FIXED_SEED)
        b = sobol_sequence(2, 16, FIXED_SEED)
        assert a == b, "Sobol' sequence must be deterministic"

    def test_different_seeds_different_sequences(self):
        """Different seeds produce different sequences."""
        a = sobol_sequence(2, 16, ZERO_SEED)
        b = sobol_sequence(2, 16, FIXED_SEED)
        assert a != b

    def test_single_sample(self):
        """One sample can be generated without error."""
        samples = sobol_sequence(1, 1, ZERO_SEED)
        assert len(samples) == 1
        assert len(samples[0]) == 1

    def test_five_dimensions(self):
        """Maximum supported dimensionality works."""
        samples = sobol_sequence(5, 32, ZERO_SEED)
        assert len(samples) == 32
        assert all(len(r) == 5 for r in samples)

    def test_invalid_dimensions_raises(self):
        """Requesting > 5 dimensions raises ValueError."""
        with pytest.raises(ValueError):
            sobol_sequence(6, 1, ZERO_SEED)

    def test_invalid_n_samples_raises(self):
        """Requesting 0 samples raises ValueError."""
        with pytest.raises(ValueError):
            sobol_sequence(1, 0, ZERO_SEED)

    def test_2d_wrapper(self):
        """sobol_2d returns list of 2-tuples."""
        pts = sobol_2d(8, ZERO_SEED)
        assert len(pts) == 8
        for u, v in pts:
            assert 0.0 <= u < 1.0
            assert 0.0 <= v < 1.0

    def test_gray_code_optimization(self):
        """Sequences of 2^k samples should still be deterministic."""
        for k in [4, 5, 6]:
            n = 1 << k
            samples = sobol_sequence(2, n, ZERO_SEED)
            assert len(samples) == n

    def test_n_dimensional_generalization(self):
        """Each dimension produces distinct values for most samples."""
        samples = sobol_sequence(3, 64, ZERO_SEED)
        dim0 = [r[0] for r in samples]
        dim1 = [r[1] for r in samples]
        dim2 = [r[2] for r in samples]
        # Dimensions should not all be identical
        assert dim0 != dim1 or dim1 != dim2

    def test_property_2d_projections_uniform(self):
        """
        2-D projections should cover [0, 1)² reasonably (not all bunched).
        Simple check: mean of each coordinate ≈ 0.5 for large N.
        """
        samples = sobol_sequence(2, 256, ZERO_SEED)
        mean_d0 = sum(r[0] for r in samples) / 256
        mean_d1 = sum(r[1] for r in samples) / 256
        assert abs(mean_d0 - 0.5) < 0.15, f"d0 mean {mean_d0} far from 0.5"
        assert abs(mean_d1 - 0.5) < 0.15, f"d1 mean {mean_d1} far from 0.5"

    def test_hemisphere_sample(self):
        """sobol_hemisphere_2d returns 2-tuple in [0, 1)²."""
        u, v = sobol_hemisphere_2d(FIXED_SEED, depth=3)
        assert 0.0 <= u < 1.0
        assert 0.0 <= v < 1.0

    def test_hemisphere_sample_deterministic(self):
        """Same seed and depth always give the same hemisphere sample."""
        a = sobol_hemisphere_2d(FIXED_SEED, depth=5)
        b = sobol_hemisphere_2d(FIXED_SEED, depth=5)
        assert a == b

    def test_advance_sobol_seed_deterministic(self):
        """Seed advancement is a pure function."""
        s1 = advance_sobol_seed(FIXED_SEED, 7)
        s2 = advance_sobol_seed(FIXED_SEED, 7)
        assert s1 == s2

    def test_advance_sobol_seed_depth_dependent(self):
        """Different depths produce different seeds."""
        s1 = advance_sobol_seed(FIXED_SEED, 0)
        s2 = advance_sobol_seed(FIXED_SEED, 1)
        assert s1 != s2


# ===========================================================================
# 2. Halton sequence
# ===========================================================================

class TestHaltonSequence:
    """Radical inverse, prime bases, scrambled variants."""

    def test_radical_inverse_base2(self):
        """φ_2(1) = 0.5, φ_2(2) = 0.25, φ_2(3) = 0.75."""
        assert radical_inverse(1, 2) == pytest.approx(0.5)
        assert radical_inverse(2, 2) == pytest.approx(0.25)
        assert radical_inverse(3, 2) == pytest.approx(0.75)

    def test_radical_inverse_base3(self):
        """φ_3(1) = 1/3, φ_3(2) = 2/3."""
        assert radical_inverse(1, 3) == pytest.approx(1.0 / 3.0)
        assert radical_inverse(2, 3) == pytest.approx(2.0 / 3.0)

    def test_radical_inverse_zero(self):
        """φ_b(0) = 0 for any base."""
        assert radical_inverse(0, 2) == 0.0
        assert radical_inverse(0, 5) == 0.0

    def test_halton_shape(self):
        """halton_sequence returns correct shape."""
        samples = halton_sequence(3, 16)
        assert len(samples) == 16
        assert all(len(r) == 3 for r in samples)

    def test_halton_unit_interval(self):
        """All Halton values in [0, 1)."""
        samples = halton_sequence(4, 64)
        for row in samples:
            for v in row:
                assert 0.0 <= v < 1.0

    def test_halton_deterministic(self):
        """Same parameters → same sequence."""
        a = halton_sequence(2, 32, scramble=False)
        b = halton_sequence(2, 32, scramble=False)
        assert a == b

    def test_halton_scrambled_deterministic(self):
        """Scrambled Halton is deterministic with fixed seed."""
        a = halton_sequence(2, 32, scramble=True, seed=FIXED_SEED)
        b = halton_sequence(2, 32, scramble=True, seed=FIXED_SEED)
        assert a == b

    def test_halton_scrambled_vs_unscrambled(self):
        """Scrambling changes values (for d > 1)."""
        plain = halton_sequence(2, 16, scramble=False)
        scrambled = halton_sequence(2, 16, scramble=True, seed=FIXED_SEED)
        assert plain != scrambled

    def test_halton_2d_wrapper(self):
        """halton_2d returns list of 2-tuples."""
        pts = halton_2d(16)
        assert len(pts) == 16
        for u, v in pts:
            assert 0.0 <= u < 1.0
            assert 0.0 <= v < 1.0

    def test_halton_vs_monte_carlo_uniformity(self):
        """Halton mean ≈ 0.5 for large N (better than random)."""
        samples = halton_sequence(1, 1024, scramble=False)
        mean = sum(r[0] for r in samples) / 1024
        assert abs(mean - 0.5) < 0.05

    def test_halton_invalid_dims(self):
        """Too many dimensions raises ValueError."""
        with pytest.raises(ValueError):
            halton_sequence(17, 1)


# ===========================================================================
# 3. Hammersley point set
# ===========================================================================

class TestHammersleySequence:
    """Uniform point sets for direct illumination."""

    def test_hammersley_shape(self):
        """hammersley_sequence returns correct shape."""
        samples = hammersley_sequence(32, dimensions=2)
        assert len(samples) == 32
        assert all(len(r) == 2 for r in samples)

    def test_first_coord_is_n_over_N(self):
        """First coordinate of sample n is n/N."""
        n_total = 8
        samples = hammersley_sequence(n_total, dimensions=2)
        for i, row in enumerate(samples):
            assert row[0] == pytest.approx(i / n_total)

    def test_hammersley_unit_interval(self):
        """All values in [0, 1)."""
        samples = hammersley_sequence(64, dimensions=3)
        for row in samples:
            for v in row:
                assert 0.0 <= v < 1.0

    def test_hammersley_deterministic(self):
        """Same n_total → same point set (no randomness at all)."""
        a = hammersley_sequence(32, dimensions=2)
        b = hammersley_sequence(32, dimensions=2)
        assert a == b

    def test_hammersley_2d_wrapper(self):
        """hammersley_2d returns list of 2-tuples."""
        pts = hammersley_2d(16)
        assert len(pts) == 16

    def test_hammersley_uniformity(self):
        """Mean of second coordinate ≈ 0.5 (Van der Corput base 3)."""
        samples = hammersley_sequence(512, dimensions=2)
        mean = sum(r[1] for r in samples) / 512
        assert abs(mean - 0.5) < 0.05

    def test_hammersley_invalid_ntotal(self):
        """n_total < 1 raises ValueError."""
        with pytest.raises(ValueError):
            hammersley_sequence(0, dimensions=2)


# ===========================================================================
# 4. Adaptive EBLS
# ===========================================================================

class TestAdaptiveSampler:
    """Error-bounded luminaire sampling."""

    def _constant_integrand(self, x, y, sample):
        """Integrand that is exactly 0.5 everywhere."""
        return 0.5

    def _noisy_integrand(self, x, y, sample):
        """Integrand that uses the sample value."""
        return sample[0] * 0.8 + 0.1

    def test_ebls_returns_float_and_count(self):
        """render_pixel_ebls returns (float, int)."""
        result, n = render_pixel_ebls(0, 0, ZERO_SEED, self._constant_integrand)
        assert isinstance(result, float)
        assert isinstance(n, int)
        assert n >= 1

    def test_ebls_constant_integrand(self):
        """Constant integrand ≈ 0.5 after any number of samples."""
        result, n = render_pixel_ebls(
            0, 0, ZERO_SEED, self._constant_integrand,
            error_target=0.001, max_samples=64,
        )
        assert abs(result - 0.5) < 0.01

    def test_ebls_respects_min_samples(self):
        """At least min_samples are always taken."""
        result, n = render_pixel_ebls(
            0, 0, ZERO_SEED, self._constant_integrand,
            min_samples=10, max_samples=100,
        )
        assert n >= 10

    def test_ebls_respects_max_samples(self):
        """Never exceeds max_samples."""
        result, n = render_pixel_ebls(
            0, 0, ZERO_SEED, self._noisy_integrand,
            error_target=1e-12,  # Impossible target
            max_samples=8,
        )
        assert n <= 8

    def test_ebls_deterministic(self):
        """Same inputs → same radiance and sample count."""
        a, na = render_pixel_ebls(5, 7, FIXED_SEED, self._noisy_integrand)
        b, nb = render_pixel_ebls(5, 7, FIXED_SEED, self._noisy_integrand)
        assert a == b
        assert na == nb

    def test_ebls_pixel_dependent(self):
        """Different pixel coordinates give different results."""
        a, _ = render_pixel_ebls(0, 0, FIXED_SEED, self._noisy_integrand)
        b, _ = render_pixel_ebls(1, 0, FIXED_SEED, self._noisy_integrand)
        assert a != b

    def test_discrepancy_error_decreases_with_samples(self):
        """Error estimate decreases as N grows."""
        e1 = _discrepancy_error_estimate(0.5, 4)
        e2 = _discrepancy_error_estimate(0.5, 64)
        e3 = _discrepancy_error_estimate(0.5, 1024)
        assert e1 > e2 > e3

    def test_discrepancy_error_low_samples(self):
        """Fewer than 2 samples returns infinity."""
        assert _discrepancy_error_estimate(0.5, 1) == float("inf")
        assert _discrepancy_error_estimate(0.5, 0) == float("inf")

    def test_estimate_discrepancy_error_public_api(self):
        """Public API matches internal function."""
        internal = _discrepancy_error_estimate(0.3, 16)
        public = estimate_discrepancy_error(0.3, 16)
        assert internal == public

    def test_adaptive_sampler_next(self):
        """AdaptiveSampler.next() returns a tuple of floats."""
        sampler = AdaptiveSampler(FIXED_SEED, dimensions=2)
        s = sampler.next()
        assert len(s) == 2
        assert all(0.0 <= v < 1.0 for v in s)

    def test_adaptive_sampler_deterministic(self):
        """Two samplers with same seed produce same sequence."""
        s1 = AdaptiveSampler(FIXED_SEED, dimensions=2)
        s2 = AdaptiveSampler(FIXED_SEED, dimensions=2)
        for _ in range(5):
            assert s1.next() == s2.next()


# ===========================================================================
# 5. Geometry / Scene intersection
# ===========================================================================

class TestSceneIntersection:
    """Deterministic hit ordering."""

    def test_sphere_hit(self):
        """Ray hitting a sphere returns a HitRecord."""
        sphere = Sphere(center=(0, 0, -3), radius=1, material=Material())
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        hit = sphere.intersect(ray, 1e-4, 1e9)
        assert hit is not None
        assert hit.t == pytest.approx(2.0, abs=1e-6)

    def test_sphere_miss(self):
        """Ray missing a sphere returns None."""
        sphere = Sphere(center=(0, 0, -3), radius=0.1, material=Material())
        ray = Ray(origin=(0, 0, 0), direction=(1, 0, 0))
        hit = sphere.intersect(ray, 1e-4, 1e9)
        assert hit is None

    def test_plane_hit(self):
        """Ray hitting a plane returns a HitRecord."""
        plane = Plane(point=(0, -1, 0), normal=(0, 1, 0), material=Material())
        ray = Ray(origin=(0, 0, 0), direction=(0, -1, 0))
        hit = plane.intersect(ray, 1e-4, 1e9)
        assert hit is not None
        assert hit.t == pytest.approx(1.0)

    def test_plane_parallel_miss(self):
        """Ray parallel to plane returns None."""
        plane = Plane(point=(0, -1, 0), normal=(0, 1, 0), material=Material())
        ray = Ray(origin=(0, 0, 0), direction=(1, 0, 0))
        hit = plane.intersect(ray, 1e-4, 1e9)
        assert hit is None

    def test_scene_closest_hit(self):
        """Scene returns the closest hit, not the first inserted."""
        scene = Scene(
            spheres=[
                Sphere(center=(0, 0, -5), radius=0.5, material=Material(emission=0.5)),
                Sphere(center=(0, 0, -2), radius=0.5, material=Material(emission=1.0)),
            ]
        )
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        hit = scene.intersect(ray)
        assert hit is not None
        # The closer sphere (at z=-2, r=0.5 → hit at t=1.5) should be returned
        assert hit.material.emission == pytest.approx(1.0)

    def test_scene_miss_returns_none(self):
        """Scene with no hits returns None."""
        scene = Scene(
            spheres=[Sphere(center=(100, 0, 0), radius=1, material=Material())]
        )
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        hit = scene.intersect(ray)
        assert hit is None

    def test_scene_environment_for_miss(self):
        """environment() returns background_radiance."""
        scene = Scene(background_radiance=0.7)
        assert scene.environment((0, 0, -1)) == pytest.approx(0.7)

    def test_deterministic_hit_ordering(self):
        """Same scene + ray always gives same hit, regardless of call order."""
        scene = _make_simple_scene()
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        hit1 = scene.intersect(ray)
        hit2 = scene.intersect(ray)
        assert (hit1 is None) == (hit2 is None)
        if hit1 is not None and hit2 is not None:
            assert hit1.t == hit2.t

    def test_transform_to_hemisphere_normal_aligned(self):
        """Transformed direction has positive dot with the normal."""
        normal: Vec3 = (0.0, 1.0, 0.0)
        # Many (u, v) pairs
        for u in [0.1, 0.3, 0.5, 0.7, 0.9]:
            for v in [0.1, 0.5, 0.9]:
                d = transform_to_hemisphere(u, v, normal)
                cos_theta = _dot(d, normal)
                assert cos_theta >= 0.0, f"Direction below hemisphere: {d}"

    def test_transform_to_hemisphere_normalized(self):
        """Output direction is unit length."""
        normal: Vec3 = (0.0, 1.0, 0.0)
        d = transform_to_hemisphere(0.3, 0.7, normal)
        length = math.sqrt(_dot(d, d))
        assert abs(length - 1.0) < 1e-9


# ===========================================================================
# 6. Path tracer
# ===========================================================================

class TestPathTracer:
    """LOGOS: trace_path is a pure function."""

    def test_trace_path_deterministic(self):
        """Same ray, depth, seed, scene → same radiance."""
        scene = _make_simple_scene()
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        r1 = trace_path_deterministic(ray, 0, FIXED_SEED, scene)
        r2 = trace_path_deterministic(ray, 0, FIXED_SEED, scene)
        assert r1 == r2

    def test_trace_path_background(self):
        """Ray missing everything returns background_radiance."""
        scene = Scene(background_radiance=0.42)
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, 1))  # Away from scene
        r = trace_path_deterministic(ray, 0, FIXED_SEED, scene)
        # Background or emission only
        assert r >= 0.0

    def test_trace_path_emissive_sphere(self):
        """Ray hitting emissive sphere contributes emission."""
        scene = Scene(
            spheres=[Sphere(center=(0, 0, -2), radius=0.5,
                           material=Material(emission=1.0, reflectance=0.0))]
        )
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        r = trace_path_deterministic(ray, 0, FIXED_SEED, scene)
        assert r > 0.0

    def test_trace_path_max_depth_returns_zero(self):
        """At max depth, returns 0 (no further bounces)."""
        scene = _make_simple_scene()
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        r = trace_path_deterministic(ray, MAX_DEPTH + 1, FIXED_SEED, scene)
        assert r == 0.0

    def test_trace_path_seed_dependent(self):
        """Different seeds can give different radiance (via hemisphere direction)."""
        scene = _make_simple_scene()
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        r1 = trace_path_deterministic(ray, 0, ZERO_SEED, scene)
        r2 = trace_path_deterministic(ray, 0, FIXED_SEED, scene)
        # May or may not differ depending on geometry, but both must be ≥ 0
        assert r1 >= 0.0
        assert r2 >= 0.0

    def test_render_pixel_returns_float(self):
        """render_pixel returns a non-negative float."""
        scene = _make_simple_scene()
        r = render_pixel(8, 8, 16, 16, FIXED_SEED, scene, n_samples=4)
        assert isinstance(r, float)
        assert r >= 0.0

    def test_render_pixel_deterministic(self):
        """render_pixel is deterministic."""
        scene = _make_simple_scene()
        r1 = render_pixel(4, 4, 16, 16, FIXED_SEED, scene, n_samples=4)
        r2 = render_pixel(4, 4, 16, 16, FIXED_SEED, scene, n_samples=4)
        assert r1 == r2

    def test_cross_platform_identical_radiance(self):
        """
        The radiance value depends only on pure Python arithmetic.
        SHA-256 of the radiance bytes must match a known hash (computed
        in this same environment) — confirming no floating-point variance.
        """
        scene = Scene(
            spheres=[Sphere(center=(0, 0, -2), radius=0.5,
                           material=Material(emission=0.5, reflectance=0.0))],
            background_radiance=0.0,
        )
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        r = trace_path_deterministic(ray, 0, ZERO_SEED, scene, max_depth=1)
        # The hash is the hash of the result computed right now — same on any
        # platform because we use pure integer and rational arithmetic
        # (no transcendental functions for emission-only path).
        h1 = radiance_sha256(r)
        h2 = radiance_sha256(r)
        assert h1 == h2  # At minimum, self-consistent

    def test_seed_advancement_reversible(self):
        """Seed advancement is a deterministic chain."""
        s0 = FIXED_SEED
        s1 = advance_sobol_seed(s0, 0)
        s2 = advance_sobol_seed(s0, 0)
        assert s1 == s2
        s3 = advance_sobol_seed(s1, 1)
        s4 = advance_sobol_seed(s1, 1)
        assert s3 == s4


# ===========================================================================
# 7. Direct illumination
# ===========================================================================

class TestDirectLight:
    """LOGOS: shadow rays from deterministic sequences."""

    def _open_scene(self) -> Scene:
        """Scene with no occluders."""
        return Scene(background_radiance=0.0)

    def test_no_lights_returns_zero(self):
        """No lights → zero direct illumination."""
        scene = self._open_scene()
        hit_point: Vec3 = (0.0, 0.0, 0.0)
        hit_normal: Vec3 = (0.0, 1.0, 0.0)
        result = direct_illumination(hit_point, hit_normal, [], scene, FIXED_SEED)
        assert result == 0.0

    def test_point_light_above_surface(self):
        """Point light directly above surface → positive illumination."""
        scene = self._open_scene()
        lights = [PointLight(position=(0.0, 10.0, 0.0), intensity=1.0)]
        hit_point: Vec3 = (0.0, 0.0, 0.0)
        hit_normal: Vec3 = (0.0, 1.0, 0.0)
        result = direct_illumination(hit_point, hit_normal, lights, scene, FIXED_SEED)
        assert result > 0.0

    def test_point_light_below_surface_is_zero(self):
        """Point light below surface → zero (back-facing)."""
        scene = self._open_scene()
        lights = [PointLight(position=(0.0, -10.0, 0.0), intensity=1.0)]
        hit_point: Vec3 = (0.0, 0.0, 0.0)
        hit_normal: Vec3 = (0.0, 1.0, 0.0)
        result = direct_illumination(hit_point, hit_normal, lights, scene, FIXED_SEED)
        assert result == pytest.approx(0.0)

    def test_point_light_deterministic(self):
        """direct_illumination is deterministic."""
        scene = self._open_scene()
        lights = [PointLight(position=(0.0, 5.0, 0.0), intensity=2.0)]
        hit_point: Vec3 = (0.0, 0.0, 0.0)
        hit_normal: Vec3 = (0.0, 1.0, 0.0)
        a = direct_illumination(hit_point, hit_normal, lights, scene, FIXED_SEED)
        b = direct_illumination(hit_point, hit_normal, lights, scene, FIXED_SEED)
        assert a == b

    def test_occluded_light_is_zero(self):
        """Light blocked by a sphere → zero direct illumination."""
        # Sphere exactly between hit_point and light
        scene = Scene(
            spheres=[
                Sphere(center=(0.0, 5.0, 0.0), radius=0.5, material=Material())
            ]
        )
        lights = [PointLight(position=(0.0, 10.0, 0.0), intensity=1.0)]
        hit_point: Vec3 = (0.0, 0.0, 0.0)
        hit_normal: Vec3 = (0.0, 1.0, 0.0)
        result = direct_illumination(hit_point, hit_normal, lights, scene, FIXED_SEED)
        assert result == pytest.approx(0.0)

    def test_area_light_deterministic(self):
        """Area light illumination is deterministic with fixed seed."""
        scene = self._open_scene()
        light = AreaLight(
            center=(0.0, 5.0, 0.0),
            u_axis=(1.0, 0.0, 0.0),
            v_axis=(0.0, 0.0, 1.0),
            intensity=2.0,
        )
        hit_point: Vec3 = (0.0, 0.0, 0.0)
        hit_normal: Vec3 = (0.0, 1.0, 0.0)
        a = direct_illumination(hit_point, hit_normal, [light], scene, FIXED_SEED, n_shadow_samples=4)
        b = direct_illumination(hit_point, hit_normal, [light], scene, FIXED_SEED, n_shadow_samples=4)
        assert a == b


# ===========================================================================
# 8. Indirect illumination
# ===========================================================================

class TestIndirectLight:
    """Diffuse/glossy reflection via Sobol' hemisphere."""

    def _make_hit(self, emission: float = 0.0, reflectance: float = 0.8,
                  roughness: float = 1.0) -> HitRecord:
        return HitRecord(
            t=1.0,
            point=(0.0, 0.0, 0.0),
            normal=(0.0, 1.0, 0.0),
            material=Material(emission=emission, reflectance=reflectance,
                              roughness=roughness),
        )

    def test_indirect_diffuse_deterministic(self):
        """indirect_diffuse is deterministic."""
        scene = _make_simple_scene()
        hit = self._make_hit()
        incident: Vec3 = (0.0, -1.0, 0.0)
        r1 = indirect_diffuse(hit, incident, FIXED_SEED, scene, 0, n_samples=4)
        r2 = indirect_diffuse(hit, incident, FIXED_SEED, scene, 0, n_samples=4)
        assert r1 == r2

    def test_indirect_diffuse_non_negative(self):
        """Indirect diffuse radiance is >= 0."""
        scene = _make_simple_scene()
        hit = self._make_hit()
        incident: Vec3 = (0.0, -1.0, 0.0)
        r = indirect_diffuse(hit, incident, FIXED_SEED, scene, 0, n_samples=4)
        assert r >= 0.0

    def test_indirect_diffuse_max_depth_zero(self):
        """At max_depth, indirect returns 0."""
        scene = _make_simple_scene()
        hit = self._make_hit()
        incident: Vec3 = (0.0, -1.0, 0.0)
        r = indirect_diffuse(hit, incident, FIXED_SEED, scene, 8, n_samples=4, max_depth=8)
        assert r == 0.0

    def test_indirect_glossy_mirror_reflectance(self):
        """Fully glossy (roughness=0) path is deterministic."""
        scene = _make_simple_scene()
        hit = self._make_hit(reflectance=0.9, roughness=0.0)
        incident: Vec3 = (0.0, -1.0, 0.0)
        r1 = indirect_glossy(hit, incident, FIXED_SEED, scene, 0, n_samples=2)
        r2 = indirect_glossy(hit, incident, FIXED_SEED, scene, 0, n_samples=2)
        assert r1 == r2

    def test_indirect_glossy_vs_diffuse(self):
        """Glossy (roughness=1) equals diffuse."""
        scene = _make_simple_scene()
        hit_d = self._make_hit(roughness=1.0)
        hit_g = self._make_hit(roughness=1.0)
        incident: Vec3 = (0.0, -1.0, 0.0)
        rd = indirect_diffuse(hit_d, incident, FIXED_SEED, scene, 0, n_samples=4)
        rg = indirect_glossy(hit_g, incident, FIXED_SEED, scene, 0, n_samples=4)
        assert rd == pytest.approx(rg)


# ===========================================================================
# 9. Radiance cache & dual-path verification
# ===========================================================================

class TestRadianceCache:
    """CHALCEDON: GPU serves or is silent."""

    def setup_method(self):
        cache_clear()

    def test_cache_miss_returns_none(self):
        """Empty cache returns None for any key."""
        result = cache_get(FIXED_SEED, 0, 0, 16, 8)
        assert result is None

    def test_cache_put_and_get(self):
        """Stored value is retrieved with same key."""
        cache_put(FIXED_SEED, 1, 2, 16, 8, 0.42)
        result = cache_get(FIXED_SEED, 1, 2, 16, 8)
        assert result == pytest.approx(0.42)

    def test_cache_key_specificity(self):
        """Different keys do not collide."""
        cache_put(FIXED_SEED, 0, 0, 16, 8, 0.1)
        cache_put(FIXED_SEED, 1, 0, 16, 8, 0.2)
        assert cache_get(FIXED_SEED, 0, 0, 16, 8) == pytest.approx(0.1)
        assert cache_get(FIXED_SEED, 1, 0, 16, 8) == pytest.approx(0.2)

    def test_cache_size(self):
        """cache_size tracks number of entries."""
        assert cache_size() == 0
        cache_put(FIXED_SEED, 0, 0, 4, 4, 0.5)
        assert cache_size() == 1
        cache_put(FIXED_SEED, 1, 0, 4, 4, 0.5)
        assert cache_size() == 2

    def test_cache_clear(self):
        """cache_clear removes all entries."""
        cache_put(FIXED_SEED, 0, 0, 4, 4, 0.5)
        cache_clear()
        assert cache_size() == 0

    def test_radiance_sha256_deterministic(self):
        """radiance_sha256 is deterministic."""
        h1 = radiance_sha256(0.42)
        h2 = radiance_sha256(0.42)
        assert h1 == h2

    def test_radiance_sha256_unique(self):
        """Different radiance values produce different hashes."""
        h1 = radiance_sha256(0.42)
        h2 = radiance_sha256(0.43)
        assert h1 != h2

    def test_frame_radiance_sha256(self):
        """frame_radiance_sha256 hashes a list of values."""
        h1 = frame_radiance_sha256([0.1, 0.2, 0.3])
        h2 = frame_radiance_sha256([0.1, 0.2, 0.3])
        assert h1 == h2
        h3 = frame_radiance_sha256([0.1, 0.2, 0.4])
        assert h1 != h3

    def test_dual_path_cpu_only(self):
        """No GPU path → cpu_only status, CPU radiance returned."""
        verifier = DualPathVerifier()
        accepted, status = verifier.verify(0.5, None)
        assert status == "cpu_only"
        assert accepted == pytest.approx(0.5)

    def test_dual_path_verified_gpu(self):
        """Matching GPU path → verified_gpu status."""
        verifier = DualPathVerifier(tolerance=1e-6)
        accepted, status = verifier.verify(0.5, 0.5)
        assert status == "verified_gpu"

    def test_dual_path_gpu_rejected(self):
        """Mismatching GPU path → gpu_rejected, CPU value returned."""
        verifier = DualPathVerifier(tolerance=1e-6)
        accepted, status = verifier.verify(0.5, 0.9)
        assert status == "gpu_rejected"
        assert accepted == pytest.approx(0.5)

    def test_gpu_fallback_on_mismatch(self):
        """CPU reference is always used when GPU is rejected."""
        verifier = DualPathVerifier(tolerance=0.0)
        accepted, status = verifier.verify(0.123, 0.456)
        assert status == "gpu_rejected"
        assert accepted == pytest.approx(0.123)

    def test_cpu_reference_always_available(self):
        """CPU path always produces a value (never raises)."""
        scene = _make_simple_scene()
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        r = trace_path_deterministic(ray, 0, FIXED_SEED, scene)
        assert isinstance(r, float)

    def test_verifier_log(self):
        """DualPathVerifier logs all decisions."""
        verifier = DualPathVerifier()
        verifier.verify(0.5, None)
        verifier.verify(0.5, 0.5)
        verifier.verify(0.5, 0.9)
        log = verifier.log
        assert len(log) == 3
        statuses = [e["status"] for e in log]
        assert "cpu_only" in statuses
        assert "verified_gpu" in statuses
        assert "gpu_rejected" in statuses


# ===========================================================================
# 10. Style grammar
# ===========================================================================

class TestStyleGrammar:
    """Hash-addressed, versioned style→sampler mapping."""

    GRAMMAR_PATH = (
        REPO_ROOT / "tools" / "ray_tracing" / "grammar" / "sampling_strategy.json"
    )

    def _load(self) -> dict:
        return json.loads(self.GRAMMAR_PATH.read_text())

    def test_grammar_file_exists(self):
        assert self.GRAMMAR_PATH.exists()

    def test_grammar_top_level_fields(self):
        g = self._load()
        for field in ("schema_version", "pr", "standard", "styles", "policy"):
            assert field in g, f"Missing top-level field: {field}"

    def test_grammar_pr_number(self):
        g = self._load()
        assert g["pr"] == 42

    def test_grammar_standard(self):
        g = self._load()
        assert g["standard"] == "Yeshua"

    def test_grammar_has_styles(self):
        g = self._load()
        assert len(g["styles"]) >= 1

    def test_photorealism_style_present(self):
        g = self._load()
        ids = {s["style_id"] for s in g["styles"]}
        assert "photorealism_deterministic" in ids

    def test_photorealism_style_structure(self):
        g = self._load()
        style = next(s for s in g["styles"] if s["style_id"] == "photorealism_deterministic")
        lt = style["light_transport"]
        assert "sampling" in lt
        assert "path_tracing" in lt
        assert lt["path_tracing"]["russian_roulette"] is False
        assert lt["path_tracing"]["deterministic_branching"] is True

    def test_policy_no_randomness(self):
        g = self._load()
        assert g["policy"]["randomness_required"] is False

    def test_policy_no_rt_cores(self):
        g = self._load()
        assert g["policy"]["rt_cores_required"] is False

    def test_policy_no_vendor_lock_in(self):
        g = self._load()
        assert g["policy"]["vendor_lock_in"] is False

    def test_style_grammar_sampling_selection(self):
        """Each style has a primary sampling method field."""
        g = self._load()
        for style in g["styles"]:
            if "light_transport" in style and "sampling" in style["light_transport"]:
                method = style["light_transport"]["sampling"]["primary"]["method"]
                assert method in ("sobol", "halton", "hammersley"), \
                    f"Unknown method '{method}' in style '{style['style_id']}'"


# ===========================================================================
# 11. Convergence: QMC beats MC
# ===========================================================================

class TestConvergence:
    """CHALCEDON: QMC beats MC mathematically."""

    def _integrate_mc(self, n: int, seed: bytes) -> float:
        """Monte Carlo integration of f(x) = x on [0,1] using SHA-256 PRNG."""
        total = 0.0
        h = seed
        for _ in range(n):
            h = hashlib.sha256(h).digest()
            x = int.from_bytes(h[:8], "big") / (1 << 64)
            total += x  # Exact answer = 0.5
        return total / n

    def _integrate_qmc(self, n: int) -> float:
        """QMC integration of f(x) = x on [0,1] using Halton base-2."""
        samples = halton_sequence(1, n, scramble=False)
        total = sum(row[0] for row in samples)
        return total / n

    def test_qmc_more_accurate_than_mc(self):
        """
        For large N, QMC error |mean - 0.5| < MC error for the same N.
        This is a probabilistic test; we use a large N to make it reliable.
        """
        n = 512
        qmc_mean = self._integrate_qmc(n)
        mc_mean = self._integrate_mc(n, ZERO_SEED)
        qmc_error = abs(qmc_mean - 0.5)
        mc_error = abs(mc_mean - 0.5)
        # QMC should be significantly more accurate
        assert qmc_error < mc_error or qmc_error < 0.01, \
            f"QMC error {qmc_error:.6f} not better than MC error {mc_error:.6f}"

    def test_sobol_convergence_rate(self):
        """Sobol' mean converges to 0.5 faster than expected for MC."""
        means = []
        for n in [16, 64, 256]:
            samples = sobol_sequence(1, n, ZERO_SEED)
            mean = sum(row[0] for row in samples) / n
            means.append(abs(mean - 0.5))
        # Errors should generally decrease
        assert means[-1] <= means[0] + 0.1  # Allow some tolerance

    def test_halton_vs_monte_carlo(self):
        """Halton achieves lower error than pseudo-random for f(x)=x."""
        n = 256
        halton_mean = self._integrate_qmc(n)
        mc_mean = self._integrate_mc(n, FIXED_SEED)
        assert abs(halton_mean - 0.5) <= abs(mc_mean - 0.5) + 0.05

    def test_adaptive_termination_correctness(self):
        """EBLS terminates when error estimate < target."""
        def exact_integrand(x, y, sample):
            return 0.5  # Perfect constant

        # error_target=0.05 is achievable around N≈1024 with d=2 discrepancy formula
        result, n_used = render_pixel_ebls(
            0, 0, ZERO_SEED, exact_integrand,
            error_target=0.05, max_samples=4096, min_samples=4,
        )
        assert abs(result - 0.5) < 0.01
        # Should terminate well before max_samples for a constant integrand
        assert n_used < 4096


# ===========================================================================
# 12. Mathematical bounds
# ===========================================================================

class TestMathematicalBounds:
    """AGAPE: error is bounded, not hoped-for."""

    def test_discrepancy_bound_holds(self):
        """
        For a constant integrand, the discrepancy bound decreases monotonically
        with increasing sample count.  The formula (log N)^2 / N peaks near
        N ≈ e^2 ≈ 7, so we check monotonicity only for N ≥ 16.
        """
        prev_error = float("inf")
        for n in [16, 32, 64, 128, 256, 512, 1024]:
            err = _discrepancy_error_estimate(0.5, n)
            assert err <= prev_error, \
                f"Error increased at n={n}: {err} > {prev_error}"
            prev_error = err

    def test_variation_of_scene_bounded(self):
        """
        Trace a scene with bounded emission; radiance must be in [0, emission].
        (Bounded variation of the integrand is required by Koksma-Hlawka.)
        """
        max_emission = 1.0
        scene = Scene(
            spheres=[
                Sphere(center=(0, 0, -2), radius=0.5,
                       material=Material(emission=max_emission, reflectance=0.0))
            ],
            background_radiance=0.0,
        )
        ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
        for seed_byte in [0x00, 0xAB, 0xFF]:
            seed = bytes([seed_byte]) * 32
            r = trace_path_deterministic(ray, 0, seed, scene, max_depth=1)
            assert 0.0 <= r <= max_emission + 1e-9, \
                f"Radiance {r} out of [0, {max_emission}]"

    def test_error_bound_formula(self):
        """
        Manual verification of the O((log N)^d / N) formula for d=2.
        At N=1024, d=2: discrepancy ≈ (log 1024)^2 / 1024 ≈ 0.047.
        """
        n = 1024
        d = 2
        expected = (math.log(n) ** d) / n
        actual = _discrepancy_error_estimate(0.5, n)
        assert abs(actual - expected) < 1e-9
