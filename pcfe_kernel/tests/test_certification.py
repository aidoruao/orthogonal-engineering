"""
pcfe_kernel/tests/test_certification.py

Tests for CertificationSimulator and ExamResult.
"""

import pytest

from pcfe_kernel.certification import CertificationSimulator, ExamResult
from pcfe_kernel.departments import D_FDACS, D_TRAIN, build_default_registry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_simulator() -> CertificationSimulator:
    """Return a CertificationSimulator with the default registry."""
    from pcfe_kernel.certification import _load_falsification_ids
    return CertificationSimulator(
        regulatory_dept=D_FDACS,
        training_dept=D_TRAIN,
        falsification_engine=_load_falsification_ids(),
        registry=build_default_registry(),
    )


# ---------------------------------------------------------------------------
# Scenario generation
# ---------------------------------------------------------------------------

class TestScenarioGeneration:
    def test_generate_scenario_returns_ortho_state(self):
        from minimal_ai_ide.ortho_kernel import OrthoState
        sim = _make_simulator()
        state = sim.generate_scenario()
        assert isinstance(state, OrthoState)

    def test_generate_scenario_manifest_non_empty(self):
        sim = _make_simulator()
        state = sim.generate_scenario()
        assert len(state.manifest) > 0

    def test_generate_scenario_deterministic(self):
        sim = _make_simulator()
        s1 = sim.generate_scenario()
        s2 = sim.generate_scenario()
        # Same simulator → same manifest (order may vary, content must match)
        assert set(s1.manifest) == set(s2.manifest)

    def test_generate_scenario_logos_id_set(self):
        sim = _make_simulator()
        state = sim.generate_scenario()
        assert state.logos_id.startswith("PCFE_SCENARIO")

    def test_generate_scenario_contains_d_train_entities(self):
        sim = _make_simulator()
        state = sim.generate_scenario()
        # At least one D_train entity should appear in manifest
        train_entities = set(D_TRAIN.manifest_entries())
        assert train_entities & set(state.manifest)


# ---------------------------------------------------------------------------
# Exam evaluation — valid actions
# ---------------------------------------------------------------------------

class TestExamEvaluationValid:
    def test_evaluate_returns_exam_result(self):
        sim = _make_simulator()
        result = sim.evaluate(["inspect:premises"], candidate_id="test_candidate")
        assert isinstance(result, ExamResult)

    def test_exam_result_has_transcript_hash(self):
        sim = _make_simulator()
        result = sim.evaluate(["inspect:premises"])
        assert len(result.transcript_hash) == 64  # SHA-256 hex

    def test_exam_result_candidate_id_preserved(self):
        sim = _make_simulator()
        result = sim.evaluate([], candidate_id="alice")
        assert result.candidate_id == "alice"

    def test_exam_result_score_in_range(self):
        sim = _make_simulator()
        result = sim.evaluate(["inspect:premises"])
        assert 0.0 <= result.score <= 1.0

    def test_exam_result_gates_dict_non_empty(self):
        sim = _make_simulator()
        result = sim.evaluate(["inspect:premises"])
        assert isinstance(result.gates, dict)
        assert len(result.gates) > 0

    def test_transcript_hash_deterministic(self):
        sim = _make_simulator()
        r1 = sim.evaluate(["inspect:premises"], candidate_id="bob")
        r2 = sim.evaluate(["inspect:premises"], candidate_id="bob")
        assert r1.transcript_hash == r2.transcript_hash

    def test_different_actions_produce_different_hashes(self):
        sim = _make_simulator()
        r1 = sim.evaluate(["inspect:premises"], candidate_id="bob")
        r2 = sim.evaluate(["assess:damage"], candidate_id="bob")
        assert r1.transcript_hash != r2.transcript_hash


# ---------------------------------------------------------------------------
# Exam evaluation — prohibited actions fail
# ---------------------------------------------------------------------------

class TestExamEvaluationProhibited:
    def test_prohibited_action_gate_fails(self):
        sim = _make_simulator()
        result = sim.evaluate(["apply:unregistered_pesticide"])
        gate_key = "action_allowed:apply:unregistered_pesticide"
        assert gate_key in result.gates
        assert result.gates[gate_key] is False

    def test_prohibited_action_causes_overall_fail(self):
        sim = _make_simulator()
        result = sim.evaluate(["apply:banned_organochlorine"])
        assert result.passed is False

    def test_mix_of_valid_and_prohibited_actions_fails(self):
        sim = _make_simulator()
        result = sim.evaluate(["inspect:premises", "apply:cancelled_registration"])
        assert result.passed is False


# ---------------------------------------------------------------------------
# Falsification engine
# ---------------------------------------------------------------------------

class TestFalsificationEngine:
    def test_falsification_engine_loaded(self):
        from pcfe_kernel.certification import _load_falsification_ids
        ids = _load_falsification_ids()
        assert isinstance(ids, list)

    def test_known_falsification_id_present(self):
        from pcfe_kernel.certification import _load_falsification_ids
        ids = _load_falsification_ids()
        # F_PLATFORM_001 is guaranteed to exist in ontology/falsification_tests.json
        assert "F_PLATFORM_001" in ids
