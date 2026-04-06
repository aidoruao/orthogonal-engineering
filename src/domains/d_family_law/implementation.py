"""D_FAMILY_LAW implementation — Family Law

Implements family law principles including custody determinations,
child support calculations, and best interest of the child analysis.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Uniform Marriage and Divorce Act (UMDA), Child Support Standards Act,
        State custody statutes, ICPC (Interstate Compact on Placement of Children)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from fractions import Fraction


class CustodyType(Enum):
    """Types of custody arrangements."""
    SOLE_PHYSICAL = auto()          # Child resides primarily with one parent
    SOLE_LEGAL = auto()             # One parent makes major decisions
    JOINT_PHYSICAL = auto()         # Child resides with both parents
    JOINT_LEGAL = auto()            # Both parents make major decisions
    SPLIT = auto()                  # Different children to different parents


class CustodyFactor(Enum):
    """Factors considered in custody determinations."""
    PARENTAL_WISHES = auto()        # Wishes of the parents
    CHILD_WISHES = auto()           # Wishes of the child (if mature)
    INTERPERSONAL_RELATIONSHIP = auto()  # Child's relationship with each parent
    ADJUSTMENT = auto()             # Child's adjustment to home/school/community
    MENTAL_PHYSICAL_HEALTH = auto()  # Mental and physical health of all parties
    DOMESTIC_VIOLENCE = auto()      # Evidence of domestic violence
    SUBSTANCE_ABUSE = auto()        # Evidence of substance abuse
    STABILITY = auto()              # Stability of proposed home environment
    COOPERATION = auto()            # Willingness to cooperate with other parent


@dataclass
class Parent:
    """A parent in a custody or support proceeding."""
    name: str
    parent_id: str
    annual_income: Fraction
    has_primary_physical: bool = False
    overnight_nights: int = 0  # Number of overnights per year
    parenting_time_percentage: Fraction = field(default_factory=lambda: Fraction(0))
    
    def __post_init__(self):
        """Calculate parenting time percentage from overnights."""
        if self.overnight_nights > 0 and self.parenting_time_percentage == 0:
            self.parenting_time_percentage = Fraction(self.overnight_nights, 365)


@dataclass
class Child:
    """A child in a family law proceeding."""
    name: str
    child_id: str
    age: int
    special_needs: bool = False
    special_needs_costs: Fraction = field(default_factory=lambda: Fraction(0))
    preferences: Optional[str] = None
    maturity_level: Optional[str] = None  # "immature", "developing", "mature"


@dataclass
class CustodyEvaluation:
    """Evaluation for custody determination."""
    child: Child
    parents: List[Parent]
    current_arrangement: str = ""
    
    # Factor scores (0-10, higher is better for custodial parent)
    factor_scores: Dict[str, Dict[CustodyFactor, int]] = field(default_factory=dict)
    
    def score_parent_on_factor(self, parent_id: str, factor: CustodyFactor, score: int):
        """Score a parent on a specific custody factor."""
        if parent_id not in self.factor_scores:
            self.factor_scores[parent_id] = {}
        self.factor_scores[parent_id][factor] = max(0, min(10, score))
    
    def get_parent_score(self, parent_id: str) -> int:
        """Get total score for a parent across all factors."""
        scores = self.factor_scores.get(parent_id, {})
        return sum(scores.values())
    
    def get_primary_custodian(self) -> Optional[str]:
        """Get parent with highest custody score."""
        if not self.parents:
            return None
        
        return max(
            self.parents,
            key=lambda p: self.get_parent_score(p.parent_id),
        ).parent_id


class BestInterestAnalyzer:
    """Analyzer for "best interest of the child" standard.
    
    The best interest standard is the cornerstone of family law—
    reflecting the biblical principle that children are to be
    protected and nurtured (Psalm 127:3: "Children are a heritage
    from the LORD").
    """
    
    def __init__(self):
        self.relevant_factors: Set[CustodyFactor] = set(CustodyFactor)
    
    def evaluate_best_interest(
        self,
        evaluation: CustodyEvaluation,
    ) -> Dict:
        """Comprehensive best interest evaluation.
        
        Args:
            evaluation: The custody evaluation to analyze
            
        Returns:
            Best interest analysis with recommendation
        """
        child = evaluation.child
        parents = evaluation.parents
        
        analysis = {
            "child_id": child.child_id,
            "child_age": child.age,
            "factors_evaluated": [],
            "parent_scores": {},
            "concerns": [],
            "recommendation": None,
        }
        
        # Evaluate each factor
        for factor in self.relevant_factors:
            factor_analysis = self._analyze_factor(factor, evaluation)
            analysis["factors_evaluated"].append(factor_analysis)
            
            if factor_analysis.get("concern"):
                analysis["concerns"].append(factor_analysis["concern"])
        
        # Calculate parent scores
        for parent in parents:
            score = evaluation.get_parent_score(parent.parent_id)
            analysis["parent_scores"][parent.name] = score
        
        # Determine recommendation
        if len(parents) == 2:
            score_0 = evaluation.get_parent_score(parents[0].parent_id)
            score_1 = evaluation.get_parent_score(parents[1].parent_id)
            
            # If scores are close, recommend joint custody
            score_diff = abs(score_0 - score_1)
            if score_diff <= 5:
                analysis["recommendation"] = "JOINT_CUSTODY"
            elif score_0 > score_1:
                analysis["recommendation"] = f"PRIMARY_TO_{parents[0].name}"
            else:
                analysis["recommendation"] = f"PRIMARY_TO_{parents[1].name}"
        
        return analysis
    
    def _analyze_factor(
        self,
        factor: CustodyFactor,
        evaluation: CustodyEvaluation,
    ) -> Dict:
        """Analyze a specific custody factor."""
        child = evaluation.child
        
        result = {
            "factor": factor.name,
            "weight": "HIGH" if factor in [
                CustodyFactor.DOMESTIC_VIOLENCE,
                CustodyFactor.SUBSTANCE_ABUSE,
                CustodyFactor.STABILITY,
            ] else "NORMAL",
        }
        
        # Special handling for child's wishes
        if factor == CustodyFactor.CHILD_WISHES:
            if child.maturity_level == "mature" and child.age >= 14:
                result["considered"] = True
                result["child_input_weight"] = "HIGH"
            elif child.maturity_level == "developing" and child.age >= 10:
                result["considered"] = True
                result["child_input_weight"] = "MODERATE"
            else:
                result["considered"] = False
                result["reason"] = "Child too young or immature"
        
        # Check for domestic violence concerns
        if factor == CustodyFactor.DOMESTIC_VIOLENCE:
            for parent_id, scores in evaluation.factor_scores.items():
                if scores.get(CustodyFactor.DOMESTIC_VIOLENCE, 10) < 5:
                    result["concern"] = f"Domestic violence issue with parent {parent_id}"
        
        return result


class ChildSupportCalculator:
    """Calculator for child support obligations.
    
    Implements income shares model—both parents contribute according
    to their ability to pay, reflecting shared responsibility for
    children's welfare (1 Timothy 5:8: "Anyone who does not provide
    for their relatives... has denied the faith").
    """
    
    # Basic support schedule (simplified)
    # Maps combined income to basic support obligation
    def __init__(self):
        self.basic_support_percentages = {
            1: Fraction(17, 100),   # 1 child: 17%
            2: Fraction(25, 100),   # 2 children: 25%
            3: Fraction(29, 100),   # 3 children: 29%
            4: Fraction(31, 100),   # 4 children: 31%
            5: Fraction(34, 100),   # 5+ children: 34%
        }
    
    def calculate_support(
        self,
        parents: List[Parent],
        children: List[Child],
        custodial_parent_id: str,
    ) -> Dict:
        """Calculate child support obligation.
        
        Args:
            parents: List of parents
            children: List of children
            custodial_parent_id: ID of parent with primary custody
            
        Returns:
            Support calculation details
        """
        if len(parents) != 2:
            raise ValueError("Income shares model requires exactly 2 parents")
        
        # Calculate combined income
        combined_income = sum((p.annual_income for p in parents), Fraction(0))
        
        # Get basic support obligation percentage
        num_children = len(children)
        percentage = self.basic_support_percentages.get(
            min(num_children, 5),
            Fraction(34, 100),
        )
        
        # Calculate basic support obligation
        basic_obligation = combined_income * percentage
        
        # Add special needs costs
        special_needs_total = sum(
            (c.special_needs_costs for c in children if c.special_needs),
            Fraction(0),
        )
        total_obligation = basic_obligation + special_needs_total
        
        # Calculate each parent's share
        parent_shares = {}
        for parent in parents:
            income_share = parent.annual_income / combined_income if combined_income > 0 else Fraction(0)
            parent_shares[parent.parent_id] = {
                "income_share": income_share,
                "support_share": total_obligation * income_share,
            }
        
        # Determine obligor (non-custodial parent pays)
        obligor = next(
            (p for p in parents if p.parent_id != custodial_parent_id),
            None,
        )
        
        if obligor is None:
            raise ValueError("Custodial parent not found in parents list")
        
        monthly_obligation = parent_shares[obligor.parent_id]["support_share"] / 12
        
        return {
            "combined_income": combined_income,
            "basic_obligation": basic_obligation,
            "special_needs_costs": special_needs_total,
            "total_obligation": total_obligation,
            "parent_shares": parent_shares,
            "obligor": obligor.name,
            "monthly_obligation": monthly_obligation,
            "annual_obligation": parent_shares[obligor.parent_id]["support_share"],
        }
    
    def adjust_for_parenting_time(
        self,
        base_monthly_obligation: Fraction,
        non_custodial_parent: Parent,
    ) -> Fraction:
        """Adjust support for shared parenting time.
        
        Args:
            base_monthly_obligation: Base monthly support amount
            non_custodial_parent: Non-custodial parent (with parenting time %)
            
        Returns:
            Adjusted monthly obligation
        """
        # If parenting time exceeds certain thresholds, reduce obligation
        parenting_pct = non_custodial_parent.parenting_time_percentage
        
        if parenting_pct >= Fraction(50, 100):
            # Equal time - significant reduction
            return base_monthly_obligation * Fraction(50, 100)
        elif parenting_pct >= Fraction(40, 100):
            # Substantial time - moderate reduction
            return base_monthly_obligation * Fraction(75, 100)
        elif parenting_pct >= Fraction(30, 100):
            # Significant time - slight reduction
            return base_monthly_obligation * Fraction(90, 100)
        
        return base_monthly_obligation


class FamilyLawComplianceChecker:
    """Comprehensive family law compliance checker."""
    
    def __init__(self):
        self.best_interest_analyzer = BestInterestAnalyzer()
        self.support_calculator = ChildSupportCalculator()
    
    def check_custody_compliance(
        self,
        evaluation: CustodyEvaluation,
    ) -> Dict:
        """Check custody arrangement compliance with best interest standard."""
        analysis = self.best_interest_analyzer.evaluate_best_interest(evaluation)
        
        return {
            "compliant": len(analysis["concerns"]) == 0,
            "concerns": analysis["concerns"],
            "analysis": analysis,
        }
    
    def check_support_compliance(
        self,
        parents: List[Parent],
        children: List[Child],
        actual_payment: Fraction,
        custodial_parent_id: str,
    ) -> Dict:
        """Check if support payment complies with guidelines."""
        calculation = self.support_calculator.calculate_support(
            parents, children, custodial_parent_id
        )
        
        expected = calculation["monthly_obligation"]
        variance = abs(actual_payment - expected) / expected if expected > 0 else Fraction(0)
        
        # Within 5% is typically considered compliant
        compliant = variance <= Fraction(5, 100)
        
        return {
            "compliant": compliant,
            "expected_monthly": expected,
            "actual_payment": actual_payment,
            "variance_percentage": variance * 100,
            "variance_amount": actual_payment - expected,
        }


def calculate_child_support(
    parent1_income: Fraction,
    parent2_income: Fraction,
    num_children: int,
    parent1_nights: int = 0,
    parent2_nights: int = 365,
) -> Dict:
    """Convenience function to calculate child support.
    
    Usage:
        result = calculate_child_support(
            parent1_income=Fraction(60000),
            parent2_income=Fraction(40000),
            num_children=2,
            parent1_nights=100,
            parent2_nights=265,
        )
        print(f"Monthly support: ${float(result['monthly']):.2f}")
    """
    parents = [
        Parent(name="Parent1", parent_id="P1", annual_income=parent1_income, overnight_nights=parent1_nights),
        Parent(name="Parent2", parent_id="P2", annual_income=parent2_income, overnight_nights=parent2_nights, has_primary_physical=True),
    ]
    
    children = [
        Child(name=f"Child_{i}", child_id=f"C{i}", age=10)
        for i in range(num_children)
    ]
    
    calculator = ChildSupportCalculator()
    result = calculator.calculate_support(parents, children, "P2")
    
    # Apply parenting time adjustment
    parent1 = parents[0]
    adjusted = calculator.adjust_for_parenting_time(
        result["monthly_obligation"],
        parent1,
    )
    
    return {
        "monthly": adjusted,
        "annual": adjusted * 12,
        "basic_obligation": result["basic_obligation"],
    }
