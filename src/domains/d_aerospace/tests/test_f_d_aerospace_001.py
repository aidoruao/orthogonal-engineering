#!/usr/bin/env python3
"""Tests for Aerospace Domain — DO-178C compliance."""

import pytest
from fractions import Fraction

from ..implementation import (
    SoftwareComponent, CertificationLevel, RedundantChannel,
    RedundancyChecker, StructuralHealthSensor, StructuralHealthMonitor
)
from ..invariants import (
    check_certification_coverage, check_redundancy_agreement, check_structural_health
)


class TestCertification:
    """DO-178C certification level requirements."""
    
    def test_level_a_requires_mc_dc(self):
        """Level A software requires 100% MC/DC coverage."""
        comp = SoftwareComponent(
            name="FlightControl",
            dal=CertificationLevel.LEVEL_A,
            lines_of_code=1000,
            structural_coverage_mc_dc=Fraction(100)
        )
        ok, proof = check_certification_coverage(comp)
        assert ok, proof.conclusion
    
    def test_level_a_fails_without_mc_dc(self):
        """Level A without 100% MC/DC coverage fails."""
        comp = SoftwareComponent(
            name="FlightControl",
            dal=CertificationLevel.LEVEL_A,
            lines_of_code=1000,
            structural_coverage_mc_dc=Fraction(80)
        )
        ok, proof = check_certification_coverage(comp)
        assert not ok, "Should fail without 100% MC/DC"
        assert "VIOLATION" in proof.conclusion


class TestRedundancy:
    """Triple modular redundancy requirements."""
    
    def test_channels_agree(self):
        """Healthy redundant channels must agree."""
        channels = [
            RedundantChannel("A", output_value=Fraction(100)),
            RedundantChannel("B", output_value=Fraction(100)),
            RedundantChannel("C", output_value=Fraction(100)),
        ]
        checker = RedundancyChecker(channels)
        ok, proof = check_redundancy_agreement(checker)
        assert ok, proof.conclusion
    
    def test_channels_disagree_fails(self):
        """Disagreeing channels fail consensus."""
        channels = [
            RedundantChannel("A", output_value=Fraction(100)),
            RedundantChannel("B", output_value=Fraction(200)),
            RedundantChannel("C", output_value=Fraction(100)),
        ]
        checker = RedundancyChecker(channels)
        ok, proof = check_redundancy_agreement(checker)
        assert not ok, "Should fail when channels disagree"


class TestStructuralHealth:
    """Structural health monitoring."""
    
    def test_sensors_within_spec(self):
        """Sensors within thresholds pass."""
        sensors = [
            StructuralHealthSensor("S1", strain_reading=Fraction(1000)),
            StructuralHealthSensor("S2", strain_reading=Fraction(500)),
        ]
        monitor = StructuralHealthMonitor(sensors)
        ok, proof = check_structural_health(monitor)
        assert ok, proof.conclusion
    
    def test_sensor_alert(self):
        """Sensor exceeding threshold triggers alert."""
        sensors = [
            StructuralHealthSensor("S1", strain_reading=Fraction(3500)),  # Over threshold
        ]
        monitor = StructuralHealthMonitor(sensors)
        ok, proof = check_structural_health(monitor)
        assert not ok, "Should fail when sensor exceeds threshold"
