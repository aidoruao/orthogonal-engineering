"""D_SEPARATION_OF_POWERS implementation — Separation of Powers

Implements checks for executive, legislative, and judicial branch separation.
Ensures no branch exercises powers belonging to another branch.

Layer: 1 (Constitutional)
CardinalStrength: INACCESSIBLE
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum, auto
from fractions import Fraction


class Branch(Enum):
    """The three branches of government."""
    EXECUTIVE = auto()
    LEGISLATIVE = auto()
    JUDICIAL = auto()


class GovernmentPower(Enum):
    """Powers assigned to specific branches."""
    MAKING_LAWS = auto()           # Legislative
    ENFORCING_LAWS = auto()        # Executive
    INTERPRETING_LAWS = auto()     # Judicial
    APPOINTING_JUDGES = auto()     # Executive (with advice/consent)
    DECLARING_WAR = auto()         # Legislative
    COMMANDING_MILITARY = auto()   # Executive
    ISSUING_VETO = auto()          # Executive check on Legislative
    IMPEACHMENT = auto()           # Legislative check on Executive/Judicial


class SeparationViolation(Enum):
    """Types of separation of powers violations."""
    EXECUTIVE_LEGISLATING = auto()
    LEGISLATURE_ADJUDICATING = auto()
    JUDICIARY_ENFORCING = auto()
    SELF_DEALING = auto()
    NON_DELEGATION = auto()


POWER_ASSIGNMENTS: dict[GovernmentPower, Branch] = {
    GovernmentPower.MAKING_LAWS: Branch.LEGISLATIVE,
    GovernmentPower.ENFORCING_LAWS: Branch.EXECUTIVE,
    GovernmentPower.INTERPRETING_LAWS: Branch.JUDICIAL,
    GovernmentPower.APPOINTING_JUDGES: Branch.EXECUTIVE,
    GovernmentPower.DECLARING_WAR: Branch.LEGISLATIVE,
    GovernmentPower.COMMANDING_MILITARY: Branch.EXECUTIVE,
    GovernmentPower.ISSUING_VETO: Branch.EXECUTIVE,
    GovernmentPower.IMPEACHMENT: Branch.LEGISLATIVE,
}


@dataclass
class PowerExercise:
    """Record of a branch exercising a power."""
    branch: Branch
    power: GovernmentPower
    description: str
    claimed_authority: str
    
    def is_constitutional(self) -> bool:
        """Check if this power exercise is constitutional."""
        assigned_branch = POWER_ASSIGNMENTS.get(self.power)
        if assigned_branch is None:
            return False  # Unknown power assignment
        return self.branch == assigned_branch


@dataclass
class SeparationCheckResult:
    """Result of separation of powers check."""
    constitutional: bool
    violations: List[SeparationViolation]
    action_description: str
    remediation_required: bool
    severity_score: Fraction = field(init=False)
    
    def __post_init__(self):
        """Calculate severity based on number of violations."""
        self.severity_score = Fraction(len(self.violations), 1)


class BranchAuthority:
    """Authority and powers of a government branch."""
    
    def __init__(self, branch: Branch):
        self.branch = branch
        self.powers_exercised: List[PowerExercise] = []
        self.checks_made: int = 0
    
    def exercise_power(
        self,
        power: GovernmentPower,
        description: str,
        claimed_authority: str,
    ) -> SeparationCheckResult:
        """Attempt to exercise a power and check constitutionality."""
        self.checks_made += 1
        
        exercise = PowerExercise(
            branch=self.branch,
            power=power,
            description=description,
            claimed_authority=claimed_authority,
        )
        self.powers_exercised.append(exercise)
        
        violations = []
        
        if not exercise.is_constitutional():
            # Determine violation type
            if self.branch == Branch.EXECUTIVE and power == GovernmentPower.MAKING_LAWS:
                violations.append(SeparationViolation.EXECUTIVE_LEGISLATING)
            elif self.branch == Branch.LEGISLATIVE and power == GovernmentPower.INTERPRETING_LAWS:
                violations.append(SeparationViolation.LEGISLATURE_ADJUDICATING)
            elif self.branch == Branch.JUDICIAL and power == GovernmentPower.ENFORCING_LAWS:
                violations.append(SeparationViolation.JUDICIARY_ENFORCING)
            else:
                violations.append(SeparationViolation.NON_DELEGATION)
        
        return SeparationCheckResult(
            constitutional=len(violations) == 0,
            violations=violations,
            action_description=description,
            remediation_required=len(violations) > 0,
        )
    
    def can_exercise(self, power: GovernmentPower) -> bool:
        """Check if this branch can constitutionally exercise this power."""
        return POWER_ASSIGNMENTS.get(power) == self.branch


class SeparationOfPowersChecker:
    """Comprehensive separation of powers checker."""
    
    def __init__(self):
        self.executive = BranchAuthority(Branch.EXECUTIVE)
        self.legislative = BranchAuthority(Branch.LEGISLATIVE)
        self.judicial = BranchAuthority(Branch.JUDICIAL)
        self.all_violations: List[SeparationCheckResult] = []
    
    def check_executive_action(
        self,
        power: GovernmentPower,
        description: str,
        claimed_authority: str,
    ) -> SeparationCheckResult:
        """Check executive action for separation of powers compliance."""
        result = self.executive.exercise_power(power, description, claimed_authority)
        if not result.constitutional:
            self.all_violations.append(result)
        return result
    
    def check_legislative_action(
        self,
        power: GovernmentPower,
        description: str,
        claimed_authority: str,
    ) -> SeparationCheckResult:
        """Check legislative action for separation of powers compliance."""
        result = self.legislative.exercise_power(power, description, claimed_authority)
        if not result.constitutional:
            self.all_violations.append(result)
        return result
    
    def check_judicial_action(
        self,
        power: GovernmentPower,
        description: str,
        claimed_authority: str,
    ) -> SeparationCheckResult:
        """Check judicial action for separation of powers compliance."""
        result = self.judicial.exercise_power(power, description, claimed_authority)
        if not result.constitutional:
            self.all_violations.append(result)
        return result
    
    def check_self_dealing(
        self, branch: Branch, action_benefits_branch: bool) -> Optional[SeparationViolation]:
        """
        Check for self-dealing (branch expanding its own power).
        
        This catches cases where a branch attempts to authorize its own
        expansion of authority.
        """
        if action_benefits_branch:
            return SeparationViolation.SELF_DEALING
        return None
    
    def get_violation_summary(self) -> dict:
        """Get summary of all separation of powers violations."""
        total_checks = (
            self.executive.checks_made +
            self.legislative.checks_made +
            self.judicial.checks_made
        )
        
        by_type = {}
        for violation in SeparationViolation:
            by_type[violation.name] = sum(
                1 for r in self.all_violations 
                if violation in r.violations
            )
        
        return {
            "total_checks": total_checks,
            "violations": len(self.all_violations),
            "by_type": by_type,
        }


def check_non_delegation_doctrine(
    legislative_power: GovernmentPower,
    delegated_to: Branch,
) -> bool:
    """
    Check if power delegation complies with non-delegation doctrine.
    
    The non-delegation doctrine prohibits Congress from delegating its
    legislative powers to other branches.
    
    Returns True if delegation is constitutional, False otherwise.
    """
    # Legislative power cannot be delegated to executive or judicial
    if legislative_power == GovernmentPower.MAKING_LAWS:
        if delegated_to != Branch.LEGISLATIVE:
            return False
    return True


@dataclass(frozen=True)
class ExecutiveAction:
    """An executive branch action subject to separation of powers analysis."""
    action_id: str
    statutory_authorization: bool
    commander_in_chief_power: bool
    legislative_veto_used: bool  # unconstitutional per INS v. Chadha
    congress_acquiescence: bool
    judicial_review_available: bool


@dataclass(frozen=True)
class LegislativeAction:
    """A legislative action subject to presentment and bicameralism requirements."""
    action_id: str
    enumerated_power_basis: str
    presentment_followed: bool
    bicameralism_followed: bool
    nondelegation_intelligible_principle: bool
