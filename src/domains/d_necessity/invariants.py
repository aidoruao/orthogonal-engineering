#!/usr/bin/env python3
"""Necessity Domain Invariants — Modal logic frame conditions.

Standards:
- Kripke semantics
- Modal systems (K, T, S4, S5)
- Frame correspondence theory

Falsifies if:
- T axiom fails (reflexivity)
- 4 axiom fails (transitivity)
- 5 axiom fails (Euclidean)
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import KripkeFrame, ModalSystem


def check_frame_reflexivity(frame: KripkeFrame) -> Tuple[bool, ProofObject]:
    """T axiom: □p → p requires reflexive frames.
    
    Falsifies if: any world is not accessible from itself.
    falsifies_if: any world is not accessible from itself.
    """
    for world in frame.worlds:
        accessible = frame.accessibility.get(world.world_id, set())
        if world.world_id not in accessible:
            return False, ProofObject(
                conclusion=f"VIOLATION: Frame not reflexive - world {world.world_id} cannot see itself",
                premises=[
                    f"World: {world.world_id}",
                    "Self-accessibility: False"
                ],
                rule="modal_axiom_t_reflexivity"
            )
    
    return True, ProofObject(
        conclusion="Frame reflexive - T axiom satisfied",
        premises=[f"Worlds: {len(frame.worlds)}"],
        rule="frame_reflexive"
    )


def check_frame_transitivity(frame: KripkeFrame) -> Tuple[bool, ProofObject]:
    """4 axiom: □p → □□p requires transitive frames.
    
    Falsifies if: wRv and vRu hold but wRu does not.
    falsifies_if: wRv and vRu hold but wRu does not.
    """
    for w in frame.worlds:
        for v_id in frame.accessibility.get(w.world_id, set()):
            for u_id in frame.accessibility.get(v_id, set()):
                if u_id not in frame.accessibility.get(w.world_id, set()):
                    return False, ProofObject(
                        conclusion=f"VIOLATION: Frame not transitive - {w.world_id}→{v_id}→{u_id} but {w.world_id}↛{u_id}",
                        premises=[
                            f"Path: {w.world_id} → {v_id} → {u_id}",
                            f"Missing: {w.world_id} → {u_id}"
                        ],
                        rule="modal_axiom_4_transitivity"
                    )
    
    return True, ProofObject(
        conclusion="Frame transitive - 4 axiom satisfied",
        premises=[f"Worlds: {len(frame.worlds)}"],
        rule="frame_transitive"
    )


def check_frame_symmetry(frame: KripkeFrame) -> Tuple[bool, ProofObject]:
    """B axiom: p → □◇p requires symmetric frames.
    
    Falsifies if: wRv holds but vRw does not.
    falsifies_if: wRv holds but vRw does not.
    """
    for w in frame.worlds:
        for v_id in frame.accessibility.get(w.world_id, set()):
            if w.world_id not in frame.accessibility.get(v_id, set()):
                return False, ProofObject(
                    conclusion=f"VIOLATION: Frame not symmetric - {w.world_id}→{v_id} but {v_id}↛{w.world_id}",
                    premises=[
                        f"Relation: {w.world_id} → {v_id}",
                        f"Reverse: Not present"
                    ],
                    rule="modal_axiom_b_symmetry"
                )
    
    return True, ProofObject(
        conclusion="Frame symmetric - B axiom satisfied",
        premises=[f"Worlds: {len(frame.worlds)}"],
        rule="frame_symmetric"
    )


def check_system_compliance(frame: KripkeFrame, system: ModalSystem) -> Tuple[bool, ProofObject]:
    """Frame validates modal system axioms.
    
    Falsifies if: frame fails the reflexive/transitive/symmetric requirements for the modal system.
    falsifies_if: frame fails the reflexive/transitive/symmetric requirements for the modal system.
    """
    if system == ModalSystem.T and not frame.is_reflexive():
        return False, ProofObject(
            conclusion="VIOLATION: Frame does not satisfy T system (not reflexive)",
            premises=["Required: Reflexive", "Frame: Not reflexive"],
            rule="modal_system_t"
        )
    
    if system == ModalSystem.S4 and not (frame.is_reflexive() and frame.is_transitive()):
        return False, ProofObject(
            conclusion="VIOLATION: Frame does not satisfy S4 system",
            premises=["Required: Reflexive + Transitive"],
            rule="modal_system_s4"
        )
    
    if system == ModalSystem.S5 and not (frame.is_reflexive() and frame.is_transitive() and frame.is_symmetric()):
        return False, ProofObject(
            conclusion="VIOLATION: Frame does not satisfy S5 system",
            premises=["Required: Reflexive + Transitive + Symmetric"],
            rule="modal_system_s5"
        )
    
    return True, ProofObject(
        conclusion=f"Frame satisfies {system.name} system",
        premises=[f"System: {system.name}"],
        rule="system_compliant"
    )


def check_accessibility_non_empty(frame: KripkeFrame) -> Tuple[bool, ProofObject]:
    """Serial frames require every world has at least one accessible world.
    
    Falsifies if: any world has an empty accessibility set.
    falsifies_if: any world has an empty accessibility set.
    """
    for world in frame.worlds:
        if not frame.accessibility.get(world.world_id, set()):
            return False, ProofObject(
                conclusion=f"VIOLATION: World {world.world_id} has no accessible worlds",
                premises=[f"World: {world.world_id}", "Accessibility: Empty"],
                rule="modal_serial_frames"
            )
    
    return True, ProofObject(
        conclusion="All worlds have accessible successors",
        premises=[f"Worlds: {len(frame.worlds)}"],
        rule="accessibility_non_empty"
    )


def run_all_invariants() -> dict:
    """Run all D_NECESSITY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    kripke_frame = KripkeFrame(
        worlds=None,
        accessibility=None,
    )

    checks = [
        ("check_accessibility_non_empty", lambda: check_accessibility_non_empty(kripke_frame)),
        ("check_frame_reflexivity", lambda: check_frame_reflexivity(kripke_frame)),
        ("check_frame_symmetry", lambda: check_frame_symmetry(kripke_frame)),
        ("check_frame_transitivity", lambda: check_frame_transitivity(kripke_frame)),
        ("check_system_compliance", lambda: check_system_compliance(kripke_frame, ModalSystem.K)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_NECESSITY invariants: PASS")
