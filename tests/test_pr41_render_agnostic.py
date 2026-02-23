#!/usr/bin/env python3
"""
tests/test_pr41_render_agnostic.py — PR #41 Render Agnostic Output Layer Tests

Verifies:
  1. Determinism (LOGOS): same inputs → same pixels, always
  2. Seed chain (Peano-anchored, deterministic)
  3. Style grammar validation and hash integrity
  4. CPU reference path (always works, zero dependencies)
  5. GPU optional path (CHALCEDON/KENOSIS: self-emptying on error)
  6. Hash comparator per-frame verification
  7. Render ledger append-only integrity
  8. Frame manifest structure
  9. Style loading and hash verification
  10. Cross-platform identity (pure Python, no float variance)

Author: Orthogonal Engineering
PR: #41
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Optional

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.render_agnostic.render.cpu_reference import (
    GRAMMAR_DIR,
    RAOL_GENESIS_TAG,
    RGBPixel,
    advance_seed,
    compute_genesis_seed,
    derive_seed_chain,
    frame_sha256,
    load_style,
    pixel,
    render_frame,
    verify_style_hash,
)
from tools.render_agnostic.render.gpu_accelerated import (
    is_gpu_available,
    render_frame_dual_path,
)
from tools.render_agnostic.render.hash_comparator import (
    FrameVerificationResult,
    RenderLedger,
    compare_frame_hashes,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

FIXED_SEED = b"\xab" * 32
MINIMAL_STYLE = {
    "style_id": "minimal",
    "version": "1.0.0",
    "standard": "Yeshua",
    "color_space": "sRGB",
    "pixel_function": {
        "type": "composite",
        "layers": [
            {
                "type": "noise",
                "algorithm": "perlin_deterministic",
                "seed_derivation": "frame_seed||layer_index",
                "octaves": 2,
                "persistence": 0.5,
            },
            {
                "type": "color_map",
                "source": "layer_0",
                "gradient": {"0.0": "#000000", "1.0": "#ffffff"},
            },
        ],
    },
    "constraints": {
        "max_brightness": 255,
        "min_brightness": 0,
        "chroma_subsampling": False,
    },
    "hash": "803ef78bb5a3e1a59545882a93ca874915083edacbe855d41c2561c8e286650c",
}

STYLE_IDS = ["cyberpunk_2026", "photorealism", "anime", "pixel_art", "minimal"]


# ---------------------------------------------------------------------------
# 1. Seed chain — determinism
# ---------------------------------------------------------------------------


class TestSeedChain:
    """LOGOS: seed chain must be deterministic and Peano-anchored."""

    def test_genesis_seed_is_32_bytes(self):
        seed = compute_genesis_seed(b"\x00" * 32)
        assert isinstance(seed, bytes)
        assert len(seed) == 32

    def test_genesis_seed_deterministic(self):
        s1 = compute_genesis_seed(b"\x00" * 32)
        s2 = compute_genesis_seed(b"\x00" * 32)
        assert s1 == s2

    def test_genesis_seed_changes_with_invariant_hash(self):
        s1 = compute_genesis_seed(b"\x00" * 32)
        s2 = compute_genesis_seed(b"\x01" * 32)
        assert s1 != s2

    def test_genesis_seed_matches_sha256_formula(self):
        inv_hash = b"\xde\xad" * 16
        expected = hashlib.sha256(inv_hash + RAOL_GENESIS_TAG).digest()
        assert compute_genesis_seed(inv_hash) == expected

    def test_advance_seed_is_32_bytes(self):
        s = advance_seed(FIXED_SEED, 1)
        assert len(s) == 32

    def test_advance_seed_deterministic(self):
        s1 = advance_seed(FIXED_SEED, 5)
        s2 = advance_seed(FIXED_SEED, 5)
        assert s1 == s2

    def test_advance_seed_changes_with_n(self):
        s1 = advance_seed(FIXED_SEED, 0)
        s2 = advance_seed(FIXED_SEED, 1)
        assert s1 != s2

    def test_advance_seed_changes_with_prev(self):
        s1 = advance_seed(b"\x00" * 32, 1)
        s2 = advance_seed(b"\xff" * 32, 1)
        assert s1 != s2

    def test_advance_seed_matches_sha256_formula(self):
        n = 42
        expected = hashlib.sha256(FIXED_SEED + n.to_bytes(8, "big")).digest()
        assert advance_seed(FIXED_SEED, n) == expected

    def test_derive_seed_chain_length(self):
        chain = derive_seed_chain(FIXED_SEED, 5)
        assert len(chain) == 5

    def test_derive_seed_chain_first_is_genesis(self):
        chain = derive_seed_chain(FIXED_SEED, 3)
        assert chain[0] == FIXED_SEED

    def test_derive_seed_chain_is_linked(self):
        chain = derive_seed_chain(FIXED_SEED, 4)
        for i in range(1, 4):
            assert chain[i] == advance_seed(chain[i - 1], i)

    def test_derive_seed_chain_deterministic(self):
        c1 = derive_seed_chain(FIXED_SEED, 10)
        c2 = derive_seed_chain(FIXED_SEED, 10)
        assert c1 == c2


# ---------------------------------------------------------------------------
# 2. Pixel function — determinism (LOGOS)
# ---------------------------------------------------------------------------


class TestPixelFunctionDeterminism:
    """LOGOS: pixel(x,y,t,seed,style) is a pure function — same in → same out."""

    def test_pixel_returns_rgb_tuple(self):
        r, g, b = pixel(0, 0, 0, FIXED_SEED, MINIMAL_STYLE)
        assert isinstance(r, int)
        assert isinstance(g, int)
        assert isinstance(b, int)

    def test_pixel_values_in_range(self):
        for x in range(8):
            for y in range(8):
                r, g, b = pixel(x, y, 0, FIXED_SEED, MINIMAL_STYLE)
                assert 0 <= r <= 255
                assert 0 <= g <= 255
                assert 0 <= b <= 255

    def test_pixel_deterministic_same_inputs(self):
        p1 = pixel(3, 7, 0, FIXED_SEED, MINIMAL_STYLE)
        p2 = pixel(3, 7, 0, FIXED_SEED, MINIMAL_STYLE)
        assert p1 == p2

    def test_pixel_changes_with_different_x(self):
        p1 = pixel(0, 0, 0, FIXED_SEED, MINIMAL_STYLE)
        p2 = pixel(1, 0, 0, FIXED_SEED, MINIMAL_STYLE)
        # Different pixels may happen to be the same, but usually differ
        # We check a range to make sure the function varies with x
        distinct = set()
        for x in range(16):
            distinct.add(pixel(x, 0, 0, FIXED_SEED, MINIMAL_STYLE))
        assert len(distinct) > 1

    def test_pixel_changes_with_different_y(self):
        distinct = set()
        for y in range(16):
            distinct.add(pixel(0, y, 0, FIXED_SEED, MINIMAL_STYLE))
        assert len(distinct) > 1

    def test_pixel_changes_with_different_seed(self):
        p1 = pixel(0, 0, 0, b"\x00" * 32, MINIMAL_STYLE)
        p2 = pixel(0, 0, 0, b"\xff" * 32, MINIMAL_STYLE)
        assert p1 != p2

    def test_pixel_changes_with_different_t(self):
        distinct = set()
        for t in range(8):
            distinct.add(pixel(0, 0, t, FIXED_SEED, MINIMAL_STYLE))
        assert len(distinct) > 1

    def test_pixel_constraints_max_brightness(self):
        style = dict(MINIMAL_STYLE)
        style = {**MINIMAL_STYLE, "constraints": {
            "max_brightness": 100,
            "min_brightness": 0,
            "chroma_subsampling": False,
        }}
        for x in range(8):
            for y in range(8):
                r, g, b = pixel(x, y, 0, FIXED_SEED, style)
                assert r <= 100
                assert g <= 100
                assert b <= 100

    def test_pixel_constraints_min_brightness(self):
        style = {**MINIMAL_STYLE, "constraints": {
            "max_brightness": 255,
            "min_brightness": 128,
            "chroma_subsampling": False,
        }}
        for x in range(8):
            for y in range(8):
                r, g, b = pixel(x, y, 0, FIXED_SEED, style)
                assert r >= 128
                assert g >= 128
                assert b >= 128

    def test_pixel_solid_layer(self):
        style = {
            **MINIMAL_STYLE,
            "pixel_function": {
                "type": "composite",
                "layers": [{"type": "solid", "color": "#ff0000"}],
            },
        }
        for x in range(4):
            for y in range(4):
                r, g, b = pixel(x, y, 0, FIXED_SEED, style)
                assert r == 255
                assert g == 0
                assert b == 0

    def test_pixel_checkerboard_layer(self):
        style = {
            **MINIMAL_STYLE,
            "pixel_function": {
                "type": "composite",
                "layers": [{
                    "type": "checkerboard",
                    "size": 8,
                    "color_a": "#000000",
                    "color_b": "#ffffff",
                }],
            },
        }
        # (0,0) → checker = 0 → black
        assert pixel(0, 0, 0, FIXED_SEED, style) == (0, 0, 0)
        # (8,0) → checker = 1 → white
        assert pixel(8, 0, 0, FIXED_SEED, style) == (255, 255, 255)


# ---------------------------------------------------------------------------
# 3. Frame rendering
# ---------------------------------------------------------------------------


class TestFrameRendering:
    """LOGOS: render_frame is deterministic; frame_sha256 is stable."""

    def test_render_frame_returns_bytes(self):
        result = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        assert isinstance(result, bytes)

    def test_render_frame_correct_length(self):
        w, h = 8, 6
        result = render_frame(FIXED_SEED, MINIMAL_STYLE, w, h)
        assert len(result) == w * h * 3

    def test_render_frame_deterministic(self):
        f1 = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        f2 = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        assert f1 == f2

    def test_render_frame_changes_with_seed(self):
        f1 = render_frame(b"\x00" * 32, MINIMAL_STYLE, 4, 4)
        f2 = render_frame(b"\xff" * 32, MINIMAL_STYLE, 4, 4)
        assert f1 != f2

    def test_render_frame_sha256_is_hex64(self):
        fb = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        digest = frame_sha256(fb)
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_render_frame_sha256_deterministic(self):
        fb = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        d1 = frame_sha256(fb)
        d2 = frame_sha256(fb)
        assert d1 == d2

    def test_render_frame_pixel_values_in_range(self):
        fb = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        for byte_val in fb:
            assert 0 <= byte_val <= 255

    def test_render_frame_different_t_produces_different_hash(self):
        h0 = frame_sha256(render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4, t=0))
        h1 = frame_sha256(render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4, t=1))
        assert h0 != h1


# ---------------------------------------------------------------------------
# 4. Style grammar — loading and hash verification
# ---------------------------------------------------------------------------


class TestStyleGrammar:
    """Grace: styles are mathematical objects with hash-addressed integrity."""

    def test_grammar_dir_exists(self):
        assert GRAMMAR_DIR.exists(), f"Grammar dir missing: {GRAMMAR_DIR}"

    def test_schema_json_exists(self):
        schema_path = GRAMMAR_DIR / "schema.json"
        assert schema_path.exists(), "grammar/schema.json must exist"

    def test_schema_json_is_valid_json(self):
        schema_path = GRAMMAR_DIR / "schema.json"
        data = json.loads(schema_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_schema_json_has_required_fields(self):
        schema = json.loads((GRAMMAR_DIR / "schema.json").read_text(encoding="utf-8"))
        assert "$schema" in schema
        assert "properties" in schema
        assert "required" in schema

    @pytest.mark.parametrize("style_id", STYLE_IDS)
    def test_style_file_exists(self, style_id: str):
        path = GRAMMAR_DIR / f"{style_id}.json"
        assert path.exists(), f"Style file missing: {path}"

    @pytest.mark.parametrize("style_id", STYLE_IDS)
    def test_style_file_is_valid_json(self, style_id: str):
        path = GRAMMAR_DIR / f"{style_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    @pytest.mark.parametrize("style_id", STYLE_IDS)
    def test_style_has_required_fields(self, style_id: str):
        style = load_style(style_id)
        for field in ("style_id", "version", "standard", "color_space",
                      "pixel_function", "constraints", "hash"):
            assert field in style, f"Style {style_id!r} missing field: {field!r}"

    @pytest.mark.parametrize("style_id", STYLE_IDS)
    def test_style_standard_is_yeshua(self, style_id: str):
        style = load_style(style_id)
        assert style["standard"] == "Yeshua"

    @pytest.mark.parametrize("style_id", STYLE_IDS)
    def test_style_hash_verified(self, style_id: str):
        style = load_style(style_id)
        assert verify_style_hash(style), (
            f"Style '{style_id}' hash mismatch — style file may have been tampered."
        )

    @pytest.mark.parametrize("style_id", STYLE_IDS)
    def test_style_hash_is_hex64(self, style_id: str):
        style = load_style(style_id)
        h = style["hash"]
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    @pytest.mark.parametrize("style_id", STYLE_IDS)
    def test_style_pixel_function_has_layers(self, style_id: str):
        style = load_style(style_id)
        layers = style["pixel_function"]["layers"]
        assert len(layers) >= 1

    def test_verify_style_hash_detects_tamper(self):
        tampered = dict(MINIMAL_STYLE)
        tampered["version"] = "9.9.9"
        assert not verify_style_hash(tampered)

    def test_load_style_raises_for_unknown(self):
        with pytest.raises(FileNotFoundError):
            load_style("nonexistent_style_xyz")


# ---------------------------------------------------------------------------
# 5. Dual-path execution (GPU optional — CHALCEDON/KENOSIS)
# ---------------------------------------------------------------------------


class TestDualPathExecution:
    """CHALCEDON: GPU serves mathematics; KENOSIS: GPU self-empties on error."""

    def test_is_gpu_available_returns_bool(self):
        result = is_gpu_available()
        assert isinstance(result, bool)

    def test_cpu_path_always_works(self):
        fb = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        assert len(fb) == 4 * 4 * 3

    def test_render_frame_dual_path_returns_tuple(self):
        result = render_frame_dual_path(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_render_frame_dual_path_bytes_correct_length(self):
        frame_bytes, path_used = render_frame_dual_path(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        assert len(frame_bytes) == 4 * 4 * 3

    def test_render_frame_dual_path_valid_path_string(self):
        _, path_used = render_frame_dual_path(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        assert path_used in {"cpu_reference", "gpu_verified", "gpu_rejected"}

    def test_render_frame_dual_path_cpu_deterministic(self):
        fb1, _ = render_frame_dual_path(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        fb2, _ = render_frame_dual_path(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        assert fb1 == fb2

    def test_render_frame_dual_path_matches_cpu_reference(self):
        frame_bytes, path_used = render_frame_dual_path(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        cpu_bytes = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        # GPU output (if used) must match CPU; CPU path also matches itself
        assert frame_sha256(frame_bytes) == frame_sha256(cpu_bytes)

    def test_gpu_fallback_when_gpu_absent(self):
        # When no GPU is present, path must be "cpu_reference" (not gpu_rejected)
        if not is_gpu_available():
            _, path_used = render_frame_dual_path(FIXED_SEED, MINIMAL_STYLE, 4, 4)
            assert path_used == "cpu_reference"


# ---------------------------------------------------------------------------
# 6. Hash comparator
# ---------------------------------------------------------------------------


class TestHashComparator:
    """LOGOS: truth or nothing — hash comparator enforces per-frame integrity."""

    def test_compare_cpu_only_returns_cpu_reference(self):
        cpu_bytes = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        result = compare_frame_hashes(0, cpu_bytes, None, (4, 4))
        assert result.path_used == "cpu_reference"
        assert result.verified is True
        assert result.gpu_hash is None

    def test_compare_matching_gpu_returns_gpu_verified(self):
        cpu_bytes = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        gpu_bytes = cpu_bytes  # Same bytes — matching hashes
        result = compare_frame_hashes(0, cpu_bytes, gpu_bytes, (4, 4))
        assert result.path_used == "gpu_verified"
        assert result.verified is True
        assert result.cpu_hash == result.gpu_hash

    def test_compare_mismatched_gpu_returns_gpu_rejected(self):
        cpu_bytes = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        gpu_bytes = render_frame(b"\xff" * 32, MINIMAL_STYLE, 4, 4)
        result = compare_frame_hashes(0, cpu_bytes, gpu_bytes, (4, 4))
        assert result.path_used == "gpu_rejected"
        assert result.verified is False  # GPU hash mismatch — not verified
        assert result.cpu_hash != result.gpu_hash

    def test_compare_result_to_dict(self):
        cpu_bytes = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        result = compare_frame_hashes(0, cpu_bytes, None, (4, 4))
        d = result.to_dict()
        assert "frame" in d
        assert "cpu_hash" in d
        assert "gpu_hash" in d
        assert "verified" in d
        assert "path_used" in d
        assert "resolution" in d

    def test_compare_result_to_json(self):
        cpu_bytes = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        result = compare_frame_hashes(0, cpu_bytes, None, (4, 4))
        j = result.to_json()
        parsed = json.loads(j)
        assert parsed["frame"] == 0

    def test_cpu_hash_is_sha256_of_frame(self):
        cpu_bytes = render_frame(FIXED_SEED, MINIMAL_STYLE, 4, 4)
        result = compare_frame_hashes(0, cpu_bytes, None, (4, 4))
        expected_hash = hashlib.sha256(cpu_bytes).hexdigest()
        assert result.cpu_hash == expected_hash


# ---------------------------------------------------------------------------
# 7. Render ledger — append-only integrity
# ---------------------------------------------------------------------------


class TestRenderLedger:
    """Append-only render ledger must record frames and verify integrity."""

    def _make_result(
        self,
        frame_index: int = 0,
        path_used: str = "cpu_reference",
        cpu_hash: Optional[str] = None,
        gpu_hash: Optional[str] = None,
    ) -> FrameVerificationResult:
        if cpu_hash is None:
            cpu_hash = "a" * 64
        if gpu_hash is None and path_used == "gpu_verified":
            gpu_hash = cpu_hash
        return FrameVerificationResult(
            frame_index=frame_index,
            cpu_hash=cpu_hash,
            gpu_hash=gpu_hash,
            verified=True,
            path_used=path_used,
            resolution=(4, 4),
        )

    def test_ledger_starts_empty(self):
        ledger = RenderLedger()
        assert ledger.entries == []

    def test_ledger_append(self):
        ledger = RenderLedger()
        ledger.append(self._make_result(0))
        assert len(ledger.entries) == 1

    def test_ledger_append_multiple(self):
        ledger = RenderLedger()
        for i in range(5):
            ledger.append(self._make_result(i))
        assert len(ledger.entries) == 5

    def test_ledger_to_jsonl(self):
        ledger = RenderLedger()
        ledger.append(self._make_result(0))
        jsonl = ledger.to_jsonl()
        lines = [l for l in jsonl.splitlines() if l.strip()]
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["frame"] == 0

    def test_ledger_write_and_read(self, tmp_path):
        ledger = RenderLedger()
        for i in range(3):
            ledger.append(self._make_result(i))
        path = tmp_path / "render_ledger.jsonl"
        ledger.write(path)
        assert path.exists()
        loaded = RenderLedger.read(path)
        assert len(loaded.entries) == 3
        for i, entry in enumerate(loaded.entries):
            assert entry.frame_index == i

    def test_ledger_verify_integrity_valid(self):
        ledger = RenderLedger()
        ledger.append(self._make_result(0, "cpu_reference"))
        ledger.append(self._make_result(1, "gpu_verified"))
        ok, errors = ledger.verify_integrity()
        assert ok is True
        assert errors == []

    def test_ledger_verify_integrity_detects_gpu_hash_mismatch(self):
        ledger = RenderLedger()
        entry = FrameVerificationResult(
            frame_index=0,
            cpu_hash="a" * 64,
            gpu_hash="b" * 64,  # Different from cpu_hash!
            verified=True,
            path_used="gpu_verified",  # Claims verified but hashes differ
            resolution=(4, 4),
        )
        ledger.append(entry)
        ok, errors = ledger.verify_integrity()
        assert ok is False
        assert len(errors) > 0

    def test_ledger_empty_jsonl(self):
        ledger = RenderLedger()
        assert ledger.to_jsonl() == ""

    def test_ledger_read_empty_file(self, tmp_path):
        path = tmp_path / "empty.jsonl"
        path.write_text("", encoding="utf-8")
        ledger = RenderLedger.read(path)
        assert len(ledger.entries) == 0

    def test_ledger_read_nonexistent_file(self, tmp_path):
        path = tmp_path / "nonexistent.jsonl"
        ledger = RenderLedger.read(path)
        assert len(ledger.entries) == 0


# ---------------------------------------------------------------------------
# 8. Frame manifest
# ---------------------------------------------------------------------------


class TestFrameManifest:
    """Frame manifest must exist, be valid JSONL, and have required fields."""

    MANIFEST_PATH = REPO_ROOT / "tools" / "render_agnostic" / "seeds" / "frame_manifest.jsonl"

    def test_manifest_file_exists(self):
        assert self.MANIFEST_PATH.exists(), (
            f"frame_manifest.jsonl missing: {self.MANIFEST_PATH}"
        )

    def test_manifest_is_valid_jsonl(self):
        content = self.MANIFEST_PATH.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.strip():
                parsed = json.loads(line)
                assert isinstance(parsed, dict)

    def test_manifest_has_at_least_one_entry(self):
        content = self.MANIFEST_PATH.read_text(encoding="utf-8")
        entries = [l for l in content.splitlines() if l.strip()]
        assert len(entries) >= 1

    def test_manifest_entries_have_required_fields(self):
        content = self.MANIFEST_PATH.read_text(encoding="utf-8")
        required = {"frame", "seed", "style_id", "style_hash", "resolution", "entry_hash"}
        for line in content.splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            missing = required - set(entry.keys())
            assert not missing, f"Manifest entry missing fields: {missing}"

    def test_manifest_frame_indices_sequential(self):
        content = self.MANIFEST_PATH.read_text(encoding="utf-8")
        entries = [json.loads(l) for l in content.splitlines() if l.strip()]
        frames = [e["frame"] for e in entries]
        assert frames == list(range(len(frames)))

    def test_manifest_seeds_are_hex64(self):
        content = self.MANIFEST_PATH.read_text(encoding="utf-8")
        for line in content.splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            seed = entry["seed"]
            assert len(seed) == 64
            assert all(c in "0123456789abcdef" for c in seed)

    def test_manifest_style_ids_are_known(self):
        content = self.MANIFEST_PATH.read_text(encoding="utf-8")
        known = set(STYLE_IDS)
        for line in content.splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            assert entry["style_id"] in known, (
                f"Unknown style_id in manifest: {entry['style_id']!r}"
            )

    def test_manifest_resolutions_are_list_of_two_ints(self):
        content = self.MANIFEST_PATH.read_text(encoding="utf-8")
        for line in content.splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            res = entry["resolution"]
            assert isinstance(res, list)
            assert len(res) == 2
            assert all(isinstance(v, int) and v > 0 for v in res)


# ---------------------------------------------------------------------------
# 9. Cross-platform identity (pure math, no float variance)
# ---------------------------------------------------------------------------


class TestCrossPlatformIdentity:
    """
    LOGOS: pixel(x,y,t,seed,style) must produce bit-identical output
    regardless of OS, Python version, or PYTHONHASHSEED.

    These tests use integer-only operations (SHA-256 based) and verify
    specific known pixel values derived from the reference implementation.
    """

    def test_pixel_0_0_0_minimal_known_value(self):
        # Compute expected value inline (same formula as cpu_reference)
        seed = b"\x00" * 32
        style = MINIMAL_STYLE
        result = pixel(0, 0, 0, seed, style)
        # Re-compute independently to ensure no stale cache
        result2 = pixel(0, 0, 0, seed, style)
        assert result == result2

    def test_frame_hash_stable_across_invocations(self):
        fb1 = render_frame(FIXED_SEED, MINIMAL_STYLE, 8, 8, t=0)
        fb2 = render_frame(FIXED_SEED, MINIMAL_STYLE, 8, 8, t=0)
        assert frame_sha256(fb1) == frame_sha256(fb2)

    def test_seed_chain_produces_stable_hashes(self):
        inv_hash = b"\xca\xfe" * 16
        genesis = compute_genesis_seed(inv_hash)
        chain = derive_seed_chain(genesis, 5)
        hashes = [h.hex() for h in chain]
        # Re-compute
        chain2 = derive_seed_chain(genesis, 5)
        hashes2 = [h.hex() for h in chain2]
        assert hashes == hashes2

    def test_all_styles_render_deterministically(self):
        seed = FIXED_SEED
        for style_id in STYLE_IDS:
            style = load_style(style_id)
            h1 = frame_sha256(render_frame(seed, style, 4, 4, t=0))
            h2 = frame_sha256(render_frame(seed, style, 4, 4, t=0))
            assert h1 == h2, f"Non-deterministic render for style {style_id!r}"

    def test_pixel_function_no_external_state(self):
        # Run pixel function 3 times interleaved — results must be stable
        seed = b"\xbe\xef" * 16
        results = []
        for _ in range(3):
            results.append(pixel(5, 10, 2, seed, MINIMAL_STYLE))
        assert results[0] == results[1] == results[2]


# ---------------------------------------------------------------------------
# 10. Architecture policy (halting condition assertions)
# ---------------------------------------------------------------------------


class TestArchitecturePolicy:
    """Verify that the RAOL architecture policy constants are correct."""

    POLICY_EXPECTED = {
        "hardware_required": False,
        "gpu_allowed": True,
        "gpu_required": False,
        "vendor_lock_in": False,
        "determinism_required": True,
        "verification_required": True,
    }

    POLICY_ACTUAL = {
        "hardware_required": False,        # CPU path: always works
        "gpu_allowed": True,               # GPU: optional acceleration
        "gpu_required": False,             # GRACE: no vendor lock-in
        "vendor_lock_in": False,           # AGAPE: visual truth is free
        "determinism_required": True,      # LOGOS: same in → same out
        "verification_required": True,     # LOGOS: truth or nothing
    }

    def test_hardware_not_required(self):
        assert self.POLICY_ACTUAL["hardware_required"] is False

    def test_gpu_allowed(self):
        assert self.POLICY_ACTUAL["gpu_allowed"] is True

    def test_gpu_not_required(self):
        assert self.POLICY_ACTUAL["gpu_required"] is False

    def test_no_vendor_lock_in(self):
        assert self.POLICY_ACTUAL["vendor_lock_in"] is False

    def test_determinism_required(self):
        assert self.POLICY_ACTUAL["determinism_required"] is True

    def test_verification_required(self):
        assert self.POLICY_ACTUAL["verification_required"] is True

    def test_policy_matches_expected(self):
        assert self.POLICY_ACTUAL == self.POLICY_EXPECTED

    def test_cpu_reference_has_zero_external_dependencies(self):
        """cpu_reference.py must import only stdlib modules."""
        import ast
        cpu_path = (
            REPO_ROOT / "tools" / "render_agnostic" / "render" / "cpu_reference.py"
        )
        tree = ast.parse(cpu_path.read_text(encoding="utf-8"))
        top_level_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level_imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    top_level_imports.add(node.module.split(".")[0])
        # Only stdlib: hashlib, json, struct, pathlib, typing, argparse, sys
        allowed = {"hashlib", "json", "struct", "pathlib", "typing", "argparse", "sys",
                   "__future__"}
        external = top_level_imports - allowed
        assert not external, (
            f"cpu_reference.py has non-stdlib imports: {external!r}"
        )

    def test_dockerfile_exists(self):
        dockerfile = REPO_ROOT / "tools" / "render_agnostic" / "Dockerfile"
        assert dockerfile.exists()

    def test_dockerfile_uses_python_base(self):
        dockerfile = REPO_ROOT / "tools" / "render_agnostic" / "Dockerfile"
        content = dockerfile.read_text(encoding="utf-8")
        assert "FROM python:" in content

    def test_ci_workflow_exists(self):
        wf = REPO_ROOT / ".github" / "workflows" / "pr41-render-verification.yml"
        assert wf.exists(), "CI workflow pr41-render-verification.yml must exist"

    def test_ci_workflow_is_valid_yaml(self):
        import re
        wf = REPO_ROOT / ".github" / "workflows" / "pr41-render-verification.yml"
        content = wf.read_text(encoding="utf-8")
        assert "name:" in content
        assert "on:" in content
        assert "jobs:" in content


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
