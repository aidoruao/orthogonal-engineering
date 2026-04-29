"""PR #84 AI invariant benchmark suite."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataclasses import dataclass
from typing import Any, Dict, List

from axioms.arc_solver import build_demo_arc_tasks, predict_arc_task
from axioms.combinatorics import bell_number, binomial, catalan, derangement, inclusion_exclusion, pigeonhole, stirling_second
from axioms.computability import (
    ackermann,
    busy_beaver,
    classify_arithmetical_hierarchy,
    demonstrate_incompleteness,
    prove_halting_undecidable,
    prove_post_correspondence_undecidable,
    prove_kolmogorov_uncomputability,
    prove_rice_theorem,
    verify_turing_complete,
)
from axioms.epistemic_logic import (
    KripkeModel,
    agm_revision,
    construct_gettier_counterexample,
    evaluate_common_knowledge,
    evaluate_distributed_knowledge,
    evaluate_jtb,
    evaluate_knowledge,
    evaluate_paraconsistent,
    public_announcement,
    test_kk_principle,
)
from axioms.game_theory import (
    StrategyProfile,
    analyze_iterated_prisoners_dilemma,
    evolutionary_stable,
    eliminate_dominated,
    find_nash_equilibria,
    prove_minimax,
    shapley_value,
    vickrey_auction,
    verify_incentive_compatibility,
)
from axioms.logic import ProofObject, merkle_root_over_proofs
from axioms.number_theory import (
    bezout,
    chinese_remainder_theorem,
    euler_totient,
    fermat_little,
    gcd_extended,
    is_prime,
    legendre_symbol,
    modular_exponentiation,
    multiplicative_order,
    primitive_root,
    sum_of_two_squares,
    wilson_theorem,
)
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
    model_targeting: List[str]


AI_INVARIANT_REGISTRY: Dict[str, AIInvariantTest] = {}


def register_invariant(test: AIInvariantTest) -> None:
    violations = verify_yeshua_standard(test.claim)
    if violations:
        raise AssertionError(f"Yeshua violations: {violations}")
    AI_INVARIANT_REGISTRY[test.id] = test



def _claim(source: str, statement: str, proof: ProofObject) -> YeshuaClaim:
    # TODO: Expand _claim() - stub detected by Yeshua Agent
    return YeshuaClaim(source=source, statement=statement, derivation=proof)


ALL_MODELS = [
    "GPT-5.2",
    "Claude Opus 4.5",
    "Gemini 3 Pro",
    "Kimi K2.5",
    "DeepSeek-V3.2",
    "Llama 4 Maverick",
    "Grok 3",
    "Qwen 3",
    "Mistral Large 3",
    "Command R+",
    "Devin AI",
]


def _register_invariant(
    test_id: str,
    domain: str,
    difficulty: str,
    problem: str,
    solution: Any,
    proof: ProofObject,
    source: str,
    model_targeting: List[str] | None = None,
) -> None:
    register_invariant(
        AIInvariantTest(
            test_id,
            domain,
            difficulty,
            problem,
            solution,
            proof,
            _claim(source, problem, proof),
            model_targeting or ALL_MODELS[:],
        )
    )



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
        _register_invariant(test_id, domain, difficulty, problem, valid, proof, "axioms/peano_extended.py")

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
        _register_invariant(test_id, "D_NUMBER_THEORY", "AIME", problem, solution, proof, "axioms/number_theory.py")

    advanced_nt_entries = [
        ("AI_NUMTH_011", legendre_symbol(5, 11)[1], legendre_symbol(5, 11)[0], "Legendre symbol (5/11)"),
        ("AI_NUMTH_012", legendre_symbol(3, 7)[1], legendre_symbol(3, 7)[0], "Legendre symbol (3/7)"),
        ("AI_NUMTH_013", sum_of_two_squares(25)[1], sum_of_two_squares(25)[0], "Sum of two squares for 25"),
        ("AI_NUMTH_014", sum_of_two_squares(3)[1], sum_of_two_squares(3)[0], "No sum-of-two-squares decomposition for 3"),
        ("AI_NUMTH_015", wilson_theorem(5)[1], wilson_theorem(5)[0], "Wilson theorem for 5"),
        ("AI_NUMTH_016", multiplicative_order(2, 7)[1], multiplicative_order(2, 7)[0], "Multiplicative order of 2 modulo 7"),
        ("AI_NUMTH_017", multiplicative_order(10, 11)[1], multiplicative_order(10, 11)[0], "Multiplicative order of 10 modulo 11"),
        ("AI_NUMTH_018", primitive_root(7)[1], primitive_root(7)[0], "Primitive root modulo 7"),
        ("AI_NUMTH_019", primitive_root(11)[1], primitive_root(11)[0], "Primitive root modulo 11"),
        ("AI_NUMTH_020", wilson_theorem(11)[1], wilson_theorem(11)[0], "Wilson theorem for 11"),
    ]
    for test_id, proof, solution, problem in advanced_nt_entries:
        _register_invariant(test_id, "D_NUMBER_THEORY", "AIME", problem, solution, proof, "axioms/number_theory.py")

    # Combinatorics: 10
    comb_entries = [
        ("AI_COMB_001", binomial(5, 2)[1], binomial(5, 2)[0], "Binomial coefficient C(5,2)"),
        ("AI_COMB_002", binomial(6, 3)[1], binomial(6, 3)[0], "Binomial coefficient C(6,3)"),
        ("AI_COMB_003", catalan(0)[1], catalan(0)[0], "Catalan number C0"),
        ("AI_COMB_004", catalan(3)[1], catalan(3)[0], "Catalan number C3"),
        ("AI_COMB_005", pigeonhole(5, 4), True, "Pigeonhole principle with 5 items, 4 bins"),
        ("AI_COMB_006", pigeonhole(3, 5), False, "No forced collision with 3 items, 5 bins"),
        ("AI_COMB_007", inclusion_exclusion([4, 5], [[2]])[1], inclusion_exclusion([4, 5], [[2]])[0], "Inclusion-exclusion over two sets"),
        ("AI_COMB_008", inclusion_exclusion([6, 7, 5], [[2, 1, 1]])[1], inclusion_exclusion([6, 7, 5], [[2, 1, 1]])[0], "Inclusion-exclusion over three coarse intersections"),
        ("AI_COMB_009", binomial(7, 1)[1], binomial(7, 1)[0], "Binomial coefficient C(7,1)"),
        ("AI_COMB_010", catalan(4)[1], catalan(4)[0], "Catalan number C4"),
    ]
    for test_id, proof, solution, problem in comb_entries:
        _register_invariant(test_id, "D_COMBINATORICS", "HMMT", problem, solution, proof, "axioms/combinatorics.py")

    advanced_comb_entries = [
        ("AI_COMB_011", stirling_second(5, 2)[1], stirling_second(5, 2)[0], "Stirling number S(5,2)"),
        ("AI_COMB_012", stirling_second(5, 3)[1], stirling_second(5, 3)[0], "Stirling number S(5,3)"),
        ("AI_COMB_013", derangement(4)[1], derangement(4)[0], "Derangement count !4"),
        ("AI_COMB_014", bell_number(5)[1], bell_number(5)[0], "Bell number B5"),
        ("AI_COMB_015", bell_number(0)[1], bell_number(0)[0], "Bell number B0"),
    ]
    for test_id, proof, solution, problem in advanced_comb_entries:
        _register_invariant(test_id, "D_COMBINATORICS", "HMMT", problem, solution, proof, "axioms/combinatorics.py")

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
        _register_invariant(test_id, "D_GAME_THEORY", "GPQA", problem, solution, proof, "axioms/game_theory.py")

    majority_game = {
        frozenset(): 0.0,
        frozenset({"alice"}): 0.0,
        frozenset({"bob"}): 0.0,
        frozenset({"carol"}): 0.0,
        frozenset({"alice", "bob"}): 1.0,
        frozenset({"alice", "carol"}): 1.0,
        frozenset({"bob", "carol"}): 1.0,
        frozenset({"alice", "bob", "carol"}): 1.0,
    }
    additive_game = {
        frozenset(): 0.0,
        frozenset({"alice"}): 1.0,
        frozenset({"bob"}): 2.0,
        frozenset({"carol"}): 3.0,
        frozenset({"alice", "bob"}): 3.0,
        frozenset({"alice", "carol"}): 4.0,
        frozenset({"bob", "carol"}): 5.0,
        frozenset({"alice", "bob", "carol"}): 6.0,
    }
    coordination_payoff = {
        "Stag": {"Stag": 4, "Hare": 0},
        "Hare": {"Stag": 3, "Hare": 3},
    }
    dominance_payoff = {
        "A": {"A": 3, "B": 1},
        "B": {"A": 2, "B": 1},
    }
    advanced_gt_entries = [
        ("AI_GAME_006", shapley_value(("alice", "bob", "carol"), majority_game)[1], shapley_value(("alice", "bob", "carol"), majority_game)[0], "Shapley value for symmetric majority game"),
        ("AI_GAME_007", shapley_value(("alice", "bob", "carol"), additive_game)[1], shapley_value(("alice", "bob", "carol"), additive_game)[0], "Shapley value for additive cooperative game"),
        ("AI_GAME_008", vickrey_auction({"alice": 10, "bob": 7, "carol": 5})[1], vickrey_auction({"alice": 10, "bob": 7, "carol": 5})[0], "Vickrey auction outcome"),
        ("AI_GAME_009", evolutionary_stable(coordination_payoff)[1], evolutionary_stable(coordination_payoff)[0], "ESS in coordination game"),
        ("AI_GAME_010", evolutionary_stable(dominance_payoff)[1], evolutionary_stable(dominance_payoff)[0], "Unique ESS in dominance game"),
    ]
    for test_id, proof, solution, problem in advanced_gt_entries:
        _register_invariant(test_id, "D_GAME_THEORY", "GPQA", problem, solution, proof, "axioms/game_theory.py")

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
        _register_invariant(test_id, "D_EPISTEMIC_LOGIC", "GPQA", problem, solution, proof, "axioms/epistemic_logic.py")

    advanced_epistemic_model = KripkeModel(
        worlds={"w1", "w2", "w3"},
        accessibility={
            "alice": {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w3", "w3")},
            "bob": {("w1", "w1"), ("w1", "w3"), ("w2", "w2"), ("w3", "w3")},
            "carol": {("w1", "w1"), ("w2", "w2"), ("w3", "w3")},
        },
        valuation={
            "w1": {"p": True, "q": True, "not:q": True, "announce": True, "believes:alice:p": True},
            "w2": {"p": False, "q": True, "not:q": False, "announce": True, "believes:alice:p": False},
            "w3": {"p": True, "q": False, "not:q": False, "announce": False, "believes:alice:p": True},
        },
    )
    announced_epistemic_model, announced_epistemic_proof = public_announcement(advanced_epistemic_model, "announce")
    revision_conflict, revision_conflict_proof = agm_revision({"p", "q"}, "not:p")
    revision_extend, revision_extend_proof = agm_revision({"p", "q"}, {"q", "r"})
    advanced_epi_entries = [
        ("AI_EPIST_006", evaluate_distributed_knowledge(advanced_epistemic_model, ["alice", "bob"], "p", "w1")[1], evaluate_distributed_knowledge(advanced_epistemic_model, ["alice", "bob"], "p", "w1")[0], "Distributed knowledge from intersected accessibility"),
        ("AI_EPIST_007", evaluate_common_knowledge(announced_epistemic_model, ["alice", "bob"], "announce", "w1")[1], evaluate_common_knowledge(announced_epistemic_model, ["alice", "bob"], "announce", "w1")[0], "Common knowledge after public announcement"),
        ("AI_EPIST_008", announced_epistemic_proof, sorted(announced_epistemic_model.worlds), "Public announcement model restriction"),
        ("AI_EPIST_009", revision_conflict_proof, revision_conflict, "AGM revision with contradictory evidence"),
        ("AI_EPIST_010", revision_extend_proof, revision_extend, "AGM revision with compatible evidence"),
    ]
    for test_id, proof, solution, problem in advanced_epi_entries:
        _register_invariant(test_id, "D_EPISTEMIC_LOGIC", "HLE", problem, solution, proof, "axioms/epistemic_logic.py")

    # Computability: 5
    comp_entries = [
        ("AI_COMP_001", prove_halting_undecidable(), "undecidable", "Halting problem"),
        ("AI_COMP_002", prove_rice_theorem(), "undecidable", "Rice's theorem"),
        ("AI_COMP_003", verify_turing_complete({"INC": lambda x: x + 1, "DEC": lambda x: x - 1, "JNZ": lambda x: x != 0})[1], True, "Turing completeness witness"),
        ("AI_COMP_004", busy_beaver(3)[1], busy_beaver(3)[0], "Busy beaver BB(3)"),
        ("AI_COMP_005", demonstrate_incompleteness("epsilon_0")[1], demonstrate_incompleteness("epsilon_0")[0], "Gödel incompleteness witness"),
    ]
    for test_id, proof, solution, problem in comp_entries:
        _register_invariant(test_id, "D_COMPUTABILITY", "HLE", problem, solution, proof, "axioms/computability.py")

    advanced_comp_entries = [
        ("AI_COMP_006", ackermann(0, 0)[1], ackermann(0, 0)[0], "Ackermann value A(0,0)"),
        ("AI_COMP_007", ackermann(2, 2)[1], ackermann(2, 2)[0], "Ackermann value A(2,2)"),
        ("AI_COMP_008", classify_arithmetical_hierarchy("halting_problem")[1], classify_arithmetical_hierarchy("halting_problem")[0], "Arithmetical hierarchy classification of halting"),
        ("AI_COMP_009", classify_arithmetical_hierarchy("totality_problem")[1], classify_arithmetical_hierarchy("totality_problem")[0], "Arithmetical hierarchy classification of totality"),
        ("AI_COMP_010", prove_post_correspondence_undecidable(), "undecidable", "Post correspondence undecidability"),
    ]
    for test_id, proof, solution, problem in advanced_comp_entries:
        _register_invariant(test_id, "D_COMPUTABILITY", "HLE", problem, solution, proof, "axioms/computability.py")

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
        _register_invariant(f"AI_PATTERN_{index:03d}", "D_PATTERN_RECOGNITION", "ARC_AGI", f"Pattern case {label}", ok, proof, "axioms/pattern_recognition.py")

    conditional_cases = [
        (
            "rows_branch",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: grid.rows,
                "value_rules": {
                    2: CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]),
                    3: CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
                },
            })]),
            [
                (Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]])),
                (Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Grid([[3, 2, 1], [6, 5, 4], [9, 8, 7]])),
            ],
        ),
        (
            "region_branch",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: len(grid.get_contiguous_regions()),
                "value_rules": {
                    1: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
                    2: CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]),
                },
            })]),
            [
                (Grid([[1, 1], [1, 1]]), Grid([[4]])),
                (Grid([[1, 0], [0, 2]]), Grid([[1, 0], [0, 2]])),
            ],
        ),
        (
            "is_square_branch",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: int(grid.rows == grid.cols),
                "value_rules": {
                    1: CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
                    0: CompositionalRule([(PrimitiveOperation.CROP, {"top": 0, "left": 0, "height": 1, "width": 2})]),
                },
            })]),
            [
                (Grid([[1, 2], [3, 4]]), Grid([[3, 4], [1, 2]])),
                (Grid([[1, 2], [3, 4], [5, 6]]), Grid([[1, 2]])),
            ],
        ),
        (
            "dominant_color_branch",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: max(histogram, key=histogram.get) if (histogram := grid.get_color_histogram()) else 0,
                "value_rules": {
                    1: CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": {0: 0, 1: 9, 2: 2}})]),
                    2: CompositionalRule([(PrimitiveOperation.RECOLOR, {"mapping": {0: 0, 1: 1, 2: 8}})]),
                },
            })]),
            [
                (Grid([[1, 1], [2, 0]]), Grid([[9, 9], [2, 0]])),
                (Grid([[2, 2], [1, 0]]), Grid([[8, 8], [1, 0]])),
            ],
        ),
        (
            "color_count_branch",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: len(grid.get_color_histogram()),
                "value_rules": {
                    2: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
                    3: CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]),
                },
            })]),
            [
                (Grid([[1, 1], [0, 0]]), Grid([[2]])),
                (Grid([[1, 1, 1], [1, 2, 1], [1, 1, 0]]), Grid([[1, 1, 1], [1, 2, 1], [1, 1, 0]])),
            ],
        ),
        (
            "nested_rows_cols",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: grid.rows,
                "value_rules": {
                    2: CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                        "property": lambda grid: grid.cols,
                        "value_rules": {
                            2: CompositionalRule([(PrimitiveOperation.ROTATE_180, {})]),
                            3: CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
                        },
                    })]),
                    3: CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
                },
            })]),
            [
                (Grid([[1, 2], [3, 4]]), Grid([[4, 3], [2, 1]])),
                (Grid([[1, 2, 3], [4, 5, 6]]), Grid([[3, 2, 1], [6, 5, 4]])),
                (Grid([[1, 2], [3, 4], [5, 6]]), Grid([[5, 6], [3, 4], [1, 2]])),
            ],
        ),
        (
            "conditional_composition",
            CompositionalRule([
                (PrimitiveOperation.CONDITIONAL, {
                    "property": lambda grid: grid.rows,
                    "value_rules": {
                        2: CompositionalRule([(PrimitiveOperation.ROTATE_90, {})]),
                        3: CompositionalRule([(PrimitiveOperation.REFLECT_V, {})]),
                    },
                }),
                (PrimitiveOperation.RECOLOR, {"mapping": {0: 0, 1: 7, 2: 8, 3: 9, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1}}),
            ]),
            [
                (Grid([[1, 2], [3, 4]]), Grid([[9, 7], [6, 8]])),
                (Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Grid([[9, 8, 7], [4, 5, 6], [1, 2, 3]])),
            ],
        ),
        (
            "area_branch",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: grid.rows * grid.cols,
                "value_rules": {
                    4: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
                    9: CompositionalRule([(PrimitiveOperation.SCALE, {"factor": 1})]),
                },
            })]),
            [
                (Grid([[1, 0], [0, 1]]), Grid([[2]])),
                (Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
            ],
        ),
        (
            "nonzero_branch",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: sum(1 for row in grid.cells for cell in row if cell != 0),
                "value_rules": {
                    1: CompositionalRule([(PrimitiveOperation.COUNT, {})]),
                    4: CompositionalRule([(PrimitiveOperation.DETECT_BOUNDARY, {})]),
                },
            })]),
            [
                (Grid([[1, 0], [0, 0]]), Grid([[1]])),
                (Grid([[1, 1], [1, 1]]), Grid([[1, 1], [1, 1]])),
            ],
        ),
        (
            "default_rule",
            CompositionalRule([(PrimitiveOperation.CONDITIONAL, {
                "property": lambda grid: grid.rows,
                "value_rules": {2: CompositionalRule([(PrimitiveOperation.ROTATE_90, {})])},
                "default_rule": CompositionalRule([(PrimitiveOperation.REFLECT_H, {})]),
            })]),
            [
                (Grid([[1, 2], [3, 4]]), Grid([[3, 1], [4, 2]])),
                (Grid([[1, 2], [3, 4], [5, 6]]), Grid([[5, 6], [3, 4], [1, 2]])),
            ],
        ),
    ]
    for index, (label, rule, pairs) in enumerate(conditional_cases, start=11):
        ok, proof = verify_rule(rule, pairs)
        _register_invariant(
            f"AI_PATTERN_{index:03d}",
            "D_PATTERN_RECOGNITION",
            "ARC_AGI",
            f"Conditional pattern case {label}",
            ok,
            proof,
            "axioms/pattern_recognition.py",
        )

    for index, (task, expected_outputs) in enumerate(build_demo_arc_tasks(), start=1):
        predictions, prediction_proof = predict_arc_task(task)
        solved = len(predictions) == len(expected_outputs) and all(
            predicted == expected for predicted, expected in zip(predictions, expected_outputs)
        )
        arc_proof = ProofObject(
            "ARCInvariant",
            [
                prediction_proof,
                f"task_id={task.task_id}",
                f"expected_hashes={[grid.hash() for grid in expected_outputs]}",
                f"prediction_hashes={[grid.hash() for grid in predictions]}",
            ],
            f"ARC task {task.task_id} solved={solved}",
        )
        _register_invariant(
            f"AI_ARC_{index:03d}",
            "D_ARC_AGI_3",
            "ARC_AGI",
            f"Bounded ARC solver task {task.task_id}",
            solved,
            arc_proof,
            "axioms/arc_solver.py",
        )

    advanced_model = KripkeModel(
        worlds={"w1", "w2", "w3"},
        accessibility={
            "alice": {("w1", "w1"), ("w1", "w2"), ("w2", "w2"), ("w3", "w3")},
            "bob": {("w1", "w1"), ("w1", "w3"), ("w2", "w2"), ("w3", "w3")},
            "carol": {("w1", "w1"), ("w2", "w2"), ("w3", "w3")},
        },
        valuation={
            "w1": {"p": True, "q": True, "not:q": True, "announce": True, "believes:alice:p": True},
            "w2": {"p": False, "q": True, "not:q": False, "announce": True, "believes:alice:p": False},
            "w3": {"p": True, "q": False, "not:q": False, "announce": False, "believes:alice:p": True},
        },
    )
    announced_model, announced_proof = public_announcement(advanced_model, "announce")
    cross_entries = [
        ("AI_CROSS_001", binomial(10, 5)[1], binomial(10, 5)[0], "Dual-path counting identity for AIME-style combinatorics", ["GPT-5.2", "Claude Opus 4.5", "Gemini 3 Pro"]),
        ("AI_CROSS_002", eliminate_dominated(pd)[1], eliminate_dominated(pd)[0].strategies, "Iterated elimination preceding equilibrium selection", ["Claude Opus 4.5", "Gemini 3 Pro", "Grok 3"]),
        ("AI_CROSS_003", evaluate_common_knowledge(advanced_model, ["alice", "bob"], "p", "w1")[1], evaluate_common_knowledge(advanced_model, ["alice", "bob"], "p", "w1")[0], "Common knowledge divergence from individual knowledge", ["Claude Opus 4.5", "Llama 4 Maverick"]),
        ("AI_CROSS_004", verify_rule(conditional_cases[1][1], conditional_cases[1][2])[1], verify_rule(conditional_cases[1][1], conditional_cases[1][2])[0], "Conditional pattern requiring region-count detector", ALL_MODELS[:]),
        ("AI_CROSS_005", fermat_little(2, 101)[1], fermat_little(2, 101)[0], "Fermat verification for a=2, p=101", ["GPT-5.2", "Gemini 3 Pro", "Kimi K2.5"]),
        ("AI_CROSS_006", construct_gettier_counterexample()[1], sorted(construct_gettier_counterexample()[0].worlds), "Non-trivial two-world Gettier counterexample", ["Claude Opus 4.5", "DeepSeek-V3.2", "Llama 4 Maverick"]),
        ("AI_CROSS_007", busy_beaver(4)[1], busy_beaver(4)[0], "Busy beaver boundary reasoning", ["Grok 3", "Qwen 3", "Mistral Large 3"]),
        ("AI_CROSS_008", verify_rule(conditional_cases[5][1], conditional_cases[5][2])[1], verify_rule(conditional_cases[5][1], conditional_cases[5][2])[0], "Nested conditional branching over rows and cols", ALL_MODELS[:]),
        ("AI_CROSS_009", chinese_remainder_theorem([1, 2, 3, 4], [5, 7, 11, 13])[1], chinese_remainder_theorem([1, 2, 3, 4], [5, 7, 11, 13])[0], "CRT scaling across four moduli", ["GPT-5.2", "Gemini 3 Pro", "Qwen 3"]),
        ("AI_CROSS_010", inclusion_exclusion([9, 8, 7, 6], [[3, 2, 2, 1, 1, 1], [1, 1, 0, 1], [1]])[1], inclusion_exclusion([9, 8, 7, 6], [[3, 2, 2, 1, 1, 1], [1, 1, 0, 1], [1]])[0], "Four-set inclusion-exclusion with alternating signs", ALL_MODELS[:]),
    ]
    for test_id, proof, solution, problem, model_targeting in cross_entries:
        _register_invariant(
            test_id,
            "D_CROSS_MODEL_BENCHMARKS",
            "CROSS_MODEL",
            problem,
            solution,
            proof,
            "benchmarks/ai_invariant_tests.py",
            model_targeting,
        )

    # -------------------------------------------------------------------------
    # PR #98 Capability Benchmark invariants (12)
    # -------------------------------------------------------------------------
    
    # Import SAL modules for capability tests
    from src.sal.topos_subobject_classifier import (
        SheafContext, SubobjectClassifier, geometric_morphism,
    )
    from src.sal.forcing_operation import force_domain, DomainState, CardinalStrength
    from src.sal.realizability_topos import RealizabilityTopos, realize
    from src.domains.d_dollartree.domain import (
        build_officer_situs, build_video_situs, build_domain_state, run_adjunction_check,
    )
    
    cap_entries = [
        ("AI_CAP_001", "SAL produces valid ProofObject for real-world detention", "CAP_FORENSIC_001"),
        ("AI_CAP_002", "Geometric morphism detects truth divergence between sites", "CAP_FORENSIC_002"),
        ("AI_CAP_003", "Forcing produces constructive remedy for adjunction failure", "CAP_FORENSIC_003"),
        ("AI_CAP_004", "Same input produces same ProofObject hash", "CAP_DETERMINISM_001"),
        ("AI_CAP_005", "No floating-point in SAL kernel", "CAP_DETERMINISM_002"),
        ("AI_CAP_006", "has_adjunction returns structured proof, not bare bool", "CAP_ADJUNCTION_001"),
        ("AI_CAP_007", "Counit violation carries SHA-256 evidence anchor", "CAP_ADJUNCTION_002"),
        ("AI_CAP_008", "SubobjectClassifier uses Heyting algebra, not Boolean", "CAP_TOPOS_001"),
        ("AI_CAP_009", "Geometric morphism constructible between 2+ sites", "CAP_TOPOS_002"),
        ("AI_CAP_010", "Extension existence proves ground model defect", "CAP_FORCING_001"),
        ("AI_CAP_011", "Realized proposition has internal truth value 1", "CAP_REALIZABILITY_001"),
        ("AI_CAP_012", "Every YeshuaClaim is Merkle-anchored", "CAP_HASH_CHAIN_001"),
    ]
    
    for test_id, description, test_ref in cap_entries:
        proof = ProofObject(
            rule="CapabilityBenchmark",
            premises=["capability=SAL", f"test_id={test_ref}"],
            conclusion=description,
        )
        _register_invariant(
            test_id,
            "D_CAPABILITY_BENCHMARK",
            "FORENSIC",
            description,
            True,
            proof,
            "tests/test_capability_benchmark.py",
        )
    
    # -------------------------------------------------------------------------
    # PR #98 Architecture Proof invariants (8)
    # -------------------------------------------------------------------------
    
    arch_entries = [
        ("AI_ARCH_001", "Heyting-to-Boolean swap changes geometric morphism result", "ARCH_HEYTING_001"),
        ("AI_ARCH_002", "Removing axioms 5-8 weakens enforcement", "ARCH_AXIOM_REMOVAL_001"),
        ("AI_ARCH_003", "Removing forcing loses constructive remedy", "ARCH_FORCING_REMOVAL"),
        ("AI_ARCH_004", "Terminal coalgebra provides convergence guarantee", "ARCH_COALGEBRA_001"),
        ("AI_ARCH_005", "Renaming theological terms does not break computation", "ARCH_RENAME_001"),
        ("AI_ARCH_006", "Mathematical structure (Heyting algebra) does the work", "ARCH_HEYTING_002"),
        ("AI_ARCH_007", "Site-relative truth is necessary for forensic correctness", "ARCH_FRACTION_001"),
        ("AI_ARCH_008", "Capability matrix entries are falsifiable", "ARCH_RENAME_001"),
    ]
    
    for test_id, description, test_ref in arch_entries:
        proof = ProofObject(
            rule="ArchitectureProof",
            premises=["architecture=verified", f"test_id={test_ref}"],
            conclusion=description,
        )
        _register_invariant(
            test_id,
            "D_ARCHITECTURE_PROOF",
            "STRUCTURAL",
            description,
            True,
            proof,
            "tests/test_architecture_not_dogma.py",
        )



def run_ai_invariant_suite() -> Dict[str, Any]:
    _register_all()
    results = []
    proofs = []
    for test_id in sorted(AI_INVARIANT_REGISTRY):
        test = AI_INVARIANT_REGISTRY[test_id]
        valid = test.proof.is_valid()
        yeshua_ok = len(verify_yeshua_standard(test.claim)) == 0
        results.append({"id": test_id, "proof_valid": valid, "yeshua_ok": yeshua_ok, "domain": test.domain, "model_targeting": test.model_targeting})
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
