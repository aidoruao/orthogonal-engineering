#!/usr/bin/env python3
"""Tests for Civil Procedure Domain."""

import pytest
from datetime import datetime
from ..implementation import Lawsuit, Party
from ..invariants import check_class_certification, check_12b6_plausibility

class TestClassCertification:
    """FRCP 23 class action requirements."""
    
    def test_valid_class_certification(self):
        """All four requirements met."""
        suit = Lawsuit(
            plaintiff=Party("Smith"),
            defendant=Party("Corp"),
            case_number="1:24-cv-001",
            filed_date=datetime(2024, 1, 1),
            class_action=True,
            class_size_estimate=100,
            numerosity=True,
            commonality=True,
            typicality=True,
            adequacy=True,
        )
        ok, proof = check_class_certification(suit)
        assert ok
    
    def test_missing_commonality(self):
        """Missing commonality fails certification."""
        suit = Lawsuit(
            plaintiff=Party("Smith"),
            defendant=Party("Corp"),
            case_number="1:24-cv-002",
            filed_date=datetime(2024, 1, 1),
            class_action=True,
            class_size_estimate=100,
            numerosity=True,
            commonality=False,
            typicality=True,
            adequacy=True,
        )
        ok, proof = check_class_certification(suit)
        assert not ok

class TestPlausibility:
    """FRCP 12(b)(6) plausibility standard."""
    
    def test_empty_complaint_fails(self):
        """No allegations = failure to state claim."""
        suit = Lawsuit(
            plaintiff=Party("Jones"),
            defendant=Party("Corp"),
            case_number="1:24-cv-003",
            filed_date=datetime(2024, 1, 1),
            complaint_allegations=[],
        )
        ok, proof = check_12b6_plausibility(suit)
        assert not ok
