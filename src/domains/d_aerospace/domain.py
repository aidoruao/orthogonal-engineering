"""D_AEROSPACE domain definition — Aerospace

Layer: 3
CardinalStrength: PREDICATIVE

Aerospace engineering covers aircraft, spacecraft, and related systems.
Safety-critical software follows DO-178C (airborne software) and DO-254 (hardware).
Redundancy, fault tolerance, and certification are mandatory.
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_AEROSPACE"
DOMAIN_NAME = "Aerospace"
LAYER = 3
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = [
    'DO-178C',
    'DO-254',
    'avionics',
    'flight-control',
    'autopilot',
    'navigation',
    'communication',
    'structural-health',
    'redundancy',
    'fault-tolerance',
    'fly-by-wire',
    'fly-by-light',
    'FADEC',
    'glass-cockpit',
    'TCAS',
    'GPWS',
    'FMS',
    'AHRS',
    'INS',
    'GPS',
    'VOR',
    'ILS',
    'ADS-B',
    'ACARS',
    'certification',
]

INVARIANTS = [
    'Redundant channels produce byte-identical output (Byzantine fault tolerance).',
    'Structural health sensor alerts within spec (fatigue, vibration, temperature).',
    'DO-178C Level A software: 100% MC/DC coverage, formal methods, independent verification.',
    'Flight control laws remain stable under all flight envelope conditions.',
    'Autopilot mode transitions are deterministic and reversible.',
    'Navigation errors bounded by certified accuracy (GPS: <10m, INS: drift rate).',
    'Communication protocols follow ARINC 429, 664, or MIL-STD-1553 with integrity checks.',
    'Fault detection latency meets safety requirements (typically <100ms for critical faults).',
    'Fly-by-wire control surfaces respond within certified latency bounds (<20ms).',
    'FADEC (Full Authority Digital Engine Control) maintains engine parameters within limits.',
    'TCAS (Traffic Collision Avoidance System) alerts within certified reaction time.',
    'GPWS (Ground Proximity Warning System) terrain clearance warnings with <1s latency.',
    'FMS (Flight Management System) route calculations deterministic and reproducible.',
    'AHRS (Attitude Heading Reference System) drift bounded by gyro specs.',
    'Certification artifacts (test plans, requirements traceability matrix) hash-anchored.',
]

FALSIFICATION_TESTS = ["F_AEROSPACE_001"]
ONTOLOGICAL_ISSUES = ["OI_AEROSPACE_001"]
