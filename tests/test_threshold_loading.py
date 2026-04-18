"""
Tests for threshold configuration loader.

Validates YAML loading, CLI override precedence, and Fraction parsing.
"""

from fractions import Fraction
from pathlib import Path

import pytest

from threshold_loader import load_thresholds


class TestLoadThresholds:
    def test_defaults_return_fractions(self):
        thresholds = load_thresholds()
        assert isinstance(thresholds["certain"], Fraction)
        assert thresholds["certain"] == Fraction(247, 1)
        assert thresholds["high_confidence"] == Fraction(200, 1)
        assert thresholds["probable"] == Fraction(150, 1)
        assert thresholds["unknown"] == Fraction(100, 1)
        assert thresholds["suspicious"] == Fraction(50, 1)
        assert thresholds["invalid"] == Fraction(0, 1)

    def test_config_file_loading(self, tmp_path):
        config = tmp_path / "thresholds.yaml"
        config.write_text(
            'certain: "300/1"\nhigh_confidence: "250/1"\nprobable: "180/1"\n'
        )
        thresholds = load_thresholds(path=str(config))
        assert thresholds["certain"] == Fraction(300, 1)
        assert thresholds["high_confidence"] == Fraction(250, 1)
        assert thresholds["probable"] == Fraction(180, 1)
        # Unspecified keys retain defaults
        assert thresholds["unknown"] == Fraction(100, 1)

    def test_cli_override_single(self):
        thresholds = load_thresholds(overrides=["certain=500/1"])
        assert thresholds["certain"] == Fraction(500, 1)

    def test_cli_override_multiple(self):
        thresholds = load_thresholds(
            overrides=["certain=500/1", "suspicious=75/1"]
        )
        assert thresholds["certain"] == Fraction(500, 1)
        assert thresholds["suspicious"] == Fraction(75, 1)
        assert thresholds["high_confidence"] == Fraction(200, 1)

    def test_override_precedence_over_config(self, tmp_path):
        config = tmp_path / "thresholds.yaml"
        config.write_text('certain: "300/1"\n')
        thresholds = load_thresholds(
            path=str(config), overrides=["certain=500/1"]
        )
        # CLI override wins over config
        assert thresholds["certain"] == Fraction(500, 1)

    def test_config_precedence_over_defaults(self, tmp_path):
        config = tmp_path / "thresholds.yaml"
        config.write_text('certain: "300/1"\n')
        thresholds = load_thresholds(path=str(config))
        assert thresholds["certain"] == Fraction(300, 1)
        assert thresholds["high_confidence"] == Fraction(200, 1)

    def test_invalid_override_ignored(self):
        # Missing '=' should be skipped
        thresholds = load_thresholds(overrides=["certain500/1"])
        assert thresholds["certain"] == Fraction(247, 1)

    def test_missing_config_file_falls_back_to_defaults(self):
        thresholds = load_thresholds(path="/nonexistent/path.yaml")
        assert thresholds["certain"] == Fraction(247, 1)

    def test_parse_fraction_integer(self):
        thresholds = load_thresholds(overrides=["certain=300"])
        assert thresholds["certain"] == Fraction(300, 1)

    def test_parse_fraction_rational(self):
        thresholds = load_thresholds(overrides=["certain=3/2"])
        assert thresholds["certain"] == Fraction(3, 2)

    def test_no_float_pollution(self):
        thresholds = load_thresholds(overrides=["certain=247/1"])
        assert isinstance(thresholds["certain"], Fraction)
        assert thresholds["certain"].denominator == 1

    def test_default_config_file_exists(self):
        default_path = Path("config/thresholds.yaml")
        assert default_path.exists(), "Default thresholds.yaml should exist"
        thresholds = load_thresholds(path=str(default_path))
        assert thresholds["certain"] == Fraction(247, 1)
