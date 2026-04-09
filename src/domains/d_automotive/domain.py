"""D_AUTOMOTIVE domain definition — Automotive

Layer: 3
CardinalStrength: PREDICATIVE

Automotive engineering encompasses vehicle design, manufacturing, and safety.
ISO 26262 (functional safety) and AUTOSAR (software architecture) are industry standards.
CAN bus, OTA updates, and ADAS (advanced driver assistance systems) are critical domains.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AUTOMOTIVE"
DOMAIN_NAME = "Automotive"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'AUTOSAR',
    'ISO-26262',
    'OTA',
    'CAN-bus',
    'FlexRay',
    'Ethernet-automotive',
    'ADAS',
    'lane-keeping',
    'adaptive-cruise-control',
    'automatic-emergency-braking',
    'blind-spot-detection',
    'parking-assist',
    'V2X',
    'telematics',
    'ECU',
    'powertrain',
    'chassis-control',
    'body-electronics',
    'infotainment',
    'cyber-security',
    'diagnostics',
    'UDS',
    'MISRA-C',
]

INVARIANTS = [
    'OTA update rejected if cryptographic signature invalid (ECDSA or RSA).',
    'CAN bus message timing within spec (e.g., critical safety messages <10ms latency).',
    'ISO 26262 ASIL-D: >99.9% diagnostic coverage for single-point faults.',
    'AUTOSAR Adaptive Platform: deterministic scheduling with worst-case execution time (WCET) guarantees.',
    'FlexRay time-triggered communication: slot allocation deterministic and reproducible.',
    'Automotive Ethernet (100BASE-T1): Time-Sensitive Networking (TSN) for critical data streams.',
    'ADAS sensor fusion: lidar, radar, camera data timestamps synchronized within 1ms.',
    'Lane-keeping assist: lateral deviation <0.1m at highway speeds under normal conditions.',
    'Adaptive cruise control: headway distance maintains safe following (e.g., 2-second rule).',
    'Automatic emergency braking: activation within 100ms of obstacle detection.',
    'V2X (Vehicle-to-Everything): message authentication with certificate management (SCMS).',
    'ECU diagnostics: UDS (Unified Diagnostic Services) responses within 50ms for critical requests.',
    'Powertrain control: fuel injection timing accurate to ±0.1 crank angle degree.',
    'Chassis control (ESC): brake actuation within 30ms of stability loss detection.',
    'Cyber security: intrusion detection system (IDS) monitors CAN/FlexRay for anomalies.',
]

FALSIFICATION_TESTS = ["F_AUTOMOTIVE_001"]
ONTOLOGICAL_ISSUES = ["OI_AUTOMOTIVE_001"]
