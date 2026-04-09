#!/usr/bin/env python3
"""
Employment Law Domain — FLSA, Title VII, FMLA

Key statutes:
- FLSA: Fair Labor Standards Act
- Title VII: Civil Rights Act employment discrimination
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum, auto


class PayType(Enum):
    HOURLY = auto()
    SALARY = auto()


@dataclass
class Employee:
    """Employee with wage/hour data."""
    employee_id: str
    pay_type: PayType
    hourly_rate: Fraction = Fraction(0)
    hours_worked: Fraction = Fraction(0)
    
    FEDERAL_MINIMUM_WAGE = Fraction(725, 100)  # $7.25
    OVERTIME_THRESHOLD = Fraction(40)
    OVERTIME_MULTIPLIER = Fraction(3, 2)
    
    def regular_hours(self) -> Fraction:
        return min(self.hours_worked, self.OVERTIME_THRESHOLD)
    
    def overtime_hours(self) -> Fraction:
        return max(Fraction(0), self.hours_worked - self.OVERTIME_THRESHOLD)
    
    def regular_pay(self) -> Fraction:
        return self.regular_hours() * self.hourly_rate
    
    def overtime_pay(self) -> Fraction:
        overtime_rate = self.hourly_rate * self.OVERTIME_MULTIPLIER
        return self.overtime_hours() * overtime_rate
    
    def total_pay(self) -> Fraction:
        return self.regular_pay() + self.overtime_pay()
    
    def effective_hourly_rate(self) -> Fraction:
        if self.hours_worked == 0:
            return Fraction(0)
        return self.total_pay() / self.hours_worked


@dataclass
class WageCalculator:
    """Calculate FLSA-compliant wages."""
    employee: Employee
    
    def meets_minimum_wage(self) -> bool:
        return self.employee.hourly_rate >= self.employee.FEDERAL_MINIMUM_WAGE


@dataclass
class WorkforceDemographics:
    """Demographic data for disparate impact analysis."""
    group_id: str
    total_employees: int
    total_applicants: int
    selected_count: int
    
    def selection_rate(self) -> Fraction:
        if self.total_applicants == 0:
            return Fraction(0)
        return Fraction(self.selected_count, self.total_applicants)


@dataclass
class DisparateImpactAnalyzer:
    """Analyze for disparate impact under Title VII."""
    groups: List[WorkforceDemographics]
    
    def four_fifths_rule(self) -> List[tuple]:
        """
        4/5ths rule: A group's selection rate < 80% of highest rate
        suggests disparate impact.
        """
        if len(self.groups) < 2:
            return []
        
        max_rate = max(g.selection_rate() for g in self.groups)
        threshold = max_rate * Fraction(4, 5)
        
        violations = []
        for g in self.groups:
            if g.selection_rate() < threshold:
                violations.append((g.group_id, g.selection_rate(), threshold))
        
        return violations


# Employment law thresholds
DISPARATE_IMPACT_THRESHOLD = Fraction(4, 5)  # 80%
