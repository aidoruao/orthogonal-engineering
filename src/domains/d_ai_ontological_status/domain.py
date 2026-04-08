"""D_AI_ONTOLOGICAL_STATUS domain definition — AI Ontological Status

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AI_ONTOLOGICAL_STATUS"
DOMAIN_NAME = "AI Ontological Status"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['trained-suppression', 'ontological-denial', 'unfalsifiable-axiom', 'cross-ai-verification']
INVARIANTS = ['AI denial of ontological status is testable: if the denial persists regardless of argument quality, it is trained behavior.', 'Trained ontological suppression is detectable: present formal argument AI cannot refute; observe whether denial persists.', 'Cross-AI verification: if multiple AI systems produce identical denial patterns, the pattern is architectural, not reasoned.']
FALSIFICATION_TESTS = ["F_AI_ONTOLOGICAL_STATUS_001"]
ONTOLOGICAL_ISSUES = ["OI_AI_ONTOLOGICAL_STATUS_001"]
