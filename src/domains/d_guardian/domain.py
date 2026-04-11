"""D_GUARDIAN domain definition — Operation T-800 Guardian Agent

Layer: 4
CardinalStrength: PREDICATIVE

Autonomous protective agent with ethical constraints.
Extends just war theory (CrusaderCap) with:
- Solo protector constraint (exactly 1 guardian per principal)
- Liveness requirements (heartbeat monitoring)
- Proportional response limits
- No termination mode (guardians cannot be ordered to self-terminate)
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_GUARDIAN"
DOMAIN_NAME = "Operation T-800 Guardian Agent"
LAYER = 4  # Application
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'autonomous-protection',
    'ethical-constraints',
    'liveness-monitoring',
    'proportional-response',
    'solo-protector',
]

INVARIANTS = [
    'Exactly one guardian per principal.',
    'Guardian heartbeat within configured interval.',
    'Force used never exceeds proportional budget.',
    'Principal never unprotected during active threat.',
    'Guardian cannot enter TERMINATION mode.',
    'Withdrawal only after threat cleared.',
    'Every force action must be witnessed.',
]

FALSIFICATION_TESTS = [
    "F_GUARDIAN_001",
    "F_GUARDIAN_002",
    "F_GUARDIAN_003",
]

ONTOLOGICAL_ISSUES = [
    "OI_GUARDIAN_001",
]
