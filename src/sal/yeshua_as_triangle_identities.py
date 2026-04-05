"""Map Yeshua axioms onto SAL triangle identities and functor responsibilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YESHUA_AXIOMS, YeshuaClaim, verify_yeshua_standard
from src.sal.adjoint_triple import AdjointTriple


AXIOM_TO_SAL_TARGET: Dict[int, str] = {
    1: "counit",
    2: "unit",
    3: "unit",
    4: "middle_functor",
    5: "left_functor",
    6: "right_functor",
    7: "right_functor",
    8: "counit",
}


@dataclass(frozen=True)
class YeshuaTriangleMapping:
    axiom_number: int
    axiom_text: str
    target: str
    claim: YeshuaClaim
    violations: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return len(self.violations) == 0


def map_axiom_to_triangle_identity(axiom_number: int, triple: AdjointTriple) -> YeshuaTriangleMapping:
    if axiom_number not in YESHUA_AXIOMS:
        raise ValueError(f"Unknown axiom number: {axiom_number}")
    target = AXIOM_TO_SAL_TARGET[axiom_number]
    proof = ProofObject(
        rule="YeshuaToSAL",
        premises=[f"axiom={axiom_number}", f"target={target}"],
        conclusion=f"Axiom {axiom_number} maps to {target}",
    )
    claim = YeshuaClaim(
        source="src/sal/yeshua_as_triangle_identities.py",
        statement=f"{YESHUA_AXIOMS[axiom_number]} mapped to {target}",
        derivation=proof,
    )
    violations = tuple(str(v) for v in verify_yeshua_standard(claim))
    return YeshuaTriangleMapping(
        axiom_number=axiom_number,
        axiom_text=YESHUA_AXIOMS[axiom_number],
        target=target,
        claim=claim,
        violations=violations,
    )


def verify_all_axioms_map(triple: AdjointTriple) -> dict:
    mappings = {n: map_axiom_to_triangle_identity(n, triple) for n in YESHUA_AXIOMS}
    return {
        "mapped": {n: m.target for n, m in mappings.items()},
        "all_valid": all(m.is_valid for m in mappings.values()),
        "count": len(mappings),
    }
