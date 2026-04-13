"""D_INTERNATIONAL_HUMANITARIAN invariants — Yeshua Standard. 0 floats.

Standards:
- Geneva Conventions (1949) — Common Article 3
- Additional Protocol I (1977) — AP I Articles 51, 57
- ICRC Customary IHL Study — Rule 1: Distinction
- Martens Clause — HPCR Manual on Air and Missile Warfare
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import ProtectedPerson, MilitaryTarget, ProtectedCategory


def check_protected_person_receiving_protection(person: ProtectedPerson) -> Tuple[bool, ProofObject]:
    """Protected person must be receiving protection.

    Standard: Geneva Convention IV Article 4 — protected persons
    falsifies_if: person.receiving_protection is False.
    """
    ok = person.receiving_protection
    premises = [
        f"person_id={person.person_id}",
        f"location={person.location}",
        f"receiving_protection={person.receiving_protection}",
    ]
    return ok, ProofObject(
        rule="ProtectedPersonReceivingProtection",
        premises=premises,
        conclusion="PASS: person is protected" if ok else "VIOLATION: protected person not receiving protection",
    )


def check_military_target_proportionality(target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Military target proportionality must be assessed.

    Standard: AP I Article 57(2)(a)(iii) — proportionality assessment required
    falsifies_if: target.proportionality_assessed is False.
    """
    ok = target.proportionality_assessed
    premises = [
        f"target_id={target.target_id}",
        f"military_necessity={target.military_necessity}",
        f"proportionality_assessed={target.proportionality_assessed}",
    ]
    return ok, ProofObject(
        rule="MilitaryTargetProportionality",
        premises=premises,
        conclusion="PASS: proportionality assessed" if ok else "VIOLATION: proportionality not assessed",
    )


def check_military_target_necessity(target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Military target must have military necessity established.

    Standard: AP I Article 52(2) — military objective definition
    falsifies_if: target.military_necessity is False.
    """
    ok = target.military_necessity
    premises = [
        f"target_id={target.target_id}",
        f"military_necessity={target.military_necessity}",
    ]
    return ok, ProofObject(
        rule="MilitaryTargetNecessity",
        premises=premises,
        conclusion="PASS: military necessity established" if ok else "VIOLATION: military necessity not established",
    )


def check_civilian_harm_nonneg(target: MilitaryTarget) -> Tuple[bool, ProofObject]:
    """Expected civilian harm must be >= 0.

    Standard: AP I Article 57 — precautions in attack
    falsifies_if: target.expected_civilian_harm < 0.
    """
    ok = target.expected_civilian_harm >= 0
    premises = [
        f"target_id={target.target_id}",
        f"expected_civilian_harm={target.expected_civilian_harm}",
    ]
    return ok, ProofObject(
        rule="CivilianHarmNonNeg",
        premises=premises,
        conclusion=f"PASS: civilian harm {target.expected_civilian_harm} >= 0" if ok else "VIOLATION: negative civilian harm value",
    )


def check_person_id_nonempty(person: ProtectedPerson) -> Tuple[bool, ProofObject]:
    """Protected person must have a non-empty identifier.

    Standard: ICRC registration requirements
    falsifies_if: person.person_id is empty.
    """
    ok = bool(person.person_id.strip())
    premises = [f"person_id={person.person_id!r}"]
    return ok, ProofObject(
        rule="PersonIdNonEmpty",
        premises=premises,
        conclusion="PASS: person_id set" if ok else "VIOLATION: person_id empty",
    )


def check_protected_category_valid(category: ProtectedCategory) -> Tuple[bool, ProofObject]:
    """Protected category must be a valid ProtectedCategory enum.

    Standard: Geneva Convention IV — categories of protected persons
    falsifies_if: category is not a ProtectedCategory instance.
    """
    ok = isinstance(category, ProtectedCategory)
    premises = [f"category={category!r}"]
    return ok, ProofObject(
        rule="ProtectedCategoryValid",
        premises=premises,
        conclusion=f"PASS: {category.name}" if ok else "VIOLATION: invalid protected category",
    )


def check_harm_objective_ratio(target: MilitaryTarget, military_advantage: int) -> Tuple[bool, ProofObject]:
    """Civilian harm / military advantage ratio must be < 1.

    Standard: AP I Article 51(5)(b) — proportionality in attack
    falsifies_if: target.expected_civilian_harm / military_advantage >= 1.
    """
    if military_advantage <= 0:
        ok = False
        ratio = Fraction(-1)
    else:
        ratio = Fraction(target.expected_civilian_harm, military_advantage)
        ok = ratio < Fraction(1)
    premises = [
        f"target_id={target.target_id}",
        f"expected_civilian_harm={target.expected_civilian_harm}",
        f"military_advantage={military_advantage}",
        f"ratio={ratio}",
    ]
    return ok, ProofObject(
        rule="HarmObjectiveRatio",
        premises=premises,
        conclusion=f"PASS: ratio {ratio} < 1" if ok else f"VIOLATION: ratio {ratio} >= 1",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    category = list(ProtectedCategory)[0]
    person = ProtectedPerson(
        person_id="P001",
        category=category,
        location="Field Hospital",
        receiving_protection=True,
    )
    target = MilitaryTarget(
        target_id="T001",
        military_necessity=True,
        proportionality_assessed=True,
        expected_civilian_harm=0,
    )
    military_advantage = 10
    results = {}
    for fn, args in [
        (check_protected_person_receiving_protection, (person,)),
        (check_military_target_proportionality, (target,)),
        (check_military_target_necessity, (target,)),
        (check_civilian_harm_nonneg, (target,)),
        (check_person_id_nonempty, (person,)),
        (check_protected_category_valid, (category,)),
        (check_harm_objective_ratio, (target, military_advantage)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
