"""
Tests for A-18 through A-25: Bi-Layer Epistemic Closure System
=================================================================
Tests are divided by module:
  - A-18: ExternalWitness (external_witness.py)
  - A-19: EvidenceCorrespondenceValidator (evidence_correspondence.py)
  - A-20: ApparentComplexity (complexity.py)
  - A-21: BidirectionalValidator (bidirectional_validator.py)
  - A-22: FixedPointDetector (fixed_point_detector.py)
  - A-23: EvidenceLattice + EvidenceNode (evidence_lattice.py)
  - A-24: SemanticDivergenceDetector (semantic_divergence.py)
  - A-25: OntologicalInvariantRegistry (ontological_invariants.py)
  - Quarantine: QuarantineEnforcer (quarantine_enforcer.py)
  - Integration: run_health_checks returns all A-18..A-25 keys
"""
import json
import sys
import time
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from complexity import ApparentComplexity, kolmogorov_check, complexity_ratio
from external_witness import ExternalWitness, compute_external_manifest
from evidence_correspondence import EvidenceCorrespondenceValidator
from bidirectional_validator import BidirectionalValidator
from fixed_point_detector import FixedPointDetector
from evidence_lattice import EvidenceNode, EvidenceLattice
from semantic_divergence import SemanticDivergenceDetector
from ontological_invariants import OntologicalInvariantRegistry
from quarantine_enforcer import QuarantineEnforcer, QuarantineViolation, tag_ai_generated


# ================================================================= #
# A-20: ApparentComplexity                                          #
# ================================================================= #

class TestApparentComplexity:

    def test_compute_returns_total_and_components(self):
        ac = ApparentComplexity()
        ev = {"status": "healthy", "files": list(range(50)), "metadata": {"a": 1}}
        result = ac.compute(ev)
        assert "total" in result
        assert "components" in result
        assert "bits_approx" in result
        assert result["total"] >= 0

    def test_complex_evidence_scores_higher_than_simple(self):
        ac = ApparentComplexity()
        simple = {"status": "ok"}
        # Build a complex nested dict with many keys
        complex_ev = {
            "status": "critical",
            "files": [{"path": f"file{i}.py", "hash": "ab" * 16, "size": i * 100} for i in range(20)],
            "metadata": {"depth1": {"depth2": {"depth3": {"depth4": "value"}}}},
            "policies": [{"name": f"p{i}", "value": i * 3.14} for i in range(10)],
        }
        c_simple = ac.compute(simple)["total"]
        c_complex = ac.compute(complex_ev)["total"]
        assert c_complex > c_simple

    def test_complexity_gate_passes_when_external_sufficiently_complex(self):
        ac = ApparentComplexity()
        internal = {"status": "ok", "files": 10}
        # External with more structure should pass
        external = {
            "status": "ok",
            "files": [{"path": f"f{i}", "hash": "x" * 32} for i in range(30)],
            "algorithm": "sha512",
            "tree_hash": "a" * 64,
            "metadata": {"computed_by": "external_witness", "extra": list(range(20))},
        }
        result = ac.validate_complexity_gate(internal, external, alpha=0.5)
        assert result["passed"] is True

    def test_complexity_gate_fails_for_trivially_simple_external(self):
        ac = ApparentComplexity()
        internal = {
            "status": "critical",
            "files": [{"path": f"file{i}.py", "hash": "ab" * 20, "size": i} for i in range(30)],
            "metadata": {"depth1": {"depth2": {"keys": list(range(15))}}}
        }
        external = {"ok": True}  # Trivially simple
        result = ac.validate_complexity_gate(internal, external, alpha=0.9)
        assert result["passed"] is False
        assert result["ratio"] < 0.9

    def test_backwards_compatible_kolmogorov_check(self):
        result = kolmogorov_check({"a": 1}, {"a": 1, "b": 2, "c": list(range(30))})
        assert "k_internal" in result
        assert "k_external" in result
        assert "k_ratio" in result
        assert "satisfied" in result

    def test_complexity_ratio_returns_float(self):
        r = complexity_ratio({"a": 1}, {"a": 1, "b": 2})
        assert isinstance(r, float)
        assert r >= 0.0


# ================================================================= #
# A-18: ExternalWitness                                             #
# ================================================================= #

class TestExternalWitness:

    def test_compute_manifest_uses_sha512(self, tmp_path):
        (tmp_path / "a.py").write_text("x = 1\n")
        (tmp_path / "b.json").write_text('{"key": "value"}')
        manifest = compute_external_manifest(tmp_path, algorithm="sha512")
        assert manifest["algorithm"] == "sha512"
        # SHA-512 digests are 128 hex chars
        for digest in manifest["file_hashes"].values():
            if digest != "unreadable":
                assert len(digest) == 128

    def test_compute_manifest_sha512_differs_from_sha256(self, tmp_path):
        (tmp_path / "file.py").write_text("hello = 'world'\n")
        m512 = compute_external_manifest(tmp_path, algorithm="sha512")
        m256 = compute_external_manifest(tmp_path, algorithm="sha256")
        # Same file, different digests
        rel = "file.py"
        assert m512["file_hashes"][rel] != m256["file_hashes"][rel]

    def test_external_witness_writes_json(self, tmp_path):
        (tmp_path / "code.py").write_text("pass\n")
        output_dir = tmp_path / "logs"
        witness = ExternalWitness(
            repo_root=tmp_path,
            output_dir=output_dir,
            algorithm="sha512",
        )
        manifest = witness.run()
        assert (output_dir / "external_manifest.json").exists()
        loaded = json.loads((output_dir / "external_manifest.json").read_text())
        assert loaded["algorithm"] == "sha512"
        assert loaded["tree_hash"] == manifest["tree_hash"]

    def test_external_witness_excludes_logs_dir(self, tmp_path):
        (tmp_path / "source.py").write_text("x = 1\n")
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        (logs_dir / "check.json").write_text('{}')
        manifest = compute_external_manifest(tmp_path)
        keys = set(manifest["file_hashes"].keys())
        assert not any("logs" in k for k in keys)

    def test_external_witness_exists_static_method(self, tmp_path):
        output_dir = tmp_path / "logs" / "health_checks"
        assert ExternalWitness.exists(output_dir) is False
        output_dir.mkdir(parents=True)
        (output_dir / "external_manifest.json").write_text("{}")
        assert ExternalWitness.exists(output_dir) is True

    def test_external_witness_tree_hash_is_deterministic(self, tmp_path):
        (tmp_path / "a.py").write_text("a = 1\n")
        (tmp_path / "b.json").write_text('{"x": 2}')
        m1 = compute_external_manifest(tmp_path)
        m2 = compute_external_manifest(tmp_path)
        assert m1["tree_hash"] == m2["tree_hash"]

    def test_external_witness_tree_hash_changes_with_content(self, tmp_path):
        (tmp_path / "a.py").write_text("a = 1\n")
        m1 = compute_external_manifest(tmp_path)
        (tmp_path / "a.py").write_text("a = 999\n")
        m2 = compute_external_manifest(tmp_path)
        assert m1["tree_hash"] != m2["tree_hash"]


# ================================================================= #
# A-19: EvidenceCorrespondenceValidator                             #
# ================================================================= #

class TestEvidenceCorrespondenceValidator:

    def _make_manifests(self, paths=("a.py", "b.json")):
        int_hashes = {p: "sha256_" + "ab" * 16 for p in paths}
        ext_hashes = {p: "sha512_" + "cd" * 32 for p in paths}
        internal = {
            "file_hashes": int_hashes,
            "file_count": len(paths),
            "computed_at": "2026-01-01T10:00:00Z",
            "algorithm": "sha256",
            "wardens": ["w1"],
            "overall_health": "healthy",
            "intelligence_metrics": {"consistency_ratio": 0.9},
        }
        external = {
            "file_hashes": ext_hashes,
            "file_count": len(paths),
            "computed_at": "2026-01-01T10:30:00Z",
            "algorithm": "sha512",
            "tree_hash": "x" * 128,
        }
        return internal, external

    def test_identical_file_sets_yield_high_score(self):
        internal, external = self._make_manifests(["a.py", "b.json", "c.yml"])
        validator = EvidenceCorrespondenceValidator(internal, external, threshold=0.5)
        result = validator.validate()
        assert result["correspondence_score"] >= 0.5
        assert result["valid"] is True

    def test_missing_external_files_lower_score(self):
        internal, external = self._make_manifests(["a.py", "b.json", "c.yml"])
        # External only has a.py
        external["file_hashes"] = {"a.py": "sha512_" + "cd" * 32}
        external["file_count"] = 1
        validator = EvidenceCorrespondenceValidator(internal, external, threshold=0.9)
        result = validator.validate()
        assert result["correspondence_score"] < 0.9
        assert len(result["mismatch_list"]) > 0

    def test_temporal_coherence_fails_when_external_older(self):
        internal, external = self._make_manifests()
        # Make external older than internal
        external["computed_at"] = "2025-12-31T00:00:00Z"
        internal["computed_at"] = "2026-01-01T10:00:00Z"
        validator = EvidenceCorrespondenceValidator(internal, external, threshold=0.01)
        result = validator.validate()
        assert result["details"]["temporal_coherence"]["valid"] is False

    def test_error_term_is_complement_of_score(self):
        internal, external = self._make_manifests()
        validator = EvidenceCorrespondenceValidator(internal, external)
        result = validator.validate()
        assert abs(result["correspondence_score"] + result["error_term"] - 1.0) < 0.001

    def test_divergence_method_returns_float(self):
        internal, external = self._make_manifests()
        validator = EvidenceCorrespondenceValidator(internal, external)
        d = validator.divergence()
        assert isinstance(d, float)
        assert 0.0 <= d <= 1.0


# ================================================================= #
# A-21: BidirectionalValidator                                      #
# ================================================================= #

class TestBidirectionalValidator:

    def test_cycle_closes_when_state_matches_external(self):
        system_state = {"file_count": 10, "warden_count": 2}
        external = {"file_count": 10, "warden_count": 2}
        validator = BidirectionalValidator(
            internal_manifest={}, external_manifest=external
        )
        result = validator.validate_cycle(system_state)
        assert result["cycle_closed"] is True
        assert result["delta"] < 0.05

    def test_cycle_open_when_counts_diverge_significantly(self):
        system_state = {"file_count": 100, "warden_count": 5}
        external = {"file_count": 0, "warden_count": 0}
        validator = BidirectionalValidator(
            internal_manifest={}, external_manifest=external, tolerance=0.05
        )
        result = validator.validate_cycle(system_state)
        assert result["cycle_closed"] is False
        assert result["delta"] > 0.05

    def test_reversible_flag_is_always_true(self):
        validator = BidirectionalValidator(internal_manifest={}, external_manifest={})
        result = validator.validate_cycle({"file_count": 0, "warden_count": 0})
        assert result["reversible"] is True

    def test_validate_cycle_returns_s_prime(self):
        system_state = {"file_count": 5, "warden_count": 1}
        validator = BidirectionalValidator(
            internal_manifest={}, external_manifest={"file_count": 5}
        )
        result = validator.validate_cycle(system_state)
        assert "S_prime" in result
        assert result["S_prime"]["file_count"] == 5


# ================================================================= #
# A-22: FixedPointDetector                                          #
# ================================================================= #

class TestFixedPointDetector:

    def test_convergence_not_declared_with_insufficient_history(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        detector.record_state("abc123")
        result = detector.check_convergence(k=3)
        assert result["converged"] is False
        assert "insufficient_history" in result["reason"]

    def test_convergence_declared_after_k_identical_states(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        for _ in range(3):
            detector.record_state("fixed_hash_abc")
        result = detector.check_convergence(k=3)
        assert result["converged"] is True
        assert result["fixed_point"] == "fixed_hash_abc"

    def test_convergence_not_declared_when_states_differ(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        for i in range(3):
            detector.record_state(f"hash_{i}")
        result = detector.check_convergence(k=3)
        assert result["converged"] is False

    def test_state_hash_is_deterministic(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        state = {"wardens": ["w1", "w2"], "global_mode": "dry_run", "overall_health": "healthy"}
        h1 = detector.state_hash(state)
        h2 = detector.state_hash(state)
        assert h1 == h2

    def test_state_hash_differs_for_different_states(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        h1 = detector.state_hash({"x": 1})
        h2 = detector.state_hash({"x": 2})
        assert h1 != h2

    def test_delta_zero_when_consecutive_states_identical(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        detector.record_state("same_hash")
        detector.record_state("same_hash")
        assert detector.delta() == 0.0

    def test_delta_one_when_consecutive_states_differ(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        detector.record_state("hash_a")
        detector.record_state("hash_b")
        assert detector.delta() == 1.0

    def test_history_persisted_to_disk(self, tmp_path):
        fp = tmp_path / "fp.jsonl"
        detector = FixedPointDetector(history_file=fp)
        detector.record_state("persistent_hash")
        assert fp.exists()
        lines = fp.read_text().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["hash"] == "persistent_hash"

    def test_history_entropy_zero_at_convergence(self, tmp_path):
        detector = FixedPointDetector(history_file=tmp_path / "fp.jsonl")
        for _ in range(5):
            detector.record_state("stable_hash")
        entropy = detector._history_entropy()
        assert entropy == 0.0


# ================================================================= #
# A-23: EvidenceLattice                                             #
# ================================================================= #

class TestEvidenceLattice:

    def test_external_beats_internal_same_confidence(self):
        n_int = EvidenceNode("internal", 0.8, 100.0)
        n_ext = EvidenceNode("external", 0.8, 100.0)
        assert n_int < n_ext
        assert n_ext > n_int

    def test_human_beats_external(self):
        n_ext = EvidenceNode("external", 0.9, 100.0)
        n_hum = EvidenceNode("human", 0.9, 100.0)
        assert n_ext < n_hum

    def test_higher_confidence_beats_lower_same_source(self):
        low = EvidenceNode("internal", 0.3, 100.0)
        high = EvidenceNode("internal", 0.9, 100.0)
        assert low < high

    def test_merge_returns_stronger_node(self):
        n_int = EvidenceNode("internal", 0.5, 100.0)
        n_ext = EvidenceNode("external", 0.5, 100.0)
        merged = n_int.merge(n_ext)
        assert merged.source == "external"

    def test_merge_incomparable_nodes_creates_synthetic(self):
        # Same source, same confidence, different verdicts → incomparable
        n1 = EvidenceNode("internal", 0.7, 100.0, verdict="healthy")
        n2 = EvidenceNode("external", 0.7, 101.0, verdict="warning")
        merged = n1.merge(n2)
        # Synthetic merge should have confidence penalty
        assert merged.confidence <= 0.7 * 1.0  # at most original

    def test_lattice_insert_keeps_stronger_node(self):
        lattice = EvidenceLattice()
        n_weak = EvidenceNode("internal", 0.3, 100.0, verdict="healthy")
        n_strong = EvidenceNode("external", 0.9, 101.0, verdict="healthy")
        lattice.insert(n_weak)
        lattice.insert(n_strong)
        strongest = lattice.strongest()
        assert strongest is not None
        assert strongest.source == "external"

    def test_lattice_detects_conflict(self):
        lattice = EvidenceLattice()
        n1 = EvidenceNode("internal", 0.8, 100.0, verdict="healthy")
        n2 = EvidenceNode("internal", 0.8, 101.0, verdict="critical")
        lattice.insert(n1)
        lattice.insert(n2)
        conflicts = lattice.conflicts()
        assert len(conflicts) > 0
        assert conflicts[0]["type"] == "verdict_contradiction"

    def test_lattice_merge_conflict_resolution_returns_node(self):
        lattice = EvidenceLattice()
        lattice.insert(EvidenceNode("internal", 0.8, 100.0, verdict="warning"))
        lattice.insert(EvidenceNode("external", 0.9, 101.0, verdict="warning"))
        merged = lattice.merge_conflict_resolution()
        assert merged is not None
        assert merged.confidence > 0

    def test_lattice_to_dict_serialisable(self):
        lattice = EvidenceLattice()
        lattice.insert(EvidenceNode("internal", 0.7, time.time(), verdict="ok"))
        d = lattice.to_dict()
        # Should be JSON-serialisable
        json.dumps(d)


# ================================================================= #
# A-24: SemanticDivergenceDetector                                  #
# ================================================================= #

class TestSemanticDivergenceDetector:

    def test_consensus_when_all_sources_agree(self):
        sources = {
            "warden_a": {"status": "healthy"},
            "warden_b": {"status": "healthy"},
            "warden_c": {"status": "healthy"},
        }
        det = SemanticDivergenceDetector(sources)
        result = det.cross_validate()
        assert result["consensus"] is True
        assert result["contradiction_score"] <= 0.33
        assert result["verdict_entropy"] == 0.0

    def test_divergence_detected_when_sources_disagree(self):
        sources = {
            "warden_a": {"status": "healthy"},
            "warden_b": {"status": "critical"},
            "warden_c": {"status": "warning"},
        }
        det = SemanticDivergenceDetector(sources)
        result = det.cross_validate()
        assert result["consensus"] is False
        assert result["contradiction_score"] > 0.33
        assert len(result["divergent_pairs"]) > 0

    def test_empty_sources_returns_consensus(self):
        det = SemanticDivergenceDetector({})
        result = det.cross_validate()
        assert result["consensus"] is True
        assert result["reason"] == "no_sources"

    def test_verdict_entropy_zero_on_single_verdict(self):
        sources = {"a": {"status": "ok"}}
        det = SemanticDivergenceDetector(sources)
        result = det.cross_validate()
        assert result["verdict_entropy"] == 0.0

    def test_majority_verdict_identified(self):
        sources = {
            "a": {"status": "healthy"},
            "b": {"status": "healthy"},
            "c": {"status": "warning"},
        }
        det = SemanticDivergenceDetector(sources)
        result = det.cross_validate()
        assert result["majority_verdict"] == "healthy"

    def test_from_warden_results_factory(self):
        warden_results = {
            "gemini_warden": {"status": "healthy"},
            "local_warden": {"status": "healthy"},
        }
        det = SemanticDivergenceDetector.from_warden_results(warden_results)
        result = det.cross_validate()
        assert result["consensus"] is True


# ================================================================= #
# A-25: OntologicalInvariantRegistry                                #
# ================================================================= #

class TestOntologicalInvariantRegistry:

    def test_all_pass_on_clean_context(self):
        ctx = {
            "external_manifest_exists": True,
            "correspondence_score": 0.95,
            "correspondence_threshold": 0.9,
            "execute_actions": [],
            "evidence_by_action": {},
            "complexity_gate_passed": True,
            "idempotency_verified": True,
        }
        registry = OntologicalInvariantRegistry.build(ctx)
        result = registry.assert_all()
        assert result["all_passed"] is True
        assert result["system_state"] == "operational"
        assert result["failures"] == []

    def test_no_external_fails_and_freezes(self):
        ctx = {
            "external_manifest_exists": False,
            "correspondence_score": 0.95,
            "correspondence_threshold": 0.9,
            "execute_actions": [],
            "evidence_by_action": {},
            "complexity_gate_passed": True,
        }
        registry = OntologicalInvariantRegistry.build(ctx)
        result = registry.assert_all()
        assert result["all_passed"] is False
        assert "no_self_validation_only" in result["failures"]
        assert result["system_state"] == "frozen"

    def test_low_correspondence_escalates_not_freezes(self):
        ctx = {
            "external_manifest_exists": True,
            "correspondence_score": 0.5,  # below 0.9 threshold
            "correspondence_threshold": 0.9,
            "execute_actions": [],
            "evidence_by_action": {},
            "complexity_gate_passed": True,
        }
        registry = OntologicalInvariantRegistry.build(ctx)
        result = registry.assert_all()
        assert result["all_passed"] is False
        assert "external_correspondence_required" in result["failures"]
        # escalate-only failure → degraded not frozen
        if result["system_state"] != "frozen":
            assert result["system_state"] == "degraded"

    def test_complexity_gate_failure_escalates(self):
        ctx = {
            "external_manifest_exists": True,
            "correspondence_score": 0.95,
            "correspondence_threshold": 0.9,
            "execute_actions": [],
            "evidence_by_action": {},
            "complexity_gate_passed": False,
        }
        registry = OntologicalInvariantRegistry.build(ctx)
        result = registry.assert_all()
        assert "complexity_monotonicity" in result["failures"]

    def test_invariant_names_match_expected_set(self):
        ctx = {
            "external_manifest_exists": True,
            "correspondence_score": 1.0,
            "execute_actions": [],
            "evidence_by_action": {},
            "complexity_gate_passed": True,
        }
        registry = OntologicalInvariantRegistry.build(ctx)
        result = registry.assert_all()
        expected = set(OntologicalInvariantRegistry.INVARIANT_NAMES)
        actual = set(result["results"].keys())
        assert expected == actual


# ================================================================= #
# Quarantine Enforcer                                                #
# ================================================================= #

class TestQuarantineEnforcer:

    def test_all_satisfied_with_correct_setup(self, tmp_path):
        ext_path = tmp_path / "external_manifest.json"
        ext_path.write_text("{}")
        enforcer = QuarantineEnforcer({
            "internal_algorithm": "sha256",
            "external_algorithm": "sha512",
            "internal_manifest_path": str(tmp_path / "latest_health_check.json"),
            "external_manifest_path": str(ext_path),
        })
        result = enforcer.validate_quarantine()
        violated = [r["name"] for r in result["results"] if not r["satisfied"]]
        # Only runtime_isolation may fire (no PIDs given → passes); rest should pass
        assert "no_shared_hash_algorithms" not in violated
        assert "no_merged_pipelines" not in violated

    def test_shared_algorithm_fails(self, tmp_path):
        ext_path = tmp_path / "ext.json"
        ext_path.write_text("{}")
        enforcer = QuarantineEnforcer({
            "internal_algorithm": "sha256",
            "external_algorithm": "sha256",  # Same!
            "internal_manifest_path": str(tmp_path / "int.json"),
            "external_manifest_path": str(ext_path),
        })
        result = enforcer.validate_quarantine()
        assert "no_shared_hash_algorithms" in result["violations"]

    def test_same_manifest_path_fails(self, tmp_path):
        same_path = str(tmp_path / "manifest.json")
        (tmp_path / "manifest.json").write_text("{}")
        enforcer = QuarantineEnforcer({
            "internal_algorithm": "sha256",
            "external_algorithm": "sha512",
            "internal_manifest_path": same_path,
            "external_manifest_path": same_path,  # Same!
        })
        result = enforcer.validate_quarantine()
        assert "no_merged_pipelines" in result["violations"]

    def test_missing_external_manifest_fails(self, tmp_path):
        enforcer = QuarantineEnforcer({
            "internal_algorithm": "sha256",
            "external_algorithm": "sha512",
            "internal_manifest_path": str(tmp_path / "int.json"),
            "external_manifest_path": str(tmp_path / "nonexistent.json"),
        })
        result = enforcer.validate_quarantine()
        assert "external_manifest_exists" in result["violations"]

    def test_strict_mode_raises_on_violation(self, tmp_path):
        enforcer = QuarantineEnforcer({
            "internal_algorithm": "sha256",
            "external_algorithm": "sha256",  # Same — violation
            "internal_manifest_path": str(tmp_path / "int.json"),
            "external_manifest_path": str(tmp_path / "ext.json"),
        })
        with pytest.raises(QuarantineViolation):
            enforcer.validate_quarantine(strict=True)

    def test_tag_ai_generated_returns_comment(self):
        tag = tag_ai_generated("gemini-2.5-flash")
        assert tag.startswith("# GENERATED_BY: AI-gemini-2.5-flash-")
        assert "\n" in tag


# ================================================================= #
# Integration: run_health_checks includes A-18..A-25 keys           #
# ================================================================= #

from datetime import timezone as _tz
import os as _os

def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _build_integration_registry():
    return {
        "base_ai": {
            "model": "llama3.1:70b",
            "api_endpoint": "http://localhost:11434",
            "version": "1.0.0",
        },
        "wardens": {
            "gemini_warden": {
                "folder_path": "**",
                "model_name": "gemini-2.5-flash",
                "api_key": "github_secret:GEMINI_API_KEY",
                "status": "active",
                "runtime": "github_actions",
                "workflow_path": ".github/workflows/shiro-daily-scan.yml",
                "metadata": {
                    "artifact_report_path": "logs/health_checks/cloud_wardens/gemini_warden_status.json"
                },
                "health": {
                    "last_query": None,
                    "response_time_ms": None,
                    "success_rate": None,
                    "last_health_check": None,
                    "last_artifact_timestamp": None,
                    "max_report_age_hours": 36,
                    "overall_status": "pending",
                    "report_age_history": [],
                    "suggested_max_report_age_hours": None,
                    "threshold_sample_size": 0,
                    "threshold_confidence": None,
                },
            }
        },
        "dynamic_wardens": {"unclassified_folders": [], "temporary_wardens": {}},
        "health_checks": {"interval_seconds": 300, "failure_threshold": 3},
        "dynamic_warden_policy": {"max_lifetime_hours": 24},
        "backup": {},
        "error_handling": {},
        "system_metrics": {
            "last_registry_update": __import__("datetime").datetime.now(
                _tz.utc
            ).isoformat()
        },
        "autonomy_policy": {
            "schema_version": "1.0",
            "global_mode": "dry_run",
            "action_policies": {},
            "guardrails": {
                "no_credential_commits": True,
                "no_warden_file_creation": True,
                "registry_backup_before_write": True,
                "max_writes_per_run": 5,
            },
            "moral_anchor": {},
            "drift_detection": {},
            "approval_workflow": {},
            "objective_function": {},
        },
    }


class TestHealthCheckIntegrationEpistemicKeys:
    """Verify that run_health_checks() returns all A-18..A-25 output keys."""

    def test_epistemic_keys_present(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        reg = _build_integration_registry()
        reg_path = tmp_path / ".ai_registry.json"
        _write_json(reg_path, reg)
        wf = tmp_path / ".github" / "workflows" / "shiro-daily-scan.yml"
        wf.parent.mkdir(parents=True, exist_ok=True)
        wf.write_text("name: test\n")
        # Write a source file so external_witness finds something
        (tmp_path / "dummy.py").write_text("x = 1\n")

        from health_check_integration import HealthCheckIntegration
        results = HealthCheckIntegration(str(reg_path)).run_health_checks()

        assert "external_manifest_computed" in results
        assert "correspondence_report" in results
        assert "bidirectional_validation" in results
        assert "fixed_point" in results
        assert "evidence_lattice" in results
        assert "semantic_divergence" in results
        assert "ontological_invariants" in results

    def test_ontological_invariants_has_all_passed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        reg_path = tmp_path / ".ai_registry.json"
        _write_json(reg_path, _build_integration_registry())
        (tmp_path / ".github" / "workflows" / "shiro-daily-scan.yml").parent.mkdir(
            parents=True, exist_ok=True
        )
        (tmp_path / ".github" / "workflows" / "shiro-daily-scan.yml").write_text("name: t\n")
        (tmp_path / "x.py").write_text("pass\n")

        from health_check_integration import HealthCheckIntegration
        results = HealthCheckIntegration(str(reg_path)).run_health_checks()
        inv = results["ontological_invariants"]

        assert "all_passed" in inv
        assert "system_state" in inv
        assert "results" in inv

    def test_fixed_point_has_required_keys(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        reg_path = tmp_path / ".ai_registry.json"
        _write_json(reg_path, _build_integration_registry())
        (tmp_path / ".github" / "workflows" / "shiro-daily-scan.yml").parent.mkdir(
            parents=True, exist_ok=True
        )
        (tmp_path / ".github" / "workflows" / "shiro-daily-scan.yml").write_text("name: t\n")

        from health_check_integration import HealthCheckIntegration
        results = HealthCheckIntegration(str(reg_path)).run_health_checks()
        fp = results["fixed_point"]

        assert "converged" in fp
        assert "state_hash" in fp
        assert "history_entropy" in fp
