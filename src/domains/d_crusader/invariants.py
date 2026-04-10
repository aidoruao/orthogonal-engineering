#!/usr/bin/env python3
"""D_CRUSADER Invariants — Historical Military Law, Rules of War

Verifies just war theory (Aquinas), chivalric code, combatant protections,
siege law, ransom limits, noncombatant immunity.
Summa Theologica II-II Q.40 (1265-1274), Geneva Convention precursors.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    MilitaryOrder, RulesOfWar, Combatant, NonCombatant, SiegeLaw,
    JustCause, CombatantStatus,
    ransom_limit_knight, siege_duration_limit
)


def check_just_war_criteria(order: MilitaryOrder) -> Tuple[bool, ProofObject]:
    """
    Just war requires: just cause, legitimate authority, proportionality, necessity.

    Aquinas Summa Theologica II-II Q.40: Three conditions for just war:
    1. Legitimate authority (sovereign prince)
    2. Just cause (defense, recovery, punishment)
    3. Right intention (proportional, necessary)

    Falsifies if: any criterion fails
    """
    criteria = [
        ("legitimate_authority", order.legitimate_authority, "Legitimate authority required"),
        ("proportional", order.proportional, "Proportional force required"),
        ("necessity", order.necessity, "Necessity criterion required")
    ]

    failed = [name for name, value, _ in criteria if not value]

    if failed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Military order {order.order_id} fails just war criteria: {', '.join(failed)}",
            premises=[
                f"Order: {order.order_id}",
                f"Just cause: {order.just_cause.name}",
                f"Authority: {order.legitimate_authority}",
                f"Proportional: {order.proportional}",
                f"Necessary: {order.necessity}"
            ],
            rule="just_war_aquinas_ii_ii_q40"
        )

    return True, ProofObject(
        conclusion=f"Military order {order.order_id} satisfies just war criteria",
        premises=[f"Cause: {order.just_cause.name}", "All 3 Aquinas criteria met"],
        rule="just_war_aquinas_ii_ii_q40"
    )


def check_noncombatant_protection(rules: RulesOfWar) -> Tuple[bool, ProofObject]:
    """
    Noncombatants must be protected from intentional harm.

    Chivalric code and medieval church law: Clergy, women, children, merchants
    have immunity from deliberate targeting.

    Falsifies if: noncombatant_protection = False
    """
    if not rules.noncombatant_protection:
        return False, ProofObject(
            conclusion=f"VIOLATION: Rules {rules.rule_id} fail to protect noncombatants",
            premises=[
                f"Rule ID: {rules.rule_id}",
                f"Noncombatant protection: {rules.noncombatant_protection}",
                "Church law requires noncombatant immunity"
            ],
            rule="noncombatant_immunity"
        )

    return True, ProofObject(
        conclusion=f"Rules {rules.rule_id} protect noncombatants",
        premises=["Noncombatant protection enforced"],
        rule="noncombatant_immunity"
    )


def check_quarter_granted(combatant: Combatant, rules: RulesOfWar) -> Tuple[bool, ProofObject]:
    """
    Surrendering enemy must be granted quarter (mercy).

    Chivalric code: Knights and men-at-arms who surrender must not be killed.
    Refusal to grant quarter is a violation of the code of chivalry.

    Falsifies if: combatant.captured=True and combatant.quarter_given=False
    """
    if combatant.captured and not combatant.quarter_given:
        return False, ProofObject(
            conclusion=f"VIOLATION: Combatant {combatant.combatant_id} captured but no quarter granted",
            premises=[
                f"Combatant: {combatant.name} ({combatant.status.name})",
                f"Captured: {combatant.captured}",
                f"Quarter given: {combatant.quarter_given}",
                "Chivalric code requires quarter for surrendering enemy"
            ],
            rule="quarter_chivalric_code"
        )

    if not combatant.captured:
        return True, ProofObject(
            conclusion=f"Combatant {combatant.combatant_id} not captured, quarter N/A",
            premises=[f"Captured: {combatant.captured}"],
            rule="quarter_chivalric_code"
        )

    return True, ProofObject(
        conclusion=f"Combatant {combatant.combatant_id} granted quarter",
        premises=[f"Quarter given: {combatant.quarter_given}"],
        rule="quarter_chivalric_code"
    )


def check_ransom_limits(combatant: Combatant) -> Tuple[bool, ProofObject]:
    """
    Ransom must not exceed one year's income for the captive's rank.

    Medieval custom: Ransom is based on social status. Knights may be ransomed
    for approximately one year's income. Excessive ransom is considered extortion.

    Falsifies if: ransom_demanded > 365 (days of income) for knight
    """
    if combatant.status != CombatantStatus.KNIGHT:
        return True, ProofObject(
            conclusion=f"Combatant {combatant.combatant_id} not knight, ransom limit N/A",
            premises=[f"Status: {combatant.status.name}"],
            rule="ransom_custom"
        )

    limit = ransom_limit_knight()

    if combatant.ransom_demanded > limit:
        return False, ProofObject(
            conclusion=f"VIOLATION: Ransom {combatant.ransom_demanded} exceeds limit {limit} for knight {combatant.name}",
            premises=[
                f"Ransom demanded: {combatant.ransom_demanded}",
                f"Limit: {limit}",
                f"Status: {combatant.status.name}",
                "Medieval custom: ransom <= 1 year income"
            ],
            rule="ransom_custom"
        )

    return True, ProofObject(
        conclusion=f"Ransom {combatant.ransom_demanded} within limit for knight {combatant.name}",
        premises=[f"{combatant.ransom_demanded} <= {limit}"],
        rule="ransom_custom"
    )


def check_siege_law_compliance(siege: SiegeLaw) -> Tuple[bool, ProofObject]:
    """
    Siege must allow noncombatants to exit, offer surrender, and not exceed duration limit.

    Medieval siege law: After 40 days, garrison must be offered honorable surrender.
    Noncombatants must be allowed to leave. Starvation as sole tactic is prohibited.

    Falsifies if: duration > 40 days without surrender offer, or noncombatants not allowed exit
    """
    limit = siege_duration_limit()
    violations = []

    if not siege.surrender_offered and siege.duration_days > limit:
        violations.append(f"No surrender offered after {siege.duration_days} days (limit {limit})")

    if not siege.noncombatants_allowed_exit:
        violations.append("Noncombatants not allowed exit")

    if siege.starvation_used and not siege.surrender_offered:
        violations.append("Starvation used without surrender offer")

    if violations:
        return False, ProofObject(
            conclusion=f"VIOLATION: Siege of {siege.city} violates siege law: {'; '.join(violations)}",
            premises=[
                f"Siege ID: {siege.siege_id}",
                f"Duration: {siege.duration_days} days",
                f"Surrender offered: {siege.surrender_offered}",
                f"Noncombatants exit: {siege.noncombatants_allowed_exit}",
                f"Starvation: {siege.starvation_used}"
            ],
            rule="siege_law_medieval"
        )

    return True, ProofObject(
        conclusion=f"Siege of {siege.city} complies with siege law",
        premises=[
            f"Duration: {siege.duration_days} days",
            f"Surrender: {siege.surrender_offered}",
            f"Noncombatants exit: {siege.noncombatants_allowed_exit}"
        ],
        rule="siege_law_medieval"
    )


def check_proportional_force(rules: RulesOfWar) -> Tuple[bool, ProofObject]:
    """
    Force used must be proportional to threat and military objective.

    Just war theory: Military force must be proportional - not excessive or
    indiscriminate. Wanton destruction beyond military necessity is forbidden.

    Falsifies if: proportional_force = False
    """
    if not rules.proportional_force:
        return False, ProofObject(
            conclusion=f"VIOLATION: Rules {rules.rule_id} permit disproportionate force",
            premises=[
                f"Rule ID: {rules.rule_id}",
                f"Proportional force: {rules.proportional_force}",
                "Just war theory requires proportionality"
            ],
            rule="proportional_force_just_war"
        )

    return True, ProofObject(
        conclusion=f"Rules {rules.rule_id} enforce proportional force",
        premises=["Proportional force criterion satisfied"],
        rule="proportional_force_just_war"
    )
