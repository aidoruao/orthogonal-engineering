#!/usr/bin/env python3
"""
Test suite for Administrative Law Domain
Tests APA compliance, exhaustion, Chevron analysis.
"""

import pytest
from fractions import Fraction
from datetime import datetime, timedelta

from ..implementation import (
    Agency, Rulemaking, Comment, AdministrativeRecord, 
    ExhaustionClaim, RulemakingType, calculate_chevron_deference,
    JudicialReviewStandard, MIN_COMMENT_PERIOD_DAYS
)
from ..invariants import (
    check_notice_period, check_exhaustion, check_chevron_step_one,
    check_finality, check_record_based_decision, run_all_invariants
)


class TestNoticePeriod:
    """APA § 553(b) notice-and-comment requirements."""
    
    @pytest.fixture
    def epa(self):
        return Agency("EPA", "42 U.S.C. § 7401", "https://epa.gov")
    
    @pytest.fixture
    def proposed_rule(self, epa):
        return Rulemaking(
            docket_number="EPA-HQ-OAR-2024-0001",
            agency=epa,
            title="National Ambient Air Quality Standards",
            rule_type=RulemakingType.INFORMAL,
            notice_date=datetime(2024, 1, 1),
            comment_period_open=datetime(2024, 1, 15),
            comment_period_close=datetime(2024, 2, 28),  # 44 days
            proposed_text="Revise NAAQS..."
        )
    
    def test_sufficient_comment_period(self, proposed_rule):
        """45-day comment period exceeds 30-day minimum."""
        ok, proof = check_notice_period(proposed_rule)
        assert ok, proof.conclusion
        assert "44" in proof.conclusion or "adequate" in proof.conclusion
    
    def test_insufficient_comment_period(self, epa):
        """15-day period violates APA minimum."""
        rule = Rulemaking(
            docket_number="EPA-2024-0002",
            agency=epa,
            title="Short Comment Period Rule",
            rule_type=RulemakingType.INFORMAL,
            comment_period_open=datetime(2024, 1, 1),
            comment_period_close=datetime(2024, 1, 16),  # Only 15 days
        )
        ok, proof = check_notice_period(rule)
        assert not ok, "Should fail with 15-day period"
        assert "VIOLATION" in proof.conclusion
    
    def test_interpretive_rule_exempt(self, epa):
        """Interpretive rules exempt from notice-and-comment."""
        rule = Rulemaking(
            docket_number="EPA-2024-0003",
            agency=epa,
            title="Interpretive Guidance",
            rule_type=RulemakingType.INTERPRETIVE,
        )
        ok, proof = check_notice_period(rule)
        assert ok, "Interpretive rules are exempt"
        assert "exempt" in proof.conclusion.lower()


class TestExhaustion:
    """Exhaustion of administrative remedies doctrine."""
    
    @pytest.fixture
    def epa(self):
        return Agency("EPA", "42 U.S.C. § 7401", "https://epa.gov")
    
    def test_fully_exhausted(self, epa):
        """All remedies sought have been exhausted."""
        claim = ExhaustionClaim(
            claimant="Industry Coalition",
            agency=epa,
            issue_raised="Permit denial",
            remedies_sought=["reconsideration", "appeal_to_board"],
            remedies_exhausted=["reconsideration", "appeal_to_board"],
        )
        ok, proof = check_exhaustion(claim)
        assert ok, proof.conclusion
    
    def test_not_exhausted(self, epa):
        """Missing appeal to board."""
        claim = ExhaustionClaim(
            claimant="Industry Coalition",
            agency=epa,
            issue_raised="Permit denial",
            remedies_sought=["reconsideration", "appeal_to_board"],
            remedies_exhausted=["reconsideration"],  # Missing board appeal
        )
        ok, proof = check_exhaustion(claim)
        assert not ok, "Should fail with incomplete exhaustion"
        assert "missing" in proof.conclusion.lower() or "not exhausted" in proof.conclusion.lower()


class TestChevron:
    """Chevron deference analysis."""
    
    @pytest.fixture
    def epa(self):
        return Agency("EPA", "42 U.S.C. § 7401", "https://epa.gov")
    
    def test_unambiguous_statute_no_deference(self, epa):
        """Clear statutory language — no Chevron deference."""
        rule = Rulemaking(
            docket_number="EPA-2024-0004",
            agency=epa,
            title="Clear Statute Rule",
            rule_type=RulemakingType.INFORMAL,
            statutory_authority="42 U.S.C. § 7409",
            statutory_ambiguity=False,  # Unambiguous
        )
        ok, proof = check_chevron_step_one(rule)
        assert not ok, "Should fail Chevron Step 1 for unambiguous statute"
    
    def test_ambiguous_statute_deference_possible(self, epa):
        """Ambiguous statute — Chevron Step 2 analysis needed."""
        rule = Rulemaking(
            docket_number="EPA-2024-0005",
            agency=epa,
            title="Ambiguous Statute Rule",
            rule_type=RulemakingType.INFORMAL,
            statutory_authority="42 U.S.C. § 7409 (unclear)",
            statutory_ambiguity=True,
        )
        ok, proof = check_chevron_step_one(rule)
        assert ok, "Should pass for ambiguous statute"
    
    def test_chevron_calculation_low_ambiguity(self):
        """Low ambiguity score → de novo review."""
        standard = calculate_chevron_deference(
            "Clean Air Act § 109",
            "EPA interpretation",
            Fraction(5, 100)  # 5% ambiguous
        )
        assert standard == JudicialReviewStandard.DE_NOVO
    
    def test_chevron_calculation_high_ambiguity(self):
        """High ambiguity score → substantial evidence."""
        standard = calculate_chevron_deference(
            "Clean Air Act § 112",
            "EPA interpretation",
            Fraction(75, 100)  # 75% ambiguous
        )
        assert standard == JudicialReviewStandard.SUBSTANTIAL_EVIDENCE


class TestFinality:
    """Final agency action under Bennett v. Spear."""
    
    @pytest.fixture
    def epa(self):
        return Agency("EPA", "42 U.S.C. § 7401", "https://epa.gov")
    
    def test_final_action(self, epa):
        """Rule with final and effective dates is final."""
        rule = Rulemaking(
            docket_number="EPA-2024-0006",
            agency=epa,
            title="Final Rule",
            rule_type=RulemakingType.INFORMAL,
            final_rule_date=datetime(2024, 6, 1),
            effective_date=datetime(2024, 7, 1),
        )
        ok, proof = check_finality(rule)
        assert ok, proof.conclusion
    
    def test_not_final_no_effective_date(self, epa):
        """Rule without effective date is not final."""
        rule = Rulemaking(
            docket_number="EPA-2024-0007",
            agency=epa,
            title="Proposed Only",
            rule_type=RulemakingType.INFORMAL,
            final_rule_date=datetime(2024, 6, 1),
            effective_date=None,
        )
        ok, proof = check_finality(rule)
        assert not ok, "Should fail without effective date"


class TestRecordBasedDecision:
    """Camp v. Pitts — decisions must be record-based."""
    
    @pytest.fixture
    def epa(self):
        return Agency("EPA", "42 U.S.C. § 7401", "https://epa.gov")
    
    def test_adequate_record(self, epa):
        """Rule with public comments has adequate record."""
        rule = Rulemaking(
            docket_number="EPA-2024-0008",
            agency=epa,
            title="Commented Rule",
            rule_type=RulemakingType.INFORMAL,
        )
        rule.comments_received.append(
            Comment("Industry", "Oppose", datetime(2024, 2, 1))
        )
        ok, proof = check_record_based_decision(rule)
        assert ok, proof.conclusion
    
    def test_inadequate_record(self, epa):
        """Rule with no comments has inadequate record."""
        rule = Rulemaking(
            docket_number="EPA-2024-0009",
            agency=epa,
            title="No Comments Rule",
            rule_type=RulemakingType.INFORMAL,
        )
        ok, proof = check_record_based_decision(rule, comments_required=1)
        assert not ok, "Should fail with no comments"


class TestFractionArithmetic:
    """All calculations use exact Fraction arithmetic — 0 floats."""
    
    def test_comment_period_returns_fraction(self):
        """get_comment_period_days returns Fraction."""
        epa = Agency("EPA", "42 U.S.C. § 7401", "https://epa.gov")
        rule = Rulemaking(
            docket_number="EPA-2024-0010",
            agency=epa,
            title="Test Rule",
            rule_type=RulemakingType.INFORMAL,
            comment_period_open=datetime(2024, 1, 1),
            comment_period_close=datetime(2024, 2, 1),
        )
        days = rule.get_comment_period_days()
        assert isinstance(days, Fraction)
        assert days == Fraction(31)
