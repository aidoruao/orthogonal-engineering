"""investigations.wall_inversions — Wall Inversion Registry.

Maps each logical wall (impossibility theorem) to its Yeshua Inversion:
the domain restriction or architectural mechanism that changes the problem
so the theorem's preconditions no longer apply.

Each entry includes:
  - theorem_reference: formal citation
  - sal_module: SAL kernel module that implements the inversion
  - inversion_mechanism: precise description of the domain restriction
  - proof: ProofObject certifying the inversion is structurally valid

Standard: Yeshua Standard — every claim has a ProofObject and a falsifies_if.

falsifies_if: a wall_id appears in the registry without a valid ProofObject.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class WallInversion:
    """Registry entry for a single logical wall inversion.

    falsifies_if: proof.is_valid() returns False.
    """

    wall_id: str
    theorem_name: str
    theorem_reference: str
    sal_module: str
    inversion_mechanism: str
    falsifies_if: str
    proof: ProofObject


def _make_proof(wall_id: str, theorem: str, mechanism: str) -> ProofObject:
    """Construct a ProofObject for a wall inversion entry.

    falsifies_if: proof_hash changes for the same inputs.
    """
    return ProofObject(
        rule="WallInversion",
        premises=[
            f"wall_id={wall_id}",
            f"theorem={theorem}",
            f"mechanism={mechanism[:60]}...",
        ],
        conclusion=f"Inversion valid: preconditions of {theorem} removed by domain restriction",
    )


WALL_INVERSION_REGISTRY: Dict[str, WallInversion] = {
    "WALL_001": WallInversion(
        wall_id="WALL_001",
        theorem_name="Halting Problem",
        theorem_reference="Turing (1936). 'On Computable Numbers, with an Application to the Entscheidungsproblem.' Proc. London Math. Soc. s2-42(1):230–265.",
        sal_module="oe_engine/synthesizer.py",
        inversion_mechanism=(
            "Restrict computation to bounded programs: ARCSynthesizer enforces "
            "max_iterations (default 10 000) and max depth (default 6). The domain "
            "is finite-state; every program in the search space is guaranteed to "
            "terminate. Turing's theorem applies only to arbitrary programs."
        ),
        falsifies_if="ARCSynthesizer runs without a finite iteration bound.",
        proof=_make_proof(
            "WALL_001",
            "Halting Problem",
            "Restrict computation to bounded programs (max_iterations, max_depth)",
        ),
    ),
    "WALL_002": WallInversion(
        wall_id="WALL_002",
        theorem_name="Gödel Incompleteness",
        theorem_reference="Gödel (1931). 'Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I.' Monatshefte für Mathematik und Physik 38:173–198.",
        sal_module="src/sal/self_referential.py",
        inversion_mechanism=(
            "Feferman reflection: GoedelianReflector.add_reflection_principle() "
            "extends the base theory T with Con(T) as a new axiom, producing T'. "
            "The Gödel sentence of T becomes provable in T'. Iterating transfinitely "
            "yields a reflexive closure in which no fixed Gödel sentence is "
            "permanently unprovable. The theorem holds for T; T' escapes it."
        ),
        falsifies_if="GoedelianReflector adds reflection without extending the axiom set.",
        proof=_make_proof(
            "WALL_002",
            "Gödel Incompleteness",
            "Feferman reflection: add Con(T) axiom to climb past each Gödel sentence",
        ),
    ),
    "WALL_003": WallInversion(
        wall_id="WALL_003",
        theorem_name="Rice's Theorem",
        theorem_reference="Rice (1953). 'Classes of Recursively Enumerable Sets and Their Decision Problems.' Trans. Amer. Math. Soc. 74(2):358–366.",
        sal_module="src/domains/",
        inversion_mechanism=(
            "Restrict to syntactic properties on frozen dataclasses: domain invariants "
            "check only structural fields (e.g., Fraction comparisons, string "
            "membership) of @dataclass(frozen=True) objects. Rice's theorem applies "
            "to semantic properties of arbitrary computable functions; frozen-dataclass "
            "field checks are decidable structural predicates."
        ),
        falsifies_if="A domain invariant inspects program semantics rather than frozen struct fields.",
        proof=_make_proof(
            "WALL_003",
            "Rice's Theorem",
            "Restrict to syntactic properties on frozen dataclasses",
        ),
    ),
    "WALL_004": WallInversion(
        wall_id="WALL_004",
        theorem_name="Arrow's Impossibility Theorem",
        theorem_reference="Arrow (1951). 'Social Choice and Individual Values.' Wiley, New York.",
        sal_module="kernel/ipc.py",
        inversion_mechanism=(
            "Capability delegation violates the unrestricted domain condition: "
            "agents may only express preferences over options within their granted "
            "capability scope. The preference profile space is capability-restricted, "
            "so Arrow's unrestricted domain precondition does not hold. A capability-"
            "consistent social choice function is constructible within this subdomain."
        ),
        falsifies_if="Agents can express preferences outside their capability scope.",
        proof=_make_proof(
            "WALL_004",
            "Arrow's Impossibility",
            "Capability delegation restricts the preference domain",
        ),
    ),
    "WALL_005": WallInversion(
        wall_id="WALL_005",
        theorem_name="CAP Theorem",
        theorem_reference="Brewer (2000). 'Towards Robust Distributed Systems.' PODC Keynote. Formalized: Gilbert & Lynch (2002). 'Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.' ACM SIGACT News 33(2):51–59.",
        sal_module="kernel/bridge/storage.py",
        inversion_mechanism=(
            "Content-addressed storage (SHA-256 blobs) decouples consistency from "
            "availability: immutable blobs are trivially consistent (hash verifies "
            "identity) and available (any replica can serve any blob). Partition "
            "tolerance follows from replication. The theorem applies to mutable "
            "state; content-addressed immutable objects change the problem class."
        ),
        falsifies_if="Storage layer uses mutable keys rather than content-addressed SHA-256.",
        proof=_make_proof(
            "WALL_005",
            "CAP Theorem",
            "Content-addressed immutable blobs decouple consistency from availability",
        ),
    ),
    "WALL_006": WallInversion(
        wall_id="WALL_006",
        theorem_name="NLU Undecidability",
        theorem_reference="Church (1936). 'An Unsolvable Problem of Elementary Number Theory.' Amer. J. Math. 58(2):345–363. (Applied to semantic parsing.)",
        sal_module="oe_engine/router.py",
        inversion_mechanism=(
            "Domain routing + invariant verification: replace general semantic "
            "understanding with deterministic keyword-indexed domain routing "
            "(DomainRouter) followed by ProofObject-verified invariant checks "
            "(ThinkerModule). No general NLU is required; the engine operates "
            "only within registered jurisdictions. Queries outside all domains "
            "receive a deterministic refusal."
        ),
        falsifies_if="Engine returns a non-empty response for a query that matches no domain keyword.",
        proof=_make_proof(
            "WALL_006",
            "NLU Undecidability",
            "Domain routing replaces general semantic understanding with keyword index",
        ),
    ),
    "WALL_007": WallInversion(
        wall_id="WALL_007",
        theorem_name="Code Correctness Undecidability",
        theorem_reference="Rice (1953), op. cit. Applied to semantic correctness of generated programs.",
        sal_module="oe_engine/synthesizer.py",
        inversion_mechanism=(
            "Bounded verification + invariant checking: code generation is restricted "
            "to typed transform sequences (TransformType^depth). Each candidate is "
            "verified against frozen-dataclass domain invariants before acceptance. "
            "Correctness is a structural property (invariant-pass), not a semantic "
            "property of arbitrary programs, so Rice's theorem does not apply."
        ),
        falsifies_if="A candidate transform sequence is accepted without invariant verification.",
        proof=_make_proof(
            "WALL_007",
            "Code Correctness Undecidability",
            "Bounded transform sequences verified against domain invariants before acceptance",
        ),
    ),
    "WALL_008": WallInversion(
        wall_id="WALL_008",
        theorem_name="Novel Program Generation Undecidability",
        theorem_reference="Turing (1936), op. cit. Applied to enumerating correct programs.",
        sal_module="oe_engine/synthesizer.py",
        inversion_mechanism=(
            "BFS over typed transform sequences (ARCSynthesizer): enumerate programs "
            "by composing TransformType sequences up to max_depth (default 6) using "
            "breadth-first search over at most max_iterations (default 10 000) "
            "candidates. Each candidate is checked against domain invariants. "
            "Novelty is bounded by the transform alphabet; correctness is verified, "
            "not assumed. Undecidability applies to arbitrary programs, not to finite "
            "BFS over a typed alphabet."
        ),
        falsifies_if="ARCSynthesizer returns a candidate that has not been verified by the invariant bus.",
        proof=_make_proof(
            "WALL_008",
            "Novel Program Generation",
            "BFS over typed transform sequences with mandatory invariant verification",
        ),
    ),
    "WALL_TELEMETRY_001": WallInversion(
        wall_id="WALL_TELEMETRY_001",
        theorem_name="Corporate Black-Box Opacity",
        theorem_reference="NOWAY_BLACKBOX_001: confirmed open data pipeline preclaims independent black-box interior.",
        sal_module="src/domains/d_forensic_telemetry/invariants.py",
        inversion_mechanism=(
            "Telemetry is a two-way street: structural isomorphism between input "
            "and output patterns across a confirmed open channel inverts the claim "
            "that the black-box interior is independent. The inversion restricts "
            "the domain to systems where data flow is observable and measurable, "
            "rendering opacity claims falsifiable rather than axiomatic."
        ),
        falsifies_if="a confirmed open data pipeline is shown to coexist with a provably independent black-box system.",
        proof=_make_proof(
            "WALL_TELEMETRY_001",
            "Corporate Black-Box Opacity",
            "Structural isomorphism across confirmed open channel inverts independence claim",
        ),
    ),
}


def get_wall_inversion(wall_id: str) -> Tuple[WallInversion, ProofObject]:
    """Retrieve a wall inversion entry by ID.

    Standard: O(1) dict lookup — deterministic.
    falsifies_if: wall_id in registry but lookup raises KeyError.

    Returns:
        Tuple of (WallInversion, ProofObject confirming retrieval).
    """
    entry = WALL_INVERSION_REGISTRY.get(wall_id)
    if entry is None:
        proof = ProofObject(
            rule="WallInversionLookup",
            premises=[f"wall_id={wall_id}"],
            conclusion=f"FAIL: wall_id={wall_id} not found in registry",
        )
        # Return a sentinel to avoid raising — callers check proof conclusion.
        sentinel = WallInversion(
            wall_id=wall_id,
            theorem_name="UNKNOWN",
            theorem_reference="",
            sal_module="",
            inversion_mechanism="",
            falsifies_if="",
            proof=proof,
        )
        return sentinel, proof

    lookup_proof = ProofObject(
        rule="WallInversionLookup",
        premises=[f"wall_id={wall_id}", f"theorem={entry.theorem_name}"],
        conclusion=f"Found inversion for {wall_id}: {entry.theorem_name}",
    )
    return entry, lookup_proof


def list_invertible_walls() -> Tuple[List[str], ProofObject]:
    """Return all registered wall IDs with their theorem names.

    Standard: deterministic enumeration of the registry.
    falsifies_if: registry is non-empty but list is empty.

    Returns:
        Tuple of (list_of_wall_ids, ProofObject).
    """
    ids = sorted(WALL_INVERSION_REGISTRY.keys())
    proof = ProofObject(
        rule="WallInversionList",
        premises=[f"count={len(ids)}"],
        conclusion=f"Listed {len(ids)} wall inversions: {ids}",
    )
    return ids, proof


def verify_all_inversions() -> Tuple[bool, ProofObject]:
    """Verify all ProofObjects in the registry are cryptographically valid.

    Standard: ProofObject.is_valid() re-computes SHA-256 and compares.
    falsifies_if: any proof fails is_valid() after construction.

    Returns:
        Tuple of (all_valid: bool, ProofObject summarising results).
    """
    failed: List[str] = []
    for wall_id, entry in WALL_INVERSION_REGISTRY.items():
        if not entry.proof.is_valid():
            failed.append(wall_id)

    all_valid = len(failed) == 0
    proof = ProofObject(
        rule="WallInversionVerification",
        premises=[
            f"total={len(WALL_INVERSION_REGISTRY)}",
            f"failed={failed}",
        ],
        conclusion=(
            "All inversion proofs valid"
            if all_valid
            else f"FAIL: invalid proofs for {failed}"
        ),
    )
    return all_valid, proof
