#!/usr/bin/env python3
"""Tests for Contract Law Domain."""

import pytest
from fractions import Fraction
from datetime import datetime

from ..implementation import Contract, Party, Breach, ContractType, ContractStatus, STATUTE_OF_FRAUDS_THRESHOLD
from ..invariants import check_statute_of_frauds, check_formation, check_expectation_principle


class TestStatuteOfFrauds:
    """UCC § 2-201 — Writing requirement for contracts >= $500."""
    
    def test_oral_contract_below_threshold(self):
        """$400 oral contract is valid."""
        contract = Contract(
            offeror=Party("Alice"),
            offeree=Party("Bob"),
            contract_type=ContractType.SALE_OF_GOODS,
            price=Fraction(400),
            is_written=False,
        )
        ok, proof = check_statute_of_frauds(contract)
        assert ok
    
    def test_written_contract_above_threshold(self):
        """$600 written contract satisfies Statute of Frauds."""
        contract = Contract(
            offeror=Party("Alice"),
            offeree=Party("Bob"),
            contract_type=ContractType.SALE_OF_GOODS,
            price=Fraction(600),
            is_written=True,
            written_terms="Sale of 100 widgets for $600",
        )
        ok, proof = check_statute_of_frauds(contract)
        assert ok
    
    def test_oral_contract_above_threshold_violation(self):
        """$600 oral contract violates Statute of Frauds."""
        contract = Contract(
            offeror=Party("Alice"),
            offeree=Party("Bob"),
            contract_type=ContractType.SALE_OF_GOODS,
            price=Fraction(600),
            is_written=False,
        )
        ok, proof = check_statute_of_frauds(contract)
        assert not ok
        assert "VIOLATION" in proof.conclusion


class TestFormation:
    """Offer + Acceptance + Consideration = Contract."""
    
    def test_valid_formation(self):
        """Complete formation elements."""
        contract = Contract(
            offeror=Party("Alice"),
            offeree=Party("Bob"),
            contract_type=ContractType.SERVICES,
            price=Fraction(1000),
            offer_date=datetime(2024, 1, 1),
            acceptance_date=datetime(2024, 1, 2),
        )
        ok, proof = check_formation(contract)
        assert ok
    
    def test_missing_acceptance(self):
        """No acceptance = no contract."""
        contract = Contract(
            offeror=Party("Alice"),
            offeree=Party("Bob"),
            contract_type=ContractType.SERVICES,
            price=Fraction(1000),
            offer_date=datetime(2024, 1, 1),
            acceptance_date=None,
        )
        ok, proof = check_formation(contract)
        assert not ok


class TestDamages:
    """Expectation damages principle."""
    
    def test_damages_within_expectation(self):
        """Damages cannot exceed expectation interest."""
        contract = Contract(
            offeror=Party("Alice"),
            offeree=Party("Bob"),
            contract_type=ContractType.SALE_OF_GOODS,
            price=Fraction(1000),
        )
        breach = Breach(
            contract=contract,
            breach_date=datetime(2024, 2, 1),
            expectation_damages=Fraction(200),
            reliance_damages=Fraction(100),
            restitution=Fraction(50),
        )
        ok, proof = check_expectation_principle(breach)
        assert ok
    
    def test_fraction_type(self):
        """All monetary values are Fraction, not float."""
        assert isinstance(STATUTE_OF_FRAUDS_THRESHOLD, Fraction)
