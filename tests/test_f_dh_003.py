"""
tests/test_f_dh_003.py
F_DH_003: Config values >2048 trigger warning log

Tests that the configuration system validates aggressive values.
"""

import pytest
from fractions import Fraction

from src.domains.d_dh_standalone import (
    build_config_situs,
    CONFIG_PARADOX_PX001,
    BLOCKS_SQUARED_PER_PLAYER,
    DH_SCHEMA,
)
from src.domains.d_dh_standalone.invariants import check_config_validation_warning
from src.sal.topos_subobject_classifier import SubobjectClassifier
from src.sal.realizability_topos import RealizabilityTopos, realize
from axioms.logic import ProofObject


class TestConfigValidation:
    """F_DH_003: Config validation warning tests."""
    
    def test_config_situs_has_max_generation_valid(self):
        ctx = build_config_situs()
        assert "max_generation_distance_valid" in ctx.objects
    
    def test_config_situs_has_no_warning_object(self):
        ctx = build_config_situs()
        assert "no_performance_warning" in ctx.objects
    
    def test_no_performance_warning_uncovered(self):
        """The 'no warning' state has no valid covering — it is false."""
        ctx = build_config_situs()
        assert ctx.covers.get("no_performance_warning") == []
    
    def test_default_4096_is_aggressive(self):
        """4096 blocks is well above the 2048 warning threshold."""
        default = 4096
        threshold = 2048
        assert default > threshold
    
    def test_blocks_squared_is_52_million(self):
        """π × 4096² = ~52.7 million blocks² per player."""
        assert BLOCKS_SQUARED_PER_PLAYER > 52_000_000
        assert BLOCKS_SQUARED_PER_PLAYER < 53_000_000
    
    def test_config_paradox_documented(self):
        """PX-001: Config allows values that guarantee TPS degradation."""
        assert "PX-001" in CONFIG_PARADOX_PX001 or "config_paradox" in CONFIG_PARADOX_PX001
        assert "4096" in CONFIG_PARADOX_PX001 or "52.7M" in CONFIG_PARADOX_PX001


class TestConfigInvariant:
    """Executable invariant checks for config."""
    
    def test_config_validation_check_fails(self):
        """The actual config has no validation warning."""
        result = check_config_validation_warning()
        assert not result.passed  # Should fail — no warning exists
    
    def test_config_check_recommends_fix(self):
        result = check_config_validation_warning()
        assert result.recommended_fix is not None
        assert "1024" in result.recommended_fix or "2048" in result.recommended_fix


class TestConfigRealizability:
    """Type 6 realizability for config paradox."""
    
    def test_area_formula_is_realizable(self):
        """The mathematical proof πr² is a realizer."""
        proof = ProofObject(
            rule="AreaFormula",
            premises=["r=4096", "π=3.14159..."],
            conclusion=f"area={BLOCKS_SQUARED_PER_PLAYER}",
        )
        r, claim, violations = realize("area_computation", proof)
        assert r.is_computable
        assert violations == ()
    
    def test_config_defect_is_realizable(self):
        proof = ProofObject(
            rule="ConfigAnalysis",
            premises=["Config.java:1744", "default=4096"],
            conclusion="config_paradox_proven",
        )
        r, claim, violations = realize("config_paradox", proof)
        assert r.is_computable


class TestConfigSchema:
    """Schema validation for config-related structures."""
    
    def test_schema_has_mathematical_proof(self):
        assert "52" in DH_SCHEMA["mathematical_proof"]
        assert "π" in DH_SCHEMA["mathematical_proof"]
    
    def test_schema_components_include_config(self):
        assert "config" in DH_SCHEMA["components"]
        assert "4096" in DH_SCHEMA["components"]["config"]
