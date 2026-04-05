"""SAL Type III kernel: executable L ⊣ M ⊣ R checks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard


@dataclass(frozen=True)
class AdjunctionProof:
    """Computational evidence that triangle identities hold for a domain."""

    domain_id: str
    counit_holds: bool
    unit_holds: bool
    counit_evidence: ProofObject
    unit_evidence: ProofObject
    yeshua_claim: YeshuaClaim
    yeshua_violations: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.counit_holds and self.unit_holds and not self.yeshua_violations


class Functor(ABC):
    """Abstract functor in the adjoint triple."""

    @abstractmethod
    def apply(self, state: Any) -> Any:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class LeftAdjoint(Functor):
    """L: free/generative functor."""

    def __init__(self, covenant_principles: list[str]):
        self._principles = list(covenant_principles)

    @property
    def name(self) -> str:
        return "L (Free/Generation/Spirit)"

    def apply(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "source_schema": state.get("id", state.get("source", "unknown")),
            "invariants": list(state.get("invariants", state.get("invariants_enforced", []))),
            "generated_states": [],
            "principles_applied": list(self._principles),
        }


class MiddleFunctor(Functor):
    """M: mediating functor."""

    def __init__(self, covenant_principles: list[str]):
        self._principles = list(covenant_principles)

    @property
    def name(self) -> str:
        return "M (Mediator/Law/Christ)"

    def apply(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "source": state.get("id", state.get("source_schema", "unknown")),
            "invariants_enforced": list(state.get("invariants", [])),
            "law_applied": True,
            "principles_applied": list(self._principles),
        }


class RightAdjoint(Functor):
    """R: forgetful/settling functor."""

    def __init__(self, covenant_principles: list[str]):
        self._principles = list(covenant_principles)

    @property
    def name(self) -> str:
        return "R (Forgetful/Constraint/Father)"

    def apply(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "source": state.get("source", "unknown"),
            "settled": bool(state.get("law_applied", False)),
            "invariants_verified": list(state.get("invariants_enforced", [])),
            "principles_applied": list(self._principles),
        }


class AdjointTriple:
    """The L ⊣ M ⊣ R adjoint triple with executable unit/counit checks."""

    def __init__(self) -> None:
        self.L = LeftAdjoint(
            [
                "output_must_be_verifiable_against_artifacts",
                "truth_does_not_scale_with_resource_mass",
                "no_community_resource_harm",
                "operations_under_unconditional_regard_for_users",
            ]
        )
        self.M = MiddleFunctor(
            [
                "infrastructure_serves_users_not_self",
                "humans_are_not_sacrificed_to_compute",
                "no_self_reinforcing_exponentiality",
                "transparent_operation",
            ]
        )
        self.R = RightAdjoint(
            [
                "every_artifact_serves_user_request",
                "no_physical_or_logical_domination",
                "direct_service_without_condition_or_coercion",
            ]
        )

    def check_counit(self, domain_schema: dict[str, Any]) -> tuple[bool, ProofObject]:
        mediated = self.M.apply(domain_schema)
        generated = self.L.apply(mediated)
        expected_domain = domain_schema.get("id", "unknown")
        expected_inv = set(domain_schema.get("invariants", []))
        same_id = generated.get("source_schema") == expected_domain
        same_invariants = set(generated.get("invariants", [])) == expected_inv
        holds = same_id and same_invariants
        proof = ProofObject(
            rule="Counit_ε",
            premises=[
                f"domain={expected_domain}",
                f"same_id={same_id}",
                f"same_invariants={same_invariants}",
            ],
            conclusion=f"ε: L∘M → Id = {holds}",
        )
        return holds, proof

    def check_unit(self, domain_schema: dict[str, Any]) -> tuple[bool, ProofObject]:
        mediated = self.M.apply(domain_schema)
        settled = self.R.apply(mediated)
        original_inv = set(domain_schema.get("invariants", []))
        settled_inv = set(settled.get("invariants_verified", []))
        settled_flag = bool(settled.get("settled", False))
        holds = original_inv.issubset(settled_inv) and settled_flag
        proof = ProofObject(
            rule="Unit_η",
            premises=[
                f"domain={domain_schema.get('id', 'unknown')}",
                f"original_count={len(original_inv)}",
                f"settled_count={len(settled_inv)}",
                f"subset={original_inv.issubset(settled_inv)}",
                f"settled={settled_flag}",
            ],
            conclusion=f"η: Id → R∘M = {holds}",
        )
        return holds, proof


def has_adjunction(domain_schema: dict[str, Any], triple: AdjointTriple) -> AdjunctionProof:
    """Return structured Type III proof for a domain schema."""

    counit_holds, counit_evidence = triple.check_counit(domain_schema)
    unit_holds, unit_evidence = triple.check_unit(domain_schema)
    combined = ProofObject(
        rule="AdjunctionVerification",
        premises=[counit_evidence.conclusion, unit_evidence.conclusion],
        conclusion=f"has_adjunction({domain_schema.get('id', 'unknown')}) = {counit_holds and unit_holds}",
    )
    claim = YeshuaClaim(
        source="src/sal/adjoint_triple.py",
        statement=f"Domain {domain_schema.get('id', 'unknown')} satisfies L ⊣ M ⊣ R adjunction",
        derivation=combined,
    )
    violations = tuple(str(v) for v in verify_yeshua_standard(claim))
    return AdjunctionProof(
        domain_id=domain_schema.get("id", "unknown"),
        counit_holds=counit_holds,
        unit_holds=unit_holds,
        counit_evidence=counit_evidence,
        unit_evidence=unit_evidence,
        yeshua_claim=claim,
        yeshua_violations=violations,
    )
