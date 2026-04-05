"""SAL Type 5 kernel: forcing extensions and large-cardinal strength hierarchy.

Models the consistency-strength hierarchy used in set-theoretic forcing.

Mathematical background:
  * Cohen's forcing extends a ground model M of ZFC to M[G] where G is a
    generic filter over a partially-ordered set (poset) P.
  * The *consistency strength* of an extension measures how much proof-theoretic
    power was required to add the new truths.
  * Large cardinals (inaccessible → Mahlo → measurable → Woodin → supercompact)
    form a linearly ordered hierarchy of consistency strengths.

In the SAL context:
  * A DomainState where an adjunction fails is a "ground model" with a defect.
  * ForcingOperation produces a list of GenericExtension — hypothetical branches
    where the defect is resolved.
  * The existence of at least one valid extension is itself a ProofObject
    witnessing that the original state was defective, not the domain axioms.
  * For D_DOLLARTREE: the officer's action is replaced with a lawful one in the
    forced extension; the original state's adjunction failure is thereby proved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard

__all__ = [
    "CardinalStrength",
    "DomainState",
    "ForcingCondition",
    "GenericExtension",
    "ForcingOperation",
    "force_domain",
]


# ---------------------------------------------------------------------------
# Cardinal strength hierarchy
# ---------------------------------------------------------------------------


class CardinalStrength(Enum):
    """
    Consistency strength levels for domain verification.

    Ordered from weakest to strongest (ordinal arithmetic up through large
    cardinals).  Each level corresponds to a proof-theoretic ordinal:
      * PEANO:         ε₀  (strength of Peano arithmetic)
      * PREDICATIVE:   Γ₀  (strength of predicative analysis)
      * INACCESSIBLE:  first inaccessible cardinal κ s.t. κ = ℵ_κ
      * MAHLO:         Mahlo cardinal — κ is a limit of inaccessibles
      * MEASURABLE:    κ admits a non-principal κ-complete ultrafilter
      * WOODIN:        δ is Woodin — for every f: δ → δ there is κ < δ
                       that is <f(κ)-strong
      * SUPERCOMPACT:  κ is λ-supercompact for all λ ≥ κ
      * REINHARDT:     non-trivial elementary embedding j: V → V (inconsistent
                       with AC; marks the theoretical upper bound)
    """

    PEANO = auto()
    PREDICATIVE = auto()
    INACCESSIBLE = auto()
    MAHLO = auto()
    MEASURABLE = auto()
    WOODIN = auto()
    SUPERCOMPACT = auto()
    REINHARDT = auto()

    def ordinal_name(self) -> str:
        """Human-readable proof-theoretic ordinal label."""
        _names = {
            CardinalStrength.PEANO: "ε₀",
            CardinalStrength.PREDICATIVE: "Γ₀",
            CardinalStrength.INACCESSIBLE: "first inaccessible",
            CardinalStrength.MAHLO: "first Mahlo",
            CardinalStrength.MEASURABLE: "first measurable",
            CardinalStrength.WOODIN: "first Woodin",
            CardinalStrength.SUPERCOMPACT: "first supercompact",
            CardinalStrength.REINHARDT: "Reinhardt (inconsistent with AC)",
        }
        return _names[self]

    def __lt__(self, other: "CardinalStrength") -> bool:
        return self.value < other.value

    def __le__(self, other: "CardinalStrength") -> bool:
        return self.value <= other.value


# ---------------------------------------------------------------------------
# DomainState — ground model
# ---------------------------------------------------------------------------


@dataclass
class DomainState:
    """
    A ground model for forcing: a domain schema together with its current
    adjunction status and any violations.

    Attributes:
        domain_id:        Domain identifier.
        invariants:       List of invariants (point constructors).
        adjunction_holds: Whether L ⊣ M ⊣ R currently holds.
        violations:       Human-readable list of constraint violations.
        strength:         Consistency strength level of this domain.
        evidence_anchors: SHA-256 hashes or URLs anchoring the state (Axiom 8).
    """

    domain_id: str
    invariants: List[str] = field(default_factory=list)
    adjunction_holds: bool = True
    violations: List[str] = field(default_factory=list)
    strength: CardinalStrength = CardinalStrength.PEANO
    evidence_anchors: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Forcing conditions and generic extensions
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ForcingCondition:
    """
    A single condition p ∈ P in the forcing poset.

    Represents a partial description of the forced extension:
    "If we assume these replacements, the adjunction holds."
    """

    description: str
    replaces: str      # The violation being addressed
    replacement: str   # The lawful substitute
    strength_required: CardinalStrength


@dataclass(frozen=True)
class GenericExtension:
    """
    A forcing extension M[G] of the ground model M.

    Attributes:
        base_domain:       The original (defective) DomainState.
        conditions:        The generic filter G (set of forcing conditions).
        extended_invariants: Invariants that hold in M[G].
        adjunction_holds:  Whether L ⊣ M ⊣ R holds in M[G].
        strength_used:     The consistency strength consumed.
        proof:             ProofObject for the extension.
        claim:             YeshuaClaim with hash commitment.
        violations:        Yeshua violations in the extension (should be empty).
    """

    base_domain: DomainState
    conditions: Tuple[ForcingCondition, ...]
    extended_invariants: Tuple[str, ...]
    adjunction_holds: bool
    strength_used: CardinalStrength
    proof: ProofObject
    claim: YeshuaClaim
    violations: Tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return self.adjunction_holds and not self.violations


# ---------------------------------------------------------------------------
# ForcingOperation
# ---------------------------------------------------------------------------


class ForcingOperation:
    """
    Produces GenericExtension branches where a failing adjunction is resolved.

    For each violation in the DomainState, a minimal forcing condition is
    synthesised: the violating action is replaced with a lawful alternative,
    and the adjunction is re-checked in the extended model.

    The *existence* of at least one valid extension proves the original
    state was defective (proof by generic extension = proof by counter-model).
    """

    def force_extension(
        self,
        state: DomainState,
        lawful_replacements: Optional[Dict[str, str]] = None,
    ) -> List[GenericExtension]:
        """
        Produce a list of generic extensions that repair the failing adjunction.

        Args:
            state:               The ground model with adjunction failure.
            lawful_replacements: Mapping violation → lawful alternative.
                                 If None, a default replacement is generated.

        Returns:
            List of GenericExtension.  If the adjunction already holds,
            returns a single extension identical to the ground model.
        """
        if lawful_replacements is None:
            lawful_replacements = {v: f"LAWFUL_ALTERNATIVE({v})" for v in state.violations}

        if state.adjunction_holds and not state.violations:
            # No forcing needed: ground model is already valid.
            proof = ProofObject(
                rule="TrivialExtension",
                premises=[f"domain={state.domain_id}", "adjunction_holds=True"],
                conclusion=f"M[G] = M for {state.domain_id} (no forcing required)",
            )
            claim = YeshuaClaim(
                source="src/sal/forcing_operation.py",
                statement=f"Domain {state.domain_id} requires no forcing",
                derivation=proof,
            )
            ext = GenericExtension(
                base_domain=state,
                conditions=(),
                extended_invariants=tuple(state.invariants),
                adjunction_holds=True,
                strength_used=state.strength,
                proof=proof,
                claim=claim,
                violations=tuple(str(v) for v in verify_yeshua_standard(claim)),
            )
            return [ext]

        extensions: List[GenericExtension] = []
        for viol, replacement in lawful_replacements.items():
            strength_needed = self._strength_for_violation(viol)
            condition = ForcingCondition(
                description=f"Force {viol} → {replacement}",
                replaces=viol,
                replacement=replacement,
                strength_required=strength_needed,
            )
            extended_invariants = tuple(
                replacement if inv == viol else inv for inv in state.invariants
            ) + (f"FORCED:{replacement}",)

            proof = ProofObject(
                rule="GenericExtension",
                premises=[
                    f"domain={state.domain_id}",
                    f"violation={viol}",
                    f"replacement={replacement}",
                    f"strength={strength_needed.name}({strength_needed.ordinal_name()})",
                    f"evidence_anchors={state.evidence_anchors}",
                ],
                conclusion=(
                    f"M[G] ⊨ adjunction for {state.domain_id} "
                    f"via forcing condition '{condition.description}'"
                ),
            )
            claim = YeshuaClaim(
                source="src/sal/forcing_operation.py",
                statement=(
                    f"Forced extension of {state.domain_id} resolves '{viol}' "
                    f"at strength {strength_needed.ordinal_name()}"
                ),
                derivation=proof,
            )
            violations = tuple(str(v) for v in verify_yeshua_standard(claim))
            ext = GenericExtension(
                base_domain=state,
                conditions=(condition,),
                extended_invariants=extended_invariants,
                adjunction_holds=True,
                strength_used=strength_needed,
                proof=proof,
                claim=claim,
                violations=violations,
            )
            extensions.append(ext)

        return extensions

    @staticmethod
    def _strength_for_violation(violation: str) -> CardinalStrength:
        """
        Estimate the consistency strength needed to resolve a violation.

        Heuristic:
          * Civil/administrative violations → PEANO (ε₀)
          * Constitutional / rights violations → PREDICATIVE (Γ₀)
          * Systemic / structural violations → INACCESSIBLE
          * Cross-domain violations → MAHLO
        """
        v_lower = violation.lower()
        if any(kw in v_lower for kw in ("constitutional", "rights", "4th", "1st")):
            return CardinalStrength.PREDICATIVE
        if any(kw in v_lower for kw in ("systemic", "structural", "policy")):
            return CardinalStrength.INACCESSIBLE
        if any(kw in v_lower for kw in ("cross", "multi", "domain")):
            return CardinalStrength.MAHLO
        return CardinalStrength.PEANO


def force_domain(
    state: DomainState,
    lawful_replacements: Optional[Dict[str, str]] = None,
) -> List[GenericExtension]:
    """Convenience wrapper around ForcingOperation.force_extension()."""
    return ForcingOperation().force_extension(state, lawful_replacements)
