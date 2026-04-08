"""D_HABEAS_CORPUS domain definition — Habeas Corpus

Layer: 1
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_HABEAS_CORPUS"
DOMAIN_NAME = "Habeas Corpus"
LAYER = 1
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['article-i', 'detention-review', 'suspension-limits']
INVARIANTS = ['No detention without judicial review.', 'Suspension only in cases of rebellion/invasion (Article I, §9).']
FALSIFICATION_TESTS = ["F_HABEAS_CORPUS_001"]
ONTOLOGICAL_ISSUES = ["OI_HABEAS_CORPUS_001"]
