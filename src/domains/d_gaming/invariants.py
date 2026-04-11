#!/usr/bin/env python3
"""Gaming Domain Invariants — Age ratings, accessibility, monetization ethics.

Standards:
- ESRB/PEGI rating compliance
- COPPA (under 13 parental consent)
- CVAA accessibility requirements
- Loot box odds disclosure (various jurisdictions)

Falsifies if:
- Minor accesses age-inappropriate content
- Loot box odds not disclosed
- Accessibility features missing without justification
- COPPA violations (under-13 without parental consent)
"""

from fractions import Fraction
from typing import Tuple, Dict
from axioms.logic import ProofObject
from .implementation import (
    Game, Player, LootBox, GamingSession, AgeRating,
    RatingSystem, ContentDescriptor, MonetizationType
)


def check_age_appropriateness(game: Game, player: Player) -> Tuple[bool, ProofObject]:
    """Player must meet minimum age requirement for game.

    Falsifies if: player age is unknown or below the game's minimum age.
    """
    player_age = player.age()
    min_age = game.minimum_age()
    
    if player_age is None:
        return False, ProofObject(
            conclusion="VIOLATION: Unknown player age for age-gated content",
            premises=[
                f"Game: {game.title}",
                f"Minimum age: {min_age}",
                "Player age: unknown"
            ],
            rule="age_rating_verification_required"
        )
    
    if player_age < min_age:
        return False, ProofObject(
            conclusion=f"VIOLATION: Player age {player_age} below minimum {min_age}",
            premises=[
                f"Player: {player.player_id}",
                f"Age: {player_age}",
                f"Game minimum: {min_age}",
                f"Game: {game.title}"
            ],
            rule="esrb_pegi_age_restriction"
        )
    
    return True, ProofObject(
        conclusion="Player meets age requirement",
        premises=[f"Age: {player_age}", f"Minimum: {min_age}"],
        rule="age_appropriate"
    )


def check_loot_box_odds_disclosure(loot_box: LootBox) -> Tuple[bool, ProofObject]:
    """Loot boxes must disclose drop rates (China, Belgium, Netherlands, etc.).

    Falsifies if: odds_disclosed is False or drop rates do not sum to 1.
    """
    if not loot_box.odds_disclosed:
        return False, ProofObject(
            conclusion="VIOLATION: Loot box odds not disclosed to players",
            premises=[
                f"Box: {loot_box.name}",
                f"Price: {loot_box.price} {loot_box.currency}",
                "Odds disclosed: False"
            ],
            rule="loot_box_odds_disclosure_required"
        )
    
    total_rate = sum(loot_box.drop_rates.values(), Fraction(0))
    if total_rate != Fraction(1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Loot box drop rates sum to {total_rate}, not 1.0",
            premises=[
                f"Sum: {total_rate}",
                f"Rates: {loot_box.drop_rates}"
            ],
            rule="loot_box_probability_axiom"
        )
    
    return True, ProofObject(
        conclusion="Loot box odds properly disclosed and valid",
        premises=[
            f"Odds disclosed: {loot_box.odds_disclosed}",
            f"Rate sum: {total_rate}"
        ],
        rule="loot_box_odds_compliant"
    )


def check_coppa_compliance(player: Player) -> Tuple[bool, ProofObject]:
    """COPPA requires parental consent for collecting data from under-13s.

    Falsifies if: player is under 13 without recorded parental consent.
    """
    if player.coppa_requires_consent():
        if player.parent_email is None:
            return False, ProofObject(
                conclusion="VIOLATION: Under-13 player without parental consent",
                premises=[
                    f"Player: {player.player_id}",
                    f"Age: {player.age()}",
                    "Parent email: None",
                    "COPPA consent required"
                ],
                rule="coppa_parental_consent"
            )
    
    return True, ProofObject(
        conclusion="COPPA compliance verified",
        premises=[f"Age: {player.age()}", f"Parent email: {player.parent_email is not None}"],
        rule="coppa_compliant"
    )


def check_accessibility_minimum(game: Game, required_coverage: Fraction) -> Tuple[bool, ProofObject]:
    """CVAA requires certain accessibility features for communication.

    Falsifies if: game has online features and accessibility coverage is below the
    required threshold.
    """
    coverage = game.accessibility_coverage()
    
    if game.online_features and coverage < required_coverage:
        return False, ProofObject(
            conclusion=f"VIOLATION: Accessibility coverage {coverage} below required {required_coverage}",
            premises=[
                f"Game: {game.title}",
                f"Coverage: {coverage}",
                f"Required: {required_coverage}",
                f"Features: {len(game.accessibility_features)}"
            ],
            rule="cvaa_accessibility_requirements"
        )
    
    return True, ProofObject(
        conclusion="Accessibility coverage meets requirements",
        premises=[f"Coverage: {coverage}", f"Required: {required_coverage}"],
        rule="accessibility_compliant"
    )


def check_spending_limits(session: GamingSession, player: Player) -> Tuple[bool, ProofObject]:
    """Player spending must respect set limits.

    Falsifies if: spending exceeds configured weekly limits or minor spending rate
    exceeds safe thresholds.
    """
    if player.spending_limit_weekly is not None:
        if session.purchase_amount > player.spending_limit_weekly:
            return False, ProofObject(
                conclusion="VIOLATION: Session spending exceeds weekly limit",
                premises=[
                    f"Player: {player.player_id}",
                    f"Spent: {session.purchase_amount}",
                    f"Limit: {player.spending_limit_weekly}"
                ],
                rule="spending_limit_enforcement"
            )
    
    # Flag high spending rates for minors
    if player.is_minor() and session.spending_rate() > Fraction(10):  # > $10/hour
        return False, ProofObject(
            conclusion="VIOLATION: Minor spending rate exceeds recommended limit",
            premises=[
                f"Player: {player.player_id}",
                f"Rate: {session.spending_rate()}/hour",
                "Minor: True"
            ],
            rule="minor_spending_protection"
        )
    
    return True, ProofObject(
        conclusion="Spending within limits",
        premises=[
            f"Amount: {session.purchase_amount}",
            f"Rate: {session.spending_rate()}/hour"
        ],
        rule="spending_compliant"
    )


def check_content_descriptor_consistency(rating: AgeRating) -> Tuple[bool, ProofObject]:
    """Content descriptors must be consistent with age rating.

    Falsifies if: age rating is Everyone/EC but includes gambling or sexual content
    descriptors, or other descriptors conflict with the assigned rating.
    """
    if rating.rating in ("E", "EC") and ContentDescriptor.SEXUAL_CONTENT in rating.descriptors:
        return False, ProofObject(
            conclusion="VIOLATION: Everyone-rated content with sexual content descriptor",
            premises=[
                f"Rating: {rating.rating}",
                f"Descriptors: {rating.descriptors}"
            ],
            rule="content_descriptor_rating_consistency"
        )
    
    if rating.rating in ("E", "EC") and ContentDescriptor.GAMBLING in rating.descriptors:
        return False, ProofObject(
            conclusion="VIOLATION: Everyone-rated content with gambling descriptor",
            premises=[
                f"Rating: {rating.rating}",
                "Gambling content in family game"
            ],
            rule="content_descriptor_gambling_rating"
        )
    
    return True, ProofObject(
        conclusion="Content descriptors consistent with age rating",
        premises=[f"Rating: {rating.rating}", f"Descriptors: {len(rating.descriptors)}"],
        rule="content_descriptor_consistent"
    )
