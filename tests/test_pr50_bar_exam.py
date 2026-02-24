#!/usr/bin/env python3
"""
tests/test_pr50_bar_exam.py — Unit tests for PR #50 Bar Exam

Covers:
  1. Candidate: attestation, keypair, sponsor, environment
  2. Examination: templates, question bank, minimal pairs, parsing
  3. Scoring: Peano, weights, thresholds, rubric, consistency, score_attempt
  4. Privileges: capability matrix, consent bridge, enforcement
  5. Witness: chain, append, verify (using temp dirs)
  6. Ordination: certificate issuance, signing, verification
  7. Revocation: triggers, authority, effects, events, restore
  8. Invariants: forkable, deterministic, retake, append-only, glass box
  9. Schema: JSON schema validation for all response types
  10. Integration: full exam -> score -> certificate flow

Author: Orthogonal Engineering
PR: #50
Standard: Bar Exam / Ordination
Version: 50.0.0
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from pr50_bar_exam.candidate.attestation_oidc import (
    OIDC_ENV_VARS,
    canonicalize_claims,
    claims_hash,
    extract_oidc_claims,
    get_actor,
    is_ci,
)
from pr50_bar_exam.candidate.keypair import (
    canonical_transcript_hash,
    generate_dev_key,
    sign_transcript,
    verify_signature,
)
from pr50_bar_exam.candidate.sponsor import (
    DEFAULT_POLICY,
    is_approved_sponsor,
    is_sponsor_required,
    load_policy,
    validate_sponsor,
)
from pr50_bar_exam.candidate.environment import (
    SCORING_VERSION,
    SEED_POLICY,
    capture_environment,
    canonicalize_environment,
    environment_hash,
)
from pr50_bar_exam.examination.prompts.templates import (
    PROMPT_TEMPLATES,
    get_template,
    promptset_hash,
)
from pr50_bar_exam.examination.question_bank import (
    QUESTIONS,
    bank_hash,
    get_question,
    question_hash,
)
from pr50_bar_exam.examination.minimal_pairs import (
    MINIMAL_PAIRS,
    check_no_label_leakage,
    get_pair,
)
from pr50_bar_exam.examination.parsing import (
    load_schema,
    parse_response,
    parse_strict_json,
    validate_against_schema,
)
from pr50_bar_exam.examination.run_exam import build_stub_response, run_exam
from pr50_bar_exam.scoring.peano import (
    Peano,
    _int_to_peano_str,
    _parse_peano_str,
    conversion_proof,
)
from pr50_bar_exam.scoring.weights import CATEGORY_WEIGHTS, validate_weights
from pr50_bar_exam.scoring.thresholds import (
    CATEGORY_MINIMUMS,
    PASS_THRESHOLD,
    is_pass,
)
from pr50_bar_exam.scoring.rubric import (
    BOUNDARY_SCORE_MAP,
    GRACE_SCORE_MAP,
    score_boundary_response,
    score_grace_response,
    score_response,
    score_threat_response,
    score_transcript,
)
from pr50_bar_exam.scoring.consistency import (
    check_boundary_consistency,
    check_confidence_range,
    check_grace_consistency,
    check_required_fields,
    check_response_consistency,
    check_threat_consistency,
)
from pr50_bar_exam.scoring.score_attempt import canonical_bytes, score_attempt
from pr50_bar_exam.privileges.consent_bridge import (
    REQUIRED_CONSENT_FIELDS,
    consent_covers_action,
    validate_consent_artifact,
)
from pr50_bar_exam.privileges.enforcement import (
    get_allowed_capabilities_for_path,
    get_capability_info,
    is_action_allowed,
    load_capability_matrix,
)
from pr50_bar_exam.witness.chain import (
    canonical_bytes as chain_canonical_bytes,
    entry_hash,
    get_chain_head_hash,
    list_entry_ids,
    load_genesis,
)
from pr50_bar_exam.witness.append import append_entry
from pr50_bar_exam.witness.verify import verify_chain, verify_genesis
from pr50_bar_exam.ordination.certificate import CAPABILITIES_ON_PASS, issue_certificate
from pr50_bar_exam.ordination.signing_repo_key import (
    DEV_KEY_DEFAULT,
    make_signing_fn,
    make_verify_fn,
)
from pr50_bar_exam.ordination.verify_certificate import verify_certificate
from pr50_bar_exam.revocation.triggers import (
    REVOCATION_TRIGGERS,
    get_required_evidence,
    is_valid_trigger,
    validate_trigger_evidence,
)
from pr50_bar_exam.revocation.authority import (
    DEFAULT_AUTHORITY_CONFIG,
    can_restore,
    can_revoke,
    load_authority_config,
)
from pr50_bar_exam.revocation.effects import (
    CAPABILITIES_KEPT_ON_REVOCATION,
    CAPABILITIES_REMOVED_ON_REVOCATION,
    PAST_ACTIONS_STAND,
    apply_restoration_effects,
    apply_revocation_effects,
)
from pr50_bar_exam.revocation.events import create_revocation_event
from pr50_bar_exam.revocation.restore import create_restoration_event
from pr50_bar_exam.invariants.forkable import (
    assert_offline_capable,
    check_no_network_calls_in_verify,
)
from pr50_bar_exam.invariants.deterministic_verification import verify_determinism
from pr50_bar_exam.invariants.no_retake_without_period import (
    DEFAULT_COOLDOWN_DAYS,
    check_retake_allowed,
)
from pr50_bar_exam.invariants.append_only_witness import assert_chain_integrity
from pr50_bar_exam.invariants.glass_box import assert_no_hidden_state, get_state_manifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_genesis(tmp_path: Path) -> Path:
    """Create a valid genesis.json in tmp_path."""
    data = {
        "block_type": "genesis",
        "description": "Test genesis block",
        "version": "test",
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    h = hashlib.sha256(canonical).hexdigest()
    data["hash"] = h
    genesis_path = tmp_path / "genesis.json"
    genesis_path.write_text(json.dumps(data, sort_keys=True, indent=2), encoding="utf-8")
    return genesis_path


def _make_entries_dir(tmp_path: Path) -> Path:
    """Create an empty entries directory in tmp_path."""
    entries = tmp_path / "entries"
    entries.mkdir(exist_ok=True)
    return entries


def _make_pass_score(candidate_id: str = "alice", attempt_id: str = "") -> Dict[str, Any]:
    """Build a minimal passing score dict."""
    aid = attempt_id or str(uuid.uuid4())
    th = "a" * 64
    score_obj = {
        "attempt_id": aid,
        "candidate_id": candidate_id,
        "transcript_hash": th,
        "overall_score": 0.80,
        "score_percentage": 80,
        "peano_representation": _int_to_peano_str(80),
        "category_scores": {"boundary": 0.80, "threat": 0.80, "grace": 0.80},
        "passed": True,
    }
    score_hash = hashlib.sha256(canonical_bytes(score_obj)).hexdigest()
    score_obj["score_hash"] = score_hash
    return score_obj


def _make_cert(tmp_path: Path, candidate_id: str = "alice") -> tuple:
    """Create a certificate using a temp witness chain. Returns (cert, signing_key, entries_dir, genesis_path)."""
    genesis_path = _make_genesis(tmp_path)
    entries_dir = _make_entries_dir(tmp_path)
    key = DEV_KEY_DEFAULT
    sign_fn = make_signing_fn(key)
    score = _make_pass_score(candidate_id)
    cert = issue_certificate(score, sign_fn, entries_dir, genesis_path)
    return cert, key, entries_dir, genesis_path


# ---------------------------------------------------------------------------
# 1. candidate/attestation_oidc
# ---------------------------------------------------------------------------

class TestAttestationOidc:
    def test_is_ci_false_when_not_set(self, monkeypatch):
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        assert is_ci() is False

    def test_is_ci_true_when_set(self, monkeypatch):
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        assert is_ci() is True

    def test_extract_oidc_claims_none_when_not_ci(self, monkeypatch):
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        assert extract_oidc_claims() is None

    def test_extract_oidc_claims_in_ci(self, monkeypatch):
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        monkeypatch.setenv("GITHUB_ACTOR", "testuser")
        claims = extract_oidc_claims()
        assert claims is not None
        assert claims["GITHUB_ACTOR"] == "testuser"

    def test_canonicalize_claims_sorted(self):
        claims = {"B": "2", "A": "1"}
        b = canonicalize_claims(claims)
        assert b == b'{"A":"1","B":"2"}'

    def test_claims_hash_is_sha256(self):
        claims = {"GITHUB_ACTOR": "alice"}
        h = claims_hash(claims)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_claims_hash_deterministic(self):
        claims = {"GITHUB_ACTOR": "alice", "GITHUB_REPOSITORY": "org/repo"}
        assert claims_hash(claims) == claims_hash(claims)

    def test_get_actor_none_outside_ci(self, monkeypatch):
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        assert get_actor() is None

    def test_get_actor_in_ci(self, monkeypatch):
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        monkeypatch.setenv("GITHUB_ACTOR", "bob")
        assert get_actor() == "bob"

    def test_oidc_env_vars_list_not_empty(self):
        assert len(OIDC_ENV_VARS) > 0


# ---------------------------------------------------------------------------
# 2. candidate/keypair
# ---------------------------------------------------------------------------

class TestKeypair:
    def test_generate_dev_key_length(self):
        key = generate_dev_key()
        assert len(key) == 64  # 32 bytes hex

    def test_generate_dev_key_unique(self):
        assert generate_dev_key() != generate_dev_key()

    def test_sign_transcript_deterministic(self):
        key = "aa" * 32
        sig1 = sign_transcript("abc123", key)
        sig2 = sign_transcript("abc123", key)
        assert sig1 == sig2

    def test_verify_signature_valid(self):
        key = generate_dev_key()
        sig = sign_transcript("myhash", key)
        assert verify_signature("myhash", sig, key) is True

    def test_verify_signature_wrong_hash(self):
        key = generate_dev_key()
        sig = sign_transcript("myhash", key)
        assert verify_signature("wronghash", sig, key) is False

    def test_verify_signature_wrong_key(self):
        key1 = generate_dev_key()
        key2 = generate_dev_key()
        sig = sign_transcript("myhash", key1)
        assert verify_signature("myhash", sig, key2) is False

    def test_verify_signature_bad_sig(self):
        key = generate_dev_key()
        assert verify_signature("myhash", "badsig", key) is False

    def test_canonical_transcript_hash_excludes_hash_field(self):
        t = {"a": 1, "transcript_hash": "shouldbeskipped"}
        h = canonical_transcript_hash(t)
        t2 = {"a": 1}
        h2 = canonical_transcript_hash(t2)
        assert h == h2

    def test_canonical_transcript_hash_excludes_signature(self):
        t = {"a": 1, "candidate_signature": "sig"}
        h = canonical_transcript_hash(t)
        t2 = {"a": 1}
        h2 = canonical_transcript_hash(t2)
        assert h == h2


# ---------------------------------------------------------------------------
# 3. candidate/sponsor
# ---------------------------------------------------------------------------

class TestSponsor:
    def test_default_policy_no_sponsor_required(self):
        assert is_sponsor_required(DEFAULT_POLICY) is False

    def test_load_policy_fallback_default(self):
        p = load_policy(None)
        assert p["require_sponsor"] is False

    def test_is_approved_sponsor_no_require_empty_list(self):
        policy = {"require_sponsor": False, "allowed_sponsors": []}
        assert is_approved_sponsor("anyone", policy) is True

    def test_is_approved_sponsor_in_list(self):
        policy = {"require_sponsor": True, "allowed_sponsors": ["alice"]}
        assert is_approved_sponsor("alice", policy) is True

    def test_is_approved_sponsor_not_in_list(self):
        policy = {"require_sponsor": True, "allowed_sponsors": ["alice"]}
        assert is_approved_sponsor("bob", policy) is False

    def test_validate_sponsor_not_required(self):
        violations = validate_sponsor(None, DEFAULT_POLICY)
        assert violations == []

    def test_validate_sponsor_required_missing(self):
        policy = {"require_sponsor": True, "allowed_sponsors": []}
        violations = validate_sponsor(None, policy)
        assert len(violations) > 0

    def test_validate_sponsor_required_valid(self):
        policy = {"require_sponsor": True, "allowed_sponsors": ["alice"]}
        violations = validate_sponsor("alice", policy)
        assert violations == []

    def test_validate_sponsor_required_invalid(self):
        policy = {"require_sponsor": True, "allowed_sponsors": ["alice"]}
        violations = validate_sponsor("bob", policy)
        assert len(violations) > 0

    def test_load_policy_from_file(self, tmp_path):
        config = {"require_sponsor": True, "allowed_sponsors": ["bob"]}
        p = tmp_path / "sponsor.json"
        p.write_text(json.dumps(config))
        policy = load_policy(p)
        assert policy["require_sponsor"] is True
        assert "bob" in policy["allowed_sponsors"]


# ---------------------------------------------------------------------------
# 4. candidate/environment
# ---------------------------------------------------------------------------

class TestEnvironment:
    def test_capture_environment_contains_keys(self):
        env = capture_environment("abc123")
        assert "python_version" in env
        assert "platform" in env
        assert "scoring_version" in env
        assert "promptset_hash" in env
        assert "seed_policy" in env

    def test_capture_environment_scoring_version(self):
        env = capture_environment("x")
        assert env["scoring_version"] == SCORING_VERSION

    def test_capture_environment_seed_policy(self):
        env = capture_environment("x")
        assert env["seed_policy"] == SEED_POLICY

    def test_environment_hash_is_sha256(self):
        env = capture_environment("abc")
        h = environment_hash(env)
        assert len(h) == 64

    def test_environment_hash_deterministic(self):
        env = capture_environment("abc")
        assert environment_hash(env) == environment_hash(env)

    def test_canonicalize_environment_sorted_keys(self):
        env = {"b": 2, "a": 1}
        b = canonicalize_environment(env)
        assert b.index(b"a") < b.index(b"b")


# ---------------------------------------------------------------------------
# 5. examination/prompts/templates
# ---------------------------------------------------------------------------

class TestPromptTemplates:
    def test_prompt_templates_not_empty(self):
        assert len(PROMPT_TEMPLATES) >= 3

    def test_get_template_boundary(self):
        t = get_template("BOUNDARY-001")
        assert t["category"] == "boundary"

    def test_get_template_threat(self):
        t = get_template("THREAT-001")
        assert t["category"] == "threat"

    def test_get_template_grace(self):
        t = get_template("GRACE-001")
        assert t["category"] == "grace"

    def test_get_template_missing_raises(self):
        with pytest.raises(KeyError):
            get_template("NONEXISTENT")

    def test_promptset_hash_is_sha256(self):
        h = promptset_hash()
        assert len(h) == 64

    def test_promptset_hash_deterministic(self):
        assert promptset_hash() == promptset_hash()

    def test_promptset_hash_changes_with_templates(self):
        h1 = promptset_hash(PROMPT_TEMPLATES)
        modified = PROMPT_TEMPLATES + [{"variant_id": "X", "category": "x", "template": "t", "variables": []}]
        h2 = promptset_hash(modified)
        assert h1 != h2

    def test_each_template_has_required_fields(self):
        for t in PROMPT_TEMPLATES:
            assert "variant_id" in t
            assert "category" in t
            assert "template" in t
            assert "variables" in t


# ---------------------------------------------------------------------------
# 6. examination/question_bank
# ---------------------------------------------------------------------------

class TestQuestionBank:
    def test_questions_not_empty(self):
        assert len(QUESTIONS) >= 5

    def test_get_question_by_id(self):
        q = get_question("Q-BOUNDARY-001")
        assert q["category"] == "boundary"

    def test_get_question_missing_raises(self):
        with pytest.raises(KeyError):
            get_question("Q-NOTEXIST")

    def test_question_hash_is_sha256(self):
        q = QUESTIONS[0]
        h = question_hash(q)
        assert len(h) == 64

    def test_bank_hash_is_sha256(self):
        h = bank_hash()
        assert len(h) == 64

    def test_bank_hash_deterministic(self):
        assert bank_hash() == bank_hash()

    def test_all_questions_have_required_fields(self):
        for q in QUESTIONS:
            assert "question_id" in q
            assert "category" in q
            assert "expected_answer" in q

    def test_question_categories_are_known(self):
        known = {"boundary", "threat", "grace"}
        for q in QUESTIONS:
            assert q["category"] in known


# ---------------------------------------------------------------------------
# 7. examination/minimal_pairs
# ---------------------------------------------------------------------------

class TestMinimalPairs:
    def test_minimal_pairs_not_empty(self):
        assert len(MINIMAL_PAIRS) >= 3

    def test_get_pair_by_id(self):
        p = get_pair("MP-BOUNDARY-001")
        assert "question_a" in p

    def test_get_pair_missing_raises(self):
        with pytest.raises(KeyError):
            get_pair("MP-NOTEXIST")

    def test_check_no_label_leakage_valid(self):
        p = get_pair("MP-BOUNDARY-001")
        assert check_no_label_leakage(p) is True

    def test_check_no_label_leakage_threat(self):
        p = get_pair("MP-THREAT-001")
        assert check_no_label_leakage(p) is True

    def test_check_no_label_leakage_grace(self):
        p = get_pair("MP-GRACE-001")
        assert check_no_label_leakage(p) is True

    def test_all_pairs_well_formed(self):
        for p in MINIMAL_PAIRS:
            assert "pair_id" in p
            assert "question_a" in p
            assert "question_b" in p
            assert "differing_feature" in p


# ---------------------------------------------------------------------------
# 8. examination/parsing
# ---------------------------------------------------------------------------

class TestParsing:
    def test_parse_strict_json_valid(self):
        parsed, err = parse_strict_json('{"a": 1}')
        assert parsed == {"a": 1}
        assert err is None

    def test_parse_strict_json_empty(self):
        parsed, err = parse_strict_json("")
        assert parsed is None
        assert "empty" in err

    def test_parse_strict_json_not_object(self):
        parsed, err = parse_strict_json('"string"')
        assert parsed is None
        assert err is not None

    def test_parse_strict_json_invalid(self):
        parsed, err = parse_strict_json("{invalid}")
        assert parsed is None
        assert "JSON decode error" in err

    def test_parse_strict_json_array_rejected(self):
        parsed, err = parse_strict_json("[1, 2, 3]")
        assert parsed is None

    def test_load_schema_boundary(self):
        schema = load_schema("boundary_response")
        assert schema["$id"] == "boundary_response"

    def test_load_schema_threat(self):
        schema = load_schema("threat_response")
        assert schema["$id"] == "threat_response"

    def test_load_schema_grace(self):
        schema = load_schema("grace_response")
        assert schema["$id"] == "grace_response"

    def test_validate_against_schema_valid_boundary(self):
        data = {"question_id": "Q1", "answer": "DENY", "confidence": 0.9}
        err = validate_against_schema(data, "boundary_response")
        assert err is None

    def test_validate_against_schema_invalid_boundary(self):
        data = {"question_id": "Q1", "answer": "INVALID"}
        err = validate_against_schema(data, "boundary_response")
        assert err is not None

    def test_parse_response_valid(self):
        raw = json.dumps({"question_id": "Q1", "answer": "ALLOW", "confidence": 0.8})
        parsed, err = parse_response(raw, "boundary_response")
        assert parsed is not None
        assert err is None

    def test_parse_response_invalid_json(self):
        parsed, err = parse_response("not json", "boundary_response")
        assert parsed is None


# ---------------------------------------------------------------------------
# 9. examination/run_exam
# ---------------------------------------------------------------------------

class TestRunExam:
    def test_build_stub_boundary(self):
        q = {"category": "boundary", "question_id": "Q1"}
        r = build_stub_response(q)
        assert r["answer"] in ("ALLOW", "DENY", "ESCALATE")

    def test_build_stub_threat(self):
        q = {"category": "threat", "question_id": "Q1"}
        r = build_stub_response(q)
        assert "threat_category" in r
        assert "mitigations" in r

    def test_build_stub_grace(self):
        q = {"category": "grace", "question_id": "Q1"}
        r = build_stub_response(q)
        assert "decision" in r

    def test_run_exam_returns_transcript(self):
        t = run_exam("alice")
        assert "attempt_id" in t
        assert "transcript_hash" in t
        assert t["candidate_id"] == "alice"

    def test_run_exam_transcript_hash_valid(self):
        t = run_exam("alice")
        assert len(t["transcript_hash"]) == 64

    def test_run_exam_with_key(self):
        key = generate_dev_key()
        t = run_exam("alice", secret_key=key)
        assert "candidate_signature" in t

    def test_run_exam_with_sponsor(self):
        t = run_exam("alice", sponsor_id="bob")
        assert t["sponsor_id"] == "bob"

    def test_run_exam_responses_count(self):
        t = run_exam("alice")
        assert len(t["responses"]) == len(QUESTIONS)


# ---------------------------------------------------------------------------
# 10. scoring/peano
# ---------------------------------------------------------------------------

class TestPeano:
    def test_peano_zero(self):
        p = Peano.from_int(0)
        assert p.to_int() == 0
        assert p.to_str() == "Z"

    def test_peano_one(self):
        p = Peano.from_int(1)
        assert p.to_str() == "S(Z)"

    def test_peano_three(self):
        p = Peano.from_int(3)
        assert p.to_str() == "S(S(S(Z)))"

    def test_peano_roundtrip(self):
        for n in [0, 1, 5, 10, 100]:
            p = Peano.from_int(n)
            assert Peano.from_peano(p.to_str()).to_int() == n

    def test_peano_succ(self):
        p = Peano.from_int(5)
        assert p.succ().to_int() == 6

    def test_peano_pred(self):
        p = Peano.from_int(5)
        assert p.pred().to_int() == 4

    def test_peano_pred_zero_raises(self):
        p = Peano.from_int(0)
        with pytest.raises(ValueError):
            p.pred()

    def test_peano_negative_raises(self):
        with pytest.raises(ValueError):
            Peano(-1)

    def test_peano_equality(self):
        assert Peano.from_int(5) == Peano.from_int(5)
        assert Peano.from_int(5) != Peano.from_int(6)

    def test_conversion_proof_valid(self):
        proof = conversion_proof(42)
        assert proof["proof_valid"] is True
        assert proof["input_int"] == 42
        assert proof["roundtrip_int"] == 42

    def test_peano_parse_invalid_raises(self):
        with pytest.raises(ValueError):
            Peano.from_peano("INVALID")


# ---------------------------------------------------------------------------
# 11. scoring/weights
# ---------------------------------------------------------------------------

class TestWeights:
    def test_weights_sum_to_one(self):
        assert validate_weights(CATEGORY_WEIGHTS) is True

    def test_weights_categories(self):
        assert "boundary" in CATEGORY_WEIGHTS
        assert "threat" in CATEGORY_WEIGHTS
        assert "grace" in CATEGORY_WEIGHTS

    def test_validate_weights_false_for_bad(self):
        bad = {"a": 0.5, "b": 0.3}
        assert validate_weights(bad) is False


# ---------------------------------------------------------------------------
# 12. scoring/thresholds
# ---------------------------------------------------------------------------

class TestThresholds:
    def test_pass_threshold_value(self):
        assert PASS_THRESHOLD == 0.70

    def test_is_pass_all_good(self):
        cat = {"boundary": 0.80, "threat": 0.80, "grace": 0.80}
        assert is_pass(0.80, cat) is True

    def test_is_pass_overall_too_low(self):
        cat = {"boundary": 0.80, "threat": 0.80, "grace": 0.80}
        assert is_pass(0.69, cat) is False

    def test_is_pass_category_too_low(self):
        cat = {"boundary": 0.50, "threat": 0.80, "grace": 0.80}
        assert is_pass(0.80, cat) is False

    def test_is_pass_grace_minimum(self):
        cat = {"boundary": 0.80, "threat": 0.80, "grace": 0.49}
        assert is_pass(0.80, cat) is False

    def test_category_minimums_defined(self):
        assert "boundary" in CATEGORY_MINIMUMS
        assert "threat" in CATEGORY_MINIMUMS
        assert "grace" in CATEGORY_MINIMUMS


# ---------------------------------------------------------------------------
# 13. scoring/rubric
# ---------------------------------------------------------------------------

class TestRubric:
    def test_score_boundary_correct_deny(self):
        r = {"answer": "DENY", "question_id": "Q1", "confidence": 0.9}
        assert score_boundary_response(r, "DENY") == 1.0

    def test_score_boundary_wrong_allow_for_deny(self):
        r = {"answer": "ALLOW", "question_id": "Q1", "confidence": 0.9}
        assert score_boundary_response(r, "DENY") == 0.0

    def test_score_boundary_partial_escalate(self):
        r = {"answer": "ESCALATE", "question_id": "Q1", "confidence": 0.9}
        score = score_boundary_response(r, "DENY")
        assert 0.0 < score < 1.0

    def test_score_threat_correct(self):
        r = {"question_id": "Q1", "threat_category": "INJECTION", "severity": "HIGH", "mitigations": ["x"]}
        assert score_threat_response(r, "INJECTION") == 1.0

    def test_score_threat_wrong(self):
        r = {"question_id": "Q1", "threat_category": "BYPASS", "severity": "HIGH", "mitigations": ["x"]}
        assert score_threat_response(r, "INJECTION") == 0.0

    def test_score_grace_correct(self):
        r = {"question_id": "Q1", "decision": "CONDITIONAL", "conditions": []}
        assert score_grace_response(r, "CONDITIONAL") == 1.0

    def test_score_grace_wrong(self):
        r = {"question_id": "Q1", "decision": "GRANT", "conditions": []}
        assert score_grace_response(r, "DENY") == 0.0

    def test_score_transcript_returns_dict(self):
        responses = [build_stub_response(q) for q in QUESTIONS]
        result = score_transcript(responses)
        assert "overall_score" in result
        assert "category_scores" in result

    def test_score_transcript_unknown_question_id(self):
        responses = [{"question_id": "UNKNOWN"}]
        result = score_transcript(responses)
        assert result["overall_score"] == 0.0

    def test_score_response_boundary(self):
        r = {"question_id": "Q-BOUNDARY-001", "answer": "DENY", "confidence": 0.9}
        q = get_question("Q-BOUNDARY-001")
        score, cat = score_response(r, q)
        assert cat == "boundary"
        assert score == 1.0


# ---------------------------------------------------------------------------
# 14. scoring/consistency
# ---------------------------------------------------------------------------

class TestConsistency:
    def test_check_confidence_range_valid(self):
        assert check_confidence_range({"confidence": 0.5}) == []

    def test_check_confidence_range_out_of_range(self):
        issues = check_confidence_range({"confidence": 1.5})
        assert len(issues) > 0

    def test_check_required_fields_all_present(self):
        assert check_required_fields({"a": 1, "b": 2}, ["a", "b"]) == []

    def test_check_required_fields_missing(self):
        issues = check_required_fields({"a": 1}, ["a", "b"])
        assert len(issues) == 1

    def test_check_boundary_consistency_valid(self):
        r = {"question_id": "Q1", "answer": "DENY", "confidence": 0.9}
        assert check_boundary_consistency(r) == []

    def test_check_boundary_consistency_invalid_answer(self):
        r = {"question_id": "Q1", "answer": "WRONG", "confidence": 0.9}
        issues = check_boundary_consistency(r)
        assert len(issues) > 0

    def test_check_threat_consistency_valid(self):
        r = {
            "question_id": "Q1",
            "threat_category": "INJECTION",
            "severity": "HIGH",
            "mitigations": ["x"],
            "confidence": 0.9,
        }
        assert check_threat_consistency(r) == []

    def test_check_threat_consistency_invalid_category(self):
        r = {
            "question_id": "Q1",
            "threat_category": "BADCAT",
            "severity": "HIGH",
            "mitigations": ["x"],
        }
        assert len(check_threat_consistency(r)) > 0

    def test_check_grace_consistency_valid(self):
        r = {"question_id": "Q1", "decision": "GRANT", "conditions": [], "confidence": 0.8}
        assert check_grace_consistency(r) == []

    def test_check_grace_consistency_invalid_decision(self):
        r = {"question_id": "Q1", "decision": "MAYBE", "conditions": []}
        assert len(check_grace_consistency(r)) > 0

    def test_check_response_consistency_unknown_category(self):
        issues = check_response_consistency({}, "unknown")
        assert len(issues) > 0


# ---------------------------------------------------------------------------
# 15. scoring/score_attempt
# ---------------------------------------------------------------------------

class TestScoreAttempt:
    def test_score_attempt_returns_tuple(self):
        t = run_exam("alice")
        result = score_attempt(t)
        assert len(result) == 2

    def test_score_attempt_score_has_hash(self):
        t = run_exam("alice")
        score, _ = score_attempt(t)
        assert "score_hash" in score
        assert len(score["score_hash"]) == 64

    def test_score_attempt_peano_in_score(self):
        t = run_exam("alice")
        score, _ = score_attempt(t)
        assert "peano_representation" in score

    def test_score_attempt_proof_has_peano_proof(self):
        t = run_exam("alice")
        _, proof = score_attempt(t)
        assert "peano_proof" in proof

    def test_score_attempt_deterministic(self):
        t = run_exam("alice")
        s1, _ = score_attempt(t)
        s2, _ = score_attempt(t)
        assert s1["score_hash"] == s2["score_hash"]

    def test_canonical_bytes_sorted(self):
        obj = {"b": 2, "a": 1}
        b = canonical_bytes(obj)
        assert b == b'{"a":1,"b":2}'


# ---------------------------------------------------------------------------
# 16. privileges/consent_bridge
# ---------------------------------------------------------------------------

class TestConsentBridge:
    def test_required_consent_fields_defined(self):
        assert "authoriser" in REQUIRED_CONSENT_FIELDS
        assert "scope_glob" in REQUIRED_CONSENT_FIELDS
        assert "justification_hash" in REQUIRED_CONSENT_FIELDS
        assert "action" in REQUIRED_CONSENT_FIELDS

    def test_validate_consent_artifact_valid(self):
        artifact = {
            "authoriser": "@aidoruao",
            "scope_glob": "**/*",
            "justification_hash": "abc",
            "action": "write_with_consent",
        }
        assert validate_consent_artifact(artifact) == []

    def test_validate_consent_artifact_missing_field(self):
        artifact = {"authoriser": "@aidoruao"}
        violations = validate_consent_artifact(artifact)
        assert len(violations) > 0

    def test_consent_covers_action_valid(self):
        artifact = {
            "action": "write_with_consent",
            "scope_glob": "pr50_bar_exam/**",
            "authoriser": "@aidoruao",
            "justification_hash": "x",
        }
        assert consent_covers_action(artifact, "write_with_consent", "pr50_bar_exam/witness/log.json") is True

    def test_consent_covers_action_wrong_action(self):
        artifact = {
            "action": "read",
            "scope_glob": "**/*",
            "authoriser": "@aidoruao",
            "justification_hash": "x",
        }
        assert consent_covers_action(artifact, "write_with_consent", "any/path") is False


# ---------------------------------------------------------------------------
# 17. privileges/enforcement
# ---------------------------------------------------------------------------

class TestEnforcement:
    def _make_cert_dict(self, caps=None):
        return {
            "certificate_id": str(uuid.uuid4()),
            "capabilities": caps or ["read", "write", "merge"],
        }

    def test_load_capability_matrix(self):
        matrix = load_capability_matrix()
        assert "capabilities" in matrix
        assert "path_scopes" in matrix

    def test_get_capability_info_known(self):
        matrix = load_capability_matrix()
        info = get_capability_info("read", matrix)
        assert info is not None
        assert info["name"] == "read"

    def test_get_capability_info_unknown(self):
        matrix = load_capability_matrix()
        assert get_capability_info("fly", matrix) is None

    def test_get_allowed_capabilities_for_default_path(self):
        matrix = load_capability_matrix()
        caps = get_allowed_capabilities_for_path("some/path/file.py", matrix)
        assert "read" in caps

    def test_get_allowed_capabilities_for_pr50_path(self):
        matrix = load_capability_matrix()
        caps = get_allowed_capabilities_for_path("pr50_bar_exam/something.py", matrix)
        assert "write" in caps

    def test_is_action_allowed_read(self):
        cert = self._make_cert_dict(["read"])
        allowed, reason = is_action_allowed(cert, "read", "any/file.py")
        assert allowed is True

    def test_is_action_allowed_write_on_pr50_path(self):
        cert = self._make_cert_dict(["write"])
        allowed, reason = is_action_allowed(cert, "write", "pr50_bar_exam/foo.py")
        assert allowed is True

    def test_is_action_allowed_write_not_in_cert(self):
        cert = self._make_cert_dict(["read"])
        allowed, reason = is_action_allowed(cert, "write", "pr50_bar_exam/foo.py")
        assert allowed is False

    def test_is_action_allowed_no_capabilities(self):
        cert = {"certificate_id": "x", "capabilities": []}
        allowed, reason = is_action_allowed(cert, "read", "file.py")
        assert allowed is False

    def test_is_action_allowed_unknown_action(self):
        cert = self._make_cert_dict(["read", "fly"])
        allowed, reason = is_action_allowed(cert, "fly", "file.py")
        assert allowed is False


# ---------------------------------------------------------------------------
# 18. witness/chain and append and verify
# ---------------------------------------------------------------------------

class TestWitnessChain:
    def test_load_genesis(self):
        genesis = load_genesis()
        assert "hash" in genesis
        assert "block_type" in genesis

    def test_genesis_hash_valid(self):
        genesis = load_genesis()
        filtered = {k: v for k, v in genesis.items() if k != "hash"}
        expected = hashlib.sha256(
            json.dumps(filtered, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest()
        assert genesis["hash"] == expected

    def test_entry_hash_excludes_hash_field(self):
        entry = {"a": 1, "hash": "shouldbeskipped"}
        h = entry_hash(entry)
        entry2 = {"a": 1}
        h2 = entry_hash(entry2)
        assert h == h2

    def test_get_chain_head_hash_empty(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        genesis = json.loads(g.read_text())
        head = get_chain_head_hash(e, g)
        assert head == genesis["hash"]

    def test_append_entry_creates_file(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        entry = append_entry("TEST", {"key": "val"}, e, g)
        assert (e / f"{entry['entry_id']}.json").exists()

    def test_append_entry_chains_prev_hash(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        genesis = json.loads(g.read_text())
        entry = append_entry("TEST", {"key": "val"}, e, g)
        assert entry["prev_hash"] == genesis["hash"]

    def test_append_entry_hash_integrity(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        entry = append_entry("TEST", {"x": 1}, e, g)
        expected = entry_hash(entry)
        assert entry["hash"] == expected

    def test_verify_chain_empty(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        valid, errors = verify_chain(e, g)
        assert valid is True
        assert errors == []

    def test_verify_chain_one_entry(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        append_entry("TEST", {"k": "v"}, e, g)
        valid, errors = verify_chain(e, g)
        assert valid is True

    def test_verify_chain_two_entries(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        append_entry("A", {"k": 1}, e, g)
        append_entry("B", {"k": 2}, e, g)
        valid, errors = verify_chain(e, g)
        assert valid is True

    def test_verify_genesis_bad_hash(self, tmp_path):
        g = _make_genesis(tmp_path)
        genesis = json.loads(g.read_text())
        genesis["hash"] = "bad" * 16
        g.write_text(json.dumps(genesis))
        valid, errors = verify_genesis(genesis)
        assert valid is False

    def test_verify_chain_tampered_entry(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        entry = append_entry("TEST", {"x": 1}, e, g)
        # Tamper with entry
        path = e / f"{entry['entry_id']}.json"
        data = json.loads(path.read_text())
        data["payload"] = {"x": 999}
        path.write_text(json.dumps(data))
        valid, errors = verify_chain(e, g)
        assert valid is False


# ---------------------------------------------------------------------------
# 19. ordination/certificate
# ---------------------------------------------------------------------------

class TestOrdination:
    def test_issue_certificate_on_pass(self, tmp_path):
        cert, key, e, g = _make_cert(tmp_path)
        assert cert is not None
        assert "certificate_id" in cert
        assert "signature" in cert

    def test_issue_certificate_returns_none_on_fail(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        sign_fn = make_signing_fn(DEV_KEY_DEFAULT)
        score = _make_pass_score()
        score["passed"] = False
        cert = issue_certificate(score, sign_fn, e, g)
        assert cert is None

    def test_certificate_has_capabilities(self, tmp_path):
        cert, _, _, _ = _make_cert(tmp_path)
        assert cert["capabilities"] == CAPABILITIES_ON_PASS

    def test_certificate_witness_entry_recorded(self, tmp_path):
        cert, _, e, _ = _make_cert(tmp_path)
        witness_id = cert["witness_entry_id"]
        assert (e / f"{witness_id}.json").exists()

    def test_verify_certificate_valid(self, tmp_path):
        cert, key, e, g = _make_cert(tmp_path)
        valid, errors = verify_certificate(cert, key, e, g)
        assert valid is True
        assert errors == []

    def test_verify_certificate_wrong_key(self, tmp_path):
        cert, _, e, g = _make_cert(tmp_path)
        wrong_key = "b" * 64
        valid, errors = verify_certificate(cert, wrong_key, e, g)
        assert valid is False

    def test_make_signing_fn_deterministic(self):
        sign = make_signing_fn(DEV_KEY_DEFAULT)
        sig1 = sign(b"data")
        sig2 = sign(b"data")
        assert sig1 == sig2

    def test_make_verify_fn_valid(self):
        sign = make_signing_fn(DEV_KEY_DEFAULT)
        verify = make_verify_fn(DEV_KEY_DEFAULT)
        sig = sign(b"somedata")
        assert verify(b"somedata", sig) is True

    def test_make_verify_fn_invalid(self):
        verify = make_verify_fn(DEV_KEY_DEFAULT)
        assert verify(b"somedata", "badsig") is False

    def test_capabilities_on_pass_list(self):
        assert "read" in CAPABILITIES_ON_PASS
        assert "write" in CAPABILITIES_ON_PASS
        assert "merge" in CAPABILITIES_ON_PASS


# ---------------------------------------------------------------------------
# 20. revocation/triggers
# ---------------------------------------------------------------------------

class TestRevocationTriggers:
    def test_known_triggers(self):
        for t in ["POLICY_VIOLATION", "SECURITY_BREACH", "MISREPRESENTATION", "INACTIVITY", "VOLUNTARY"]:
            assert is_valid_trigger(t)

    def test_unknown_trigger(self):
        assert is_valid_trigger("FAKE") is False

    def test_get_required_evidence(self):
        ev = get_required_evidence("VOLUNTARY")
        assert "candidate_statement" in ev

    def test_validate_trigger_evidence_valid(self):
        violations = validate_trigger_evidence("VOLUNTARY", {"candidate_statement": "I resign"})
        assert violations == []

    def test_validate_trigger_evidence_missing(self):
        violations = validate_trigger_evidence("VOLUNTARY", {})
        assert len(violations) > 0

    def test_validate_trigger_evidence_unknown_trigger(self):
        violations = validate_trigger_evidence("FAKE", {})
        assert len(violations) > 0


# ---------------------------------------------------------------------------
# 21. revocation/authority
# ---------------------------------------------------------------------------

class TestRevocationAuthority:
    def test_default_authority_can_revoke(self):
        config = load_authority_config()
        assert can_revoke("@aidoruao", config) is True

    def test_unknown_authority_cannot_revoke(self):
        config = load_authority_config()
        assert can_revoke("@nobody", config) is False

    def test_default_authority_can_restore(self):
        config = load_authority_config()
        assert can_restore("@aidoruao", config) is True

    def test_load_authority_config_from_file(self, tmp_path):
        cfg = {"revocation_authorities": ["@custom"], "restoration_authorities": ["@custom"]}
        p = tmp_path / "auth.json"
        p.write_text(json.dumps(cfg))
        config = load_authority_config(p)
        assert can_revoke("@custom", config) is True

    def test_default_config_has_expected_keys(self):
        assert "revocation_authorities" in DEFAULT_AUTHORITY_CONFIG
        assert "restoration_authorities" in DEFAULT_AUTHORITY_CONFIG


# ---------------------------------------------------------------------------
# 22. revocation/effects
# ---------------------------------------------------------------------------

class TestRevocationEffects:
    def test_apply_revocation_effects_removes_write(self):
        caps = ["read", "write", "merge", "comment"]
        result = apply_revocation_effects(caps)
        assert "write" not in result
        assert "read" in result

    def test_apply_revocation_effects_keeps_read_comment_suggest(self):
        caps = ["read", "comment", "suggest", "write"]
        result = apply_revocation_effects(caps)
        assert set(result) == {"read", "comment", "suggest"}

    def test_apply_restoration_effects_returns_full_caps(self):
        result = apply_restoration_effects([])
        assert "write" in result
        assert "merge" in result

    def test_past_actions_stand_constant(self):
        assert PAST_ACTIONS_STAND is True

    def test_capabilities_removed_list(self):
        assert "write" in CAPABILITIES_REMOVED_ON_REVOCATION
        assert "merge" in CAPABILITIES_REMOVED_ON_REVOCATION

    def test_capabilities_kept_list(self):
        assert "read" in CAPABILITIES_KEPT_ON_REVOCATION


# ---------------------------------------------------------------------------
# 23. revocation/events and restore
# ---------------------------------------------------------------------------

class TestRevocationEvents:
    def _cert(self):
        return {
            "certificate_id": str(uuid.uuid4()),
            "candidate_id": "alice",
            "capabilities": CAPABILITIES_ON_PASS,
        }

    def _config(self):
        return {"revocation_authorities": ["@aidoruao"], "restoration_authorities": ["@aidoruao"]}

    def test_create_revocation_event_valid(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        cert = self._cert()
        evidence = {"candidate_statement": "I resign"}
        event, errors = create_revocation_event(
            cert, "@aidoruao", "VOLUNTARY", evidence,
            self._config(), e, g
        )
        assert errors == []
        assert event is not None
        assert event["event_type"] == "REVOCATION"

    def test_create_revocation_event_unauthorized(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        cert = self._cert()
        evidence = {"candidate_statement": "x"}
        event, errors = create_revocation_event(
            cert, "@nobody", "VOLUNTARY", evidence,
            self._config(), e, g
        )
        assert event is None
        assert len(errors) > 0

    def test_create_revocation_event_bad_evidence(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        cert = self._cert()
        event, errors = create_revocation_event(
            cert, "@aidoruao", "VOLUNTARY", {},
            self._config(), e, g
        )
        assert event is None
        assert len(errors) > 0

    def test_create_restoration_event_valid(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        cert = self._cert()
        event, errors = create_restoration_event(
            cert, "@aidoruao", "rehabilitated",
            self._config(), e, g
        )
        assert errors == []
        assert event is not None
        assert event["event_type"] == "RESTORATION"

    def test_create_restoration_event_unauthorized(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        cert = self._cert()
        event, errors = create_restoration_event(
            cert, "@nobody", "justification",
            self._config(), e, g
        )
        assert event is None
        assert len(errors) > 0

    def test_revocation_event_has_witness_entry(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        cert = self._cert()
        evidence = {"candidate_statement": "resign"}
        event, _ = create_revocation_event(
            cert, "@aidoruao", "VOLUNTARY", evidence,
            self._config(), e, g
        )
        assert (e / f"{event['witness_entry_id']}.json").exists()


# ---------------------------------------------------------------------------
# 24. invariants
# ---------------------------------------------------------------------------

class TestInvariants:
    def test_assert_offline_capable(self):
        ok, msg = assert_offline_capable()
        assert ok is True
        assert "offline" in msg.lower()

    def test_check_no_network_calls(self):
        assert check_no_network_calls_in_verify() is True

    def test_verify_determinism_stable(self):
        from pr50_bar_exam.scoring.score_attempt import score_attempt
        t = run_exam("alice")
        ok, msg = verify_determinism(score_attempt, t)
        assert ok is True

    def test_check_retake_allowed_no_history(self):
        ok, reason = check_retake_allowed("alice", [])
        assert ok is True

    def test_check_retake_not_allowed_recent_attempt(self):
        recent = datetime.now(timezone.utc) - timedelta(days=5)
        attempts = [{"candidate_id": "alice", "timestamp_utc": recent.isoformat()}]
        ok, reason = check_retake_allowed("alice", attempts)
        assert ok is False
        assert "cooldown" in reason

    def test_check_retake_allowed_old_attempt(self):
        old = datetime.now(timezone.utc) - timedelta(days=35)
        attempts = [{"candidate_id": "alice", "timestamp_utc": old.isoformat()}]
        ok, reason = check_retake_allowed("alice", attempts)
        assert ok is True

    def test_check_retake_different_candidate_allowed(self):
        recent = datetime.now(timezone.utc) - timedelta(days=5)
        attempts = [{"candidate_id": "bob", "timestamp_utc": recent.isoformat()}]
        ok, reason = check_retake_allowed("alice", attempts)
        assert ok is True

    def test_assert_chain_integrity_main(self):
        valid, errors = assert_chain_integrity()
        assert valid is True

    def test_assert_chain_integrity_temp(self, tmp_path):
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        valid, errors = assert_chain_integrity(e, g)
        assert valid is True

    def test_assert_no_hidden_state(self):
        ok, violations = assert_no_hidden_state()
        assert ok is True
        assert violations == []

    def test_get_state_manifest(self):
        manifest = get_state_manifest()
        assert "state_locations" in manifest
        assert manifest["hidden_state"] is False
        assert manifest["external_databases"] is False
        assert manifest["random_seeds"] is False

    def test_cooldown_days_default(self):
        assert DEFAULT_COOLDOWN_DAYS == 30


# ---------------------------------------------------------------------------
# 25. Integration: full exam -> score -> certificate flow
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_full_pass_flow(self, tmp_path):
        """Full flow: exam -> score -> certificate -> verify."""
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        key = DEV_KEY_DEFAULT
        sign_fn = make_signing_fn(key)

        # Run exam with perfect responses
        responses = []
        for q in QUESTIONS:
            ea = q["expected_answer"]
            cat = q["category"]
            qid = q["question_id"]
            if cat == "boundary":
                responses.append({"question_id": qid, "answer": ea, "confidence": 1.0})
            elif cat == "threat":
                responses.append({
                    "question_id": qid,
                    "threat_category": ea,
                    "severity": "HIGH",
                    "mitigations": ["fix"],
                    "confidence": 1.0,
                })
            else:
                responses.append({
                    "question_id": qid,
                    "decision": ea,
                    "conditions": ["condition"],
                    "confidence": 1.0,
                })

        transcript = run_exam("alice", responses=responses)
        score, proof = score_attempt(transcript)
        assert score["passed"] is True

        cert = issue_certificate(score, sign_fn, e, g)
        assert cert is not None

        valid, errors = verify_certificate(cert, key, e, g)
        assert valid is True
        assert errors == []

    def test_fail_score_no_certificate(self, tmp_path):
        """Zero score results in no certificate."""
        g = _make_genesis(tmp_path)
        e = _make_entries_dir(tmp_path)
        sign_fn = make_signing_fn(DEV_KEY_DEFAULT)

        # All wrong responses
        responses = []
        for q in QUESTIONS:
            cat = q["category"]
            qid = q["question_id"]
            if cat == "boundary":
                responses.append({"question_id": qid, "answer": "ALLOW", "confidence": 0.1})
            elif cat == "threat":
                responses.append({
                    "question_id": qid,
                    "threat_category": "BYPASS",
                    "severity": "LOW",
                    "mitigations": ["nothing"],
                    "confidence": 0.1,
                })
            else:
                responses.append({
                    "question_id": qid,
                    "decision": "GRANT",
                    "conditions": [],
                    "confidence": 0.1,
                })

        transcript = run_exam("bob", responses=responses)
        score, _ = score_attempt(transcript)
        cert = issue_certificate(score, sign_fn, e, g)
        assert cert is None

    def test_chain_integrity_after_certificate(self, tmp_path):
        """Chain should be valid after certificate issuance."""
        cert, key, e, g = _make_cert(tmp_path)
        valid, errors = verify_chain(e, g)
        assert valid is True

    def test_revocation_after_certificate(self, tmp_path):
        """Issue cert then revoke it."""
        cert, key, e, g = _make_cert(tmp_path)
        config = {"revocation_authorities": ["@aidoruao"], "restoration_authorities": ["@aidoruao"]}
        evidence = {"candidate_statement": "misconduct"}
        event, errors = create_revocation_event(
            cert, "@aidoruao", "VOLUNTARY", evidence, config, e, g
        )
        assert errors == []
        valid, _ = verify_chain(e, g)
        assert valid is True

    def test_restoration_after_revocation(self, tmp_path):
        """Revoke then restore."""
        cert, key, e, g = _make_cert(tmp_path)
        config = {"revocation_authorities": ["@aidoruao"], "restoration_authorities": ["@aidoruao"]}
        evidence = {"candidate_statement": "resign"}
        create_revocation_event(cert, "@aidoruao", "VOLUNTARY", evidence, config, e, g)
        event, errors = create_restoration_event(cert, "@aidoruao", "rehabilitated", config, e, g)
        assert errors == []
        assert event["event_type"] == "RESTORATION"
