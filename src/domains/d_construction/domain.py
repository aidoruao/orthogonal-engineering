"""D_CONSTRUCTION domain definition — Construction

Layer: 3
CardinalStrength: PREDICATIVE

Construction engineering covers building design, structural analysis, and site safety.
Building Information Modeling (BIM) enables 3D design with clash detection.
Finite Element Method (FEM) validates structural integrity under load.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CONSTRUCTION"
DOMAIN_NAME = "Construction"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'BIM',
    'structural-analysis',
    'site-safety',
    'FEM',
    'clash-detection',
    'scheduling',
    'CPM',
    'PERT',
    'cost-estimation',
    'quantity-takeoff',
    'load-bearing',
    'seismic-design',
    'wind-load',
    'foundation-design',
    'concrete-strength',
    'rebar-placement',
    'formwork',
    'OSHA',
    'fall-protection',
    'excavation-safety',
    'crane-operations',
    'PPE',
]

INVARIANTS = [
    'FEM (Finite Element Method) results within 1% of analytical reference for benchmark problems.',
    'Site safety alerts delivered within SLO (e.g., <30 seconds for critical hazards).',
    'BIM clash detection: geometric conflicts identified before construction with <0.1% false negative rate.',
    'Critical Path Method (CPM): project completion date deterministic given activity durations.',
    'PERT (Program Evaluation and Review Technique): probabilistic scheduling with confidence intervals.',
    'Quantity takeoff: material quantities accurate to ±2% for cost estimation.',
    'Structural load factors: dead load + live load + environmental loads per building code (ASCE 7).',
    'Seismic design: structures withstand design-basis earthquake with <1% collapse probability.',
    'Wind load: structures withstand 50-year wind speed with occupancy category factors.',
    'Foundation design: bearing capacity ≥applied load with safety factor ≥3 (geotechnical).',
    'Concrete strength: 28-day compressive strength meets specification (e.g., 4000 psi ± 10%).',
    'Rebar placement: cover depth maintains corrosion protection (ACI 318 code).',
    'OSHA fall protection: guardrails, safety nets, or personal fall arrest systems at >6 ft height.',
    'Excavation safety: shoring, sloping, or benching for trenches >5 ft depth (OSHA 1926 Subpart P).',
    'Crane operations: load ≤rated capacity with safety factors, operator certified.',
]

FALSIFICATION_TESTS = ["F_CONSTRUCTION_001"]
ONTOLOGICAL_ISSUES = ["OI_CONSTRUCTION_001"]
