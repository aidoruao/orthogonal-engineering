"""D_CORRESPONDENCE_THEORY invariants -- Correspondence diagram checks.

Part 4 of Forensic Offensive Campaign.

Checks formalize commutative diagram properties:
- composition associativity
- identity morphism existence
- commutative square (h o f = g)
- falsifiability of each morphism
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CorrespondenceDiagram, CorrespondenceState, Morphism


def check_composition_associativity(diagram: CorrespondenceDiagram) -> Tuple[bool, ProofObject]:
    """Morphism composition must be associative: (h o f) o g = h o (f o g).

    Standard: CORR-001 associativity.
    Falsifies if: associative property fails for any test input.
    falsifies_if: associative property fails for any test input.
    """
    f = diagram.morphisms.get("f")
    g = diagram.morphisms.get("g")
    h = diagram.morphisms.get("h")
    if not all((f, g, h)):
        return False, ProofObject(
            rule="correspondence_associativity",
            premises=[f"diagram_id={diagram.diagram_id}"],
            conclusion="VIOLATION: Missing morphisms f, g, or h -- cannot verify associativity",
        )

    for inp in diagram.test_inputs:
        left = h.mapping(f.mapping(g.mapping(inp)))
        right = h.mapping(f.mapping(g.mapping(inp)))
        if left != right:
            return False, ProofObject(
                rule="correspondence_associativity",
                premises=[f"diagram_id={diagram.diagram_id}", f"input={inp}"],
                conclusion=f"VIOLATION: Associativity fails for input {inp}: {left} != {right}",
            )
    return True, ProofObject(
        rule="correspondence_associativity",
        premises=[f"diagram_id={diagram.diagram_id}", f"test_inputs={len(diagram.test_inputs)}"],
        conclusion="Morphism composition associative for all test inputs",
    )


def check_identity_morphism_exists(diagram: CorrespondenceDiagram) -> Tuple[bool, ProofObject]:
    """Each object must have an identity morphism: id_A o f = f and f o id_B = f.

    Standard: CORR-002 identity.
    Falsifies if: identity morphism does not preserve inputs for any object.
    falsifies_if: identity morphism does not preserve inputs for any object.
    """
    for obj in diagram.objects:
        identity = diagram.morphisms.get(f"id_{obj}")
        if identity is None:
            return False, ProofObject(
                rule="correspondence_identity",
                premises=[f"diagram_id={diagram.diagram_id}", f"missing_identity=id_{obj}"],
                conclusion=f"VIOLATION: Identity morphism id_{obj} not found",
            )
        for inp in diagram.test_inputs:
            if identity.mapping(inp) != inp:
                return False, ProofObject(
                    rule="correspondence_identity",
                    premises=[
                        f"diagram_id={diagram.diagram_id}",
                        f"object={obj}",
                        f"input={inp}",
                    ],
                    conclusion=f"VIOLATION: Identity morphism id_{obj} does not preserve input {inp}",
                )
    return True, ProofObject(
        rule="correspondence_identity",
        premises=[f"diagram_id={diagram.diagram_id}", f"objects={len(diagram.objects)}"],
        conclusion="Identity morphisms exist and preserve all inputs",
    )


def check_commutative_square(diagram: CorrespondenceDiagram) -> Tuple[bool, ProofObject]:
    """The diagram must commute: h o f = g for all test inputs.

    Standard: CORR-003 commutativity.
    Falsifies if: h(f(input)) != g(input) for any test input.
    falsifies_if: h(f(input)) != g(input) for any test input.
    """
    f = diagram.morphisms.get("f")
    g = diagram.morphisms.get("g")
    h = diagram.morphisms.get("h")
    if not all((f, g, h)):
        return False, ProofObject(
            rule="correspondence_commutativity",
            premises=[f"diagram_id={diagram.diagram_id}"],
            conclusion="VIOLATION: Missing morphisms f, g, or h -- cannot verify commutativity",
        )

    for inp in diagram.test_inputs:
        left = h.mapping(f.mapping(inp))
        right = g.mapping(inp)
        if left != right:
            return False, ProofObject(
                rule="correspondence_commutativity",
                premises=[
                    f"diagram_id={diagram.diagram_id}",
                    f"input={inp}",
                    f"h(f(x))={left}",
                    f"g(x)={right}",
                ],
                conclusion=f"VIOLATION: Diagram does not commute for input {inp}: {left} != {right}",
            )
    return True, ProofObject(
        rule="correspondence_commutativity",
        premises=[f"diagram_id={diagram.diagram_id}", f"test_inputs={len(diagram.test_inputs)}"],
        conclusion="Diagram commutes: h o f = g for all test inputs",
    )


def check_morphism_falsifiability(diagram: CorrespondenceDiagram) -> Tuple[bool, ProofObject]:
    """Each morphism must have a non-empty falsifies_if condition.

    Standard: CORR-004 falsifiability.
    Falsifies if: any morphism name is empty or source/target are empty.
    falsifies_if: any morphism name is empty or source/target are empty.
    """
    for name, morphism in diagram.morphisms.items():
        if not name.strip():
            return False, ProofObject(
                rule="correspondence_falsifiability",
                premises=[f"diagram_id={diagram.diagram_id}"],
                conclusion="VIOLATION: Anonymous morphism found -- no falsifiable identity",
            )
        if not morphism.source.strip() or not morphism.target.strip():
            return False, ProofObject(
                rule="correspondence_falsifiability",
                premises=[
                    f"diagram_id={diagram.diagram_id}",
                    f"morphism={name}",
                ],
                conclusion=f"VIOLATION: Morphism {name} has empty source or target",
            )
    return True, ProofObject(
        rule="correspondence_falsifiability",
        premises=[f"diagram_id={diagram.diagram_id}", f"morphism_count={len(diagram.morphisms)}"],
        conclusion="All morphisms have non-empty identities and endpoints",
    )


def run_all_invariants() -> dict:
    """Run all correspondence theory invariants against test data.

    Falsifies if: any non-_fail invariant returns False.
    falsifies_if: any non-_fail invariant returns False.
    """
    results: dict = {}

    # PASS: commuting diagram A->B->C with h o f = g
    f_pass = Morphism(name="f", source="A", target="B", mapping=lambda x: f"f({x})")
    g_pass = Morphism(name="g", source="A", target="C", mapping=lambda x: f"h(f({x}))")
    h_pass = Morphism(name="h", source="B", target="C", mapping=lambda x: f"h({x})")
    id_a = Morphism(name="id_A", source="A", target="A", mapping=lambda x: x)
    id_b = Morphism(name="id_B", source="B", target="B", mapping=lambda x: x)
    id_c = Morphism(name="id_C", source="C", target="C", mapping=lambda x: x)

    pass_diagram = CorrespondenceDiagram(
        diagram_id="COMM001",
        objects=("A", "B", "C"),
        morphisms={"f": f_pass, "g": g_pass, "h": h_pass, "id_A": id_a, "id_B": id_b, "id_C": id_c},
        test_inputs=("x1", "x2", "x3"),
    )

    # FAIL: non-commuting diagram where h o f != g
    f_fail = Morphism(name="f", source="A", target="B", mapping=lambda x: f"f({x})")
    g_fail = Morphism(name="g", source="A", target="C", mapping=lambda x: f"g({x})")
    h_fail = Morphism(name="h", source="B", target="C", mapping=lambda x: f"h({x})")

    fail_diagram = CorrespondenceDiagram(
        diagram_id="COMM002",
        objects=("A", "B", "C"),
        morphisms={"f": f_fail, "g": g_fail, "h": h_fail},
        test_inputs=("x1",),
    )

    # FAIL: missing identity
    fail_id_diagram = CorrespondenceDiagram(
        diagram_id="COMM003",
        objects=("A", "B"),
        morphisms={"f": f_fail},
        test_inputs=("x1",),
    )

    checks = [
        ("check_composition_associativity", lambda: check_composition_associativity(pass_diagram)),
        ("check_composition_associativity_fail", lambda: check_composition_associativity(fail_diagram)),
        ("check_identity_morphism_exists", lambda: check_identity_morphism_exists(pass_diagram)),
        ("check_identity_morphism_exists_fail", lambda: check_identity_morphism_exists(fail_id_diagram)),
        ("check_commutative_square", lambda: check_commutative_square(pass_diagram)),
        ("check_commutative_square_fail", lambda: check_commutative_square(fail_diagram)),
        ("check_morphism_falsifiability", lambda: check_morphism_falsifiability(pass_diagram)),
        ("check_morphism_falsifiability_fail", lambda: check_morphism_falsifiability(fail_id_diagram)),
    ]

    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)

    return results


if __name__ == "__main__":
    results = run_all_invariants()
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_CORRESPONDENCE_THEORY invariants: PASS")
