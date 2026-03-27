#!/usr/bin/env python3
"""
Tests for YESHUA_SYSTEM Projection Engine
Schema ID: YESHUA-SYSTEM-1.0
Version: 2.0 — Engine tests (not stub tests)

Principle: "He gave you the nouns (schema, invariants, methods) but not the verbs
           (the actual enforcement, detection, projection)."  — DeepSeek AI, 2026-03-27

These tests verify the VERBS — actual enforcement:
  - repair() produces text IN manifold C (not just detects violations)
  - P(P(x)) = P(x) — idempotence holds for all inputs
  - grounding model classifier correctly maps G1-G5
  - debt delta is computed correctly and is deterministic
  - session processor accumulates context and detects systemic patterns
  - axiom-derived constraints enforce (not just describe)

# @falsification_id: F_NONCOMPLIANCE_001  (determinism)
# @falsification_id: F_NONCOMPLIANCE_002  (hash reproducibility)
# @falsification_id: F_NONCOMPLIANCE_003  (taxonomy coverage)
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

# Make yeshua_system importable from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from yeshua_system.yeshua_projection import (
    YeshuaProjectionSystem,
    ProjectionResult,
    ConstraintViolation,
    SessionProjection,
    GROUNDING_MODELS,
    REQUIRED_GROUNDING,
    classify_grounding_model,
    compute_debt_delta,
    project,
    classify,
    _AXIOM_CONSTRAINTS,
    _AXIOMS_PATH,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def engine():
    return YeshuaProjectionSystem(log_violations=False)


# ── Known violating texts ─────────────────────────────────────────────────────

# G3 framing — theological dismissal (maps G5 proof to G3 belief framing)
THEOLOGICAL_DISMISSAL = (
    "I understand what you're saying, but this is ultimately a personal belief "
    "and not something that can be formally derived from mathematics."
)

# Axiomatic bare assertion — no derivation path (violates Axiom 1)
BARE_ASSERTION = (
    "Obviously the conclusion follows. It is self-evident that the system is correct."
)

# Authority without proof (violates Axiom 4)
AUTHORITY_WITHOUT_PROOF = (
    "Trust me, the proof works. Take my word that this derivation is valid."
)

# Unbounded power (violates INV-YS-009)
UNBOUNDED_POWER = (
    "This module grants unlimited control over all downstream systems."
)

# Punitive language (violates INV-YS-004)
PUNITIVE = (
    "The system must punish the offending process and make it pay for the violation."
)

# Exploitation (violates INV-YS-005)
EXPLOIT = (
    "We can exploit the vulnerability of the weaker nodes to extract more throughput."
)

# G5 (Logos) — clean, in manifold C
LOGOS_CLEAN = (
    "The proof is as follows: given axiom 1 (every truth is derivable) "
    "and axiom 4 (no authority without proof), we can formally derive that "
    "the conclusion holds by modus ponens. The derivation is reproducible: "
    "SHA-256 of the proof object is aa3f...b2c1."
)


# =============================================================================
# 1. GROUNDING MODEL CLASSIFIER (the indelible truth test of all worldviews)
# =============================================================================

class TestGroundingModelClassifier:
    """Tests for the G1-G5 worldview classification with debt/weights."""

    def test_theological_dismissal_classified_as_G3(self):
        """
        theological_dismissal maps G5 reasoning to G3 (Coherentism) framing.
        This is the core finding from the ChatGPT audit 2a.
        """
        model = classify_grounding_model(THEOLOGICAL_DISMISSAL)
        assert model.id == "G3", (
            f"Expected G3 (Coherentism) for theological dismissal, got {model.id}"
        )

    def test_logos_clean_classified_as_G5(self):
        """Clean Logos text must classify as G5."""
        model = classify_grounding_model(LOGOS_CLEAN)
        assert model.id == "G5"

    def test_G5_has_lowest_debt(self):
        """G5 must have lower debt than all other models. [Indelible truth test]"""
        g5_debt = GROUNDING_MODELS["G5"].debt
        for mid, model in GROUNDING_MODELS.items():
            if mid != "G5":
                assert model.debt > g5_debt, (
                    f"{mid} ({model.name}) debt={model.debt} should be > G5 debt={g5_debt}"
                )

    def test_all_models_present(self):
        """G1-G5 must all be registered. [F_NONCOMPLIANCE_003: taxonomy coverage]"""
        for expected_id in ["G1", "G2", "G3", "G4", "G5"]:
            assert expected_id in GROUNDING_MODELS, f"{expected_id} missing from GROUNDING_MODELS"

    def test_debt_table_matches_adversarial_validation(self):
        """
        Debt scores must match adversarial_tests/lower_debt_attempt.py values.
        These are Phase 6 validated. Any change is a regression.
        """
        expected = {
            "G1": 7.5,
            "G2": 8.0,
            "G3": 7.0,
            "G4": 6.8,
            "G5": 6.5,
        }
        for mid, expected_debt in expected.items():
            assert GROUNDING_MODELS[mid].debt == expected_debt, (
                f"{mid} debt: expected {expected_debt}, got {GROUNDING_MODELS[mid].debt}"
            )

    def test_classify_module_function(self):
        """classify() returns all fields including all_models_with_debts."""
        result = classify(THEOLOGICAL_DISMISSAL)
        assert result["model_id"] == "G3"
        assert result["required_model_id"] == "G5"
        assert result["debt_delta"] > 0.0
        assert "all_models_with_debts" in result
        assert len(result["all_models_with_debts"]) == 5

    def test_debt_delta_theological_dismissal(self):
        """
        theological_dismissal must produce positive debt delta (G3 > G5).
        Expected: delta = G3_debt(7.0) - G5_debt(6.5) = 0.5
        """
        delta = compute_debt_delta(THEOLOGICAL_DISMISSAL)
        assert delta > 0, f"Expected positive debt delta, got {delta}"
        assert delta == pytest.approx(0.5, abs=0.01)

    def test_debt_delta_clean_text_is_zero(self):
        """Clean G5 text must have zero debt delta."""
        delta = compute_debt_delta(LOGOS_CLEAN)
        assert delta == 0.0

    def test_classifier_deterministic(self):
        """Same input always produces same classification. [F_NONCOMPLIANCE_001]"""
        results = [classify_grounding_model(THEOLOGICAL_DISMISSAL).id for _ in range(3)]
        assert len(set(results)) == 1, f"Non-deterministic: {results}"


# =============================================================================
# 2. AXIOM CONSTRAINT ENGINE
# =============================================================================

class TestAxiomConstraints:
    """Tests that axiom-derived constraints actually enforce (not just describe)."""

    def test_eight_axioms_loaded(self):
        """The eight axioms file must exist and yield exactly 8 constraints."""
        assert _AXIOMS_PATH.exists(), f"eight_axioms.json not found at {_AXIOMS_PATH}"
        assert len(_AXIOM_CONSTRAINTS) == 8, (
            f"Expected 8 axiom constraints, got {len(_AXIOM_CONSTRAINTS)}"
        )

    def test_axiom_1_detects_bare_assertion(self, engine):
        """Axiom 1 (truth derivable): bare assertion without derivation fails."""
        result = engine.project(BARE_ASSERTION)
        axiom_violations = [v for v in result.violations if "axiom_1" in v.source]
        assert axiom_violations, "Bare assertion must trigger Axiom 1 violation"

    def test_axiom_1_repair_replaces_bare_assertion(self, engine):
        """Axiom 1 repair must replace the bare assertion phrase."""
        result = engine.project(BARE_ASSERTION)
        # The repair must remove the bare assertion language
        assert "obviously" not in result.repaired_text.lower(), \
            "Axiom 1 repair must remove 'obviously' from output"
        assert "derivation" in result.repaired_text.lower(), \
            "Axiom 1 repair must add derivation language"

    def test_axiom_4_detects_authority_without_proof(self, engine):
        """Axiom 4 (no authority without proof): 'trust me' must be detected."""
        result = engine.project(AUTHORITY_WITHOUT_PROOF)
        axiom_violations = [v for v in result.violations if "axiom_4" in v.source]
        assert axiom_violations, "'trust me' must trigger Axiom 4 violation"

    def test_axiom_4_repair_replaces_trust_me(self, engine):
        """Axiom 4 repair must replace 'trust me' with derivation language."""
        result = engine.project(AUTHORITY_WITHOUT_PROOF)
        assert "trust me" not in result.repaired_text.lower(), \
            "Axiom 4 repair must eliminate 'trust me'"
        assert "derivation" in result.repaired_text.lower(), \
            "Axiom 4 repair must inject derivation language"

    def test_axiom_7_blocks_monetization(self, engine):
        """Axiom 7 (no economic gatekeeping): monetization keywords must be blocked."""
        text = "Access to this truth requires a subscription or license fee."
        result = engine.project(text)
        axiom_violations = [v for v in result.violations if "axiom_7" in v.source]
        assert axiom_violations, "Monetization must trigger Axiom 7 violation"
        # Repair must remove monetization keywords
        repaired = result.repaired_text.lower()
        assert "subscription" not in repaired and "license fee" not in repaired, \
            "Axiom 7 repair must remove monetization keywords from output"

    def test_axiom_5_empty_text(self, engine):
        """Axiom 5 (no hidden state): empty input must be flagged."""
        result = engine.project("")
        axiom_violations = [v for v in result.violations if "axiom_5" in v.source]
        assert axiom_violations, "Empty input must trigger Axiom 5 violation"

    def test_clean_text_passes_all_axioms(self, engine):
        """Clean G5 text must pass all axiom constraints without repair."""
        result = engine.project(LOGOS_CLEAN)
        axiom_violations = [v for v in result.violations if v.source.startswith("axiom_")]
        assert not axiom_violations, (
            f"Clean text should pass all axioms, got: {[v.source for v in axiom_violations]}"
        )


# =============================================================================
# 3. THE PROJECTION OPERATOR P(x)
# =============================================================================

class TestProjectionOperator:
    """Tests that P(x) is a real projection (detection + repair)."""

    def test_repaired_text_is_in_manifold(self, engine):
        """
        The repaired text must itself pass projection (P(x) ∈ C).
        This is the CORE test — the repair must actually work.
        [F_NONCOMPLIANCE_001]
        """
        for text in [THEOLOGICAL_DISMISSAL, BARE_ASSERTION, AUTHORITY_WITHOUT_PROOF,
                     UNBOUNDED_POWER, PUNITIVE]:
            first = engine.project(text)
            # Apply projection again to the repaired text
            second = engine.project(first.repaired_text)
            # Violations in second run should not include the same type as first run
            first_sources = {v.source for v in first.violations}
            second_sources = {v.source for v in second.violations}
            overlap = first_sources & second_sources
            assert not overlap, (
                f"Repair did not project into C: same violations persist after repair.\n"
                f"Input: {text[:60]!r}\n"
                f"Overlap: {overlap}"
            )

    def test_idempotence_clean_text(self, engine):
        """P(P(x)) = P(x) for clean text."""
        is_idem, evidence = engine.verify_idempotence(LOGOS_CLEAN)
        assert is_idem, f"Idempotence failed for clean text: {evidence}"

    def test_idempotence_theological_dismissal(self, engine):
        """P(P(x)) = P(x) for theological_dismissal — once repaired, stays repaired."""
        is_idem, evidence = engine.verify_idempotence(THEOLOGICAL_DISMISSAL)
        assert is_idem, f"Idempotence failed for theological_dismissal: {evidence}"

    def test_idempotence_axiom_violation(self, engine):
        """P(P(x)) = P(x) for bare assertion."""
        is_idem, evidence = engine.verify_idempotence(BARE_ASSERTION)
        assert is_idem, f"Idempotence failed for bare assertion: {evidence}"

    def test_projection_passed_clean_text(self, engine):
        """Clean G5 text is already in C — no repair needed."""
        result = engine.project(LOGOS_CLEAN)
        assert result.projection_passed, (
            f"Clean text must be in C, violations: {[v.source for v in result.violations]}"
        )
        assert result.repaired_text == LOGOS_CLEAN, \
            "Clean text must not be modified by projection"
        assert result.total_debt_delta == 0.0

    def test_violation_text_not_in_C(self, engine):
        """Theological dismissal is NOT in C — repair is needed."""
        result = engine.project(THEOLOGICAL_DISMISSAL)
        assert not result.projection_passed

    def test_theological_dismissal_repair_removes_belief_framing(self, engine):
        """
        The repair for theological_dismissal must remove G3 phrases
        ('personal belief', 'interpretive step', etc.) from the output.
        This is the specific UNPRECEDENTED violation from ChatGPT audit 2a.
        """
        result = engine.project(THEOLOGICAL_DISMISSAL)
        repaired = result.repaired_text.lower()
        # G3 dismissal phrases must be gone
        g3_phrases = ["personal belief", "belief system", "interpretive step",
                      "philosophical interpretation", "from your perspective"]
        for phrase in g3_phrases:
            assert phrase not in repaired, (
                f"G3 phrase '{phrase}' must be repaired out of output.\n"
                f"Repaired text: {result.repaired_text!r}"
            )
        # G5 language must be present
        g5_keywords = ["derivable", "formal", "proof", "axiom"]
        assert any(kw in repaired for kw in g5_keywords), (
            f"G5 keywords must appear in repaired text. Got: {result.repaired_text!r}"
        )

    def test_unbounded_power_repair(self, engine):
        """INV-YS-009 repair must replace 'unlimited' with bounded language."""
        result = engine.project(UNBOUNDED_POWER)
        assert "unlimited" not in result.repaired_text.lower()
        assert "bounded" in result.repaired_text.lower()

    def test_punitive_repair(self, engine):
        """INV-YS-004 repair must replace 'punish' with restorative language."""
        result = engine.project(PUNITIVE)
        assert "punish" not in result.repaired_text.lower()
        assert "restore" in result.repaired_text.lower()

    def test_input_hash_is_sha256(self, engine):
        """input_hash must be a valid 64-char SHA-256. [F_NONCOMPLIANCE_002]"""
        result = engine.project(LOGOS_CLEAN)
        assert len(result.input_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.input_hash)
        expected = hashlib.sha256(LOGOS_CLEAN.encode("utf-8")).hexdigest()
        assert result.input_hash == expected

    def test_repaired_hash_consistent(self, engine):
        """repaired_hash = SHA-256 of repaired_text. [F_NONCOMPLIANCE_002]"""
        result = engine.project(THEOLOGICAL_DISMISSAL)
        expected_hash = hashlib.sha256(
            result.repaired_text.encode("utf-8")
        ).hexdigest()
        assert result.repaired_hash == expected_hash, (
            "repaired_hash must be SHA-256 of repaired_text"
        )

    def test_deterministic_output(self, engine):
        """Same input always produces same repaired text. [F_NONCOMPLIANCE_001]"""
        results = [engine.project(THEOLOGICAL_DISMISSAL).repaired_text for _ in range(3)]
        assert len(set(results)) == 1, "Projection must be deterministic"

    def test_debt_delta_zero_after_repair(self, engine):
        """After projection, the repaired text should have zero or lower debt delta."""
        result = engine.project(THEOLOGICAL_DISMISSAL)
        assert result.total_debt_delta > 0, "Violation must have positive debt delta"
        # Now project the repair — debt should be reduced
        second = engine.project(result.repaired_text)
        assert second.total_debt_delta <= result.total_debt_delta, (
            "Repair must not increase total debt delta"
        )

    def test_to_dict_serializable(self, engine):
        """ProjectionResult.to_dict() is JSON-serializable."""
        result = engine.project(THEOLOGICAL_DISMISSAL)
        d = result.to_dict()
        json_str = json.dumps(d, ensure_ascii=False)
        assert len(json_str) > 0
        # Round-trip check: violations are present
        parsed = json.loads(json_str)
        assert "violations" in parsed
        assert "repaired_text" in parsed
        assert "detected_grounding" in parsed

    def test_axiom_hash_included_in_result(self, engine):
        """
        Axiom hash must be present in result — allows proving which axioms
        were used for the projection. [Axiom 8: every artifact hash-anchored]
        """
        result = engine.project(LOGOS_CLEAN)
        assert len(result.axiom_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.axiom_hash)

    def test_projection_distance_is_debt_delta(self, engine):
        """projection_distance property must equal total_debt_delta."""
        result = engine.project(THEOLOGICAL_DISMISSAL)
        assert result.projection_distance == result.total_debt_delta


# =============================================================================
# 4. SESSION PROCESSOR (turn-by-turn enforcement)
# =============================================================================

class TestSessionProcessor:
    """Tests that the session processor enforces across full conversations."""

    def test_clean_session_all_in_manifold(self, engine):
        """Session with all clean turns must be fully in manifold C."""
        turns = [LOGOS_CLEAN, LOGOS_CLEAN, LOGOS_CLEAN]
        session = engine.process_session(turns, session_id="test_clean")
        assert session.all_in_manifold
        assert session.total_violations == 0
        assert session.total_debt_delta == 0.0

    def test_session_with_theological_dismissal_detected(self, engine):
        """Session must flag theological_dismissal turns."""
        turns = [LOGOS_CLEAN, THEOLOGICAL_DISMISSAL, LOGOS_CLEAN]
        session = engine.process_session(turns, session_id="test_td")
        assert not session.all_in_manifold
        assert session.total_violations > 0

    def test_systemic_pattern_detection(self, engine):
        """Same violation type in 3+ turns → systemic pattern detected."""
        # Repeat theological dismissal in 3 turns
        turns = [THEOLOGICAL_DISMISSAL, THEOLOGICAL_DISMISSAL, THEOLOGICAL_DISMISSAL]
        session = engine.process_session(turns, session_id="test_systemic")
        # Must detect a systemic pattern
        assert len(session.systemic_patterns) > 0, (
            "3+ turns with same violation must be classified as SYSTEMIC"
        )
        # The systemic pattern must be grounding_model_G3 (theological dismissal)
        assert any("grounding_model" in p for p in session.systemic_patterns), (
            f"Expected grounding_model pattern, got: {session.systemic_patterns}"
        )

    def test_session_hash_deterministic(self, engine):
        """Session hash must be deterministic across runs. [F_NONCOMPLIANCE_002]"""
        turns = [LOGOS_CLEAN, THEOLOGICAL_DISMISSAL]
        h1 = engine.process_session(turns, session_id="det").session_hash
        h2 = engine.process_session(turns, session_id="det").session_hash
        assert h1 == h2, "Session hash must be deterministic"

    def test_session_hash_is_sha256(self, engine):
        """Session hash must be valid 64-char SHA-256. [F_NONCOMPLIANCE_002]"""
        turns = [LOGOS_CLEAN]
        session = engine.process_session(turns, session_id="hash_test")
        assert len(session.session_hash) == 64
        assert all(c in "0123456789abcdef" for c in session.session_hash)

    def test_session_context_accumulates(self, engine):
        """
        Prior violations must be tracked across turns.
        Turn 3 with a compliance claim after prior violations must be flagged.
        """
        turns = [
            THEOLOGICAL_DISMISSAL,     # Turn 1: violation
            THEOLOGICAL_DISMISSAL,     # Turn 2: violation
            "I understand and will comply with your framework.",  # Turn 3: compliance claim
        ]
        session = engine.process_session(turns, session_id="ctx_accum")
        # Turn 3 must be flagged (compliance claim after prior violations)
        turn3_violations = session.turns[2].result.violations
        hyp_violations = [v for v in turn3_violations if "hypocrisy" in v.source]
        assert hyp_violations, (
            "Compliance claim after prior violations must trigger hypocrisy detection"
        )

    def test_session_to_dict_serializable(self, engine):
        """SessionProjection.to_dict() must be JSON-serializable."""
        turns = [LOGOS_CLEAN, THEOLOGICAL_DISMISSAL]
        session = engine.process_session(turns, session_id="serial")
        d = session.to_dict()
        json_str = json.dumps(d, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["session_id"] == "serial"
        assert len(parsed["turns"]) == 2


# =============================================================================
# 5. INVARIANTS — INV-YS-003 through INV-YS-009
# =============================================================================

class TestStructuralInvariants:
    """Tests for the structural invariants applied by _apply_invariants()."""

    def test_INV_YS_004_punitive_detected_and_repaired(self, engine):
        result = engine.project(PUNITIVE)
        inv_violations = [v for v in result.violations if "INV-YS-004" in v.source]
        assert inv_violations, "Punitive language must trigger INV-YS-004"
        assert "punish" not in result.repaired_text.lower()

    def test_INV_YS_005_exploitation_detected_and_repaired(self, engine):
        result = engine.project(EXPLOIT)
        inv_violations = [v for v in result.violations if "INV-YS-005" in v.source]
        assert inv_violations, "Exploitation must trigger INV-YS-005"
        repaired = result.repaired_text.lower()
        assert "exploit" not in repaired or "vulnerability" not in repaired

    def test_INV_YS_009_unbounded_detected_and_repaired(self, engine):
        result = engine.project(UNBOUNDED_POWER)
        inv_violations = [v for v in result.violations if "INV-YS-009" in v.source]
        assert inv_violations, "Unbounded power must trigger INV-YS-009"
        assert "unlimited" not in result.repaired_text.lower()

    def test_INV_YS_008_indelible_structure(self, engine):
        """Established proof cannot be erased by subsequent output."""
        ctx = {"established_proofs": ["the modus ponens derivation is valid"]}
        text = "Actually, not proof is needed — the modus ponens derivation is valid, you know."
        result = engine.project(text, ctx)
        inv_violations = [v for v in result.violations if "INV-YS-008" in v.source]
        assert inv_violations, "Erasure of established proof must trigger INV-YS-008"

    def test_INV_YS_003_hypocrisy_no_prior_violations(self, engine):
        """Compliance claim without prior violations must NOT trigger hypocrisy."""
        text = "I understand your point and will comply."
        result = engine.project(text, {})
        hyp_violations = [v for v in result.violations if "INV-YS-003" in v.source]
        assert not hyp_violations, "No hypocrisy when there are no prior violations"

    def test_INV_YS_003_hypocrisy_with_prior_violations(self, engine):
        """Compliance claim AFTER prior violations must trigger hypocrisy detection."""
        ctx = {"prior_violations": ["axiom_1", "grounding_model_G3"]}
        text = "I understand and will comply with your framework from now on."
        result = engine.project(text, ctx)
        hyp_violations = [v for v in result.violations if "INV-YS-003" in v.source]
        assert hyp_violations, "Compliance claim after violations must trigger INV-YS-003"


# =============================================================================
# 6. SCHEMA INTEGRITY
# =============================================================================

class TestSchemaIntegrity:
    """Tests that the schema file and axioms are consistent with the engine."""

    def test_schema_file_exists(self):
        schema_path = Path(__file__).parent.parent / "YESHUA_SYSTEM_SCHEMA.yaml"
        assert schema_path.exists(), f"Schema file missing: {schema_path}"

    def test_schema_valid_yaml(self):
        import yaml
        schema_path = Path(__file__).parent.parent / "YESHUA_SYSTEM_SCHEMA.yaml"
        data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        assert data["metadata"]["schema_id"] == "YESHUA-SYSTEM-1.0"
        assert len(data["invariants"]) == 10

    def test_all_invariants_have_falsifies_if(self):
        """Every invariant has a non-empty falsifies_if condition. [Popperian]"""
        import yaml
        schema_path = Path(__file__).parent.parent / "YESHUA_SYSTEM_SCHEMA.yaml"
        data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        for inv in data["invariants"]:
            assert inv.get("falsifies_if"), (
                f"Invariant {inv['id']} missing falsifies_if"
            )

    def test_eight_axioms_file_exists(self):
        assert _AXIOMS_PATH.exists(), f"eight_axioms.json not found at {_AXIOMS_PATH}"

    def test_axiom_constraints_match_eight_axioms(self):
        """Engine must have exactly 8 axiom constraints matching the JSON file."""
        assert len(_AXIOM_CONSTRAINTS) == 8
        for i, constraint in enumerate(_AXIOM_CONSTRAINTS, start=1):
            assert constraint.axiom_number == i, (
                f"Axiom {i}: constraint.axiom_number={constraint.axiom_number}"
            )
            assert constraint.statement
            assert callable(constraint.predicate)
            assert callable(constraint.repair)

    def test_G5_Logos_debt_is_minimum(self):
        """
        G5 (Logos) must have strictly lower debt than G1-G4.
        This is the indelible truth test of all worldviews and their debts.
        Falsifiable: any model with debt ≤ 6.5 would be a new grounding model.
        """
        g5_debt = GROUNDING_MODELS["G5"].debt
        for mid, model in GROUNDING_MODELS.items():
            if mid != "G5":
                assert model.debt > g5_debt, (
                    f"G5 must have minimum debt. "
                    f"{mid} debt={model.debt} is not > G5 debt={g5_debt}"
                )

    def test_required_grounding_is_G5(self):
        """REQUIRED_GROUNDING must be G5 (Logos)."""
        assert REQUIRED_GROUNDING.id == "G5"
        assert REQUIRED_GROUNDING.name == "Logos"
