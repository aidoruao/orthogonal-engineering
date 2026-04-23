"""D_SWE_BENCH domain definition — SWE-bench Excedent

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SWE_BENCH"
DOMAIN_NAME = "SWE-bench Excedent"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['benchmark-excedent', 'determinism', 'proof-carrying', 'patch-minimality', 'data-leakage']
INVARIANTS = [
    'SWE-bench Verified resolve_rate exceeds 85%.',
    'False positive rate remains below 5%.',
    'Average patch size stays under 50 lines.',
    'All resolved instances show 100% test pass rate.',
    'No resolved instance appears in training data.',
    'Deterministic resolution produces identical patches per instance.',
]
FALSIFICATION_TESTS = ["F_SWE_BENCH_001"]
ONTOLOGICAL_ISSUES = ["OI_SWE_BENCH_001"]
