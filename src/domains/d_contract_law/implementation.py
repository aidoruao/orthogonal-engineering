#!/usr/bin/env python3
"""
Contract Law Implementation — Formation, Performance, Breach

Key thresholds:
- Statute of Frauds: contracts > $500 must be written (UCC § 2-201)
- UCC Article 2: governing sales of goods
"""

from fractions import Fraction
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum, auto


class ContractType(Enum):
    SALE_OF_GOODS = auto()      # UCC Article 2
    SERVICES = auto()           # Common law
    HYBRID = auto()             # Mixed goods/services
    REAL_ESTATE = auto()        # Statute of Frauds required


class ContractStatus(Enum):
    OFFER = auto()
    ACCEPTANCE = auto()
    CONSIDERATION = auto()
    BREACH = auto()
    PERFORMED = auto()


@dataclass
class Party:
    """Contracting party."""
    name: str
    is_merchant: bool = False  # UCC § 2-104


@dataclass
class Contract:
    """A contract with offer, acceptance, consideration."""
    offeror: Party
    offeree: Party
    contract_type: ContractType
    
    # Terms
    subject_matter: str = ""
    price: Fraction = Fraction(0)
    
    # Formation
    offer_date: Optional[datetime] = None
    acceptance_date: Optional[datetime] = None
    
    # Writing requirements
    is_written: bool = False
    written_terms: str = ""
    
    # Performance
    status: ContractStatus = ContractStatus.OFFER
    
    def is_within_statute_of_frauds(self) -> bool:
        """UCC § 2-201: Contracts for goods >= $500 must be written."""
        if self.contract_type == ContractType.SALE_OF_GOODS:
            return self.price >= Fraction(500)
        return False
    
    def is_valid_formation(self) -> bool:
        """Offer + Acceptance + Consideration = Valid Contract."""
        has_offer = self.offer_date is not None
        has_acceptance = self.acceptance_date is not None
        has_consideration = self.price > Fraction(0)
        return has_offer and has_acceptance and has_consideration


@dataclass
class Breach:
    """Contract breach with damages calculation."""
    contract: Contract
    breach_date: datetime
    material: bool = False  # Material vs. minor breach
    
    # Damages
    expectation_damages: Fraction = Fraction(0)
    reliance_damages: Fraction = Fraction(0)
    restitution: Fraction = Fraction(0)
    
    def total_damages(self) -> Fraction:
        """Total recoverable damages (cannot exceed expectation)."""
        return min(
            self.expectation_damages,
            self.reliance_damages + self.restitution
        )


# UCC § 2-207 Battle of the Forms
@dataclass
class UCCBattleOfForms:
    """Track divergent terms in merchant transactions."""
    buyer: Party
    seller: Party
    
    offer_terms: Dict[str, str] = field(default_factory=dict)
    acceptance_terms: Dict[str, str] = field(default_factory=dict)
    
    def has_additional_terms(self) -> bool:
        """Check if acceptance contains terms not in offer."""
        return not set(self.acceptance_terms.keys()) <= set(self.offer_terms.keys())
    
    def is_between_merchants(self) -> bool:
        """UCC § 2-207(2): Additional terms become part of contract between merchants."""
        return self.buyer.is_merchant and self.seller.is_merchant


STATUTE_OF_FRAUDS_THRESHOLD = Fraction(500)  # UCC § 2-201
