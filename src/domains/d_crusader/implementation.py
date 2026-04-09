"""D_CRUSADER implementation — Historical Military Law, Rules of War

Layer: 3 (Historical/Legal)
CardinalStrength: PREDICATIVE

Crusader-era military law, chivalric code, just war theory, rules of engagement.
Aquinas (1265-1274): Summa Theologica on Just War. Geneva Conventions (historical precedents).
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import List, Optional


class CombatantStatus(Enum):
    """Combatant classification"""
    KNIGHT = 1
    MAN_AT_ARMS = 2
    ARCHER = 3
    PEASANT_LEVY = 4
    NON_COMBATANT = 5


class JustCause(Enum):
    """Just war causes per Aquinas"""
    DEFENSIVE = 1
    RECOVERY_OF_TERRITORY = 2
    PUNISHMENT_OF_WRONGDOING = 3
    RELIGIOUS = 4


@dataclass
class MilitaryOrder:
    """Military order or command"""
    order_id: str
    issuing_authority: str
    just_cause: JustCause
    proportional: bool
    necessity: bool
    legitimate_authority: bool


@dataclass
class RulesOfWar:
    """Rules of war enforcement"""
    rule_id: str
    noncombatant_protection: bool
    quarter_granted: bool  # Mercy to surrendering enemy
    siege_law_followed: bool
    proportional_force: bool


@dataclass
class Combatant:
    """Military combatant"""
    combatant_id: str
    name: str
    status: CombatantStatus
    captured: bool
    ransom_demanded: Fraction  # In currency units
    quarter_given: bool


@dataclass
class NonCombatant:
    """Protected non-combatant"""
    person_id: str
    protected_status: str  # Clergy, women, children, merchants
    immunity_granted: bool


@dataclass
class SiegeLaw:
    """Siege warfare law"""
    siege_id: str
    city: str
    surrender_offered: bool
    noncombatants_allowed_exit: bool
    starvation_used: bool
    duration_days: Fraction


def ransom_limit_knight() -> Fraction:
    """Maximum ransom for knight (1 year income)"""
    return Fraction(365, 1)  # Days


def siege_duration_limit() -> Fraction:
    """Maximum siege duration before quarter must be given (days)"""
    return Fraction(40, 1)
