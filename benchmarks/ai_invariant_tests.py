"""PR #83 AI invariant benchmark suite."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataclasses import dataclass
from typing import Any, Dict, List

from axioms.combinatorics import binomial, catalan, inclusion_exclusion, pigeonhole
from axioms.computability import (
    busy_beaver,
    demonstrate_incompleteness,
    prove_halting_undecidable,
    prove_kolmogorov_uncomputability,
    prove_rice_theorem,
    verify_turing_complete,
)
from axioms.epistemic_logic import (
    KripkeModel,
    construct_gettier_counterexample,
    evaluate_common_knowledge,
    evaluate_jtb,
    evaluate_knowledge,
    test_kk_principle,
)
from axioms.game_theory import (
    StrategyProfile,
    analyze_iterated_prisoners_dilemma,
    eliminate_dominated,
    find_nash_equilibria,
    prove_minimax,
    verify_incentive_compatibility,
)
from axioms.logic import ProofObject, merkle_root_over_proofs
from axioms.number_theory import bezout, chinese_remainder_theorem, euler_totient, fermat_little, gcd_extended, is_prime, modular_exponentiation
from axioms.pattern_recognition import CompositionalRule, Grid, PrimitiveOperation, verify_rule
from axioms.peano_extended import (
    verify_p10_distributivity,
    verify_p11_additive_identity,
    verify_p12_multiplicative_identity,
    verify_p13_multiplicative_annihilation,
    verify_p14_well_ordering,
)
from axioms.yeshua_axioms import YeshuaClaim, verify_yeshua_standard


@dataclass
class AIInvariantTest:
    id: str
    domain: str
    difficulty: str
    problem: str
    solution: Any
    proof: ProofObject
    claim: YeshuaClaim


AI_INVARIANT_REGISTRY: Dict[str, AIInvariantTest] = {}


def register_invariant(test: AIInvariantTest) -> None:
    violations = verify_yeshua_standard(test.claim)
    if violations:
        raise AssertionError(f"Yeshua violations: {violations}")
    AI_INVARIANT_REGISTRY[test.id] = test



def _claim(source: str, statement: str, proof: ProofObject) -> YeshuaClaim:
    return YeshuaClaim(source=source, statement=statement, derivation=proof)



def _register_all() -> None:
    if AI_INVARIANT_REGISTRY:
        return

    # Peano: 5
    peano_specs = [
        ("AI_PEANO_001", verify_p10_distributivity(2, 3, 4), "D_PEANO_EXT", "FOUNDATION", "Distributivity over Peano addition"),
        ("AI_PEANO_002", verify_p11_additive_identity(7), "D_PEANO_EXT", "FOUNDATION", "Additive identity"),
        ("AI_PEANO_003", verify_p12_multiplicative_identity(9), "D_PEANO_EXT", "FOUNDATION", "Multiplicative identity"),
        ("AI_PEANO_004", verify_p13_multiplicative_annihilation(11), "D_PEANO_EXT", "FOUNDATION", "Multiplicative annihilation"),
        ("AI_PEANO_005", verify_p14_well_ordering([5, 2, 9]), "D_PEANO_EXT", "FOUNDATION", "Well ordering on a finite subset"),
    ]
    for test_id, (valid, proof), domain, difficulty, problem in peano_specs:
        register_invariant(AIInvariantTest(test_id, domain, difficulty, problem, valid, proof, _claim("axioms/peano_extended.py", problem, proof)))

    # Number theory: 10
    nt_entries = [
        ("AI_NUMTH_001", gcd_extended(30, 21)[1], gcd_extended(30, 21)[0], "Extended gcd for 30 and 21"),
        ("AI_NUMTH_002", bezout(30, 21)[1], bezout(30, 21)[0], "Bezout coefficients for 30 and 21"),
        ("AI_NUMTH_003", euler_totient(9)[1], euler_totient(9)[0], "Euler totient of 9"),
        ("AI_NUMTH_004", euler_totient(10)[1], euler_totient(10)[0], "Euler totient of 10"),
        ("AI_NUMTH_005", modular_exponentiation(2, 10, 17)[1], modular_exponentiation(2, 10, 17)[0], "Modular exponentiation 2^10 mod 17"),
        ("AI_NUMTH_006", modular_exponentiation(3, 7, 11)[1], modular_exponentiation(3, 7, 11)[0], "Modular exponentiation 3^7 mod 11"),
        ("AI_NUMTH_007", fermat_little(2, 5)[1], fermat_little(2, 5)[0], "Fermat's little theorem for 2 mod 5"),
        ("AI_NUMTH_008", chinese_remainder_theorem([2, 3, 2], [3, 5, 7])[1], chinese_remainder_theorem([2, 3, 2], [3, 5, 7])[0], "CRT for 2,3,2 / 3,5,7"),
        ("AI_NUMTH_009", is_prime(29)[1], is_prime(29)[0], "Primality of 29"),
        ("AI_NUMTH_010", is_prime(21)[1], is_prime(21)[0], "Compositeness of 21"),
    ]
    for test_id, proof, solution, problem in nt_entries:
        register_invariant(AIInvariantTest(test_id, "D_NUMBER_THEORY", "AIME", problem, solution, proof, _claim("axioms/number_theory.py", problem, proof)))

    # Combinatorics: 10
    comb_entries = [
        ("AI_COMB_001", binomial(5, 2)[1], binomial(5, 2)[0], "Binomial coefficient C(5,2)"),
        ("AI_COMB_002", binomial(6, 3)[1], binomial(6, 3)[0], "Binomial coefficient C(6,3)"),
        ("AI_COMB_003", catalan(0)[1], catalan(0)[0], "Catalan number C0"),
        ("AI_COMB_004", catalan(3)[1], catalan(3)[0], "Catalan number C3"),
        ("AI_COMB_005", pigeonhole(5, 4), True, "Pigeonhole principle with 5 items, 4 bins"),
        ("AI_COMB_006", pigeonhole(3, 5), False, "No forced collision with 3 items, 5 bins"),
        ("AI_COMB_007", inclusion_exclusion([4, 5], [2])[1], inclusion_exclusion([4, 5], [2])[0], "Inclusion-exclusion over two sets"),
        ("AI_COMB_008", inclusion_exclusion([6, 7, 5], [2, 1, 1])[1], inclusion_exclusion([6, 7, 5], [2, 1, 1])[0], "Inclusion-exclusion over three coarse intersections"),
        ("AI_COMB_009", binomial(7, 1)[1], binomial(7, 1)[0], "Binomial coefficient C(7,1)"),
        ("AI_COMB_010", catalan(4)[1], catalan(4)[0], "Catalan number C4"),
    ]
    for test_id, proof, solution, problem in comb_entries:
        register_invariant(AIInvariantTest(test_id, "D_COMBINATORICS", "HMMT", problem, solution, proof, _claim("axioms/combinatorics.py", problem, proof)))

    # Game theory: 5
    pd = StrategyProfile(
        players=("alice", "bob"),
        strategies=(("C", "D"), ("C", "D")),
        payoffs={
            ("C", "C"): (3, 3),
            ("C", "D"): (0, 5),
            ("D", "C"): (5, 0),
            ("D", "D"): (1, 1),
        },
    )
    zero_sum = StrategyProfile(
        players=("row", "col"),
        strategies=(("U", "D"), ("L", "R")),
        payoffs={
            ("U", "L"): (1, -1),
            ("U", "R"): (-1, 1),
            ("D", "L"): (-1, 1),
            ("D", "R"): (1, -1),
        },
    )
    gt_entries = [
        ("AI_GAME_001", find_nash_equilibria(pd)[1], find_nash_equilibria(pd)[0], "Pure Nash equilibria in prisoner's dilemma"),
        ("AI_GAME_002", eliminate_dominated(pd)[1], eliminate_dominated(pd)[0].strategies, "Eliminate dominated strategies in prisoner's dilemma"),
        ("AI_GAME_003", prove_minimax(zero_sum), "value", "Minimax in matching pennies"),
        ("AI_GAME_004", analyze_iterated_prisoners_dilemma(3, {"tit_for_tat": lambda own, opp: "C" if not opp or opp[-1] == "C" else "D", "defect": lambda own, opp: "D"}), "trace", "Iterated prisoner's dilemma analysis"),
        ("AI_GAME_005", verify_incentive_compatibility({"high": {"high": 5, "low": 1}, "low": {"high": 4, "low": 1}}, [{"high": 5, "low": 1}])[1], verify_incentive_compatibility({"high": {"high": 5, "low": 1}, "low": {"high": 4, "low": 1}}, [{"high": 5, "low": 1}])[0], "Incentive compatibility check"),
    ]
    for test_id, proof, solution, problem in gt_entries:
        register_invariant(AIInvariantTest(test_id, "D_GAME_THEORY", "GPQA", problem, solution, proof, _claim("axioms/game_theory.py", problem, proof)))

    # Epistemic logic: 5
    model = KripkeModel(
        worlds={"w1", "w2"},
        accessibility={"alice": {("w1", "w1"), ("w1", "w2"), ("w2", "w2")}, "bob": {("w1", "w1"), ("w2", "w2")}},
        valuation={
            "w1": {"p": True, "believes:alice:p": True},
            "w2": {"p": True, "believes:alice:p": True},
        },
    )
    just = ProofObject("Justification", ["observation chain is valid"], "belief is justified")
    gettier_model, gettier_proof = construct_gettier_counterexample()
    epi_entries = [
        ("AI_EPIST_001", evaluate_knowledge(model, "alice", "p", "w1")[1], evaluate_knowledge(model, "alice", "p", "w1")[0], "Agent knowledge in a two-world model"),
        ("AI_EPIST_002", evaluate_common_knowledge(model, ["alice", "bob"], "p", "w1")[1], evaluate_common_knowledge(model, ["alice", "bob"], "p", "w1")[0], "Common knowledge closure"),
        ("AI_EPIST_003", evaluate_jtb(model, "alice", "p", "w1", just)[1], evaluate_jtb(model, "alice", "p", "w1", just)[0], "Justified true belief check"),
        ("AI_EPIST_004", gettier_proof, gettier_model.worlds, "Gettier counterexample construction"),
        ("AI_EPIST_005", test_kk_principle(model, "alice", "p")[1], test_kk_principle(model, "alice", "p")[0], "KK principle test"),
    ]
    for test_id, proof, solution, problem in epi_entries:
        register_invariant(AIInvariantTest(test_id, "D_EPISTEMIC_LOGIC", "GPQA", problem, solution, proof, _claim("axioms/epistemic_logic.py", problem, proof)))

    # Computability: 5
    comp_entries = [
        ("AI_COMP_001", prove_halting_undecidable(), "undecidable", "Halting problem"),
        ("AI_COMP_002", prove_rice_theorem(), "undecidable", "Rice's theorem"),
        ("AI_COMP_003", verify_turing_complete({"INC": lambda x: x + 1, "DEC": lambda x: x - 1, "JNZ": lambda x: x != 0})[1], True, "Turing completeness witness"),
        ("AI_COMP_004", busy_beaver(3)[1], busy_beaver(3)[0], "Busy beaver BB(3)"),
        ("AI_COMP_005", demonstrate_incompleteness("epsilon_0")[1], demonstrate_incompleteness("epsilon_0")[0], "Gödel incompleteness witness"),
    ]
    for test_id, proof, solution, problem in comp_entries:
        register_invariant(AIInvariantTest(test_id, "D_COMPUTABILITY", "HLE", problem, solution, proof, _claim("axioms/computability.py", problem, proof)))

    # Pattern recognition: 10
    pattern_cases = [
        (Grid([[1, 0], [0, 1]]), Grid([[1, 0], [0, 1]]), CompositionalRule([(PrimitiveOperation.IDENTITY, {})]), "identity"),
        (Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]]), CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]), "rotate_90"),
        (Grid([[1, 2], [3, 4]]), Grid([[4, 3], [2, 1]]), CompositionalRule([(PrimitiveOperation.ROTATE_180, {})]), "rotate_180"),
        (Grid([[1, 2], [3, 4]]), Grid([[2, 1], [4, 3]]), CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]), "reflect_v"),
        (Grid([[1, 0], [1, 0]]), Grid([[2, 0], [2, 0]]), CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": {0: 0, 1: 2}})]), "recolor_a"),
        (Grid([[2, 0], [2, 0]]), Grid([[3, 0], [3, 0]]), CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": {0: 0, 2: 3}})]), "recolor_b"),
        (Grid([[1, 1, 0], [1, 0, 0], [0, 0, 0]]), Grid([[1, 1], [1, 0]]), CompositionalRule([(PrimitiveOperation.EXTRACT_OBJECT, {})]), "extract_object"),
        (Grid([[1, 1, 1], [1, 1, 1], [1, 1, 1]]), Grid([[1, 1, 1], [1, 0, 1], [1, 1, 1]]), CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]), "detect_boundary"),
        (Grid([[1, 0], [0, 1]]), Grid([[2]]), CompositionalRule([(PrimitiveOperation.COUNT, {})]), "count"),
        (Grid([[1, 2], [0, 0]]), Grid([[2, 1], [0, 0]]), CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]), "reflect_v_2"),
    ]
    for index, (inp, out, rule, label) in enumerate(pattern_cases, start=1):
        ok, proof = verify_rule(rule, [(inp, out)])
        register_invariant(AIInvariantTest(f"AI_PATTERN_{index:03d}", "D_PATTERN_RECOGNITION", "ARC_AGI", f"Pattern case {label}", ok, proof, _claim("axioms/pattern_recognition.py", f"Pattern case {label}", proof)))



def run_ai_invariant_suite() -> Dict[str, Any]:
    _register_all()
    results = []
    proofs = []
    for test_id in sorted(AI_INVARIANT_REGISTRY):
        test = AI_INVARIANT_REGISTRY[test_id]
        valid = test.proof.is_valid()
        yeshua_ok = len(verify_yeshua_standard(test.claim)) == 0
        results.append({"id": test_id, "proof_valid": valid, "yeshua_ok": yeshua_ok, "domain": test.domain})
        proofs.append(test.proof)
    return {
        "total": len(results),
        "all_valid": all(entry["proof_valid"] and entry["yeshua_ok"] for entry in results),
        "merkle_root": merkle_root_over_proofs(proofs),
        "results": results,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_ai_invariant_suite(), indent=2, sort_keys=True))
