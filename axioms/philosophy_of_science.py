"""axioms/philosophy_of_science.py — Philosophy of science invariant checks.

Implements Popperian demarcation, verisimilitude ordering, Kuhn's paradigm
incommensurability bound, Quine-Duhem underdetermination, inference to the
best explanation, computational exactness, and Shannon token-cost information
bound — all with exact Fraction arithmetic and full ProofObject evidence.

Standard: Yeshua / Orthogonal Engineering
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class ScientificTheory:
    """A scientific theory and its measurable properties."""

    name: str
    is_falsifiable: bool
    true_consequence_count: Fraction  # integer count as Fraction
    false_consequence_count: Fraction  # integer count as Fraction
    paradigm_shift_decided_in_constant_time: bool  # True = bad (violates Kuhn)
    compatible_theory_count: Fraction  # theories compatible with data D, should be > 1
    explanatory_power: Fraction  # in [0,1]
    complexity: Fraction  # must be > 0
    uses_float: bool  # True = violates computational exactness invariant
    token_count: Fraction  # n_tokens as Fraction
    vocab_size: Fraction  # vocab size as Fraction
    information_bits_claimed: Fraction  # claimed Shannon entropy bound


def check_demarcation_criterion(theory: ScientificTheory) -> Tuple[bool, ProofObject]:
    """Popper's demarcation: science requires falsifiability.

    Standard: Popper (1959) — The Logic of Scientific Discovery, Ch. 1
    Falsifies if: theory.is_falsifiable is False.
    falsifies_if: theory.is_falsifiable is False.
    """
    success = theory.is_falsifiable
    proof = ProofObject(
        rule="DemarcationCriterion",
        premises=[
            f"theory.name = {theory.name!r}",
            f"theory.is_falsifiable = {theory.is_falsifiable}",
        ],
        conclusion=(
            f"Theory {theory.name!r} satisfies Popper demarcation (is falsifiable)"
            if success
            else f"FAIL: Theory {theory.name!r} is not falsifiable — not scientific"
        ),
    )
    return success, proof


def check_verisimilitude_ordering(
    t1: ScientificTheory, t2: ScientificTheory
) -> Tuple[bool, ProofObject]:
    """Theory t1 has more verisimilitude than t2 iff t1 has more true and fewer false consequences.

    Standard: Popper (1963) — Conjectures and Refutations, Ch. 10
    Falsifies if: t1.true_consequence_count <= t2.true_consequence_count OR t1.false_consequence_count >= t2.false_consequence_count.
    falsifies_if: t1.true_consequence_count <= t2.true_consequence_count or t1.false_consequence_count >= t2.false_consequence_count.
    """
    more_truths = t1.true_consequence_count > t2.true_consequence_count
    fewer_falsehoods = t1.false_consequence_count < t2.false_consequence_count
    success = more_truths and fewer_falsehoods
    proof = ProofObject(
        rule="VerisimilitudeOrdering",
        premises=[
            f"t1.name = {t1.name!r}",
            f"t2.name = {t2.name!r}",
            f"t1.true_consequence_count = {t1.true_consequence_count}",
            f"t2.true_consequence_count = {t2.true_consequence_count}",
            f"t1.false_consequence_count = {t1.false_consequence_count}",
            f"t2.false_consequence_count = {t2.false_consequence_count}",
            f"more_truths = {more_truths}",
            f"fewer_falsehoods = {fewer_falsehoods}",
        ],
        conclusion=(
            f"Verisimilitude: {t1.name!r} > {t2.name!r}"
            if success
            else f"FAIL: {t1.name!r} does not have strictly greater verisimilitude than {t2.name!r}"
        ),
    )
    return success, proof


def check_paradigm_incommensurability_bound(theory: ScientificTheory) -> Tuple[bool, ProofObject]:
    """Kuhn: paradigm shifts are not purely rational; no algorithm decides paradigm superiority in O(1).

    Standard: Kuhn (1962) — The Structure of Scientific Revolutions, Ch. 9
    Falsifies if: theory.paradigm_shift_decided_in_constant_time is True.
    falsifies_if: theory.paradigm_shift_decided_in_constant_time is True.
    """
    success = not theory.paradigm_shift_decided_in_constant_time
    proof = ProofObject(
        rule="ParadigmIncommensurabilityBound",
        premises=[
            f"theory.name = {theory.name!r}",
            f"paradigm_shift_decided_in_constant_time = {theory.paradigm_shift_decided_in_constant_time}",
        ],
        conclusion=(
            "Paradigm incommensurability respected: no O(1) decision algorithm claimed"
            if success
            else "FAIL: O(1) paradigm shift decision claimed — violates Kuhn incommensurability"
        ),
    )
    return success, proof


def check_underdetermination_of_theory(theory: ScientificTheory) -> Tuple[bool, ProofObject]:
    """Quine-Duhem: given data D, multiple theories are compatible; check cardinality > 1.

    Standard: Quine (1951) — Two Dogmas of Empiricism; Duhem (1906) — The Aim and Structure of Physical Theory
    Falsifies if: theory.compatible_theory_count <= 1.
    falsifies_if: theory.compatible_theory_count <= 1.
    """
    success = theory.compatible_theory_count > Fraction(1)
    proof = ProofObject(
        rule="UnderdeterminationOfTheory",
        premises=[
            f"theory.name = {theory.name!r}",
            f"compatible_theory_count = {theory.compatible_theory_count}",
        ],
        conclusion=(
            f"Quine-Duhem underdetermination holds: {theory.compatible_theory_count} theories compatible with data"
            if success
            else f"FAIL: compatible_theory_count {theory.compatible_theory_count} <= 1 — underdetermination violated"
        ),
    )
    return success, proof


def check_inference_to_best_explanation(theory: ScientificTheory) -> Tuple[bool, ProofObject]:
    """IBE: best explanation maximizes explanatory_power / complexity ratio via Fraction.

    complexity must be > 0. ratio must be > 0.

    Standard: Harman (1965) — The Inference to the Best Explanation
    Falsifies if: theory.complexity <= 0 or theory.explanatory_power <= 0.
    falsifies_if: theory.complexity <= 0 or theory.explanatory_power <= 0.
    """
    complexity_ok = theory.complexity > Fraction(0)
    power_ok = theory.explanatory_power > Fraction(0)
    success = complexity_ok and power_ok

    if success:
        ratio = theory.explanatory_power / theory.complexity
        conclusion = (
            f"IBE ratio = {ratio} (explanatory_power={theory.explanatory_power} / complexity={theory.complexity})"
        )
    else:
        ratio = Fraction(0)
        conclusion = (
            f"FAIL: complexity={theory.complexity}, explanatory_power={theory.explanatory_power} — "
            "both must be > 0 for a valid IBE ratio"
        )

    proof = ProofObject(
        rule="InferenceToBestExplanation",
        premises=[
            f"theory.name = {theory.name!r}",
            f"explanatory_power = {theory.explanatory_power}",
            f"complexity = {theory.complexity}",
            f"complexity_ok = {complexity_ok}",
            f"power_ok = {power_ok}",
        ],
        conclusion=conclusion,
    )
    return success, proof


def check_computational_exactness_invariant(theory: ScientificTheory) -> Tuple[bool, ProofObject]:
    """Any numeric claim in the system must use Fraction, never float.

    Standard: Orthogonal Engineering — Computational Exactness Invariant (OE-CEI-001)
    Falsifies if: theory.uses_float is True.
    falsifies_if: theory.uses_float is True.
    """
    success = not theory.uses_float
    proof = ProofObject(
        rule="ComputationalExactnessInvariant",
        premises=[
            f"theory.name = {theory.name!r}",
            f"uses_float = {theory.uses_float}",
        ],
        conclusion=(
            "Computational exactness invariant holds: no float usage detected"
            if success
            else "FAIL: float usage detected — violates OE-CEI-001 (use Fraction)"
        ),
    )
    return success, proof


def check_token_cost_information_bound(theory: ScientificTheory) -> Tuple[bool, ProofObject]:
    """Shannon entropy of a token stream is bounded by log2(vocab_size) * n_tokens.

    The claimed information_bits_claimed must be <= this upper bound (computed exactly as Fraction).
    Uses (vocab_size - 1).bit_length() to compute ceil(log2(vocab_size)) exactly for integer vocab
    sizes: for vocab_size >= 2 this equals ceil(log2(v)), and equals 0 for vocab_size == 1.

    Standard: Shannon (1948) — A Mathematical Theory of Communication
    Falsifies if: theory.information_bits_claimed > bound.
    falsifies_if: theory.information_bits_claimed > bound.
    """
    v = int(theory.vocab_size)
    # ceil(log2(v)) for v >= 2; 0 for v == 1 (log2(1) = 0); use max(v-1, 1) to avoid bit_length(0)
    log2_upper = max(v - 1, 1).bit_length() if v >= 2 else 0
    bound = Fraction(log2_upper) * theory.token_count
    success = theory.information_bits_claimed <= bound
    proof = ProofObject(
        rule="TokenCostInformationBound",
        premises=[
            f"theory.name = {theory.name!r}",
            f"vocab_size = {theory.vocab_size}",
            f"token_count = {theory.token_count}",
            f"log2_upper (bit_length) = {log2_upper}",
            f"bound = {bound} bits",
            f"information_bits_claimed = {theory.information_bits_claimed} bits",
        ],
        conclusion=(
            f"Information bound satisfied: {theory.information_bits_claimed} <= {bound}"
            if success
            else f"FAIL: claimed {theory.information_bits_claimed} bits exceeds bound {bound} bits"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for the philosophy_of_science axiom module.

    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.
    """
    # Nominal theory — passes all checks
    t1 = ScientificTheory(
        name="nominal_theory_t1",
        is_falsifiable=True,
        true_consequence_count=Fraction(10),
        false_consequence_count=Fraction(1),
        paradigm_shift_decided_in_constant_time=False,
        compatible_theory_count=Fraction(5),
        explanatory_power=Fraction(4, 5),
        complexity=Fraction(2),
        uses_float=False,
        token_count=Fraction(100),
        vocab_size=Fraction(1024),
        information_bits_claimed=Fraction(500),  # 10 bits/token * 100 tokens = 1000; 500 <= 1000
    )

    # Second theory for verisimilitude comparison (t1 > t2)
    t2 = ScientificTheory(
        name="nominal_theory_t2",
        is_falsifiable=True,
        true_consequence_count=Fraction(5),
        false_consequence_count=Fraction(3),
        paradigm_shift_decided_in_constant_time=False,
        compatible_theory_count=Fraction(3),
        explanatory_power=Fraction(1, 2),
        complexity=Fraction(3),
        uses_float=False,
        token_count=Fraction(100),
        vocab_size=Fraction(1024),
        information_bits_claimed=Fraction(500),
    )

    results: List[Tuple[str, bool, ProofObject]] = []
    single_checks: List[Tuple[str, Tuple[bool, ProofObject]]] = [
        ("demarcation_criterion", check_demarcation_criterion(t1)),
        ("verisimilitude_ordering", check_verisimilitude_ordering(t1, t2)),
        ("paradigm_incommensurability_bound", check_paradigm_incommensurability_bound(t1)),
        ("underdetermination_of_theory", check_underdetermination_of_theory(t1)),
        ("inference_to_best_explanation", check_inference_to_best_explanation(t1)),
        ("computational_exactness_invariant", check_computational_exactness_invariant(t1)),
        ("token_cost_information_bound", check_token_cost_information_bound(t1)),
    ]
    for name, (ok, proof) in single_checks:
        results.append((name, ok, proof))
    return results
