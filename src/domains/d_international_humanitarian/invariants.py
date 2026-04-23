"""D_INTERNATIONAL_HUMANITARIAN invariants - Yeshua Standard. 0 floats.

Standards:
- Geneva Conventions (1949) - Common Article 3
- Additional Protocol I (1977) - AP I Articles 51, 57
- ICRC Customary IHL Study - Rule 1: Distinction
- Martens Clause - HPCR Manual on Air and Missile Warfare
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import ProtectedPerson, MilitaryTarget, ProtectedCategory


def check_protection_coverage_ratio(person: ProtectedPerson) -> Tuple[bool, ProofObject]:
    """Protected person must receive adequate coverage fraction.

    Standard: Geneva Convention IV Article 4 - protected persons entitled to full protection
    Falsifies if: person.protection_coverage < Fraction(3, 4).
    falsifies_if: person.protection_coverage < Fraction(3, 4).
    """
    threshold = Fraction(3, 4)
    ok = person.protection_coverage >= threshold
    premises = [
        f"person_id={person.person_id}",
        f"category={person.category.name}",
        f"protection_coverage={person.protection_coverage}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="ProtectionCoverageRatio",
        premises=premises,
        conclusion="PASS: protection coverage adequate" if ok else "VIOLATION: protection coverage below threshold",
    )


def check_necessity_score_threshold(target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Military necessity must be established above threshold.

    Standard: AP I Article 52(2) - military objective requires definite military advantage
    Falsifies if: target.necessity_score < Fraction(1, 2).
    falsifies_if: target.necessity_score < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = target.necessity_score >= threshold
    premises = [
        f"target_id={target.target_id}",
        f"necessity_score={target.necessity_score}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="NecessityScoreThreshold",
        premises=premises,
        conclusion="PASS: necessity score above threshold" if ok else "VIOLATION: necessity score below threshold",
    )


def check_distinction_score_threshold(target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Distinction between combatants and civilians must be adequately maintained.

    Standard: AP I Article 48 - basic rule of distinction
    Falsifies if: target.distinction_score < Fraction(1, 2).
    falsifies_if: target.distinction_score < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = target.distinction_score >= threshold
    premises = [
        f"target_id={target.target_id}",
        f"distinction_score={target.distinction_score}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="DistinctionScoreThreshold",
        premises=premises,
        conclusion="PASS: distinction score above threshold" if ok else "VIOLATION: distinction score below threshold",
    )


def check_civilian_harm_fraction(target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Civilian harm fraction must remain below maximum acceptable level.

    Standard: AP I Article 51(5)(b) - proportionality in attack
    Falsifies if: target.harm_fraction >= Fraction(1, 2).
    falsifies_if: target.harm_fraction >= Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    ok = target.harm_fraction < threshold
    premises = [
        f"target_id={target.target_id}",
        f"harm_fraction={target.harm_fraction}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="CivilianHarmFraction",
        premises=premises,
        conclusion=f"PASS: harm fraction {target.harm_fraction} < 1/2" if ok else f"VIOLATION: harm fraction {target.harm_fraction} >= 1/2",
    )


def check_proportionality_composite(target: MilitaryTarget, military_advantage: int) -> Tuple[bool, ProofObject]:
    """Composite proportionality must satisfy harm-advantage balance.

    Standard: AP I Article 57(2)(a)(iii) - proportionality assessment required
    Falsifies if: (harm_fraction * 10) / max(military_advantage, 1) >= 1.
    falsifies_if: (harm_fraction * 10) / max(military_advantage, 1) >= 1.
    """
    if military_advantage <= 0:
        ok = False
        ratio = Fraction(1)
    else:
        ratio = (target.harm_fraction * 10) / military_advantage
        ok = ratio < Fraction(1)
    premises = [
        f"target_id={target.target_id}",
        f"harm_fraction={target.harm_fraction}",
        f"military_advantage={military_advantage}",
        f"proportionality_ratio={ratio}",
    ]
    return ok, ProofObject(
        rule="ProportionalityComposite",
        premises=premises,
        conclusion=f"PASS: ratio {ratio} < 1" if ok else f"VIOLATION: ratio {ratio} >= 1",
    )


def check_protection_necessity_balance(person: ProtectedPerson, target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Protection coverage must exceed harm fraction for protected persons near targets.

    Standard: Geneva Convention IV Article 27 - protected persons entitled to humane treatment
    Falsifies if: person.protection_coverage <= target.harm_fraction.
    falsifies_if: person.protection_coverage <= target.harm_fraction.
    """
    ok = person.protection_coverage > target.harm_fraction
    premises = [
        f"person_id={person.person_id}",
        f"protection_coverage={person.protection_coverage}",
        f"target_id={target.target_id}",
        f"harm_fraction={target.harm_fraction}",
    ]
    return ok, ProofObject(
        rule="ProtectionNecessityBalance",
        premises=premises,
        conclusion="PASS: protection exceeds harm" if ok else "VIOLATION: protection does not exceed harm",
    )


def check_distinction_necessity_product(target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Combined distinction and necessity must satisfy minimum product.

    Standard: ICRC Customary IHL Study Rule 1 - distinction and military necessity are complementary
    Falsifies if: target.distinction_score * target.necessity_score < Fraction(1, 4).
    falsifies_if: target.distinction_score * target.necessity_score < Fraction(1, 4).
    """
    product = target.distinction_score * target.necessity_score
    threshold = Fraction(1, 4)
    ok = product >= threshold
    premises = [
        f"target_id={target.target_id}",
        f"distinction_score={target.distinction_score}",
        f"necessity_score={target.necessity_score}",
        f"product={product}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="DistinctionNecessityProduct",
        premises=premises,
        conclusion=f"PASS: product {product} >= 1/4" if ok else f"VIOLATION: product {product} < 1/4",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS.

    Standard: International-humanitarian-law nominal executable check set (Geneva Conventions + Additional Protocols).
    Falsifies if: any check returns FAIL (nominal inputs should always pass).
    falsifies_if: any check returns FAIL (nominal inputs should always pass).
    """
    category = list(ProtectedCategory)[0]
    person = ProtectedPerson(
        person_id="P001",
        category=category,
        location="Field Hospital",
        receiving_protection=True,
        protection_coverage=Fraction(1, 1),
    )
    target = MilitaryTarget(
        target_id="T001",
        military_necessity=True,
        proportionality_assessed=True,
        expected_civilian_harm=0,
        necessity_score=Fraction(1, 1),
        distinction_score=Fraction(1, 1),
        harm_fraction=Fraction(0),
    )
    military_advantage = 10
    results = {}
    for fn, args in [
        (check_protection_coverage_ratio, (person,)),
        (check_necessity_score_threshold, (target,)),
        (check_distinction_score_threshold, (target,)),
        (check_civilian_harm_fraction, (target,)),
        (check_proportionality_composite, (target, military_advantage)),
        (check_protection_necessity_balance, (person, target)),
        (check_distinction_necessity_product, (target,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
