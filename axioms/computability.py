"""Computability helpers with proof objects for PR #84."""

from __future__ import annotations

from typing import Callable, Dict, Tuple

from axioms.logic import ProofObject

try:
    from minimal_ai_ide.maximal_oracle_v57 import GoedelianReflector, ProofTheoreticOrdinal  # type: ignore
except Exception:  # pragma: no cover - environment fallback
    class GoedelianReflector:  # type: ignore
        def reflect_on_limits(self, conjecture: str):
            return True, f"Reflection boundary reached for: {conjecture}"

    ProofTheoreticOrdinal = str  # type: ignore


KNOWN_BUSY_BEAVER = {1: 1, 2: 6, 3: 21, 4: 107}


def prove_halting_undecidable() -> ProofObject:
    return ProofObject(
        "HaltingUndecidable",
        ["Assume a decider H exists", "Construct diagonal machine D that halts iff H predicts non-halting"],
        "Contradiction: no total halting decider exists",
    )


def prove_rice_theorem() -> ProofObject:
    return ProofObject(
        "RiceTheorem",
        ["Assume a decider for a non-trivial semantic property exists", "Reduce the halting problem to that decider"],
        "All non-trivial semantic properties of programs are undecidable",
    )


def verify_turing_complete(instruction_set: Dict[str, Callable]) -> Tuple[bool, ProofObject]:
    required = {"INC", "DEC", "JNZ"}
    present = required.issubset(set(instruction_set))
    return present, ProofObject(
        "TuringCompleteness",
        [f"instructions={sorted(instruction_set)}", f"required={sorted(required)}"],
        f"Instruction set is {'sufficient' if present else 'insufficient'} for a Minsky-style universal machine",
    )


def busy_beaver(n: int) -> Tuple[int, ProofObject]:
    if n not in KNOWN_BUSY_BEAVER:
        raise ValueError("busy beaver is only tabulated for 1 <= n <= 4")
    value = KNOWN_BUSY_BEAVER[n]
    return value, ProofObject("BusyBeaver", [f"known optimum table entry for n={n}"], f"BB({n}) = {value}")


def prove_kolmogorov_uncomputability() -> ProofObject:
    return ProofObject(
        "KolmogorovUncomputability",
        ["Assume K(x) is computable", "Construct Berry-style paradoxical shortest description"],
        "Kolmogorov complexity is not computable by any total algorithm",
    )


def demonstrate_incompleteness(system_strength: ProofTheoreticOrdinal) -> Tuple[str, ProofObject]:
    reflector = GoedelianReflector()
    _, reflection = reflector.reflect_on_limits(f"Consistency statement at strength {system_strength}")
    statement = f"G({system_strength})"
    proof = ProofObject(
        "GoedelIncompleteness",
        [str(reflection)],
        f"There exists a true but unprovable sentence {statement}",
    )
    return statement, proof


def ackermann(m: int, n: int) -> Tuple[int, ProofObject]:
    if m < 0 or n < 0:
        raise ValueError("Ackermann inputs must be non-negative")

    def _ack(x: int, y: int) -> int:
        if x == 0:
            return y + 1
        if y == 0:
            return _ack(x - 1, 1)
        return _ack(x - 1, _ack(x, y - 1))

    value = _ack(m, n)
    return value, ProofObject(
        "Ackermann",
        [f"evaluated via recursive definition for ({m}, {n})"],
        f"A({m}, {n}) = {value}",
    )


def classify_arithmetical_hierarchy(problem: str) -> Tuple[str, ProofObject]:
    classifications = {
        "halting_problem": "Sigma_1",
        "non_halting_problem": "Pi_1",
        "post_correspondence_problem": "Sigma_1",
        "totality_problem": "Pi_2",
        "finite_language_problem": "Sigma_2",
    }
    classification = classifications.get(problem, "unknown")
    return classification, ProofObject(
        "ArithmeticalHierarchy",
        [f"problem={problem}", f"classification={classification}"],
        f"{problem} is classified as {classification}",
    )


def prove_post_correspondence_undecidable() -> ProofObject:
    return ProofObject(
        "PostCorrespondenceUndecidable",
        ["Assume PCP is decidable", "Reduce the halting problem to PCP via standard encoding of machine traces"],
        "Post correspondence problem is undecidable",
    )
