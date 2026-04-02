#!/usr/bin/env python3
"""Tests for PR #84 cross-model benchmark registrations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.ai_invariant_tests import run_ai_invariant_suite
from scripts.benchmark_pipeline import run_pipeline


def test_cross_model_suite():
    suite = run_ai_invariant_suite()
    cross_entries = [entry for entry in suite["results"] if entry["id"].startswith("AI_CROSS_")]
    assert len(cross_entries) == 10
    assert all(entry["domain"] == "D_CROSS_MODEL_BENCHMARKS" for entry in cross_entries)
    assert all(entry["model_targeting"] for entry in cross_entries)

    pipeline = run_pipeline()
    assert pipeline["pipeline"] == "IA-CYPHER-0005"
    assert pipeline["pr"] == 84
    assert len(pipeline["bug_fixes"]) == 7
    for entry in cross_entries:
        assert entry["id"] in pipeline["model_targeting"]


def main():
    test_cross_model_suite()
    print("PASS test_cross_model_suite")


if __name__ == "__main__":
    main()
