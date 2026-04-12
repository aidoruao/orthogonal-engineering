"""D_JUDICIAL_REVIEW invariants — Fraction only. 0 floats.

Standards:
- U.S. Constitution Article III §2 (Case or Controversy)
- Marbury v. Madison (1803) — judicial review of government action
- Lujan v. Defenders of Wildlife (1992) — standing doctrine
- Abbott Laboratories v. Gardner (1967) — ripeness doctrine
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import FrozenConstitutionalChallenge


def check_article_iii_standing(challenge: FrozenConstitutionalChallenge) -> Tuple[bool, ProofObject]:
    """
    Rule: Article III standing requires concrete injury, causation, and redressability.

    Standard: U.S. Constitution Article III §2; Lujan v. Defenders of Wildlife (1992)
    falsifies_if: standing_injury is False OR causation_established is False OR redressability is False.
    """
    success = (
        challenge.standing_injury
        and challenge.causation_established
        and challenge.redressability
    )

    premises = [
        f"challenge_id={challenge.challenge_id}",
        f"standing_injury={challenge.standing_injury}",
        f"causation_established={challenge.causation_established}",
        f"redressability={challenge.redressability}",
    ]

    if not success:
        return False, ProofObject(
            rule="ArticleIIIStanding",
            premises=premises,
            conclusion="VIOLATION: Article III standing failed — missing injury, causation, or redressability",
        )

    return True, ProofObject(
        rule="ArticleIIIStanding",
        premises=premises,
        conclusion="Article III standing satisfied — injury, causation, and redressability confirmed",
    )


def check_ripeness_mootness(challenge: FrozenConstitutionalChallenge) -> Tuple[bool, ProofObject]:
    """
    Rule: Courts may only decide ripe cases; moot cases must be dismissed.

    Standard: U.S. Constitution Article III §2; Abbott Laboratories v. Gardner (1967)
    falsifies_if: question_is_ripe is False OR not_moot is False.
    """
    success = challenge.question_is_ripe and challenge.not_moot

    premises = [
        f"challenge_id={challenge.challenge_id}",
        f"question_is_ripe={challenge.question_is_ripe}",
        f"not_moot={challenge.not_moot}",
    ]

    if not success:
        return False, ProofObject(
            rule="RipenessMootness",
            premises=premises,
            conclusion="VIOLATION: Article III case or controversy — case not ripe or moot",
        )

    return True, ProofObject(
        rule="RipenessMootness",
        premises=premises,
        conclusion="Article III ripeness and mootness requirements satisfied",
    )


def check_government_action_requirement(challenge: FrozenConstitutionalChallenge) -> Tuple[bool, ProofObject]:
    """
    Rule: Constitutional challenges must target government action; purely private conduct cannot be directly challenged under the Constitution.

    Standard: U.S. Constitution Article III; Civil Rights Cases (1883)
    falsifies_if: challenged_action_is_government is False.
    """
    success = challenge.challenged_action_is_government

    premises = [
        f"challenge_id={challenge.challenge_id}",
        f"challenged_action_is_government={challenge.challenged_action_is_government}",
        f"standard_of_review={challenge.standard_of_review}",
    ]

    if not success:
        return False, ProofObject(
            rule="GovernmentActionRequirement",
            premises=premises,
            conclusion="VIOLATION: Constitutional challenge — challenged action is not government action",
        )

    return True, ProofObject(
        rule="GovernmentActionRequirement",
        premises=premises,
        conclusion="Government action requirement satisfied — challenged action properly attributed to government",
    )


def run_all_invariants() -> dict:
    """Run all D_JUDICIAL_REVIEW invariants with nominal sample data.

    falsifies_if: any judicial review invariant check fails or raises an exception.
    """
    challenge = FrozenConstitutionalChallenge(
        challenge_id="CHALLENGE-001",
        standing_injury=True,
        causation_established=True,
        redressability=True,
        challenged_action_is_government=True,
        final_agency_action=True,
        question_is_ripe=True,
        not_moot=True,
        standard_of_review="strict_scrutiny",
    )

    checks = [
        ("check_article_iii_standing", lambda: check_article_iii_standing(challenge)),
        ("check_ripeness_mootness", lambda: check_ripeness_mootness(challenge)),
        ("check_government_action_requirement", lambda: check_government_action_requirement(challenge)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
