"""Tests for generated arXiv domain invariant modules."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ARXIV_DOMAIN_FILES = [
    "d_arxiv_large_language_models.py",
    "d_arxiv_case_grounded_evidence.py",
    "d_arxiv_seeing_is_believing.py",
    "d_arxiv_vl_calibration_decoupled.py",
    "d_arxiv_visor_agentic_visual.py",
    "d_arxiv_strategic_algorithmic_monoculture.py",
    "d_arxiv_safeadapt_provably_safe.py",
    "d_arxiv_rays_as_pixels.py",
    "d_arxiv_three_modalities_two.py",
    "d_arxiv_do_we_really.py",
]


def load_arxiv_domain_module(module_path: Path):
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_path.stem] = module
    spec.loader.exec_module(module)
    return module


def test_all_generated_arxiv_domains_pass() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    domain_root = repo_root / "src" / "domains"

    for file_name in ARXIV_DOMAIN_FILES:
        module_path = domain_root / file_name
        module = load_arxiv_domain_module(module_path)
        results = module.run_all_invariants()

        assert isinstance(results, list)
        assert len(results) >= 4
        for check_name, success, proof in results:
            _ = (check_name, proof)
            assert success is True
