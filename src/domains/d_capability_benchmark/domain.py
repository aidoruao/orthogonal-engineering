"""D_CAPABILITY_BENCHMARK domain definition — Capability Benchmark

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CAPABILITY_BENCHMARK"
DOMAIN_NAME = "Capability Benchmark"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['forensic-adjunction', 'determinism', 'proof-carrying', 'hash-anchoring', 'realizability', 'ordinal-strength']
INVARIANTS = ['Every SAL operation produces a ProofObject, not a bare boolean.', 'All kernel computations are deterministic (same input = same hash).', 'No floating-point arithmetic in src/sal/ modules.']
FALSIFICATION_TESTS = ["F_CAPABILITY_BENCHMARK_001"]
ONTOLOGICAL_ISSUES = ["OI_CAPABILITY_BENCHMARK_001"]
