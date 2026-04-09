"""D_CHEMICAL domain definition — Chemical

Layer: 3
CardinalStrength: PREDICATIVE

Chemical engineering covers process design, reactor control, and safety systems.
Process safety management (PSM) and hazardous materials (HAZMAT) handling are critical.
Thermal runaway prevention and containment systems protect against catastrophic failures.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_CHEMICAL"
DOMAIN_NAME = "Chemical"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'reactor-control',
    'process-safety',
    'hazmat',
    'thermal-runaway',
    'distillation',
    'crystallization',
    'polymerization',
    'catalysis',
    'batch-processing',
    'continuous-processing',
    'PID-control',
    'DCS',
    'SIS',
    'LOPA',
    'HAZOP',
    'SIL',
    'interlock',
    'relief-valve',
    'emergency-shutdown',
    'containment',
    'ventilation',
    'leak-detection',
]

INVARIANTS = [
    'Thermal runaway interlock activates before temperature exceeds T_critical (e.g., 10°C margin).',
    'Hazmat containment is leak-free: <10 ppm detection threshold for volatile compounds.',
    'Reactor pressure interlocks activate at 90% of design pressure (ASME Boiler Code).',
    'PID control loops: steady-state error <1% for temperature, pressure, and flow rate.',
    'Distillation column reflux ratio maintains product purity within specification (±0.5%).',
    'Batch processing: recipe execution deterministic with timestamped audit trail.',
    'Safety Instrumented Systems (SIS): SIL 3 requires probability of failure on demand <10^-3.',
    'Layer of Protection Analysis (LOPA): independent protection layers reduce risk to tolerable level.',
    'HAZOP (Hazard and Operability Study): deviations from design intent identified and mitigated.',
    'Emergency shutdown (ESD): critical systems isolated within <5 seconds of trigger.',
    'Relief valves: set pressure ≤design pressure, discharge capacity verified by calculation.',
    'Ventilation: local exhaust captures >95% of airborne contaminants at source.',
    'Leak detection: continuous monitoring with alarm at 10% of lower explosive limit (LEL).',
    'Catalyst deactivation: monitored via conversion rate, regeneration scheduled before 20% loss.',
    'Polymerization: monomer conversion and molecular weight distribution within target ranges.',
]

FALSIFICATION_TESTS = ["F_CHEMICAL_001"]
ONTOLOGICAL_ISSUES = ["OI_CHEMICAL_001"]
