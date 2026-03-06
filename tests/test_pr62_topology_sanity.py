#!/usr/bin/env python3
"""
PR #62 Topology Sanity Tests — PERCEIVABLE_INFINITY Viewport Sync
==================================================================

Tests that validate the new features introduced in the sync of
PERCEIVABLE_INFINITY with PRs #60 (Food Cart), #61 (Uncharted), #62 (Skate 4).

Coverage:
  - INV-R-004: COMMIT_INFO_SECTION_PRESENT
  - INV-R-005: DOMAIN_PANELS_PRESENT (Food Cart, Uncharted, Skate 4)
  - INV-R-006: INELASTICITY_VISUALIZATION_PRESENT (Skate 4 microtransaction nullification)
  - INV-R-007: MERKLE_PLACEHOLDER_PRESENT
  - INV-R-008: ARIA_ROLES_PRESENT (WCAG 2.1 AA accessibility)
  - INV-R-009: LOD_SECTION_PRESENT
  - INV-R-010: DARK_THEME_PRESERVED (re-affirmed after new sections)
  - INV-R-001: NO_EMBEDDED_GRAPH_DATA (re-affirmed after new sections)
  - INV-S-001: SEED_FILES_PRESENT (Food Cart, Uncharted, Skate 4)
  - INV-S-002: SKATE4_CORPORATE_CONTINGENCIES_IMPOSSIBLE
  - INV-S-003: UNIVERSE_EXPANSION_LEVELS_DEFINED

These tests run against the live PERCEIVABLE_INFINITY.html and seed YAML
files in the repository root.  They will skip if those files are absent.

Usage:
    python3 -m pytest tests/test_pr62_topology_sanity.py -v
"""

import json
import yaml
from pathlib import Path

import pytest

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
HTML_PATH = REPO_ROOT / "PERCEIVABLE_INFINITY.html"
GRAPH_PATH = REPO_ROOT / "topology_graph.json"
SEED_FOOD_CART = REPO_ROOT / "seed" / "food_cart_universe.yaml"
SEED_UNCHARTED = REPO_ROOT / "seed" / "uncharted_multiplayer_universe.yaml"
SEED_SKATE4 = REPO_ROOT / "seed" / "skate4_multiplayer_universe.yaml"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def html_content():
    """Load PERCEIVABLE_INFINITY.html (skip if absent)."""
    if not HTML_PATH.exists():
        pytest.skip(
            f"PERCEIVABLE_INFINITY.html not found at {HTML_PATH}; "
            "run generate_perceivable_infinity.py first"
        )
    return HTML_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def food_cart_seed():
    if not SEED_FOOD_CART.exists():
        pytest.skip(f"Seed file not found: {SEED_FOOD_CART}")
    return yaml.safe_load(SEED_FOOD_CART.read_text())


@pytest.fixture(scope="module")
def uncharted_seed():
    if not SEED_UNCHARTED.exists():
        pytest.skip(f"Seed file not found: {SEED_UNCHARTED}")
    return yaml.safe_load(SEED_UNCHARTED.read_text())


@pytest.fixture(scope="module")
def skate4_seed():
    if not SEED_SKATE4.exists():
        pytest.skip(f"Seed file not found: {SEED_SKATE4}")
    return yaml.safe_load(SEED_SKATE4.read_text())


# ── INV-R-001: NO_EMBEDDED_GRAPH_DATA (re-affirmed) ──────────────────────────

def test_no_embedded_graph_data_after_pr62(html_content):
    """INV-R-001: New sections must not embed graphData inline (re-affirmed)."""
    # Split on the first <script tag; content before it is pure HTML with no JS.
    # If there's no <script tag, the entire content is checked (which is fine —
    # graphData should not appear anywhere outside a script block).
    pre_script = html_content.split("<script")[0] if "<script" in html_content else html_content
    assert "graphData" not in pre_script, (
        "INV-R-001 FAILED: graphData appears to be embedded before the script block. "
        "The HTML must use fetch() at runtime — never embed the full node list."
    )
    assert "<script" in html_content, (
        "INV-R-001 WARNING: PERCEIVABLE_INFINITY.html contains no <script> block. "
        "A script block is required to call fetch(graphDataUrl) at runtime."
    )
    assert "fetch(" in html_content, (
        "INV-R-001 WARNING: PERCEIVABLE_INFINITY.html does not appear to use fetch(). "
        "Graph data must be loaded at runtime via fetch(graphDataUrl)."
    )


# ── INV-R-003: DARK_THEME_PRESERVED (re-affirmed) ─────────────────────────────

def test_dark_theme_preserved_after_pr62(html_content):
    """INV-R-003: Dark background #0a0a0a must be preserved after PR #62 changes."""
    assert "#0a0a0a" in html_content, (
        "INV-R-003 FAILED: Dark theme background '#0a0a0a' not found in HTML. "
        "The dark theme must be preserved. Do not introduce light-mode styles."
    )


# ── INV-R-004: COMMIT_INFO_SECTION_PRESENT ────────────────────────────────────

def test_commit_info_section_present(html_content):
    """INV-R-004: HTML must include a Commit Info section as a Static Witness."""
    assert "commit-info" in html_content, (
        "INV-R-004 FAILED: No commit-info section found in PERCEIVABLE_INFINITY.html. "
        "The Commit Info section must be present to display the latest substrate commit."
    )
    assert "Substrate Commit" in html_content or "commit" in html_content.lower(), (
        "INV-R-004 FAILED: Commit info section text not found in HTML."
    )


# ── INV-R-005: DOMAIN_PANELS_PRESENT ─────────────────────────────────────────

def test_food_cart_domain_panel_present(html_content):
    """INV-R-005a: Food Cart Universe domain panel must be present."""
    assert "Food Cart Universe" in html_content, (
        "INV-R-005a FAILED: Food Cart Universe panel not found in PERCEIVABLE_INFINITY.html. "
        "Substrate domain panels for all three universe PRs must be rendered."
    )


def test_uncharted_domain_panel_present(html_content):
    """INV-R-005b: Uncharted Multiplayer Universe domain panel must be present."""
    assert "Uncharted Multiplayer Universe" in html_content, (
        "INV-R-005b FAILED: Uncharted Multiplayer Universe panel not found in PERCEIVABLE_INFINITY.html."
    )


def test_skate4_domain_panel_present(html_content):
    """INV-R-005c: Skate 4 Multiplayer Universe domain panel must be present."""
    assert "Skate 4 Multiplayer Universe" in html_content, (
        "INV-R-005c FAILED: Skate 4 Multiplayer Universe panel not found in PERCEIVABLE_INFINITY.html."
    )


def test_pr_badges_present(html_content):
    """INV-R-005d: PR badges (#60, #61, #62) must appear in the domain panels."""
    for pr in ("#60", "#61", "#62"):
        assert pr in html_content, (
            f"INV-R-005d FAILED: PR badge '{pr}' not found in PERCEIVABLE_INFINITY.html."
        )


# ── INV-R-006: INELASTICITY_VISUALIZATION_PRESENT ────────────────────────────

def test_inelasticity_visualization_present(html_content):
    """INV-R-006: Skate 4 microtransaction structural nullification must be shown."""
    assert "Structural Nullification" in html_content or "nullified" in html_content.lower(), (
        "INV-R-006 FAILED: Inelasticity/Structural Nullification section not found. "
        "The Skate 4 panel must explicitly display nullified corporate contingencies."
    )


def test_microtransaction_nullification_shown(html_content):
    """INV-R-006b: Microtransaction nullification must be explicitly shown as void."""
    assert "cosmetic_microtransactions" in html_content or "microtransaction" in html_content.lower(), (
        "INV-R-006b FAILED: Microtransaction nullification not shown in PERCEIVABLE_INFINITY.html. "
        "Skate 4's structural impossibility of microtransactions must be visible."
    )
    assert "impossible" in html_content.lower() or "VOID" in html_content, (
        "INV-R-006b FAILED: The 'impossible' or 'VOID' marker for microtransactions not found."
    )


# ── INV-R-007: MERKLE_PLACEHOLDER_PRESENT ────────────────────────────────────

def test_merkle_placeholder_present(html_content):
    """INV-R-007: Merkle root placeholder sections must be present for each universe."""
    assert "Merkle Root" in html_content, (
        "INV-R-007 FAILED: Merkle Root placeholder not found in PERCEIVABLE_INFINITY.html. "
        "Each universe domain panel must include a Merkle root verification placeholder."
    )
    assert "merkle-block" in html_content, (
        "INV-R-007 FAILED: CSS class 'merkle-block' not found in PERCEIVABLE_INFINITY.html."
    )


# ── INV-R-008: ARIA_ROLES_PRESENT ─────────────────────────────────────────────

def test_aria_roles_present(html_content):
    """INV-R-008: ARIA roles must be present for WCAG 2.1 AA compliance."""
    assert 'role="banner"' in html_content, (
        "INV-R-008 FAILED: ARIA role='banner' not found on header element."
    )
    assert 'role="main"' in html_content or 'role="dialog"' in html_content, (
        "INV-R-008 FAILED: No main or dialog ARIA roles found."
    )
    assert 'aria-label' in html_content, (
        "INV-R-008 FAILED: No aria-label attributes found in PERCEIVABLE_INFINITY.html."
    )


def test_aria_live_present(html_content):
    """INV-R-008b: aria-live region must exist for dynamic content updates."""
    assert 'aria-live' in html_content, (
        "INV-R-008b FAILED: No aria-live attribute found. "
        "Dynamic zoom-level info must announce changes to screen readers."
    )


# ── INV-R-009: LOD_SECTION_PRESENT ───────────────────────────────────────────

def test_lod_section_present(html_content):
    """INV-R-009: Fractal LOD rendering section must be present."""
    assert "lod-section" in html_content or "Fractal" in html_content, (
        "INV-R-009 FAILED: LOD/Fractal rendering section not found in PERCEIVABLE_INFINITY.html."
    )
    assert "Seed-driven" in html_content or "seed" in html_content.lower(), (
        "INV-R-009 FAILED: Seed-driven rendering description not found."
    )


# ── INV-S-001: SEED_FILES_PRESENT ────────────────────────────────────────────

@pytest.mark.parametrize("seed_path,label", [
    (SEED_FOOD_CART, "Food Cart"),
    (SEED_UNCHARTED, "Uncharted"),
    (SEED_SKATE4, "Skate 4"),
])
def test_seed_files_present(seed_path, label):
    """INV-S-001: All three universe seed YAML files must exist."""
    assert seed_path.exists(), (
        f"INV-S-001 FAILED: Seed file for '{label}' not found at {seed_path}. "
        "All three universe seeds (PRs #60, #61, #62) must be present."
    )


# ── INV-S-002: SKATE4_CORPORATE_CONTINGENCIES_IMPOSSIBLE ─────────────────────

def test_skate4_corporate_contingencies_impossible(skate4_seed):
    """INV-S-002: Skate 4 seed must declare corporate contingencies as impossible."""
    universe = skate4_seed.get("universe", {})
    corp = universe.get("corporate_contingencies", {})
    assert corp, (
        "INV-S-002 FAILED: No corporate_contingencies defined in skate4_multiplayer_universe.yaml."
    )
    for key, value in corp.items():
        assert value == "impossible", (
            f"INV-S-002 FAILED: '{key}' is not marked 'impossible' in Skate 4 seed "
            f"(got: '{value}'). All corporate contingencies must be structurally impossible."
        )


# ── INV-S-003: UNIVERSE_EXPANSION_LEVELS_DEFINED ─────────────────────────────

@pytest.mark.parametrize("seed_fixture_name,label,min_levels", [
    ("food_cart_seed", "Food Cart", 2),
    ("uncharted_seed", "Uncharted", 3),
    ("skate4_seed", "Skate 4", 4),
])
def test_universe_expansion_levels_defined(request, seed_fixture_name, label, min_levels):
    """INV-S-003: Each universe seed must define at least N expansion levels."""
    seed = request.getfixturevalue(seed_fixture_name)
    universe = seed.get("universe", {})
    levels = universe.get("expansion", {}).get("levels", [])
    assert len(levels) >= min_levels, (
        f"INV-S-003 FAILED: {label} universe has {len(levels)} expansion levels; "
        f"expected at least {min_levels}. "
        "Fractal hierarchy ('Kinds') must be fully defined in the seed."
    )


# ── INV-S-004: UNIVERSE_DETERMINISTIC_FLAG ────────────────────────────────────

@pytest.mark.parametrize("seed_fixture_name,label", [
    ("food_cart_seed", "Food Cart"),
    ("uncharted_seed", "Uncharted"),
    ("skate4_seed", "Skate 4"),
])
def test_universe_deterministic_flag(request, seed_fixture_name, label):
    """INV-S-004: Each universe seed must set deterministic: true."""
    seed = request.getfixturevalue(seed_fixture_name)
    universe = seed.get("universe", {})
    deterministic = universe.get("expansion", {}).get("deterministic", False)
    assert deterministic is True, (
        f"INV-S-004 FAILED: {label} universe expansion is not marked deterministic=true. "
        "Seed-driven determinism is required for the Sabbath-Complete Schema."
    )
