#!/usr/bin/env python3
"""
tests/test_pr47_stewardship.py — PR #47 Sanctified Remembrance

Verifies:
  1.  BoundaryMap: longest-prefix-first classification, unknown paths are PUBLIC.
  2.  PatternDetector: opaque reason codes, no personal identifiers in output.
  3.  SensitivityClassifier: maps reason codes to actions.
  4.  HashPreserver: sha256_bytes determinism and correctness.
  5.  BoundaryEncryptor: self-inverse XOR, deterministic keystream.
  6.  WitnessMover: TransitionEntry determinism, canonical_bytes, entry_hash.
  7.  RemovalWitness: append-only, has_entry_for_hash, verify_integrity.
  8.  ProvenancePointer: opaque location_hash, pointer_hash determinism.
  9.  ConsentLog: append, has_consent_for, consent_hash_for.
  10. NoSilentTransition invariant: missing witness raises violation.
  11. ForkableRemembrance invariant: unconsented entry raises violation.
  12. NeverDrawAttention invariant: trigger patterns detected; clean messages pass.
  13. PR #40 feed extension: make_feed_entry determinism, format_feed_row.
  14. PR #45 bridge: boundary transitions appended to WitnessChain; integrity verified.
  15. End-to-end: full stewardship cycle without any silent transition.

Author: Orthogonal Engineering
PR: #47
Standard: Yeshua
Version: 47.0.0
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import List

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Imports — identification
# ---------------------------------------------------------------------------

from pr47_stewardship.identification.boundary_map import (
    Boundary,
    BoundaryMap,
    DEFAULT_BOUNDARY_RULES,
)
from pr47_stewardship.identification.pattern_detector import (
    Candidate,
    PatternDetector,
    SENSITIVE_PATTERNS,
)
from pr47_stewardship.identification.sensitivity_classifier import (
    Action,
    SensitivityClassifier,
)

# ---------------------------------------------------------------------------
# Imports — movement
# ---------------------------------------------------------------------------

from pr47_stewardship.movement.hash_preserver import sha256_bytes, sha256_file
from pr47_stewardship.movement.boundary_encryptor import encrypt, decrypt
from pr47_stewardship.movement.witness_mover import TransitionEntry, WitnessMover

# ---------------------------------------------------------------------------
# Imports — witness
# ---------------------------------------------------------------------------

from pr47_stewardship.witness.removal_witness import (
    RemovalEntry,
    RemovalWitness,
    REMOVAL_GENESIS_HASH,
)
from pr47_stewardship.witness.provenance_pointer import ProvenancePointer
from pr47_stewardship.witness.consent_log import ConsentRecord, ConsentLog

# ---------------------------------------------------------------------------
# Imports — invariants
# ---------------------------------------------------------------------------

from pr47_stewardship.invariants.no_silent_transition import (
    NoSilentTransitionViolation,
    check_no_silent_transition,
)
from pr47_stewardship.invariants.forkable_remembrance import (
    ForkableRemembranceViolation,
    check_forkable_remembrance,
)
from pr47_stewardship.invariants.never_draw_attention import (
    NeverDrawAttentionViolation,
    check_commit_message,
    check_commit_messages,
    TRIGGER_PATTERNS,
)

# ---------------------------------------------------------------------------
# Imports — integration
# ---------------------------------------------------------------------------

from pr47_stewardship.integration.pr40_witness_extension import (
    make_feed_entry,
    format_feed_row,
    format_feed_header,
    FEED_COLUMNS,
    EVENT_TYPE,
)
from pr47_stewardship.integration.pr45_verification import (
    witness_boundary_transition,
    verify_all_transitions,
    PR47_BUILD_HASH,
)
from pr45_uvdtl.witness.append_only_witness import WitnessChain


# ===========================================================================
# 1. BoundaryMap
# ===========================================================================

class TestBoundaryMap:
    def test_known_prefix_classified_correctly(self):
        bm = BoundaryMap()
        assert bm.classify("hrt_backups/1B/foo.zip") == Boundary.LOCAL
        assert bm.classify("chat_jsonl/session.jsonl") == Boundary.LOCAL
        assert bm.classify("downloads/export.tar.gz") == Boundary.LOCAL

    def test_unknown_prefix_is_public(self):
        bm = BoundaryMap()
        assert bm.classify("src/main.py") == Boundary.PUBLIC
        assert bm.classify("README.md") == Boundary.PUBLIC

    def test_longest_prefix_wins(self):
        """Longer rule must override shorter rule."""
        bm = BoundaryMap(rules=[
            ("hrt_", Boundary.LOCAL),
            ("hrt_backups/special/", Boundary.ENCRYPTED),
        ])
        assert bm.classify("hrt_backups/special/file.gz") == Boundary.ENCRYPTED
        assert bm.classify("hrt_other/file.txt") == Boundary.LOCAL

    def test_add_rule(self):
        bm = BoundaryMap(rules=[])
        assert bm.classify("personal_notes/diary.md") == Boundary.PUBLIC
        bm.add_rule("personal_notes/", Boundary.LOCAL)
        assert bm.classify("personal_notes/diary.md") == Boundary.LOCAL

    def test_boundary_values_are_strings(self):
        """Boundary enum members must compare equal to their string values."""
        assert Boundary.PUBLIC == "public"
        assert Boundary.LOCAL == "local"
        assert Boundary.ENCRYPTED == "encrypted"


# ===========================================================================
# 2. PatternDetector
# ===========================================================================

class TestPatternDetector:
    def _make_files(self, tmp_path: Path, names: list[str]) -> None:
        for name in names:
            p = tmp_path / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"data")

    def test_finds_backup_files(self, tmp_path):
        self._make_files(tmp_path, [
            "hrt_backups/export.zip",
            "README.md",
        ])
        detector = PatternDetector()
        candidates = detector.find_candidates(tmp_path)
        paths = {c.path for c in candidates}
        assert "hrt_backups/export.zip" in paths
        assert "README.md" not in paths

    def test_finds_chat_jsonl(self, tmp_path):
        self._make_files(tmp_path, ["chat_session.jsonl"])
        detector = PatternDetector()
        candidates = detector.find_candidates(tmp_path)
        assert any(c.path == "chat_session.jsonl" for c in candidates)

    def test_reason_codes_are_opaque(self, tmp_path):
        """Reason codes must be short alphanumeric labels — no sensitive terms."""
        self._make_files(tmp_path, [
            "hrt_backups/x.zip",
            "chat_log.jsonl",
            "conversation_notes.txt",
            "personal_journal.md",
        ])
        detector = PatternDetector()
        candidates = detector.find_candidates(tmp_path)
        for c in candidates:
            # Reason code must be short (e.g. "R1") — no words that could
            # themselves reveal sensitive categories.
            assert len(c.reason_code) <= 4, (
                f"Reason code {c.reason_code!r} is too long (should be opaque)"
            )
            assert c.reason_code.startswith("R"), (
                f"Reason code {c.reason_code!r} must start with 'R'"
            )

    def test_each_file_reported_once(self, tmp_path):
        """A file matching multiple patterns should appear only once."""
        # A file that might match both R1 and another pattern.
        self._make_files(tmp_path, ["hrt_backup_chat.jsonl"])
        detector = PatternDetector()
        candidates = detector.find_candidates(tmp_path)
        paths = [c.path for c in candidates]
        assert len(paths) == len(set(paths)), "Duplicate candidates found"

    def test_non_matching_files_excluded(self, tmp_path):
        self._make_files(tmp_path, ["src/module.py", "tests/test_core.py"])
        detector = PatternDetector()
        candidates = detector.find_candidates(tmp_path)
        assert candidates == []

    def test_extra_patterns(self, tmp_path):
        self._make_files(tmp_path, ["my_secret_file.log"])
        detector = PatternDetector(extra_patterns=[("R9", r"secret")])
        candidates = detector.find_candidates(tmp_path)
        assert any(c.reason_code == "R9" for c in candidates)


# ===========================================================================
# 3. SensitivityClassifier
# ===========================================================================

class TestSensitivityClassifier:
    def test_known_codes_map_to_expected_actions(self):
        clf = SensitivityClassifier()
        assert clf.classify("R1") == Action.MOVE_LOCAL
        assert clf.classify("R2") == Action.MOVE_LOCAL
        assert clf.classify("R5") == Action.ENCRYPT_LOCAL

    def test_unknown_code_uses_default(self):
        clf = SensitivityClassifier(default=Action.DELETE_WITH_WITNESS)
        assert clf.classify("R99") == Action.DELETE_WITH_WITNESS

    def test_custom_action_map_overrides_default(self):
        clf = SensitivityClassifier(action_map={"R1": Action.ENCRYPT_LOCAL})
        assert clf.classify("R1") == Action.ENCRYPT_LOCAL

    def test_action_values_are_strings(self):
        assert Action.MOVE_LOCAL == "move_local"
        assert Action.ENCRYPT_LOCAL == "encrypt_local"
        assert Action.DELETE_WITH_WITNESS == "delete_with_witness"
        assert Action.KEEP_PUBLIC == "keep_public"


# ===========================================================================
# 4. HashPreserver
# ===========================================================================

class TestHashPreserver:
    def test_sha256_bytes_deterministic(self):
        data = b"hello world"
        h1 = sha256_bytes(data)
        h2 = sha256_bytes(data)
        assert h1 == h2

    def test_sha256_bytes_known_value(self):
        data = b""
        expected = hashlib.sha256(b"").hexdigest()
        assert sha256_bytes(data) == expected

    def test_sha256_bytes_different_data(self):
        assert sha256_bytes(b"a") != sha256_bytes(b"b")

    def test_sha256_file(self, tmp_path):
        f = tmp_path / "test.bin"
        f.write_bytes(b"pr47 test data")
        expected = hashlib.sha256(b"pr47 test data").hexdigest()
        assert sha256_file(f) == expected

    def test_sha256_file_empty(self, tmp_path):
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        assert sha256_file(f) == hashlib.sha256(b"").hexdigest()


# ===========================================================================
# 5. BoundaryEncryptor
# ===========================================================================

class TestBoundaryEncryptor:
    def test_self_inverse(self):
        data = b"sensitive artifact content"
        key = b"test_key_123"
        assert decrypt(encrypt(data, key), key) == data

    def test_deterministic(self):
        data = b"same data"
        key = b"same_key"
        assert encrypt(data, key) == encrypt(data, key)

    def test_different_keys_different_output(self):
        data = b"same data"
        assert encrypt(data, b"key_a") != encrypt(data, b"key_b")

    def test_empty_plaintext(self):
        assert encrypt(b"", b"any_key") == b""

    def test_ciphertext_length_equals_plaintext_length(self):
        data = b"twelve bytes"
        key = b"k"
        assert len(encrypt(data, key)) == len(data)


# ===========================================================================
# 6. WitnessMover
# ===========================================================================

class TestWitnessMover:
    def _consent_hash(self) -> str:
        return sha256_bytes(b"test_consent")

    def test_record_transition_returns_entry(self):
        mover = WitnessMover(consent_hash=self._consent_hash())
        entry = mover.record_transition(
            content_hash="abc123",
            from_path="hrt_backups/file.zip",
            to_boundary="local",
            to_path=None,
            timestamp="2026-02-24T00:00:00Z",
        )
        assert entry.operation == "boundary_transition"
        assert entry.content_hash == "abc123"
        assert entry.to_boundary == "local"
        assert entry.consent_hash == self._consent_hash()

    def test_entries_appended_in_order(self):
        mover = WitnessMover(consent_hash=self._consent_hash())
        for i in range(3):
            mover.record_transition(
                content_hash=f"hash_{i}",
                from_path=f"file_{i}.txt",
                to_boundary="local",
                to_path=None,
                timestamp="2026-02-24T00:00:00Z",
            )
        entries = mover.entries()
        assert len(entries) == 3
        assert [e.content_hash for e in entries] == ["hash_0", "hash_1", "hash_2"]

    def test_transition_entry_canonical_bytes_deterministic(self):
        mover = WitnessMover(consent_hash=self._consent_hash())
        entry = mover.record_transition(
            content_hash="deadbeef",
            from_path="chat.jsonl",
            to_boundary="local",
            to_path="/local/chat.jsonl",
            timestamp="2026-02-24T00:00:00Z",
        )
        assert entry.canonical_bytes() == entry.canonical_bytes()

    def test_transition_entry_entry_hash_stable(self):
        mover = WitnessMover(consent_hash=self._consent_hash())
        entry = mover.record_transition(
            content_hash="cafebabe",
            from_path="backup.zip",
            to_boundary="encrypted",
            to_path=None,
            timestamp="2026-02-24T00:00:00Z",
        )
        h1 = entry.entry_hash()
        h2 = entry.entry_hash()
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_entries_returns_copy(self):
        mover = WitnessMover(consent_hash=self._consent_hash())
        mover.record_transition("h", "f", "local", None, "ts")
        lst = mover.entries()
        lst.clear()
        assert len(mover.entries()) == 1


# ===========================================================================
# 7. RemovalWitness
# ===========================================================================

class TestRemovalWitness:
    def _make_witness(self) -> RemovalWitness:
        return RemovalWitness()

    def test_initial_chain_hash_is_genesis(self):
        w = self._make_witness()
        assert w.chain_hash == REMOVAL_GENESIS_HASH

    def test_record_transition_returns_entry(self):
        w = self._make_witness()
        entry = w.record_transition(
            content_hash="abc",
            reason_code="R1",
            consent_hash="consent_abc",
        )
        assert entry.content_hash == "abc"
        assert entry.reason_code == "R1"
        assert entry.witnessed_by == "pr47"

    def test_has_entry_for_hash_true(self):
        w = self._make_witness()
        w.record_transition("hash_a", "R2", "c_hash")
        assert w.has_entry_for_hash("hash_a")

    def test_has_entry_for_hash_false(self):
        w = self._make_witness()
        assert not w.has_entry_for_hash("missing")

    def test_entry_for_hash_found(self):
        w = self._make_witness()
        w.record_transition("xhash", "R3", "c_hash")
        entry = w.entry_for_hash("xhash")
        assert entry.reason_code == "R3"

    def test_entry_for_hash_missing_raises(self):
        w = self._make_witness()
        with pytest.raises(KeyError):
            w.entry_for_hash("nonexistent")

    def test_chain_hash_changes_after_append(self):
        w = self._make_witness()
        before = w.chain_hash
        w.record_transition("h1", "R1", "c1")
        assert w.chain_hash != before

    def test_verify_integrity_passes(self):
        w = self._make_witness()
        w.record_transition("h1", "R1", "c1")
        w.record_transition("h2", "R2", "c2")
        assert w.verify_integrity() is True

    def test_verify_integrity_detects_tampering(self):
        w = self._make_witness()
        w.record_transition("h1", "R1", "c1")
        # Directly corrupt the internal chain hash (simulate tampering).
        w._chain_hash = "0" * 64
        with pytest.raises(ValueError, match="integrity violation"):
            w.verify_integrity()

    def test_length(self):
        w = self._make_witness()
        assert w.length == 0
        w.record_transition("h", "R1", "c")
        assert w.length == 1

    def test_entries_returns_copy(self):
        w = self._make_witness()
        w.record_transition("h", "R1", "c")
        lst = w.entries()
        lst.clear()
        assert w.length == 1

    def test_chain_links_previous_hash(self):
        """Each entry's previous_hash must equal the prior chain_hash."""
        w = self._make_witness()
        h0 = w.chain_hash
        e1 = w.record_transition("h1", "R1", "c1")
        assert e1.previous_hash == h0
        h1 = w.chain_hash
        e2 = w.record_transition("h2", "R2", "c2")
        assert e2.previous_hash == h1


# ===========================================================================
# 8. ProvenancePointer
# ===========================================================================

class TestProvenancePointer:
    def test_create_hides_destination_path(self):
        ptr = ProvenancePointer.create(
            content_hash="deadbeef",
            boundary="local",
            destination_path="/home/user/.local/artifact.zip",
            timestamp="2026-02-24T00:00:00Z",
        )
        # location_hash must not be the raw path.
        assert ptr.location_hash != "/home/user/.local/artifact.zip"
        # location_hash is a hex SHA-256.
        assert len(ptr.location_hash) == 64

    def test_same_path_same_location_hash(self):
        ptr1 = ProvenancePointer.create("h", "local", "/path/to/file", "ts")
        ptr2 = ProvenancePointer.create("h", "local", "/path/to/file", "ts")
        assert ptr1.location_hash == ptr2.location_hash

    def test_different_paths_different_location_hash(self):
        ptr1 = ProvenancePointer.create("h", "local", "/path/a", "ts")
        ptr2 = ProvenancePointer.create("h", "local", "/path/b", "ts")
        assert ptr1.location_hash != ptr2.location_hash

    def test_pointer_hash_deterministic(self):
        ptr = ProvenancePointer.create("h", "local", "/p", "ts")
        assert ptr.pointer_hash() == ptr.pointer_hash()

    def test_canonical_bytes_deterministic(self):
        ptr = ProvenancePointer.create("h", "encrypted", "/p", "ts")
        assert ptr.canonical_bytes() == ptr.canonical_bytes()

    def test_none_destination_path_supported(self):
        ptr = ProvenancePointer.create("h", "delete_with_witness", None, "ts")
        assert ptr.location_hash == hashlib.sha256(b"").hexdigest()


# ===========================================================================
# 9. ConsentLog
# ===========================================================================

class TestConsentLog:
    def _make_record(
        self,
        scope: list[str],
        action: str = "move_local",
        timestamp: str = "2026-02-24T00:00:00Z",
    ) -> ConsentRecord:
        return ConsentRecord.create(
            authoriser="human_operator",
            scope=scope,
            action=action,
            timestamp=timestamp,
        )

    def test_has_consent_for_covered_hash(self):
        log = ConsentLog()
        record = self._make_record(["hash_a", "hash_b"])
        log.append(record)
        assert log.has_consent_for("hash_a")
        assert log.has_consent_for("hash_b")

    def test_has_consent_for_uncovered_hash(self):
        log = ConsentLog()
        assert not log.has_consent_for("hash_z")

    def test_consent_hash_for_covered(self):
        log = ConsentLog()
        record = self._make_record(["h1"])
        log.append(record)
        assert log.consent_hash_for("h1") == record.consent_hash

    def test_consent_hash_for_uncovered_raises(self):
        log = ConsentLog()
        with pytest.raises(KeyError):
            log.consent_hash_for("nonexistent")

    def test_consent_hash_deterministic(self):
        r1 = self._make_record(["h"])
        r2 = self._make_record(["h"])
        assert r1.consent_hash == r2.consent_hash

    def test_scope_sorted(self):
        """Scope must be sorted for determinism regardless of input order."""
        r = ConsentRecord.create(
            authoriser="op",
            scope=["c", "a", "b"],
            action="move_local",
            timestamp="ts",
        )
        assert r.scope == ["a", "b", "c"]

    def test_covers_method(self):
        record = self._make_record(["hash_x"])
        assert record.covers("hash_x")
        assert not record.covers("hash_y")

    def test_records_returns_copy(self):
        log = ConsentLog()
        log.append(self._make_record(["h"]))
        lst = log.records()
        lst.clear()
        assert len(log.records()) == 1


# ===========================================================================
# 10. NoSilentTransition invariant
# ===========================================================================

class TestNoSilentTransition:
    def test_passes_when_all_hashes_witnessed(self):
        w = RemovalWitness()
        w.record_transition("h1", "R1", "c1")
        w.record_transition("h2", "R2", "c2")
        assert check_no_silent_transition({"h1", "h2"}, w) is True

    def test_raises_on_missing_witness(self):
        w = RemovalWitness()
        w.record_transition("h1", "R1", "c1")
        with pytest.raises(NoSilentTransitionViolation, match="h2"):
            check_no_silent_transition({"h1", "h2"}, w)

    def test_empty_removed_set_passes(self):
        w = RemovalWitness()
        assert check_no_silent_transition(set(), w) is True


# ===========================================================================
# 11. ForkableRemembrance invariant
# ===========================================================================

class TestForkableRemembrance:
    def test_passes_when_all_entries_consented(self):
        w = RemovalWitness()
        consent_hash = sha256_bytes(b"consent")
        w.record_transition("h1", "R1", consent_hash)
        log = ConsentLog()
        log.append(
            ConsentRecord.create("op", ["h1"], "move_local", "ts")
        )
        assert check_forkable_remembrance(w, log) is True

    def test_raises_on_unconsented_entry(self):
        w = RemovalWitness()
        w.record_transition("h_unconsented", "R1", "some_consent")
        log = ConsentLog()  # empty log
        with pytest.raises(ForkableRemembranceViolation, match="h_unconsented"):
            check_forkable_remembrance(w, log)

    def test_empty_witness_always_passes(self):
        log = ConsentLog()
        assert check_forkable_remembrance(RemovalWitness(), log) is True


# ===========================================================================
# 12. NeverDrawAttention invariant
# ===========================================================================

class TestNeverDrawAttention:
    def test_clean_message_passes(self):
        assert check_commit_message("pr47: boundary adjustments per consent") is True

    def test_sanitized_trigger_raises(self):
        with pytest.raises(NeverDrawAttentionViolation):
            check_commit_message("Sanitized personal files")

    def test_cleaned_up_trigger_raises(self):
        with pytest.raises(NeverDrawAttentionViolation):
            check_commit_message("Cleaned up old exports")

    def test_removed_personal_trigger_raises(self):
        with pytest.raises(NeverDrawAttentionViolation):
            check_commit_message("Removed personal backups from repo")

    def test_purged_trigger_raises(self):
        with pytest.raises(NeverDrawAttentionViolation):
            check_commit_message("purged sensitive data")

    def test_case_insensitive(self):
        with pytest.raises(NeverDrawAttentionViolation):
            check_commit_message("SANITIZED all the things")

    def test_check_commit_messages_all_clean(self):
        messages = [
            "pr47: boundary adjustments",
            "chore: update dependencies",
            "fix: correct hash computation",
        ]
        assert check_commit_messages(messages) is True

    def test_check_commit_messages_raises_on_first_bad(self):
        messages = [
            "pr47: boundary adjustments",
            "Sanitized personal exports",
        ]
        with pytest.raises(NeverDrawAttentionViolation):
            check_commit_messages(messages)


# ===========================================================================
# 13. PR #40 feed extension
# ===========================================================================

class TestPR40FeedExtension:
    def _make_entry(self) -> dict:
        return make_feed_entry(
            timestamp="2026-02-24T00:00:00Z",
            content_hash="deadbeef",
            reason_code="R1",
            consent_hash="consent_hash_abc",
            prev_entry_hash="prev_hash_xyz",
        )

    def test_make_feed_entry_deterministic(self):
        e1 = self._make_entry()
        e2 = self._make_entry()
        assert e1 == e2

    def test_make_feed_entry_has_all_columns(self):
        entry = self._make_entry()
        for col in FEED_COLUMNS:
            assert col in entry, f"Missing column {col!r}"

    def test_make_feed_entry_event_type(self):
        entry = self._make_entry()
        assert entry["event_type"] == EVENT_TYPE

    def test_make_feed_entry_entry_hash_non_empty(self):
        entry = self._make_entry()
        assert len(entry["entry_hash"]) == 64

    def test_format_feed_row_pipe_delimited(self):
        entry = self._make_entry()
        row = format_feed_row(entry)
        assert row.startswith("| ")
        assert row.endswith(" |")
        # Number of pipe-separated segments equals number of columns.
        parts = [p.strip() for p in row.strip("|").split("|")]
        assert len(parts) == len(FEED_COLUMNS)

    def test_format_feed_header_has_separator(self):
        header = format_feed_header()
        lines = header.splitlines()
        assert len(lines) == 2
        assert "---" in lines[1]

    def test_different_content_hashes_different_entry_hashes(self):
        e1 = make_feed_entry("ts", "hash_a", "R1", "c", "prev")
        e2 = make_feed_entry("ts", "hash_b", "R1", "c", "prev")
        assert e1["entry_hash"] != e2["entry_hash"]


# ===========================================================================
# 14. PR #45 bridge
# ===========================================================================

class TestPR45Bridge:
    def _make_removal_entry(self, content_hash: str = "h1") -> RemovalEntry:
        w = RemovalWitness()
        return w.record_transition(content_hash, "R1", "consent_hash")

    def test_witness_boundary_transition_appends_to_chain(self):
        chain = WitnessChain()
        entry = self._make_removal_entry()
        we = witness_boundary_transition(chain, entry)
        assert chain.length == 1
        assert we.new_hash == entry.entry_hash()

    def test_verify_all_transitions_integrity(self):
        chain = WitnessChain()
        rw = RemovalWitness()
        entries = [
            rw.record_transition(f"h{i}", "R1", "c") for i in range(3)
        ]
        wes = verify_all_transitions(chain, entries)
        assert len(wes) == 3
        assert chain.length == 3
        assert chain.verify_integrity() is True

    def test_pr47_build_hash_stable(self):
        """The build hash must be a 64-char hex string."""
        assert len(PR47_BUILD_HASH) == 64
        assert all(c in "0123456789abcdef" for c in PR47_BUILD_HASH)

    def test_pr47_build_hash_deterministic(self):
        from pr47_stewardship.integration.pr45_verification import PR47_BUILD_HASH as h2
        assert PR47_BUILD_HASH == h2

    def test_operation_id_contains_content_hash(self):
        chain = WitnessChain()
        entry = self._make_removal_entry("my_content_hash")
        we = witness_boundary_transition(chain, entry)
        assert "my_content_hash" in we.operation_id


# ===========================================================================
# 15. End-to-end stewardship cycle
# ===========================================================================

class TestEndToEnd:
    def test_full_stewardship_cycle_no_silent_transition(self):
        """
        Simulate a complete stewardship cycle:
        1. PatternDetector identifies candidates.
        2. ConsentLog records consent.
        3. WitnessMover records transitions.
        4. RemovalWitness builds the ledger.
        5. NoSilentTransition invariant is satisfied.
        6. ForkableRemembrance invariant is satisfied.
        7. WitnessChain integrity is verified via PR #45 bridge.
        """
        # Simulate two artifacts with known content hashes.
        artifact_hashes = {
            "chat_jsonl/session1.jsonl": sha256_bytes(b"session1 content"),
            "hrt_backups/1B/export.zip": sha256_bytes(b"export content"),
        }

        # --- Consent ---
        consent_record = ConsentRecord.create(
            authoriser="human_operator",
            scope=list(artifact_hashes.values()),
            action="move_local",
            timestamp="2026-02-24T00:00:00Z",
        )
        log = ConsentLog()
        log.append(consent_record)

        # --- Record transitions ---
        mover = WitnessMover(consent_hash=consent_record.consent_hash)
        removal_witness = RemovalWitness()
        timestamp = "2026-02-24T00:01:00Z"

        for rel_path, content_hash in artifact_hashes.items():
            mover.record_transition(
                content_hash=content_hash,
                from_path=rel_path,
                to_boundary="local",
                to_path=None,
                timestamp=timestamp,
            )
            removal_witness.record_transition(
                content_hash=content_hash,
                reason_code="R1",
                consent_hash=consent_record.consent_hash,
            )

        # --- Invariants ---
        removed_hashes = set(artifact_hashes.values())
        assert check_no_silent_transition(removed_hashes, removal_witness) is True
        assert check_forkable_remembrance(removal_witness, log) is True

        # --- Commit message hygiene ---
        assert check_commit_messages(["pr47: boundary adjustments per consent"]) is True

        # --- PR #45 chain integrity ---
        chain = WitnessChain()
        wes = verify_all_transitions(chain, removal_witness.entries())
        assert len(wes) == 2
        assert chain.verify_integrity() is True

        # --- RemovalWitness ledger integrity ---
        assert removal_witness.verify_integrity() is True
