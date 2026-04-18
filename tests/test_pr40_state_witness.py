#!/usr/bin/env python3
"""
tests/test_pr40_state_witness.py — PR #40 State Witness Layer Tests

Verifies:
  1. Feed entry generation is deterministic given fixed inputs
  2. Append-only rules are enforced (no row deletion/modification)
  3. Idempotency check prevents duplicate commit_sha entries
  4. AGENT_FEED.md header and structure are correct
  5. Feed chain integrity verification works

Author: Orthogonal Engineering
PR: #40
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.state_witness.generate_feed_entry import (
    AGENT_FEED_PATH,
    FEED_HEADER,
    FREEZE_PATH,
    append_to_feed,
    build_feed_entry,
    compute_freeze_hash,
    is_duplicate,
    read_feed,
    verify_feed_integrity,
    _entry_to_row,
    _parse_feed_rows,
    _sha256,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXED_TIMESTAMP = "2026-02-23T02:00:00Z"
FIXED_COMMIT = "abc1234567890abc1234567890abc1234567890ab"
FIXED_REF = "refs/heads/main"


def _make_entry(
    *,
    timestamp: str = FIXED_TIMESTAMP,
    commit_sha: str = FIXED_COMMIT,
    git_ref: str = FIXED_REF,
    prev_entry_hash: str = "",
) -> dict:
    return build_feed_entry(
        timestamp=timestamp,
        commit_sha=commit_sha,
        git_ref=git_ref,
        prev_entry_hash=prev_entry_hash,
    )


# ---------------------------------------------------------------------------
# 1. Freeze file and hash determinism
# ---------------------------------------------------------------------------

class TestFreezeHashDeterminism:
    """freeze_hash must be stable and match the freeze file bytes."""

    def test_freeze_file_exists(self):
        assert FREEZE_PATH.exists(), f"Freeze file missing: {FREEZE_PATH}"

    def test_compute_freeze_hash_is_hex_64(self):
        h = compute_freeze_hash()
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_compute_freeze_hash_is_repeatable(self):
        h1 = compute_freeze_hash()
        h2 = compute_freeze_hash()
        assert h1 == h2

    def test_sha256_helper(self):
        result = _sha256(b"hello")
        assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


# ---------------------------------------------------------------------------
# 2. Feed entry determinism
# ---------------------------------------------------------------------------

class TestFeedEntryDeterminism:
    """Given fixed inputs, build_feed_entry must produce identical output."""

    def test_entry_has_required_fields(self):
        entry = _make_entry()
        required = {
            "timestamp", "freeze_hash", "merkle_root", "invariant_spec_version",
            "source_paths", "commit_sha", "prev_entry_hash", "entry_hash",
        }
        assert required.issubset(entry.keys()), (
            f"Missing fields: {required - entry.keys()}"
        )

    def test_entry_does_not_contain_git_ref(self):
        """git_ref must NOT appear in the entry dict — it is not a ledger column.

        INT-1 fix: ghost field removed from build_feed_entry return value to
        make the producer/consumer schema contract unambiguous.
        """
        entry = _make_entry()
        assert "git_ref" not in entry, (
            "git_ref is not part of the AGENT_FEED.md ledger schema; "
            "it must not be present in the entry dict."
        )

    def test_entry_invariant_spec_version_is_v2(self):
        entry = _make_entry()
        assert entry["invariant_spec_version"] == "v2"

    def test_entry_deterministic_given_fixed_inputs(self):
        e1 = _make_entry()
        e2 = _make_entry()
        for field in (
            "freeze_hash", "merkle_root", "invariant_spec_version",
            "source_paths", "commit_sha", "prev_entry_hash", "entry_hash",
            "timestamp",
        ):
            assert e1[field] == e2[field], (
                f"Field {field!r} is not deterministic"
            )

    def test_entry_freeze_hash_matches_computed(self):
        entry = _make_entry()
        assert entry["freeze_hash"] == compute_freeze_hash()

    def test_entry_hash_changes_with_different_commit(self):
        e1 = _make_entry(commit_sha="aaa000")
        e2 = _make_entry(commit_sha="bbb111")
        assert e1["entry_hash"] != e2["entry_hash"]

    def test_entry_hash_changes_with_different_timestamp(self):
        e1 = _make_entry(timestamp="2026-01-01T00:00:00Z")
        e2 = _make_entry(timestamp="2026-01-02T00:00:00Z")
        assert e1["entry_hash"] != e2["entry_hash"]

    def test_prev_entry_hash_chained(self):
        e1 = _make_entry(commit_sha="commit1")
        e2 = _make_entry(
            commit_sha="commit2",
            timestamp="2026-02-23T03:00:00Z",
            prev_entry_hash=e1["entry_hash"],
        )
        assert e2["prev_entry_hash"] == e1["entry_hash"]

    def test_source_paths_are_sorted(self):
        entry = _make_entry()
        paths = entry["source_paths"].split(",")
        assert paths == sorted(paths)

    def test_entry_to_row_format(self):
        entry = _make_entry()
        row = _entry_to_row(entry)
        assert row.startswith("| ")
        assert row.endswith(" |")
        # Should have 8 columns
        cells = [c.strip() for c in row.strip("|").split("|")]
        assert len(cells) == 8


# ---------------------------------------------------------------------------
# 3. Append-only enforcement and idempotency
# ---------------------------------------------------------------------------

class TestAppendOnly:
    """Append-only rules: existing rows must not be modified; duplicates skipped."""

    def test_is_duplicate_by_commit_sha(self):
        entry = _make_entry(commit_sha="dupe_commit")
        existing = [{"commit_sha": "dupe_commit", "entry_hash": "xxx"}]
        assert is_duplicate(entry, existing) is True

    def test_not_duplicate_different_commit(self):
        entry = _make_entry(commit_sha="new_commit")
        existing = [{"commit_sha": "old_commit", "entry_hash": "yyy"}]
        assert is_duplicate(entry, existing) is False

    def test_not_duplicate_unknown_commit(self):
        """Unknown commit SHA should never be treated as a duplicate."""
        entry = _make_entry(commit_sha="unknown")
        existing = [{"commit_sha": "unknown", "entry_hash": "zzz"}]
        assert is_duplicate(entry, existing) is False

    def test_not_duplicate_empty_feed(self):
        entry = _make_entry()
        assert is_duplicate(entry, []) is False

    def test_append_writes_to_file(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        entry = _make_entry()
        written = append_to_feed(entry)
        assert written is True
        content = feed_path.read_text(encoding="utf-8")
        assert entry["entry_hash"] in content
        assert entry["commit_sha"] in content

    def test_append_creates_header_if_missing(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        assert not feed_path.exists()
        entry = _make_entry()
        append_to_feed(entry)
        content = feed_path.read_text(encoding="utf-8")
        assert "AGENT_FEED" in content
        assert "timestamp" in content

    def test_idempotent_same_commit_skipped(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        entry = _make_entry(commit_sha="idempotent_commit")
        w1 = append_to_feed(entry)
        w2 = append_to_feed(entry)
        assert w1 is True
        assert w2 is False  # duplicate — skipped

        # File must have exactly one data row
        rows = _parse_feed_rows(feed_path.read_text(encoding="utf-8"))
        assert len(rows) == 1

    def test_multiple_commits_all_appended(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        prev = ""
        for i, sha in enumerate(["commit_a", "commit_b", "commit_c"]):
            ts = f"2026-02-2{i + 3}T00:00:00Z"
            entry = _make_entry(commit_sha=sha, timestamp=ts, prev_entry_hash=prev)
            assert append_to_feed(entry) is True
            prev = entry["entry_hash"]

        rows = _parse_feed_rows(feed_path.read_text(encoding="utf-8"))
        assert len(rows) == 3
        assert [r["commit_sha"] for r in rows] == ["commit_a", "commit_b", "commit_c"]

    def test_existing_rows_not_modified(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        e1 = _make_entry(commit_sha="row1")
        append_to_feed(e1)
        original_content = feed_path.read_text(encoding="utf-8")

        e2 = _make_entry(commit_sha="row2", timestamp="2026-02-24T00:00:00Z")
        append_to_feed(e2)
        updated_content = feed_path.read_text(encoding="utf-8")

        # Original content must be a prefix of updated content
        assert updated_content.startswith(original_content)


# ---------------------------------------------------------------------------
# 4. Feed parsing
# ---------------------------------------------------------------------------

class TestFeedParsing:
    """_parse_feed_rows must correctly extract rows from markdown table."""

    def test_parse_empty_table(self):
        rows = _parse_feed_rows(FEED_HEADER)
        assert rows == []

    def test_parse_one_row(self):
        entry = _make_entry()
        row_line = _entry_to_row(entry) + "\n"
        content = FEED_HEADER + row_line
        rows = _parse_feed_rows(content)
        assert len(rows) == 1
        assert rows[0]["commit_sha"] == FIXED_COMMIT
        assert rows[0]["entry_hash"] == entry["entry_hash"]

    def test_parse_two_rows(self):
        e1 = _make_entry(commit_sha="first")
        e2 = _make_entry(
            commit_sha="second",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash=e1["entry_hash"],
        )
        content = FEED_HEADER + _entry_to_row(e1) + "\n" + _entry_to_row(e2) + "\n"
        rows = _parse_feed_rows(content)
        assert len(rows) == 2
        assert rows[0]["commit_sha"] == "first"
        assert rows[1]["commit_sha"] == "second"


# ---------------------------------------------------------------------------
# 5. Feed chain integrity verification
# ---------------------------------------------------------------------------

class TestFeedChainIntegrity:
    """verify_feed_integrity must confirm the prev_entry_hash chain is intact."""

    def test_empty_feed_is_valid(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        ok, errors = verify_feed_integrity()
        assert ok is True
        assert errors == []

    def test_single_row_chain_valid(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        entry = _make_entry()
        append_to_feed(entry)
        ok, errors = verify_feed_integrity()
        assert ok is True, f"Unexpected errors: {errors}"

    def test_two_row_chain_valid(self, tmp_path, monkeypatch):
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        e1 = _make_entry(commit_sha="chain1")
        append_to_feed(e1)
        e2 = _make_entry(
            commit_sha="chain2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash=e1["entry_hash"],
        )
        append_to_feed(e2)
        ok, errors = verify_feed_integrity()
        assert ok is True, f"Unexpected errors: {errors}"

    def test_broken_chain_detected(self, tmp_path, monkeypatch):
        """Manually corrupt prev_entry_hash and expect verification to fail."""
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        e1 = _make_entry(commit_sha="good1")
        # Deliberately set wrong prev_entry_hash for e2
        e2 = _make_entry(
            commit_sha="good2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash="badhash",  # should be e1["entry_hash"]
        )
        # Write both rows directly
        feed_path.write_text(
            FEED_HEADER + _entry_to_row(e1) + "\n" + _entry_to_row(e2) + "\n",
            encoding="utf-8",
        )
        ok, errors = verify_feed_integrity()
        assert ok is False
        assert len(errors) > 0

    def test_tampered_entry_hash_detected(self, tmp_path, monkeypatch):
        """If entry_hash is tampered, verification must report an error."""
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        e1 = _make_entry(commit_sha="tamper_test")
        row = _entry_to_row(e1)
        # Replace entry_hash with garbage
        tampered_row = row.rsplit("|", 2)[0] + "| deadbeef" * 8 + " |"
        feed_path.write_text(FEED_HEADER + tampered_row + "\n", encoding="utf-8")
        ok, errors = verify_feed_integrity()
        assert ok is False


# ---------------------------------------------------------------------------
# 6. AGENT_FEED.md structural checks
# ---------------------------------------------------------------------------

class TestAgentFeedStructure:
    """Verify AGENT_FEED.md at the repo root has the correct structure."""

    def test_agent_feed_exists(self):
        assert AGENT_FEED_PATH.exists(), "AGENT_FEED.md must exist at repo root"

    def test_agent_feed_has_table_header(self):
        content = AGENT_FEED_PATH.read_text(encoding="utf-8")
        assert "| timestamp |" in content
        assert "| freeze_hash |" in content
        assert "| entry_hash |" in content

    def test_agent_feed_has_separator_row(self):
        content = AGENT_FEED_PATH.read_text(encoding="utf-8")
        assert "| --- |" in content


# ---------------------------------------------------------------------------
# 7. INT-2 — unknown commit SHA unbounded-append risk
# ---------------------------------------------------------------------------

class TestUnknownCommitSHA:
    """INT-2: 'unknown' commit SHA must not silently produce unbounded rows.

    is_duplicate() returns False for commit_sha='unknown', which means every
    run appends a new row.  The following tests document the current behaviour
    explicitly so that any future change to the policy is a deliberate choice,
    not an accident.
    """

    def test_unknown_sha_is_never_duplicate(self):
        """is_duplicate must return False for 'unknown', even if already present."""
        entry = _make_entry(commit_sha="unknown")
        existing = [{"commit_sha": "unknown", "entry_hash": "xxx"}]
        # Documented behaviour: always False so the caller can decide
        assert is_duplicate(entry, existing) is False

    def test_unknown_sha_appends_multiple_rows(self, tmp_path, monkeypatch):
        """Two consecutive unknown-SHA runs must produce two distinct rows.

        This test documents the risk: in a broken CI environment where the git
        command fails, every push will add an unverifiable row.  Operators must
        monitor for this condition (OBS-3: monotonic row count check).
        """
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        e1 = _make_entry(commit_sha="unknown", timestamp="2026-01-01T00:00:00Z")
        e2 = _make_entry(commit_sha="unknown", timestamp="2026-01-01T01:00:00Z")
        assert append_to_feed(e1) is True
        assert append_to_feed(e2) is True
        rows = _parse_feed_rows(feed_path.read_text(encoding="utf-8"))
        assert len(rows) == 2
        # Both rows have 'unknown' as commit_sha
        assert all(r["commit_sha"] == "unknown" for r in rows)
        # But their entry_hashes differ because timestamps differ
        assert rows[0]["entry_hash"] != rows[1]["entry_hash"]

    def test_empty_commit_sha_also_appends(self, tmp_path, monkeypatch):
        """Empty string commit_sha behaves like 'unknown' — always appended."""
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        e1 = _make_entry(commit_sha="", timestamp="2026-01-01T00:00:00Z")
        e2 = _make_entry(commit_sha="", timestamp="2026-01-01T01:00:00Z")
        assert append_to_feed(e1) is True
        assert append_to_feed(e2) is True
        rows = _parse_feed_rows(feed_path.read_text(encoding="utf-8"))
        assert len(rows) == 2


# ---------------------------------------------------------------------------
# 8. P2 — mass-bootstrap scenario
# ---------------------------------------------------------------------------

class TestMassBootstrap:
    """P2/E12: feed initialised with N pre-existing rows accepts row N+1 correctly.

    This is the scenario that occurred with commit a27ff75 (7983-file bootstrap
    commit).  The AGENT_FEED.md shipped 183 pre-existing rows and the automated
    follow-up commit c378837 appended row 184 referencing a27ff75.
    """

    def test_bootstrap_with_prefilled_feed(self, tmp_path, monkeypatch):
        """Feed pre-populated with N rows must correctly accept row N+1."""
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        # Build 5 pre-existing rows (simulates historical import)
        prev = ""
        historical_shas = [f"histsha{i:040d}" for i in range(5)]
        content = FEED_HEADER
        for i, sha in enumerate(historical_shas):
            ts = f"2026-01-{i + 1:02d}T00:00:00Z"
            entry = _make_entry(
                commit_sha=sha,
                timestamp=ts,
                prev_entry_hash=prev,
            )
            content += _entry_to_row(entry) + "\n"
            prev = entry["entry_hash"]
        feed_path.write_text(content, encoding="utf-8")

        # Verify the pre-populated chain is intact
        ok, errors = verify_feed_integrity()
        assert ok is True, f"Pre-populated chain invalid: {errors}"

        # Now simulate the automated bot appending the bootstrap commit's row
        bootstrap_sha = "a27ff75ab7ab3f7cb0aac1ce745db40c33200401"
        existing_rows = read_feed()
        new_prev = existing_rows[-1]["entry_hash"]
        new_entry = _make_entry(
            commit_sha=bootstrap_sha,
            timestamp="2026-04-17T19:10:11Z",
            prev_entry_hash=new_prev,
        )
        written = append_to_feed(new_entry)
        assert written is True

        # Chain must remain intact after the append
        ok, errors = verify_feed_integrity()
        assert ok is True, f"Chain broken after bootstrap append: {errors}"

        # Total row count must be N+1
        rows = read_feed()
        assert len(rows) == len(historical_shas) + 1
        assert rows[-1]["commit_sha"] == bootstrap_sha

    def test_bootstrap_commit_not_duplicated(self, tmp_path, monkeypatch):
        """Appending the bootstrap commit twice must produce exactly one row."""
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        bootstrap_sha = "a27ff75ab7ab3f7cb0aac1ce745db40c33200401"
        e = _make_entry(
            commit_sha=bootstrap_sha,
            timestamp="2026-04-17T19:10:11Z",
        )
        w1 = append_to_feed(e)
        w2 = append_to_feed(e)
        assert w1 is True
        assert w2 is False  # idempotent: duplicate skipped
        rows = read_feed()
        assert len(rows) == 1

    def test_genesis_row_has_empty_prev_entry_hash(self, tmp_path, monkeypatch):
        """Genesis row (row 0 / S(0)) must have prev_entry_hash == "".

        INT-3: empty string is the valid Peano S(0) sentinel.
        """
        feed_path = tmp_path / "AGENT_FEED.md"
        monkeypatch.setattr(
            "tools.state_witness.generate_feed_entry.AGENT_FEED_PATH",
            feed_path,
        )
        e = _make_entry(commit_sha="genesis_commit", prev_entry_hash="")
        append_to_feed(e)
        rows = _parse_feed_rows(feed_path.read_text(encoding="utf-8"))
        assert len(rows) == 1
        assert rows[0]["prev_entry_hash"] == "", (
            "Genesis row prev_entry_hash must be empty string (S(0) sentinel)"
        )
