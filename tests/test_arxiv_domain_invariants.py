"""Tests for generated arXiv domain invariant modules."""

from __future__ import annotations

import importlib


ARXIV_DOMAIN_PACKAGES = [
    "d_arxiv_large_language_models",
    "d_arxiv_case_grounded_evidence",
    "d_arxiv_seeing_is_believing",
    "d_arxiv_vl_calibration_decoupled",
    "d_arxiv_visor_agentic_visual",
    "d_arxiv_strategic_algorithmic_monoculture",
    "d_arxiv_safeadapt_provably_safe",
    "d_arxiv_rays_as_pixels",
    "d_arxiv_three_modalities_two",
    "d_arxiv_do_we_really",
]


def test_all_generated_arxiv_domains_pass() -> None:
    for package_name in ARXIV_DOMAIN_PACKAGES:
        module = importlib.import_module(f"src.domains.{package_name}.invariants")
        results = module.run_all_invariants()

        assert isinstance(results, list)
        assert len(results) >= 4
        for check_name, success, proof in results:
            _ = (check_name, proof)
            assert success is True
