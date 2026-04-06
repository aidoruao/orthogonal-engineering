"""D_SECURITIES_LAW: Securities Law (Securities Act 1933, Exchange Act 1934)

Layer 2 (Statutory) domain implementing securities regulation including
registration requirements, anti-fraud provisions, and insider trading rules.

Biblical: Proverbs 11:1 — "The LORD detests dishonest scales, but accurate
weights find favor with him."
"""

from src.domains.d_securities_law.implementation import (
    SecuritiesRegistrationChecker,
    InsiderTradingAnalyzer,
    AntiFraudCompliance,
    Security,
    Transaction,
    SecurityType,
    TransactionType,
)
from src.domains.d_securities_law.invariants import (
    check_registration_required,
    check_insider_trading_prohibited,
    check_antifraud_rule_10b5,
    check_accredited_investor_limits,
    check_disclosure_requirements,
)

__all__ = [
    "SecuritiesRegistrationChecker",
    "InsiderTradingAnalyzer",
    "AntiFraudCompliance",
    "Security",
    "Transaction",
    "SecurityType",
    "TransactionType",
    "check_registration_required",
    "check_insider_trading_prohibited",
    "check_antifraud_rule_10b5",
    "check_accredited_investor_limits",
    "check_disclosure_requirements",
]
