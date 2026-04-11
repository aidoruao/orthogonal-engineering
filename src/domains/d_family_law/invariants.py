#!/usr/bin/env python3
"""Family Law Invariants — Child support, custody, asset division."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import ChildSupportCalculator, CustodyJurisdiction, AssetDivider


def check_support_calculation(calc: ChildSupportCalculator) -> Tuple[bool, ProofObject]:
    """Child support must be proportional to income shares.

    Falsifies if: sum of calculated obligations differs from basic_support_obligation.
    """
    obligations = calc.calculate_support()
    total = sum(obligations.values())
    
    if total != calc.basic_support_obligation:
        return False, ProofObject(
            conclusion=f"VIOLATION: Support obligations sum to {total}, expected {calc.basic_support_obligation}",
            premises=[],
            rule="child_support_calculation"
        )
    
    return True, ProofObject(
        conclusion=f"Support calculation correct (total: {total})",
        premises=[],
        rule="child_support_calculation"
    )


def check_home_state_determination(jurisdiction: CustodyJurisdiction) -> Tuple[bool, ProofObject]:
    """UCCJEA: Home state requires 6+ consecutive months.

    Falsifies if: jurisdiction.home_state() returns \"undetermined\".
    """
    home = jurisdiction.home_state()
    
    if home == "undetermined":
        return False, ProofObject(
            conclusion="VIOLATION: No home state established (insufficient residence)",
            premises=[],
            rule="uccjea_home_state"
        )
    
    return True, ProofObject(
        conclusion=f"Home state determined: {home}",
        premises=[],
        rule="uccjea_home_state"
    )


def check_equitable_division(divider: AssetDivider) -> Tuple[bool, ProofObject]:
    """Community property requires equal division.

    Falsifies if: distributed total differs from assets or spouse shares are unequal.
    """
    division = divider.equitable_division()
    total_distributed = sum(division.values())
    
    if total_distributed != divider.total_assets:
        return False, ProofObject(
            conclusion=f"VIOLATION: Division sums to {total_distributed}, assets are {divider.total_assets}",
            premises=[],
            rule="community_property_division"
        )
    
    # Check equal split
    share1 = division.get("spouse1", Fraction(0))
    share2 = division.get("spouse2", Fraction(0))
    
    if share1 != share2:
        return False, ProofObject(
            conclusion=f"VIOLATION: Unequal division ({share1} vs {share2})",
            premises=[],
            rule="community_property_division"
        )
    
    return True, ProofObject(
        conclusion=f"Equal division confirmed ({share1} each)",
        premises=[],
        rule="community_property_division"
    )
