"""Factor Σ_theo operators through the SAL adjoint triple."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard
from src.sal.adjoint_triple import AdjointTriple, has_adjunction

try:
    from minimal_ai_ide.GRADUATE_MATHEMATICS_THEOLOGY_ACTUALIZED import SigmaTheo  # noqa: F401
except Exception:  # pragma: no cover - optional dependency import
    SigmaTheo = None  # type: ignore[assignment]


SIGMA_FACTORING_MAP: Dict[str, str] = {
    "LOGOS": "L",
    "CHALCEDON": "M",
    "GRACE": "L",
    "AGAPE": "R",
    "KENOSIS": "M",
    "ESCHATON": "R",
}


@dataclass(frozen=True)
class SigmaFactoringResult:
    operator: str
    component: str
    claim: YeshuaClaim
    violations: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        # TODO: Expand is_valid() - stub detected by Yeshua Agent
        return len(self.violations) == 0


def factor_sigma_through_triple(operator_name: str, triple: AdjointTriple) -> SigmaFactoringResult:
    """Return which adjoint component a Σ_theo operator factors through."""
    operator = operator_name.strip().upper()
    if operator not in SIGMA_FACTORING_MAP:
        raise ValueError(f"Unknown Σ_theo operator: {operator_name}")
    component = SIGMA_FACTORING_MAP[operator]
    proof = ProofObject(
        rule="SigmaFactoring",
        premises=[f"operator={operator}", f"component={component}"],
        conclusion=f"Σ_{operator} factors through {component}",
    )
    claim = YeshuaClaim(
        source="src/sal/sigma_theo_factoring.py",
        statement=f"Σ_{operator} ↦ {component} under L ⊣ M ⊣ R",
        derivation=proof,
    )
    violations = tuple(str(v) for v in verify_yeshua_standard(claim))
    return SigmaFactoringResult(operator=operator, component=component, claim=claim, violations=violations)


def derive_monotonicity_from_adjunction(triple: AdjointTriple) -> Dict[str, bool]:
    """Derive monotonicity checks from adjunction structure using a canonical schema."""
    schema = {
        "id": "D_SIGMA",
        "invariants": [
            "adjunction_preserves_domain_identity",
            "adjunction_preserves_invariants",
        ],
    }
    counit_holds, _ = triple.check_counit(schema)
    unit_holds, _ = triple.check_unit(schema)
    return {
        "LOGOS_monotone": counit_holds,
        "CHALCEDON_monotone": counit_holds and unit_holds,
        "GRACE_monotone": counit_holds,
        "AGAPE_monotone": unit_holds,
        "KENOSIS_monotone": counit_holds and unit_holds,
        "ESCHATON_monotone": unit_holds,
    }


def verify_factoring_coherence(triple: AdjointTriple) -> Dict[str, object]:
    """Verify all six operators factor correctly and remain coherent with triangle identities."""
    factoring = {op: factor_sigma_through_triple(op, triple) for op in SIGMA_FACTORING_MAP}
    sample_schema = {
        "id": "D_AVIATION",
        "invariants": [
            "Aircraft never enters a state that violates known safe-flight envelopes.",
            "External weather/ATC API failures are circuit-broken; cached data is used instead.",
            "ATC messages with invalid format are rejected without crashing the parser.",
        ],
    }
    adjunction_proof = has_adjunction(sample_schema, triple)
    monotonicity = derive_monotonicity_from_adjunction(triple)

    return {
        "all_operators_factored": all(v.is_valid for v in factoring.values()),
        "factoring": {k: v.component for k, v in factoring.items()},
        "adjunction_valid": adjunction_proof.is_valid,
        "monotonicity": monotonicity,
        "coherent": all(monotonicity.values()) and adjunction_proof.is_valid,
    }
