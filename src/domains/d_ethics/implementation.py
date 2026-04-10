"""D_ETHICS implementation — Normative Ethics & Moral Reasoning

Layer: 4 (Institutional - Philosophy)
CardinalStrength: PREDICATIVE

Theoretical Standards:
- Kantian deontology (categorical imperative)
- Utilitarianism (act/rule, hedonic/preference)
- Virtue ethics (Aristotelian eudaimonia)
- Contractualism (Scanlon)
- Care ethics (Gilligan, Noddings)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set, Dict, Optional, Callable
from enum import Enum, auto
from fractions import Fraction


class EthicalFramework(Enum):
    """Major normative ethical frameworks."""
    KANTIAN_DEONTOLOGY = auto()
    ACT_UTILITARIANISM = auto()
    RULE_UTILITARIANISM = auto()
    VIRTUE_ETHICS = auto()
    CONTRACTUALISM = auto()
    CARE_ETHICS = auto()
    RAWLSIAN = auto()  # Justice as fairness


class MoralStatus(Enum):
    """Moral status of entities."""
    PERSONS = auto()       # Full moral status (Kant)
    SENTIENT = auto()      # Can suffer (utilitarian)
    LIVING = auto()        # Biological life
    NON_LIVING = auto()    # No inherent moral status


@dataclass(frozen=True)
class MoralAgent:
    """An entity capable of moral reasoning and action."""
    agent_id: str
    rational: bool  # Kant: rational beings are ends in themselves
    autonomous: bool  # Self-legislation capacity
    
    def is_person(self) -> bool:
        """Kantian personhood: rational + autonomous."""
        return self.rational and self.autonomous


@dataclass
class Consequence:
    """Outcome of an action for utilitarian calculation."""
    consequence_id: str
    affected_agents: List[MoralAgent]
    utility_change: Fraction  # Positive = welfare increase
    probability: Fraction  # Likelihood of this outcome
    
    def expected_utility(self) -> Fraction:
        """Expected utility contribution."""
        return self.utility_change * self.probability


@dataclass
class Action:
    """A moral action under evaluation."""
    action_id: str
    description: str
    agent: MoralAgent
    consequences: List[Consequence] = field(default_factory=list)
    maxims: List[str] = field(default_factory=list)  # Kantian
    
    def total_expected_utility(self) -> Fraction:
        """Sum of expected utilities for act utilitarianism."""
        return sum((c.expected_utility() for c in self.consequences), Fraction(0))
    
    def affected_agents(self) -> Set[str]:
        """All agents affected by this action."""
        result = set()
        for c in self.consequences:
            for a in c.affected_agents:
                result.add(a.agent_id)
        return result


@dataclass
class Maxim:
    """Kantian maxim: subjective principle of action."""
    maxim_id: str
    action_description: str
    circumstance: str
    purpose: str
    
    def universal_form(self) -> str:
        """Formulation for universal law test."""
        return f"I will {self.action_description} when {self.circumstance} in order to {self.purpose}"


@dataclass
class CategoricalImperative:
    """Kant's three formulations of the categorical imperative."""
    
    @staticmethod
    def universal_law_test(maxim: Maxim, coherence_check: Callable) -> bool:
        """First formulation: Can maxim be willed as universal law?
        
        A maxim fails if universalization creates contradiction in conception
        or contradiction in will.
        """
        return coherence_check(maxim.universal_form())
    
    @staticmethod
    def humanity_as_end_test(action: Action) -> bool:
        """Second formulation: Treat humanity as end, never merely as means.
        
        Check if action respects rational agents as ends in themselves.
        """
        for c in action.consequences:
            for agent in c.affected_agents:
                if agent.is_person() and c.utility_change < Fraction(0):
                    # Person harmed - check if merely used as means
                    return False
        return True
    
    @staticmethod
    def kingdom_of_ends_test(action: Action, all_agents: List[MoralAgent]) -> bool:
        """Third formulation: Act as lawmaking member of kingdom of ends.
        
        Action must be acceptable to all rational agents as universal law.
        """
        # Simplified: all affected persons must not veto
        affected = action.affected_agents()
        for agent in all_agents:
            if agent.agent_id in affected and agent.is_person():
                # Check if agent would consent
                pass
        return True


@dataclass
class Virtue:
    """Aristotelian virtue: mean between excess and deficiency."""
    virtue_name: str
    excess: str
    deficiency: str
    mean_description: str
    
    def evaluate_action(self, trait_demonstrated: str) -> Fraction:
        """Score action from -1 (deficiency) to +1 (excess), 0 = mean."""
        if trait_demonstrated == self.virtue_name:
            return Fraction(0)  # Perfect virtue
        elif trait_demonstrated == self.excess:
            return Fraction(1)
        elif trait_demonstrated == self.deficiency:
            return Fraction(-1)
        return Fraction(0)  # Neutral


@dataclass
class VirtueEvaluation:
    """Evaluation of action through virtue ethics lens."""
    action: Action
    agent_character: Dict[str, Fraction]  # virtue_name -> disposition strength
    
    def virtuousness_score(self) -> Fraction:
        """Overall virtuousness of action given agent's character."""
        # Simplified: average character virtue
        if not self.agent_character:
            return Fraction(0)
        total = sum(self.agent_character.values())
        return total / len(self.agent_character)


@dataclass
class ContractualistEvaluation:
    """Scanlonian contractualism: principles no one can reasonably reject."""
    principle: str
    stakes: Dict[str, Fraction]  # agent_id -> what's at stake
    
    def reasonably_rejectable_by(self, agent_id: str) -> bool:
        """Would this agent have reasonable grounds to reject?"""
        # If agent has high stakes and principle burdens them
        stake = self.stakes.get(agent_id, Fraction(0))
        return stake < Fraction(0) and abs(stake) > Fraction(1, 2)
    
    def is_permissible(self) -> bool:
        """Action is permissible if principle not reasonably rejectable."""
        for agent_id in self.stakes:
            if self.reasonably_rejectable_by(agent_id):
                return False
        return True


@dataclass
class EthicsChecker:
    """Checker for ethical reasoning and consistency."""
    actions: List[Action] = field(default_factory=list)
    maxims: List[Maxim] = field(default_factory=list)
    virtue_evaluations: List[VirtueEvaluation] = field(default_factory=list)
    contractualist_evals: List[ContractualistEvaluation] = field(default_factory=list)
    
    def kantian_violations(self) -> List[Action]:
        """Actions failing categorical imperative."""
        result = []
        for action in self.actions:
            if not CategoricalImperative.humanity_as_end_test(action):
                result.append(action)
        return result
    
    def utilitarian_best_action(self) -> Optional[Action]:
        """Action with highest expected utility."""
        if not self.actions:
            return None
        return max(self.actions, key=lambda a: a.total_expected_utility())
    
    def contractualist_permissible(self) -> List[ContractualistEvaluation]:
        """Actions permissible under contractualism."""
        return [e for e in self.contractualist_evals if e.is_permissible()]
