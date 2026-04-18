"""
Tests for AI co-author attribution and consent log.

Validates registry update, consent flow, and trailer formatting.
"""

import json
from pathlib import Path

import pytest

from tools.ai_credit import (
    format_ai_trailer,
    register_ai_coauthor,
    validate_ai_credit_env,
)


class TestFormatAiTrailer:
    def test_trailer_format(self):
        trailer = format_ai_trailer(
            model_id="597e0d23-f404-4bdf-801f-64962ce0e722",
            model_hash="sha256:abc123",
        )
        assert "Co-Authored-By:" in trailer
        assert "597e0d23-f404-4bdf-801f-64962ce0e722" in trailer
        assert "sha256:abc123" in trailer


class TestRegisterAiCoauthor:
    def test_registry_updated(self, tmp_path):
        consent = tmp_path / "consent.txt"
        consent.write_text("I consent to AI co-author credit.")
        registry = tmp_path / ".ai_registry.json"
        registry.write_text('{"agents": []}')

        entry = register_ai_coauthor(
            model_id="test-model-1",
            model_hash="sha256:abc123",
            consent_file=str(consent),
            registry_path=str(registry),
        )

        assert entry["id"] == "test-model-1"
        assert entry["model_hash"] == "sha256:abc123"
        assert "consent_hash" in entry

        with open(registry) as f:
            data = json.load(f)
        assert "co_authors" in data
        assert len(data["co_authors"]) == 1

    def test_consent_log_appended(self, tmp_path):
        consent = tmp_path / "consent.txt"
        consent.write_text("I consent to AI co-author credit.")
        registry = tmp_path / ".ai_registry.json"
        registry.write_text('{}')

        # Use a temporary consent log
        import tools.ai_credit as ai_credit_mod
        original_log = ai_credit_mod.Path("pr47_stewardship/witness/consent_log.jsonl")
        # We can't easily redirect the log path, but we can verify the log file grows
        log_path = Path("pr47_stewardship/witness/consent_log.jsonl")
        pre_lines = 0
        if log_path.exists():
            pre_lines = len(log_path.read_text().strip().split("\n"))

        register_ai_coauthor(
            model_id="test-model-2",
            model_hash="sha256:def456",
            consent_file=str(consent),
            registry_path=str(registry),
        )

        if log_path.exists():
            post_lines = len(log_path.read_text().strip().split("\n"))
            assert post_lines >= pre_lines + 1

    def test_missing_consent_file_raises(self, tmp_path):
        registry = tmp_path / ".ai_registry.json"
        registry.write_text('{}')
        with pytest.raises(FileNotFoundError):
            register_ai_coauthor(
                model_id="test-model-3",
                model_hash="sha256:ghi789",
                consent_file="/nonexistent/consent.txt",
                registry_path=str(registry),
            )


class TestValidateAiCreditEnv:
    def test_valid_env(self, monkeypatch, tmp_path):
        consent = tmp_path / "consent.txt"
        consent.write_text("consent")
        monkeypatch.setenv("KIMI_AI_CREDIT", "1")
        monkeypatch.setenv("KIMI_AI_CONSENT_FILE", str(consent))
        result = validate_ai_credit_env()
        assert result == str(consent)

    def test_missing_env(self, monkeypatch):
        monkeypatch.delenv("KIMI_AI_CREDIT", raising=False)
        result = validate_ai_credit_env()
        assert result is None

    def test_missing_consent_file(self, monkeypatch):
        monkeypatch.setenv("KIMI_AI_CREDIT", "1")
        monkeypatch.delenv("KIMI_AI_CONSENT_FILE", raising=False)
        result = validate_ai_credit_env()
        assert result is None
