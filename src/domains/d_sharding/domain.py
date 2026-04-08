"""D_SHARDING domain definition — Data Sharding Invariants

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_SHARDING"
DOMAIN_NAME = "Data Sharding Invariants"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['sharding', 'determinism', 'load-balancing', 'data-distribution']
INVARIANTS = ['Shard assignment is deterministic: the same key always maps to the same shard.', 'Shard distribution is balanced: no shard holds more than ceil(N/K)+1 keys.', 'Shard reassignment preserves all data: no record is lost during resharding.']
FALSIFICATION_TESTS = ["F_SHARDING_001"]
ONTOLOGICAL_ISSUES = ["OI_SHARDING_001"]
