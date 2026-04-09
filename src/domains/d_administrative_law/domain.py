"""D_ADMINISTRATIVE_LAW domain definition — Administrative Law

Layer: 2
CardinalStrength: PREDICATIVE

Administrative law governs the activities of administrative agencies of government.
Agencies promulgate regulations, adjudicate disputes, and enforce compliance.
The Administrative Procedure Act (APA) establishes the framework for agency rulemaking.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ADMINISTRATIVE_LAW"
DOMAIN_NAME = "Administrative Law"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'apa',
    'notice-and-comment',
    'chevron',
    'arbitrary-capricious',
    'rulemaking',
    'adjudication',
    'judicial-review',
    'standing',
    'exhaustion',
    'ripeness',
    'mootness',
    'agency-discretion',
    'hard-look-review',
    'procedural-due-process',
    'substantive-due-process',
    'freedom-of-information',
    'privacy-act',
    'government-in-sunshine',
    'federal-advisory-committee',
    'regulatory-flexibility',
    'paperwork-reduction',
    'unfunded-mandates',
]

INVARIANTS = [
    'Agency rulemaking follows APA notice-and-comment procedure (5 U.S.C. § 553).',
    'Chevron deference has bounds; ambiguous statutes require reasoned interpretation.',
    'Arbitrary/capricious standard: action must be reasoned and documented (5 U.S.C. § 706).',
    'Hard look review: agency must examine relevant data and articulate satisfactory explanation.',
    'Standing requires injury-in-fact, causation, and redressability (Lujan v. Defenders).',
    'Exhaustion of administrative remedies required before judicial review.',
    'Ripeness: challenge must be fit for judicial decision and hardship must be immediate.',
    'Mootness: live controversy required throughout litigation.',
    'Agency discretion bounded by statutory mandate and non-delegation doctrine.',
    'Procedural due process: notice and opportunity to be heard before deprivation.',
    'Substantive due process: agency action must not be arbitrary or irrational.',
    'FOIA requires disclosure unless exemption applies (5 U.S.C. § 552).',
    'Privacy Act limits government collection/dissemination of personal info (5 U.S.C. § 552a).',
    'Government in Sunshine Act: multi-member agencies meet publicly (5 U.S.C. § 552b).',
    'FACA: advisory committees follow transparency and balance requirements (5 U.S.C. App.).',
]

FALSIFICATION_TESTS = ["F_ADMINISTRATIVE_LAW_001"]
ONTOLOGICAL_ISSUES = ["OI_ADMINISTRATIVE_LAW_001"]
