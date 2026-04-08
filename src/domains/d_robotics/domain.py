"""D_ROBOTICS domain definition — Robotics

Layer: 3
CardinalStrength: PREDICATIVE
"""

from src.sal.forcing_operation import CardinalStrength

DOMAIN_ID = "D_ROBOTICS"
DOMAIN_NAME = "Robotics"
LAYER = 3  # Unassigned
CARDINAL_STRENGTH = CardinalStrength.PREDICATIVE

CATEGORIES = ['kinematics', 'collision-avoidance', 'ROS']
INVARIANTS = ['Arm stops before contacting obstacle.', 'ROS message ordering is preserved.']
FALSIFICATION_TESTS = ["F_ROBOTICS_001"]
ONTOLOGICAL_ISSUES = ["OI_ROBOTICS_001"]
