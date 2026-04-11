#!/usr/bin/env python3
"""Ethics Domain Invariants — Moral reasoning consistency and constraint checking.

Theoretical Standards:
- Kantian categorical imperative (3 formulations)
- Utilitarianism (expected utility)
- Virtue ethics (mean between extremes)
- Contractualism (reasonable rejectability)

Falsifies if:
- Maxim fails universal law test
- Person treated merely as means
- Utility calculation violates dominance
- Virtue evaluation inconsistent
"""

from fractions import Fraction
from typing import Tuple, Callable
from axioms.logic import ProofObject
from .implementation import (
    Maxim, Action, CategoricalImperative, VirtueEvaluation,
    ContractualistEvaluation, MoralAgent
)


def check_universal_law(maxim: Maxim, coherence_fn: Callable[[str], bool]) -> Tuple[bool, ProofObject]:
    """Kant's first formulation: Can maxim be willed as universal law?
    
    Falsifies if: universalized maxim is incoherent or creates contradiction in conception.
    """
    universal = maxim.universal_form()
    coherent = coherence_fn(universal)
    
    if not coherent:
        return False, ProofObject(
            conclusion="VIOLATION: Maxim cannot be universalized without contradiction",
            premises=[
                f"Maxim: {universal}",
                "Fails universal law test (contradiction in conception)"
            ],
            rule="kant_categorical_imperative_universal_law"
        )
    
    return True, ProofObject(
        conclusion="Maxim passes universal law test",
        premises=[f"Universal form: {universal}"],
        rule="kant_universal_law_satisfied"
    )


def check_humanity_as_end(action: Action) -> Tuple[bool, ProofObject]:
    """Kant's second formulation: Treat humanity as end, never merely as means.
    
    Falsifies if: rational persons are harmed or used merely as means without regard for dignity.
    """
    persons_used_as_means = []
    
    for consequence in action.consequences:
        for agent in consequence.affected_agents:
            if agent.is_person() and consequence.utility_change < Fraction(0):
                persons_used_as_means.append(agent.agent_id)
    
    if persons_used_as_means:
        return False, ProofObject(
            conclusion="VIOLATION: Rational persons treated merely as means",
            premises=[
                f"Affected persons: {persons_used_as_means}",
                "Kantian dignity violated"
            ],
            rule="kant_categorical_imperative_humanity_as_end"
        )
    
    return True, ProofObject(
        conclusion="Action respects persons as ends in themselves",
        premises=["No persons used merely as means"],
        rule="kant_humanity_as_end_satisfied"
    )


def check_utilitarian_dominance(action_a: Action, action_b: Action) -> Tuple[bool, ProofObject]:
    """Utilitarian dominance: If A has >= utility for all and > for some, A dominates B.
    
    Falsifies if: chosen action is dominated by an available higher-utility alternative.
    """
    util_a = action_a.total_expected_utility()
    util_b = action_b.total_expected_utility()
    
    if util_b > util_a:
        return False, ProofObject(
            conclusion="VIOLATION: Action dominated by higher-utility alternative",
            premises=[
                f"Chosen: {action_a.action_id} (utility: {util_a})",
                f"Dominates: {action_b.action_id} (utility: {util_b})"
            ],
            rule="utilitarian_dominance_principle"
        )
    
    return True, ProofObject(
        conclusion="Action not dominated by available alternative",
        premises=[f"Utility: {util_a}"],
        rule="utilitarian_non_dominated"
    )


def check_virtue_mean(virtue: Virtue, action_trait: str) -> Tuple[bool, ProofObject]:
    """Aristotelian virtue: action should demonstrate mean between excess and deficiency.
    
    Falsifies if: action demonstrates excess or deficiency rather than virtuous mean.
    """
    if action_trait == virtue.excess:
        return False, ProofObject(
            conclusion=f"VIOLATION: Action demonstrates excess ({virtue.excess}) instead of mean ({virtue.virtue_name})",
            premises=[
                f"Virtue: {virtue.virtue_name}",
                f"Excess: {virtue.excess}",
                f"Deficiency: {virtue.deficiency}",
                f"Demonstrated: {action_trait}"
            ],
            rule="aristotelian_virtue_mean"
        )
    
    if action_trait == virtue.deficiency:
        return False, ProofObject(
            conclusion=f"VIOLATION: Action demonstrates deficiency ({virtue.deficiency}) instead of mean ({virtue.virtue_name})",
            premises=[
                f"Virtue: {virtue.virtue_name}",
                f"Deficiency: {virtue.deficiency}",
                f"Demonstrated: {action_trait}"
            ],
            rule="aristotelian_virtue_mean"
        )
    
    return True, ProofObject(
        conclusion="Action demonstrates virtuous mean",
        premises=[f"Virtue: {virtue.virtue_name}", f"Trait: {action_trait}"],
        rule="virtue_mean_satisfied"
    )


def check_contractualist_rejectability(evaluation: ContractualistEvaluation) -> Tuple[bool, ProofObject]:
    """Scanlonian contractualism: principle must not be reasonably rejectable.
    
    Falsifies if: any agent can reasonably reject the principle due to disproportionate burden.
    """
    rejecting_agents = []
    
    for agent_id in evaluation.stakes:
        if evaluation.reasonably_rejectable_by(agent_id):
            rejecting_agents.append((agent_id, evaluation.stakes[agent_id]))
    
    if rejecting_agents:
        return False, ProofObject(
            conclusion="VIOLATION: Principle reasonably rejectable by affected agents",
            premises=[
                f"Rejecting agents: {rejecting_agents}",
                f"Principle: {evaluation.principle}"
            ],
            rule="scanlon_contractualism_rejectability"
        )
    
    return True, ProofObject(
        conclusion="Principle not reasonably rejectable by any agent",
        premises=[f"Agents considered: {len(evaluation.stakes)}"],
        rule="contractualism_satisfied"
    )


def check_agent_autonomy(agent: MoralAgent) -> Tuple[bool, ProofObject]:
    """Moral agency requires both rationality and autonomy.
    
    Falsifies if: agent lacks rationality while claiming autonomy, or lacks autonomy despite rationality.
    """
    if not agent.rational and agent.autonomous:
        return False, ProofObject(
            conclusion="VIOLATION: Agent claims autonomy without rationality",
            premises=[f"Rational: {agent.rational}", f"Autonomous: {agent.autonomous}"],
            rule="moral_agency_rationality_required"
        )
    
    if agent.rational and not agent.autonomous:
        return False, ProofObject(
            conclusion="VIOLATION: Rational agent lacks autonomy",
            premises=[f"Agent: {agent.agent_id}", "Rational but not self-legislating"],
            rule="moral_agency_autonomy_required"
        )
    
    return True, ProofObject(
        conclusion="Agent satisfies moral agency conditions",
        premises=[f"Personhood: {agent.is_person()}"],
        rule="moral_agency_valid"
    )
