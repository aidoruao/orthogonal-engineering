"""
Tests for forensic commit JSON schema validation.
"""

import json
from fractions import Fraction
from pathlib import Path

import pytest

from audit.forensic_commit import build_forensic_commit


def load_schema():
    schema_path = Path("schemas/forensic_commit_schema.json")
    with open(schema_path) as f:
        return json.load(f)


class TestForensicSchemaValidation:
    def test_schema_file_exists(self):
        schema_path = Path("schemas/forensic_commit_schema.json")
        assert schema_path.exists()

    def test_forensic_commit_validates(self, tmp_path):
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        schema = load_schema()
        metadata = {
            "commit_sha": "abc123",
            "timestamp": "2026-01-01T00:00:00Z",
            "authors": ["Test Author"],
            "co_authors": [],
        }
        artifacts = [
            {"path": "/tmp/f1.txt", "size": 100, "sha256": "a" * 64},
        ]
        thresholds = {
            "certain": Fraction(247, 1),
            "high_confidence": Fraction(200, 1),
            "probable": Fraction(150, 1),
            "unknown": Fraction(100, 1),
            "suspicious": Fraction(50, 1),
            "invalid": Fraction(0, 1),
        }
        forensic_obj = build_forensic_commit(metadata, artifacts, thresholds)
        jsonschema.validate(instance=forensic_obj, schema=schema)
