"""D_BIOTECH domain definition — Biotechnology

Layer: TBD (Unassigned)
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_BIOTECH"
DOMAIN_NAME = "Biotechnology"
LAYER = None  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['sequencing', 'lab-automation', 'biosafety']
INVARIANTS = ['VCF output is identical for identical FASTQ input.', 'Reagent dispensing within +/-2%.']
FALSIFICATION_TESTS = ["F_BIOTECH_001"]
ONTOLOGICAL_ISSUES = ["OI_BIOTECH_001"]
