#!/usr/bin/env python3
"""Family Law — Child support, custody, asset division."""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Parent:
    """Parent in family law matter."""
    parent_id: str
    monthly_income: Fraction
    custody_percentage: Fraction = Fraction(50)  # 0-100
    
    def income_share(self, total_income: Fraction) -> Fraction:
        if total_income == 0:
            return Fraction(50)
        return Fraction(self.monthly_income * 100, total_income)


@dataclass
class ChildSupportCalculator:
    """Calculate child support using income shares model."""
    parent1: Parent
    parent2: Parent
    num_children: int
    basic_support_obligation: Fraction
    
    def total_income(self) -> Fraction:
        return self.parent1.monthly_income + self.parent2.monthly_income
    
    def calculate_support(self) -> Dict[str, Fraction]:
        """Return support owed by each parent."""
        total = self.total_income()
        p1_share = self.parent1.income_share(total)
        p2_share = self.parent2.income_share(total)
        
        p1_obligation = self.basic_support_obligation * p1_share / Fraction(100)
        p2_obligation = self.basic_support_obligation * p2_share / Fraction(100)
        
        return {
            self.parent1.parent_id: p1_obligation,
            self.parent2.parent_id: p2_obligation
        }


@dataclass
class CustodyJurisdiction:
    """UCCJEA home state determination."""
    child_id: str
    state_residence_months: Dict[str, int]  # state -> months
    
    def home_state(self) -> str:
        """State where child lived 6+ consecutive months."""
        for state, months in self.state_residence_months.items():
            if months >= 6:
                return state
        return "undetermined"


@dataclass
class AssetDivider:
    """Community property division."""
    total_assets: Fraction
    spouse1_contribution: Fraction
    spouse2_contribution: Fraction
    
    def equitable_division(self) -> Dict[str, Fraction]:
        """50/50 split of community property."""
        half = self.total_assets / Fraction(2)
        return {
            "spouse1": half,
            "spouse2": half
        }
