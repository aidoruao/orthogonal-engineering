"""D_BANKING_REGULATION domain definition — Banking & Finance Regulation

Layer: 2
CardinalStrength: PREDICATIVE

Banking regulation ensures financial system stability and consumer protection.
Dodd-Frank Act (2010) established comprehensive regulatory framework post-2008 crisis.
Capital requirements (Basel III), stress testing, and FDIC insurance are core mechanisms.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BANKING_REGULATION"
DOMAIN_NAME = "Banking & Finance Regulation"
LAYER = 2
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'dodd-frank',
    'basel-iii',
    'capital-reserves',
    'liquidity-coverage-ratio',
    'fdic',
    'stress-test',
    'volcker-rule',
    'living-will',
    'risk-weighted-assets',
    'leverage-ratio',
    'countercyclical-buffer',
    'systemically-important',
    'orderly-liquidation',
    'consumer-protection',
    'cfpb',
    'fair-lending',
    'community-reinvestment',
    'anti-money-laundering',
    'know-your-customer',
    'suspicious-activity-reporting',
    'bank-secrecy-act',
]

INVARIANTS = [
    'Capital reserve ratio (CET1) ≥4.5% of risk-weighted assets (Basel III minimum).',
    'Total capital ratio ≥8% of risk-weighted assets.',
    'Leverage ratio ≥3% (Tier 1 capital / total exposure).',
    'Liquidity Coverage Ratio (LCR) ≥100% (high-quality liquid assets / net cash outflow).',
    'FDIC insurance limit is $250,000 per depositor, per insured bank, per ownership category.',
    'Stress test (CCAR/DFAST) scenarios are standardized and reproducible.',
    'Volcker Rule: proprietary trading prohibited for deposit-taking institutions (Dodd-Frank § 619).',
    'Living wills (resolution plans) required for SIFIs (systemically important financial institutions).',
    'Risk-weighted assets calculation follows Basel III standardized or internal ratings-based approach.',
    'Countercyclical capital buffer (0-2.5%) activated during periods of excess credit growth.',
    'SIFI designation triggers enhanced prudential standards (Federal Reserve supervision).',
    'Orderly Liquidation Authority (OLA) enables FDIC resolution without taxpayer bailout.',
    'CFPB (Consumer Financial Protection Bureau) enforces TILA, RESPA, fair lending laws.',
    'Fair lending compliance: no discrimination based on race, color, religion, sex, national origin.',
    'AML/KYC: Customer Identification Program (CIP) required within 90 days of account opening.',
]

FALSIFICATION_TESTS = ["F_BANKING_REGULATION_001"]
ONTOLOGICAL_ISSUES = ["OI_BANKING_REGULATION_001"]
