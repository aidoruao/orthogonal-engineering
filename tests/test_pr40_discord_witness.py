#!/usr/bin/env python3
"""
tests/test_pr40_discord_witness.py — PR #40 Discord Derivative Witness Tests

Verifies:
  1. Feed parsing (parse_feed_rows) handles empty and populated tables
  2. verify_entry_hash correctly validates and detects tampering
  3. verify_chain correctly walks the chain and detects breaks
  4. compute_speech produces deterministic output for fixed inputs
  5. Kenotic behavior: bot silences itself on chain errors
  6. social/endpoints.json schema is valid

No third-party dependencies.

Author: Orthogonal Engineering
PR: #40 extension (Discord Derivative Witness Layer)
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

from tools.discord_witness.bot import (
    _sha256,
    compute_speech,
    parse_feed_rows,
    verify_chain,
    verify_entry_hash,
)
from tools.state_witness.generate_feed_entry import (
    AGENT_FEED_PATH,
    FEED_HEADER,
    _entry_to_row,
    build_feed_entry,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FIXED_TS = "2026-02-23T02:00:00Z"
FIXED_COMMIT = "abc123def456abc123def456abc123def456abc1"
FIXED_REF = "refs/heads/main"


def _make_entry(
    *,
    timestamp: str = FIXED_TS,
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


def _build_feed(entries: list[dict]) -> str:
    rows = "\n".join(_entry_to_row(e) for e in entries)
    return FEED_HEADER + rows + ("\n" if rows else "")


# ---------------------------------------------------------------------------
# 1. Feed parsing
# ---------------------------------------------------------------------------

class TestParseFeedRows:
    def test_empty_table_returns_no_rows(self):
        rows = parse_feed_rows(FEED_HEADER)
        assert rows == []

    def test_single_entry_parsed(self):
        entry = _make_entry()
        content = _build_feed([entry])
        rows = parse_feed_rows(content)
        assert len(rows) == 1
        assert rows[0]["commit_sha"] == FIXED_COMMIT
        assert rows[0]["entry_hash"] == entry["entry_hash"]

    def test_two_entries_parsed_in_order(self):
        e1 = _make_entry(commit_sha="first1")
        e2 = _make_entry(
            commit_sha="second2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash=e1["entry_hash"],
        )
        rows = parse_feed_rows(_build_feed([e1, e2]))
        assert len(rows) == 2
        assert rows[0]["commit_sha"] == "first1"
        assert rows[1]["commit_sha"] == "second2"

    def test_non_table_lines_ignored(self):
        extra = "Some preamble text\n\nAnother paragraph.\n"
        rows = parse_feed_rows(extra + FEED_HEADER)
        assert rows == []


# ---------------------------------------------------------------------------
# 2. Entry hash verification
# ---------------------------------------------------------------------------

class TestVerifyEntryHash:
    def test_valid_entry_passes(self):
        entry = _make_entry()
        assert verify_entry_hash(entry) is True

    def test_tampered_entry_hash_fails(self):
        entry = _make_entry()
        entry["entry_hash"] = "deadbeef" * 8
        assert verify_entry_hash(entry) is False

    def test_tampered_commit_sha_fails(self):
        entry = _make_entry()
        entry["commit_sha"] = "tampered"
        # entry_hash was computed from original commit_sha — so now mismatches
        assert verify_entry_hash(entry) is False

    def test_empty_entry_passes_trivially(self):
        # An empty dict has computable payload — just checks internal consistency
        # Payload has 7 fields: timestamp, freeze_hash, merkle_root,
        # invariant_spec_version, source_paths, commit_sha, prev_entry_hash
        payload = "|".join([""] * 7)
        expected = _sha256(payload.encode("utf-8"))
        entry = {
            "timestamp": "", "freeze_hash": "", "merkle_root": "",
            "invariant_spec_version": "", "source_paths": "", "commit_sha": "",
            "prev_entry_hash": "", "entry_hash": expected,
        }
        assert verify_entry_hash(entry) is True


# ---------------------------------------------------------------------------
# 3. Chain verification
# ---------------------------------------------------------------------------

class TestVerifyChain:
    def test_empty_chain_is_valid(self):
        ok, errors = verify_chain([])
        assert ok is True
        assert errors == []

    def test_single_valid_entry(self):
        entry = _make_entry()
        ok, errors = verify_chain([entry])
        assert ok is True
        assert errors == []

    def test_two_linked_entries_valid(self):
        e1 = _make_entry(commit_sha="chain1")
        e2 = _make_entry(
            commit_sha="chain2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash=e1["entry_hash"],
        )
        ok, errors = verify_chain([e1, e2])
        assert ok is True

    def test_broken_prev_hash_detected(self):
        e1 = _make_entry(commit_sha="good1")
        e2 = _make_entry(
            commit_sha="good2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash="wronghash",  # should be e1["entry_hash"]
        )
        ok, errors = verify_chain([e1, e2])
        assert ok is False
        assert any("prev_entry_hash" in err for err in errors)

    def test_tampered_entry_hash_detected_in_chain(self):
        e1 = _make_entry(commit_sha="tamper1")
        tampered = dict(e1)
        tampered["entry_hash"] = "badhash"
        ok, errors = verify_chain([tampered])
        assert ok is False
        assert any("entry_hash" in err for err in errors)

    def test_three_valid_entries(self):
        e1 = _make_entry(commit_sha="c1")
        e2 = _make_entry(
            commit_sha="c2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash=e1["entry_hash"],
        )
        e3 = _make_entry(
            commit_sha="c3",
            timestamp="2026-02-25T00:00:00Z",
            prev_entry_hash=e2["entry_hash"],
        )
        ok, errors = verify_chain([e1, e2, e3])
        assert ok is True


# ---------------------------------------------------------------------------
# 4. Deterministic speech computation
# ---------------------------------------------------------------------------

class TestComputeSpeech:
    def test_speech_deterministic_for_same_entry(self):
        entry = _make_entry()
        s1 = compute_speech(entry)
        s2 = compute_speech(entry)
        assert s1 == s2

    def test_speech_contains_timestamp(self):
        entry = _make_entry()
        speech = compute_speech(entry)
        assert FIXED_TS in speech

    def test_speech_contains_short_commit(self):
        entry = _make_entry()
        speech = compute_speech(entry)
        assert FIXED_COMMIT[:8] in speech

    def test_speech_contains_freeze_hash_prefix(self):
        entry = _make_entry()
        speech = compute_speech(entry)
        assert entry["freeze_hash"][:16] in speech

    def test_speech_contains_verify_link(self):
        entry = _make_entry()
        speech = compute_speech(entry)
        assert "AGENT_FEED.md" in speech

    def test_speech_changes_for_different_entry(self):
        e1 = _make_entry(commit_sha="aaa000")
        e2 = _make_entry(commit_sha="bbb111", timestamp="2026-03-01T00:00:00Z")
        assert compute_speech(e1) != compute_speech(e2)

    def test_speech_is_string(self):
        entry = _make_entry()
        speech = compute_speech(entry)
        assert isinstance(speech, str)
        assert len(speech) > 0


# ---------------------------------------------------------------------------
# 5. Kenotic behavior (bot silences on chain errors)
# ---------------------------------------------------------------------------

class TestKenoticBehavior:
    """verify_chain returning False must prevent speech."""

    def test_chain_error_means_no_speech(self):
        """Simulate the bot's main loop: on chain error, return None."""
        e1 = _make_entry(commit_sha="ok1")
        bad = _make_entry(
            commit_sha="bad2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash="wronghash",
        )
        rows = [e1, bad]
        ok, _ = verify_chain(rows)
        speech = compute_speech(rows[-1]) if ok else None
        assert speech is None  # bot is silent

    def test_valid_chain_produces_speech(self):
        e1 = _make_entry(commit_sha="valid1")
        e2 = _make_entry(
            commit_sha="valid2",
            timestamp="2026-02-24T00:00:00Z",
            prev_entry_hash=e1["entry_hash"],
        )
        rows = [e1, e2]
        ok, _ = verify_chain(rows)
        speech = compute_speech(rows[-1]) if ok else None
        assert speech is not None
        assert "valid2"[:8] in speech


# ---------------------------------------------------------------------------
# 6. social/endpoints.json schema
# ---------------------------------------------------------------------------

class TestEndpointsJson:
    ENDPOINTS_PATH = REPO_ROOT / "social" / "endpoints.json"

    def test_endpoints_file_exists(self):
        assert self.ENDPOINTS_PATH.exists()

    def test_endpoints_is_valid_json(self):
        data = json.loads(self.ENDPOINTS_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_endpoints_has_required_fields(self):
        data = json.loads(self.ENDPOINTS_PATH.read_text(encoding="utf-8"))
        assert "schema_version" in data
        assert "pr" in data
        assert "standard" in data
        assert "endpoints" in data
        assert "canonical_sources" in data

    def test_endpoints_discord_is_derivative_witness(self):
        data = json.loads(self.ENDPOINTS_PATH.read_text(encoding="utf-8"))
        discord = data["endpoints"]["discord"]
        assert discord["mode"] == "stateless_derivative_witness"
        assert discord["verification_required"] is True
        assert discord["speech_policy"]["deterministic"] is True
        assert discord["speech_policy"]["interactive"] is False

    def test_endpoints_no_state_mutation(self):
        data = json.loads(self.ENDPOINTS_PATH.read_text(encoding="utf-8"))
        assert data["policy"]["state_mutation"] is False
        assert data["policy"]["engagement_tracking"] is False
        assert data["policy"]["metrics_collection"] is False

    def test_endpoints_canonical_sources_include_feed(self):
        data = json.loads(self.ENDPOINTS_PATH.read_text(encoding="utf-8"))
        paths = [s["path"] for s in data["canonical_sources"]]
        assert "AGENT_FEED.md" in paths
        assert "resilience/invariant_spec_v2.freeze" in paths
