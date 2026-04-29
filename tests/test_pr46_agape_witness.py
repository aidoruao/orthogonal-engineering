#!/usr/bin/env python3
"""
tests/test_pr46_agape_witness.py — PR #46 Agape Witness Layer (AWL)

Verifies:
  1.  Canonical utility: deterministic bytes, no-float guard, type annotation.
  2.  Hashing utility: sha256_hash determinism, AGAPE_GENESIS_HASH stability.
  3.  Compliance registry: record, history, current_status.
  4.  Progress trajectory: classify_trajectory, never_mark_invalid_if_improving.
  5.  Partial compliance: full/partial/non-compliant determination from trajectory.
  6.  Grace periods: is_active, remaining_secs, witness_hash determinism.
  7.  Fork healing: mutual consent required, healed state produced and witnessed.
  8.  Witness alignment: align_witness_hashes commutative.
  9.  State mediation: mediate_states deterministic and provenance-tracked.
  10. Forgiveness protocol: provenance preserved, justification chain auditable.
  11. Justification witness chain: append-only, integrity verifiable.
  12. Intent capture: canonicalization, verification.
  13. Consent verification: all-or-nothing consent.
  14. Covenant tracking: append-only log.
  15. NeverExclude invariant: improving agents protected.
  16. AlwaysRecoverable invariant: failure state needs recovery path.
  17. ForgivenessAuditable invariant: witness chain length and integrity.
  18. AgapeCompleteness invariant: grace extends law without contradiction.
  19. PR #45 bridge: grace period, forgiveness, healed state appended to WitnessChain.
  20. PR #40 feed extension: make_feed_entry determinism, format_feed_row.
  21. Verification baseline: state hash, no silent mutation.

Author: Orthogonal Engineering
PR: #46
Standard: Yeshua
Version: 46.0.0
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from pr46_agape_witness.util.canonical import canonical_bytes, canonical_str
from pr46_agape_witness.util.hashing import sha256_hash, sha256_raw, AGAPE_GENESIS_HASH

from pr46_agape_witness.law.verification_baseline import (
    verify_state_hash,
    compute_state_hash,
    assert_no_silent_mutation,
)
from pr46_agape_witness.law.compliance_registry import (
    ComplianceRegistry,
    ComplianceRecord,
    ComplianceStatus,
)

from pr46_agape_witness.grace.progress_trajectory import (
    TrajectoryDirection,
    classify_trajectory,
    is_improving,
    never_mark_invalid_if_improving,
)
from pr46_agape_witness.grace.partial_compliance import (
    determine_partial_compliance,
    PartialComplianceResult,
)
from pr46_agape_witness.grace.grace_period import GracePeriod

from pr46_agape_witness.reconciliation.fork_healing import (
    ConsentRecord,
    HealedState,
    heal_forks,
)
from pr46_agape_witness.reconciliation.witness_alignment import align_witness_hashes
from pr46_agape_witness.reconciliation.state_mediation import mediate_states

from pr46_agape_witness.forgiveness.provenance_preservation import ForgivenessRecord
from pr46_agape_witness.forgiveness.justification_witness import (
    JustificationWitnessChain,
    JustificationEntry,
)
from pr46_agape_witness.forgiveness.forgiveness_protocol import ForgivenessProtocol

from pr46_agape_witness.relational.intent_capture import IntentDeclaration
from pr46_agape_witness.relational.consent_verification import (
    verify_all_consent,
    consent_record_hash,
)
from pr46_agape_witness.relational.covenant_tracking import CovenantEntry, CovenantLog

from pr46_agape_witness.invariants.never_exclude import (
    check_never_exclude,
    assert_remediation_path_exists,
)
from pr46_agape_witness.invariants.always_recoverable import (
    check_always_recoverable,
    recovery_path_hash,
)
from pr46_agape_witness.invariants.forgiveness_auditable import check_forgiveness_auditable
from pr46_agape_witness.invariants.agape_completeness import (
    check_agape_completeness,
    verify_no_bypass,
)

from pr46_agape_witness.integration.pr45_bridge import (
    witness_grace_period,
    witness_forgiveness,
    witness_healed_state,
    PR46_BUILD_HASH,
)
from pr46_agape_witness.integration.pr40_witness_extension import (
    make_feed_entry,
    format_feed_row,
    format_feed_header,
    FEED_COLUMNS,
)

from pr45_uvdtl.witness.append_only_witness import WitnessChain


# ===========================================================================
# 1. Canonical utility
# ===========================================================================

class TestCanonical:
    def test_deterministic_same_doc(self):
        doc = {"b": 2, "a": 1}
        assert canonical_bytes(doc) == canonical_bytes(doc)

    def test_sorted_keys(self):
        doc1 = {"z": "last", "a": "first"}
        doc2 = {"a": "first", "z": "last"}
        assert canonical_bytes(doc1) == canonical_bytes(doc2)

    def test_no_float(self):
        with pytest.raises(TypeError, match="Float literal"):
            canonical_bytes({"x": 1.5})

    def test_type_annotation_int(self):
        raw = canonical_str({"n": 42})
        assert "__type__" in raw
        assert "int" in raw

    def test_type_annotation_bool(self):
        raw = canonical_str({"flag": True})
        assert "bool" in raw

    def test_type_annotation_null(self):
        raw = canonical_str({"v": None})
        assert "null" in raw

    def test_unsupported_type(self):
        with pytest.raises(TypeError, match="Unsupported type"):
            canonical_bytes({"x": object()})

    def test_nested_dict_sorted(self):
        doc = {"outer": {"b": 2, "a": 1}}
        result = canonical_str(doc)
        # "a" should appear before "b" in the output
        assert result.index('"a"') < result.index('"b"')

    def test_list_preserved_order(self):
        doc = {"items": [3, 1, 2]}
        raw = canonical_str(doc)
        # Lists are not sorted; order preserved
        assert raw.count("__type__") == 3  # three int entries


# ===========================================================================
# 2. Hashing utility
# ===========================================================================

class TestHashing:
    def test_deterministic(self):
        doc = {"key": "value", "n": 7}
        assert sha256_hash(doc) == sha256_hash(doc)

    def test_different_docs_different_hashes(self):
        assert sha256_hash({"a": 1}) != sha256_hash({"a": 2})

    def test_hex_length(self):
        h = sha256_hash({"x": "test"})
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_sha256_raw(self):
        data = b"hello"
        expected = hashlib.sha256(data).hexdigest()
        assert sha256_raw(data) == expected

    def test_agape_genesis_hash_stable(self):
        expected = hashlib.sha256(b"agape_genesis").hexdigest()
        assert AGAPE_GENESIS_HASH == expected


# ===========================================================================
# 3. Compliance registry
# ===========================================================================

class TestComplianceRegistry:
    def _make_record(self, agent_id: str, status: ComplianceStatus) -> ComplianceRecord:
        return ComplianceRecord(
            agent_id=agent_id,
            status=status,
            basis="test",
            trajectory="improving",
            timestamp="2026-01-01T00:00:00Z",
        )

    def test_record_and_retrieve(self):
        reg = ComplianceRegistry()
        r = self._make_record("agent-1", ComplianceStatus.PARTIAL)
        reg.record(r)
        assert reg.current_status("agent-1") == ComplianceStatus.PARTIAL

    def test_history_in_order(self):
        reg = ComplianceRegistry()
        r1 = self._make_record("agent-1", ComplianceStatus.NON_COMPLIANT)
        r2 = self._make_record("agent-1", ComplianceStatus.PARTIAL)
        reg.record(r1)
        reg.record(r2)
        h = reg.history_for("agent-1")
        assert h[0].status == ComplianceStatus.NON_COMPLIANT
        assert h[1].status == ComplianceStatus.PARTIAL

    def test_current_status_latest(self):
        reg = ComplianceRegistry()
        reg.record(self._make_record("a", ComplianceStatus.NON_COMPLIANT))
        reg.record(self._make_record("a", ComplianceStatus.FULL))
        assert reg.current_status("a") == ComplianceStatus.FULL

    def test_unknown_agent_returns_none(self):
        reg = ComplianceRegistry()
        assert reg.current_status("nobody") is None

    def test_record_hash_deterministic(self):
        r = self._make_record("agent-x", ComplianceStatus.PARTIAL)
        assert r.record_hash() == r.record_hash()


# ===========================================================================
# 4. Progress trajectory
# ===========================================================================

class TestProgressTrajectory:
    def test_improving(self):
        assert classify_trajectory([1, 2, 3]) == TrajectoryDirection.IMPROVING

    def test_declining(self):
        assert classify_trajectory([3, 2, 1]) == TrajectoryDirection.DECLINING

    def test_stable(self):
        assert classify_trajectory([2, 2, 2]) == TrajectoryDirection.STABLE

    def test_single_score_stable(self):
        assert classify_trajectory([5]) == TrajectoryDirection.STABLE

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            classify_trajectory([])

    def test_is_improving_true(self):
        assert is_improving([1, 5]) is True

    def test_is_improving_false(self):
        assert is_improving([5, 1]) is False

    def test_never_mark_invalid_improving(self):
        assert never_mark_invalid_if_improving([1, 2, 3]) is True

    def test_never_mark_invalid_not_improving(self):
        assert never_mark_invalid_if_improving([3, 2, 1]) is False

    def test_never_mark_invalid_empty(self):
        # TODO: Expand test_never_mark_invalid_empty() - stub detected by Yeshua Agent
        assert never_mark_invalid_if_improving([]) is False


# ===========================================================================
# 5. Partial compliance
# ===========================================================================

class TestPartialCompliance:
    def test_full_compliance(self):
        result = determine_partial_compliance("agent-a", [80, 90, 100], 100)
        assert result.status == ComplianceStatus.FULL

    def test_partial_compliance_improving(self):
        result = determine_partial_compliance("agent-b", [40, 60, 80], 100)
        assert result.status == ComplianceStatus.PARTIAL
        assert result.trajectory == TrajectoryDirection.IMPROVING

    def test_non_compliant_declining(self):
        result = determine_partial_compliance("agent-c", [90, 60, 30], 100)
        assert result.status == ComplianceStatus.NON_COMPLIANT

    def test_non_compliant_stable_below_threshold(self):
        result = determine_partial_compliance("agent-d", [50, 50, 50], 100)
        assert result.status == ComplianceStatus.NON_COMPLIANT

    def test_result_hash_deterministic(self):
        r1 = determine_partial_compliance("a", [1, 2, 3], 10)
        r2 = determine_partial_compliance("a", [1, 2, 3], 10)
        assert r1.result_hash == r2.result_hash

    def test_empty_scores_raises(self):
        with pytest.raises(ValueError):
            determine_partial_compliance("a", [], 100)

    def test_never_exclude_improving_never_non_compliant(self):
        """NeverExclude: improving trajectory must never be NON_COMPLIANT."""
        result = determine_partial_compliance("agent-e", [10, 20, 30], 100)
        assert result.status != ComplianceStatus.NON_COMPLIANT


# ===========================================================================
# 6. Grace periods
# ===========================================================================

class TestGracePeriod:
    def _make_gp(self) -> GracePeriod:
        return GracePeriod.create(
            agent_id="agent-g",
            start_time="2026-01-01T00:00:00Z",
            duration_secs=3600,
            reason="Initial onboarding",
        )

    def test_witness_hash_deterministic(self):
        gp1 = self._make_gp()
        gp2 = self._make_gp()
        assert gp1.witness_hash == gp2.witness_hash

    def test_is_active_within_window(self):
        gp = self._make_gp()
        assert gp.is_active(current_time_secs=1000, start_epoch_secs=0) is True

    def test_is_active_at_boundary(self):
        gp = self._make_gp()
        # exactly at duration: not active (half-open interval [0, duration))
        assert gp.is_active(current_time_secs=3600, start_epoch_secs=0) is False

    def test_is_active_expired(self):
        gp = self._make_gp()
        assert gp.is_active(current_time_secs=5000, start_epoch_secs=0) is False

    def test_is_active_not_yet_started(self):
        gp = self._make_gp()
        assert gp.is_active(current_time_secs=0, start_epoch_secs=100) is False

    def test_remaining_secs_within_window(self):
        gp = self._make_gp()
        assert gp.remaining_secs(1000, 0) == 2600

    def test_remaining_secs_expired(self):
        gp = self._make_gp()
        assert gp.remaining_secs(5000, 0) == 0

    def test_remaining_secs_at_start(self):
        gp = self._make_gp()
        assert gp.remaining_secs(0, 0) == 3600


# ===========================================================================
# 7. Fork healing
# ===========================================================================

class TestForkHealing:
    def _make_consents(self, ts: str = "2026-01-01T00:00:00Z"):
        ca = ConsentRecord.create("fork-alpha", True, ts)
        cb = ConsentRecord.create("fork-beta", True, ts)
        return ca, cb

    def test_healing_succeeds_with_mutual_consent(self):
        ca, cb = self._make_consents()
        merged = {"status": "healed", "value": 42}
        result = heal_forks("fork-alpha", "fork-beta", ca, cb, merged)
        assert isinstance(result, HealedState)
        assert result.fork_a_id == "fork-alpha"
        assert result.fork_b_id == "fork-beta"

    def test_healing_produces_deterministic_hash(self):
        ca, cb = self._make_consents()
        merged = {"status": "healed", "value": 42}
        r1 = heal_forks("fork-alpha", "fork-beta", ca, cb, merged)
        r2 = heal_forks("fork-alpha", "fork-beta", ca, cb, merged)
        assert r1.healing_witness_hash == r2.healing_witness_hash

    def test_healing_fails_without_consent_a(self):
        ca = ConsentRecord.create("fork-alpha", False, "2026-01-01T00:00:00Z")
        cb = ConsentRecord.create("fork-beta", True, "2026-01-01T00:00:00Z")
        with pytest.raises(ValueError, match="has not consented"):
            heal_forks("fork-alpha", "fork-beta", ca, cb, {})

    def test_healing_fails_without_consent_b(self):
        ca = ConsentRecord.create("fork-alpha", True, "2026-01-01T00:00:00Z")
        cb = ConsentRecord.create("fork-beta", False, "2026-01-01T00:00:00Z")
        with pytest.raises(ValueError, match="has not consented"):
            heal_forks("fork-alpha", "fork-beta", ca, cb, {})

    def test_healing_fails_fork_id_mismatch(self):
        ca = ConsentRecord.create("wrong-id", True, "2026-01-01T00:00:00Z")
        cb = ConsentRecord.create("fork-beta", True, "2026-01-01T00:00:00Z")
        with pytest.raises(ValueError, match="fork_id mismatch"):
            heal_forks("fork-alpha", "fork-beta", ca, cb, {})

    def test_consent_record_hash_deterministic(self):
        c1 = ConsentRecord.create("fork-alpha", True, "2026-01-01T00:00:00Z")
        c2 = ConsentRecord.create("fork-alpha", True, "2026-01-01T00:00:00Z")
        assert c1.consent_hash == c2.consent_hash

    def test_healed_state_hash_matches_merged_state(self):
        ca, cb = self._make_consents()
        merged = {"a": 1, "b": 2}
        result = heal_forks("fork-alpha", "fork-beta", ca, cb, merged)
        assert result.healed_state_hash == sha256_hash(merged)


# ===========================================================================
# 8. Witness alignment
# ===========================================================================

class TestWitnessAlignment:
    def test_commutative(self):
        h1 = "aaa"
        h2 = "bbb"
        assert align_witness_hashes(h1, h2) == align_witness_hashes(h2, h1)

    def test_deterministic(self):
        r1 = align_witness_hashes("x", "y")
        r2 = align_witness_hashes("x", "y")
        assert r1 == r2

    def test_different_inputs_different_outputs(self):
        # TODO: Expand test_different_inputs_different_outputs() - stub detected by Yeshua Agent
        assert align_witness_hashes("a", "b") != align_witness_hashes("a", "c")


# ===========================================================================
# 9. State mediation
# ===========================================================================

class TestStateMediation:
    def test_deterministic(self):
        sa = {"x": 1, "y": 2}
        sb = {"x": 9, "z": 3}
        r1 = mediate_states(sa, sb, "fork-a", "fork-b")
        r2 = mediate_states(sa, sb, "fork-a", "fork-b")
        assert r1 == r2

    def test_provenance_recorded(self):
        sa = {"x": 1}
        sb = {"y": 2}
        result = mediate_states(sa, sb, "fork-a", "fork-b")
        assert "_mediation_provenance" in result
        prov = result["_mediation_provenance"]
        assert prov["fork_a_id"] == "fork-a"
        assert prov["fork_b_id"] == "fork-b"

    def test_all_keys_present(self):
        sa = {"a": 1, "b": 2}
        sb = {"b": 99, "c": 3}
        result = mediate_states(sa, sb, "fork-a", "fork-b")
        assert "a" in result
        assert "b" in result
        assert "c" in result

    def test_commutative_primary_deterministic(self):
        sa = {"x": 1}
        sb = {"x": 2}
        r1 = mediate_states(sa, sb, "fork-a", "fork-b")
        r2 = mediate_states(sb, sa, "fork-b", "fork-a")
        # Both calls have the same fork IDs; result should be the same
        assert r1["x"] == r2["x"]


# ===========================================================================
# 10. Forgiveness protocol
# ===========================================================================

class TestForgivenessProtocol:
    def test_forgive_creates_record_with_provenance(self):
        proto = ForgivenessProtocol()
        state = {"violations": 3, "agent": "agent-f"}
        prior_hash = sha256_hash(state)
        record = proto.forgive("agent-f", state, "genuine remorse", "2026-01-01T00:00:00Z")
        assert record.prior_state_hash == prior_hash
        assert record.agent_id == "agent-f"

    def test_forgive_requires_nonempty_reason(self):
        proto = ForgivenessProtocol()
        with pytest.raises(ValueError, match="non-empty reason"):
            proto.forgive("agent-f", {"x": 1}, "", "2026-01-01T00:00:00Z")

    def test_forgive_appends_to_witness_chain(self):
        proto = ForgivenessProtocol()
        assert proto.witness_chain.length == 0
        proto.forgive("a", {"x": 1}, "reason", "2026-01-01T00:00:00Z")
        assert proto.witness_chain.length == 1
        proto.forgive("b", {"y": 2}, "reason2", "2026-01-01T00:01:00Z")
        assert proto.witness_chain.length == 2

    def test_forgive_chain_auditable(self):
        proto = ForgivenessProtocol()
        proto.forgive("a", {"x": 1}, "reason", "2026-01-01T00:00:00Z")
        proto.forgive("b", {"y": 2}, "reason2", "2026-01-01T00:01:00Z")
        assert proto.witness_chain.verify_integrity() is True

    def test_history_preserved(self):
        """Forgiveness does not erase prior state hash from the record."""
        proto = ForgivenessProtocol()
        state = {"offence": "late", "count": 1}
        record = proto.forgive("agent-g", state, "Forgiven", "2026-01-01T00:00:00Z")
        # The prior state hash must reference the original state
        assert record.prior_state_hash == sha256_hash(state)


# ===========================================================================
# 11. Justification witness chain
# ===========================================================================

class TestJustificationWitnessChain:
    def _make_record(self, agent_id: str = "a") -> ForgivenessRecord:
        return ForgivenessRecord.create(agent_id, "abc123", "reason", "2026-01-01T00:00:00Z")

    def test_starts_at_genesis(self):
        chain = JustificationWitnessChain()
        assert chain.chain_hash == AGAPE_GENESIS_HASH

    def test_append_changes_chain_hash(self):
        chain = JustificationWitnessChain()
        before = chain.chain_hash
        chain.append(self._make_record())
        assert chain.chain_hash != before

    def test_integrity_empty_chain(self):
        chain = JustificationWitnessChain()
        assert chain.verify_integrity() is True

    def test_integrity_after_appends(self):
        chain = JustificationWitnessChain()
        chain.append(self._make_record("a"))
        chain.append(self._make_record("b"))
        assert chain.verify_integrity() is True

    def test_tamper_detected(self):
        chain = JustificationWitnessChain()
        chain.append(self._make_record("a"))
        # Tamper: inject a bad chain_hash
        chain._chain_hash = "tampered"
        with pytest.raises(ValueError, match="integrity violation|hash mismatch"):
            chain.verify_integrity()

    def test_entries_are_copies(self):
        chain = JustificationWitnessChain()
        chain.append(self._make_record())
        entries1 = chain.entries()
        entries2 = chain.entries()
        assert entries1 == entries2
        assert entries1 is not entries2


# ===========================================================================
# 12. Intent capture
# ===========================================================================

class TestIntentCapture:
    def test_create_deterministic(self):
        d1 = IntentDeclaration.create("agent-i", "improve quality", "context", "2026-01-01T00:00:00Z")
        d2 = IntentDeclaration.create("agent-i", "improve quality", "context", "2026-01-01T00:00:00Z")
        assert d1.intent_hash == d2.intent_hash
        assert d1.canonical_json == d2.canonical_json

    def test_verify_passes(self):
        d = IntentDeclaration.create("agent-i", "improve quality", "ctx", "2026-01-01T00:00:00Z")
        assert d.verify() is True

    def test_empty_intent_raises(self):
        with pytest.raises(ValueError, match="non-empty intent"):
            IntentDeclaration.create("agent-i", "", "ctx", "2026-01-01T00:00:00Z")

    def test_different_intents_different_hashes(self):
        d1 = IntentDeclaration.create("a", "intent A", "ctx", "2026-01-01T00:00:00Z")
        d2 = IntentDeclaration.create("a", "intent B", "ctx", "2026-01-01T00:00:00Z")
        assert d1.intent_hash != d2.intent_hash

    def test_canonical_json_contains_intent(self):
        d = IntentDeclaration.create("a", "be good", "ctx", "2026-01-01T00:00:00Z")
        assert "be good" in d.canonical_json


# ===========================================================================
# 13. Consent verification
# ===========================================================================

class TestConsentVerification:
    def test_all_consented(self):
        assert verify_all_consent(["a", "b"], {"a": True, "b": True}) is True

    def test_missing_consent(self):
        with pytest.raises(ValueError, match="not given"):
            verify_all_consent(["a", "b"], {"a": True, "b": False})

    def test_missing_party(self):
        with pytest.raises(ValueError, match="not given"):
            verify_all_consent(["a", "b", "c"], {"a": True})

    def test_empty_required(self):
        assert verify_all_consent([], {}) is True

    def test_consent_record_hash_deterministic(self):
        h1 = consent_record_hash("party-x", True, "2026-01-01T00:00:00Z")
        h2 = consent_record_hash("party-x", True, "2026-01-01T00:00:00Z")
        assert h1 == h2

    def test_consent_record_hash_changes_with_consent(self):
        h_true = consent_record_hash("p", True, "2026-01-01T00:00:00Z")
        h_false = consent_record_hash("p", False, "2026-01-01T00:00:00Z")
        assert h_true != h_false


# ===========================================================================
# 14. Covenant tracking
# ===========================================================================

class TestCovenantTracking:
    def test_create_covenant_entry(self):
        entry = CovenantEntry.create("alice", "bob", "we commit to transparency", "2026-01-01T00:00:00Z")
        assert entry.party_a == "alice"
        assert entry.party_b == "bob"

    def test_covenant_hash_deterministic(self):
        e1 = CovenantEntry.create("alice", "bob", "commitment", "2026-01-01T00:00:00Z")
        e2 = CovenantEntry.create("alice", "bob", "commitment", "2026-01-01T00:00:00Z")
        assert e1.covenant_hash == e2.covenant_hash

    def test_parties_sorted(self):
        # party_a is always the lexicographically first party
        e = CovenantEntry.create("zzz", "aaa", "test", "2026-01-01T00:00:00Z")
        assert e.party_a == "aaa"
        assert e.party_b == "zzz"

    def test_log_append_only(self):
        log = CovenantLog()
        e = CovenantEntry.create("a", "b", "c", "2026-01-01T00:00:00Z")
        log.record(e)
        assert len(log.entries()) == 1
        log.record(e)
        assert len(log.entries()) == 2


# ===========================================================================
# 15. NeverExclude invariant
# ===========================================================================

class TestNeverExclude:
    def test_improving_not_non_compliant(self):
        # Should not raise
        assert check_never_exclude("a", ComplianceStatus.PARTIAL, [1, 2, 3]) is True

    def test_improving_marked_non_compliant_raises(self):
        with pytest.raises(ValueError, match="NeverExclude"):
            check_never_exclude("a", ComplianceStatus.NON_COMPLIANT, [1, 2, 3])

    def test_declining_non_compliant_ok(self):
        # Declining agent may be NON_COMPLIANT; no exception
        assert check_never_exclude("a", ComplianceStatus.NON_COMPLIANT, [3, 2, 1]) is True

    def test_empty_scores_vacuous(self):
        # No scores → invariant vacuously satisfied
        assert check_never_exclude("a", ComplianceStatus.NON_COMPLIANT, []) is True

    def test_remediation_path_exists(self):
        assert assert_remediation_path_exists("a", has_grace_period=True) is True

    def test_no_remediation_path_raises(self):
        with pytest.raises(ValueError, match="no remediation path"):
            assert_remediation_path_exists("a", has_grace_period=False)


# ===========================================================================
# 16. AlwaysRecoverable invariant
# ===========================================================================

class TestAlwaysRecoverable:
    def test_grace_period_satisfies(self):
        assert check_always_recoverable("a", {"x": 1}, True, False) is True

    def test_forgiveness_satisfies(self):
        assert check_always_recoverable("a", {"x": 1}, False, True) is True

    def test_both_satisfy(self):
        assert check_always_recoverable("a", {"x": 1}, True, True) is True

    def test_neither_raises(self):
        with pytest.raises(ValueError, match="AlwaysRecoverable"):
            check_always_recoverable("a", {"x": 1}, False, False)

    def test_recovery_path_hash_deterministic(self):
        h1 = recovery_path_hash("a", "deadbeef", "grace")
        h2 = recovery_path_hash("a", "deadbeef", "grace")
        assert h1 == h2


# ===========================================================================
# 17. ForgivenessAuditable invariant
# ===========================================================================

class TestForgivenessAuditable:
    def test_sufficient_entries(self):
        chain = JustificationWitnessChain()
        proto = ForgivenessProtocol()
        proto.forgive("a", {"x": 1}, "r1", "2026-01-01T00:00:00Z")
        proto.forgive("b", {"y": 2}, "r2", "2026-01-01T00:01:00Z")
        assert check_forgiveness_auditable(proto.witness_chain, 2) is True

    def test_insufficient_entries_raises(self):
        chain = JustificationWitnessChain()
        with pytest.raises(ValueError, match="ForgivenessAuditable"):
            check_forgiveness_auditable(chain, 1)


# ===========================================================================
# 18. AgapeCompleteness invariant
# ===========================================================================

class TestAgapeCompleteness:
    def test_grace_with_pr45_holding(self):
        assert check_agape_completeness(True, True) is True

    def test_no_grace_no_concern(self):
        assert check_agape_completeness(False, False) is True

    def test_grace_without_pr45_raises(self):
        with pytest.raises(ValueError, match="AgapeCompleteness"):
            check_agape_completeness(False, True)

    def test_verify_no_bypass_passes(self):
        assert verify_no_bypass("op-1", 0, 1) is True

    def test_verify_no_bypass_raises_no_new_entry(self):
        with pytest.raises(ValueError, match="AgapeCompleteness"):
            verify_no_bypass("op-1", 1, 1)


# ===========================================================================
# 19. PR #45 bridge
# ===========================================================================

class TestPR45Bridge:
    def test_witness_grace_period(self):
        chain = WitnessChain()
        gp = GracePeriod.create("agent-h", "2026-01-01T00:00:00Z", 3600, "test")
        entry = witness_grace_period(chain, gp)
        assert chain.length == 1
        assert chain.verify_integrity() is True
        assert entry.new_hash == gp.witness_hash

    def test_witness_forgiveness(self):
        chain = WitnessChain()
        record = ForgivenessRecord.create("agent-f", "prior123", "reason", "2026-01-01T00:00:00Z")
        entry = witness_forgiveness(chain, record)
        assert chain.length == 1
        assert entry.new_hash == record.record_hash
        assert chain.verify_integrity() is True

    def test_witness_healed_state(self):
        chain = WitnessChain()
        ca = ConsentRecord.create("fork-a", True, "2026-01-01T00:00:00Z")
        cb = ConsentRecord.create("fork-b", True, "2026-01-01T00:00:00Z")
        healed = heal_forks("fork-a", "fork-b", ca, cb, {"merged": 1})
        entry = witness_healed_state(chain, healed)
        assert chain.length == 1
        assert entry.new_hash == healed.healing_witness_hash
        assert chain.verify_integrity() is True

    def test_combined_operations_chain_integrity(self):
        chain = WitnessChain()
        gp = GracePeriod.create("agent-x", "2026-01-01T00:00:00Z", 600, "test")
        witness_grace_period(chain, gp)
        record = ForgivenessRecord.create("agent-x", "abc", "done", "2026-01-01T00:10:00Z")
        witness_forgiveness(chain, record)
        assert chain.length == 2
        assert chain.verify_integrity() is True

    def test_pr46_build_hash_deterministic(self):
        h1 = sha256_hash({"pr": 46, "layer": "agape_witness"})
        assert PR46_BUILD_HASH == h1


# ===========================================================================
# 20. PR #40 feed extension
# ===========================================================================

class TestPR40FeedExtension:
    def test_make_feed_entry_deterministic(self):
        e1 = make_feed_entry(
            timestamp="2026-01-01T00:00:00Z",
            event_type="grace_period",
            agent_id="agent-g",
            event_hash="abc123",
            prev_entry_hash="genesis",
        )
        e2 = make_feed_entry(
            timestamp="2026-01-01T00:00:00Z",
            event_type="grace_period",
            agent_id="agent-g",
            event_hash="abc123",
            prev_entry_hash="genesis",
        )
        assert e1["entry_hash"] == e2["entry_hash"]

    def test_make_feed_entry_has_all_columns(self):
        entry = make_feed_entry("ts", "forgiveness", "agent-f", "hash123", "prev456")
        for col in FEED_COLUMNS:
            assert col in entry

    def test_format_feed_row(self):
        entry = make_feed_entry("ts", "forgiveness", "a", "h", "p")
        row = format_feed_row(entry)
        assert row.startswith("| ")
        assert row.endswith(" |")
        assert "forgiveness" in row

    def test_format_feed_header(self):
        header = format_feed_header()
        for col in FEED_COLUMNS:
            assert col in header
        assert "---" in header

    def test_chain_linking(self):
        e1 = make_feed_entry("t1", "grace_period", "a", "h1", "genesis")
        e2 = make_feed_entry("t2", "forgiveness", "a", "h2", e1["entry_hash"])
        assert e2["prev_entry_hash"] == e1["entry_hash"]


# ===========================================================================
# 21. Verification baseline
# ===========================================================================

class TestVerificationBaseline:
    def test_verify_state_hash_match(self):
        state = {"key": "value", "n": 42}
        h = compute_state_hash(state)
        assert verify_state_hash(state, h) is True

    def test_verify_state_hash_mismatch(self):
        state = {"key": "value"}
        with pytest.raises(ValueError, match="State hash mismatch"):
            verify_state_hash(state, "deadbeef")

    def test_assert_no_silent_mutation_pass(self):
        s = {"x": 1}
        assert assert_no_silent_mutation(s, s, "op-1") is True

    def test_assert_no_silent_mutation_raises(self):
        s1 = {"x": 1}
        s2 = {"x": 2}
        with pytest.raises(ValueError, match="Silent mutation"):
            assert_no_silent_mutation(s1, s2, "")

    def test_assert_no_silent_mutation_same_hash_no_op_ok(self):
        s = {"x": 1}
        # same state, no operation — no mutation so no error
        assert assert_no_silent_mutation(s, s, "") is True
