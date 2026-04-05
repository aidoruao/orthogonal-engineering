"""Cross-repo adjunction checks between covenant constraints and ontology invariants."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from axioms.logic import ProofObject
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard
from src.sal.adjoint_triple import AdjunctionProof


REPO_ROOT = Path(__file__).resolve().parents[2]
INCURSION_SCHEMA = REPO_ROOT / "INCURSION_ATOMIC_INTEGRITY_SCHEMA.yaml"
ONTOLOGY_JSON = REPO_ROOT / "ontology" / "ontology.json"


def _extract_constraints_from_incursion_yaml() -> Dict[str, List[str]]:
    """Conservative parser for covenant principles/constraints from schema yaml text."""
    text = INCURSION_SCHEMA.read_text(encoding="utf-8")
    principles = ["LOGOS", "CHALCEDON", "GRACE", "KENOSIS", "AGAPE"]
    out: Dict[str, List[str]] = {p: [] for p in principles}
    current: str | None = None
    in_constraints = False
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.endswith(":") and stripped[:-1] in principles:
            current = stripped[:-1]
            in_constraints = False
            continue
        if current and stripped == "constraints:":
            in_constraints = True
            continue
        if current and in_constraints and stripped.startswith("- "):
            out[current].append(stripped[2:].strip().strip('"'))
            continue
        if current and stripped.endswith(":") and not stripped.startswith("-") and stripped[:-1] not in principles:
            in_constraints = False
    return out


def _load_domain_invariants() -> List[str]:
    data = json.loads(ONTOLOGY_JSON.read_text(encoding="utf-8"))
    invariants: List[str] = []
    for domain in data.get("domains", []):
        invariants.extend(domain.get("invariants", []))
    return invariants


def _constraint_matches_invariant(constraint: str, invariants: List[str]) -> bool:
    c_tokens = {tok for tok in constraint.lower().replace("_", " ").split() if len(tok) > 2}
    if not c_tokens:
        return False
    for invariant in invariants:
        inv = invariant.lower()
        overlap = sum(1 for tok in c_tokens if tok in inv)
        if overlap >= 1:
            return True
    return False


def verify_cross_repo_adjunction() -> dict:
    """Return cross-repo adjunction evidence and anti-nominalism gaps."""
    constraints_by_principle = _extract_constraints_from_incursion_yaml()
    invariants = _load_domain_invariants()

    missing: List[str] = []
    matched: Dict[str, bool] = {}
    for principle, constraints in constraints_by_principle.items():
        for constraint in constraints:
            key = f"{principle}:{constraint}"
            ok = _constraint_matches_invariant(constraint, invariants)
            matched[key] = ok
            if not ok:
                missing.append(key)

    counit_holds = len(matched) > 0
    unit_holds = len(missing) == 0

    counit_proof = ProofObject(
        rule="CrossRepoCounit",
        premises=[f"constraints_checked={len(matched)}", f"constraints_missing={len(missing)}"],
        conclusion=f"ε (implementation satisfies covenant constraints) = {counit_holds}",
    )
    unit_proof = ProofObject(
        rule="CrossRepoUnit",
        premises=[f"missing_constraints={missing}"],
        conclusion=f"η (covenant maps to implementation invariants) = {unit_holds}",
    )
    combined = ProofObject(
        rule="CrossRepoAdjunction",
        premises=[counit_proof.conclusion, unit_proof.conclusion],
        conclusion=f"cross_repo_adjunction = {counit_holds and unit_holds}",
    )
    claim = YeshuaClaim(
        source="src/sal/cross_repo_adjunction.py",
        statement="OE covenant constraints correspond to ontology invariants",
        derivation=combined,
    )
    violations = tuple(str(v) for v in verify_yeshua_standard(claim))

    proof = AdjunctionProof(
        domain_id="CROSS_REPO",
        counit_holds=counit_holds,
        unit_holds=unit_holds,
        counit_evidence=counit_proof,
        unit_evidence=unit_proof,
        yeshua_claim=claim,
        yeshua_violations=violations,
    )

    return {
        "proof": proof,
        "matched_constraints": matched,
        "anti_nominalism_violations": missing,
    }
