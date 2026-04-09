"""D_PHYSICS domain definition — Physics Simulation & Dynamics

Layer: 3
CardinalStrength: PREDICATIVE

Bridges axioms/classical_mechanics.py to domain invariants.
Provides real physics: energy/momentum conservation, equations of motion.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_PHYSICS"
DOMAIN_NAME = "Physics Simulation & Dynamics"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'rigid-body-dynamics',
    'energy-conservation',
    'momentum-conservation',
    'equation-of-motion',
    'joint-constraints',
    'collision-detection',
    'contact-mechanics',
    'numerical-integration'
]

INVARIANTS = [
    'Total mechanical energy must be conserved in isolated systems.',
    'Total linear momentum must be conserved in isolated systems.',
    'F = ma must be satisfied at all times.',
    'Joint torques must remain within actuator limits.',
    'Collision responses must conserve momentum.',
    'Numerical integration must respect stability criteria.'
]

FALSIFICATION_TESTS = ["F_PHYSICS_001"]
ONTOLOGICAL_ISSUES = ["OI_PHYSICS_001"]
