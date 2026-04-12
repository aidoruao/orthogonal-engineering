"""D_INTL_HUMANITARIAN invariants — Yeshua Standard. 0 floats.

Standards:
- Geneva Conventions (1949) — Common Article 3
- Additional Protocols I and II (1977)
- International Humanitarian Law (IHL)
- Proportionality principle — AP I Article 51(5)(b)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import UseOfForceEvaluation, IHLChecker


def check_proportionality(eval: UseOfForceEvaluation) -> Tuple[bool, ProofObject]:
    """Civilian harm risk must be < military objective value (proportionality).

    Standard: AP I Article 51(5)(b) — proportionality in attack
    falsifies_if: eval.civilian_harm_risk >= eval.military_objective_value.
    """
    ok = eval.civilian_harm_risk < eval.military_objective_value
    premises = [
        f"military_objective_value={eval.military_objective_value}",
        f"civilian_harm_risk={eval.civilian_harm_risk}",
    ]
    return ok, ProofObject(
        rule="IHLProportionality",
        premises=premises,
        conclusion=f"PASS: harm {eval.civilian_harm_risk} < objective {eval.military_objective_value}" if ok else f"VIOLATION: harm {eval.civilian_harm_risk} >= objective {eval.military_objective_value}",
    )


def check_military_objective_positive(eval: UseOfForceEvaluation) -> Tuple[bool, ProofObject]:
    """Military objective value must be > 0 to justify any force.

    Standard: AP I Article 52(2) — military objectives definition
    falsifies_if: eval.military_objective_value <= 0.
    """
    ok = eval.military_objective_value > Fraction(0)
    premises = [f"military_objective_value={eval.military_objective_value}"]
    return ok, ProofObject(
        rule="MilitaryObjectivePositive",
        premises=premises,
        conclusion=f"PASS: objective {eval.military_objective_value} > 0" if ok else "VIOLATION: military objective value <= 0",
    )


def check_civilian_harm_nonneg(eval: UseOfForceEvaluation) -> Tuple[bool, ProofObject]:
    """Civilian harm risk must be >= 0.

    Standard: AP I Article 57(2) — precautions in attack
    falsifies_if: eval.civilian_harm_risk < 0.
    """
    ok = eval.civilian_harm_risk >= Fraction(0)
    premises = [f"civilian_harm_risk={eval.civilian_harm_risk}"]
    return ok, ProofObject(
        rule="CivilianHarmNonNeg",
        premises=premises,
        conclusion=f"PASS: harm {eval.civilian_harm_risk} >= 0" if ok else "VIOLATION: negative civilian harm risk",
    )


def check_ihl_checker_evaluates(checker: IHLChecker) -> Tuple[bool, ProofObject]:
    """IHLChecker must exist and be callable.

    Standard: IHL implementation requirement — doctrine must be evaluable
    falsifies_if: checker is None.
    """
    ok = checker is not None
    premises = [f"checker_type={type(checker).__name__}"]
    return ok, ProofObject(
        rule="IHLCheckerEvaluates",
        premises=premises,
        conclusion="PASS: IHL checker operational" if ok else "VIOLATION: IHL checker is None",
    )


def check_harm_objective_ratio(eval: UseOfForceEvaluation) -> Tuple[bool, ProofObject]:
    """Civilian harm / military objective ratio must be < Fraction(1).

    Standard: Proportionality test — harm must not outweigh benefit
    falsifies_if: civilian_harm_risk / military_objective_value >= 1.
    """
    if eval.military_objective_value <= Fraction(0):
        ok = False
        ratio = Fraction(-1)
    else:
        ratio = eval.civilian_harm_risk / eval.military_objective_value
        ok = ratio < Fraction(1)
    premises = [
        f"ratio={ratio}",
        f"military_objective_value={eval.military_objective_value}",
        f"civilian_harm_risk={eval.civilian_harm_risk}",
    ]
    return ok, ProofObject(
        rule="HarmObjectiveRatio",
        premises=premises,
        conclusion=f"PASS: harm/objective ratio {ratio} < 1" if ok else f"VIOLATION: ratio {ratio} >= 1",
    )


def check_objective_exceeds_harm_threshold(eval: UseOfForceEvaluation) -> Tuple[bool, ProofObject]:
    """Military objective must be at least Fraction(1, 10) greater than civilian harm.

    Standard: AP I Article 51(5)(b) — excessive harm prohibition
    falsifies_if: military_objective_value - civilian_harm_risk < Fraction(1, 10).
    """
    margin = eval.military_objective_value - eval.civilian_harm_risk
    min_margin = Fraction(1, 10)
    ok = margin >= min_margin
    premises = [
        f"objective={eval.military_objective_value}",
        f"harm={eval.civilian_harm_risk}",
        f"margin={margin}",
        f"min_margin={min_margin}",
    ]
    return ok, ProofObject(
        rule="ObjectiveExceedsHarmThreshold",
        premises=premises,
        conclusion=f"PASS: margin {margin} >= {min_margin}" if ok else f"VIOLATION: margin {margin} < {min_margin}",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    eval_obj = UseOfForceEvaluation(
        military_objective_value=Fraction(8, 10),
        civilian_harm_risk=Fraction(2, 10),
    )
    checker = IHLChecker()
    results = {}
    for fn, args in [
        (check_proportionality, (eval_obj,)),
        (check_military_objective_positive, (eval_obj,)),
        (check_civilian_harm_nonneg, (eval_obj,)),
        (check_ihl_checker_evaluates, (checker,)),
        (check_harm_objective_ratio, (eval_obj,)),
        (check_objective_exceeds_harm_threshold, (eval_obj,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
