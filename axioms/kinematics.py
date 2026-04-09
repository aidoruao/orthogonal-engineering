"""Kinematics — Forward and inverse kinematics for robotic arms.

Implements DH parameter transformations using exact Fraction arithmetic.
Trigonometric functions are represented symbolically (not computed).
All operations return (result, ProofObject) pairs.

Mathematical foundation: Craig, "Introduction to Robotics"
Biblical: Ecclesiastes 3:1 — "There is a time for everything,
and a season for every activity under the heavens."
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject


@dataclass(frozen=True)
class DHParameter:
    """Denavit-Hartenberg parameter for a single joint.
    
    The DH convention defines four parameters for each link:
    - a: link length (distance along x_i from z_{i-1} to z_i)
    - alpha: link twist (angle about x_i from z_{i-1} to z_i)
    - d: link offset (distance along z_{i-1} from x_{i-1} to x_i)
    - theta: joint angle (angle about z_{i-1} from x_{i-1} to x_i)
    
    Note: angles stored as rational multiples of π.
    e.g., Fraction(1,2) represents π/2 radians (90°)
          Fraction(1,1) represents π radians (180°)
    """
    a: Fraction           # Link length
    alpha_rational: Fraction  # Link twist as multiple of π
    d: Fraction           # Link offset
    theta_rational: Fraction  # Joint angle as multiple of π
    
    def alpha_symbolic(self) -> str:
        """Return symbolic representation of alpha."""
        if self.alpha_rational == Fraction(0):
            return "0"
        elif self.alpha_rational == Fraction(1, 2):
            return "π/2"
        elif self.alpha_rational == Fraction(1, 1):
            return "π"
        elif self.alpha_rational == Fraction(-1, 2):
            return "-π/2"
        else:
            return f"{self.alpha_rational}*π"
    
    def theta_symbolic(self) -> str:
        """Return symbolic representation of theta."""
        if self.theta_rational == Fraction(0):
            return "0"
        elif self.theta_rational == Fraction(1, 2):
            return "π/2"
        elif self.theta_rational == Fraction(1, 1):
            return "π"
        elif self.theta_rational == Fraction(-1, 2):
            return "-π/2"
        else:
            return f"{self.theta_rational}*π"


@dataclass(frozen=True)
class JointState:
    """State of a single joint."""
    joint_id: str
    position: Fraction       # Joint angle (revolute) or displacement (prismatic)
    velocity: Fraction       # d(position)/dt
    torque: Fraction         # Applied torque/force


@dataclass(frozen=True)
class RobotArm:
    """Serial manipulator with DH parameters and joint states."""
    joints: List[JointState]
    dh_params: List[DHParameter]
    
    def __post_init__(self):
        if len(self.joints) != len(self.dh_params):
            raise ValueError("Number of joints must match number of DH parameters")
    
    def num_joints(self) -> int:
        return len(self.joints)


def forward_kinematics_symbolic(dh_params: List[DHParameter]) -> Tuple[List[List[str]], ProofObject]:
    """Compute symbolic forward kinematics transformation matrix.
    
    Returns a 4x4 homogeneous transformation matrix where each entry
    is a symbolic expression string involving cos(θ_i) and sin(θ_i).
    
    The DH transformation matrix for each joint i is:
    
    | cos(θ_i)  -sin(θ_i)*cos(α_i)   sin(θ_i)*sin(α_i)   a_i*cos(θ_i) |
    | sin(θ_i)   cos(θ_i)*cos(α_i)  -cos(θ_i)*sin(α_i)   a_i*sin(θ_i) |
    |    0           sin(α_i)            cos(α_i)            d_i       |
    |    0               0                   0                1       |
    
    For multiple joints, this would be the product of individual matrices.
    This implementation returns the structure for the final transformation.
    """
    n = len(dh_params)
    if n == 0:
        return [["1", "0", "0", "0"],
                ["0", "1", "0", "0"],
                ["0", "0", "1", "0"],
                ["0", "0", "0", "1"]], ProofObject(
            rule="ForwardKinematics",
            premises=["no joints"],
            conclusion="identity matrix"
        )
    
    # For a single joint, return the symbolic matrix
    # For multiple joints, we'd multiply the matrices symbolically
    dh = dh_params[-1]  # Use last joint for demonstration
    
    # Symbolic expressions
    cos_theta = f"cos({dh.theta_symbolic()})"
    sin_theta = f"sin({dh.theta_symbolic()})"
    cos_alpha = f"cos({dh.alpha_symbolic()})"
    sin_alpha = f"sin({dh.alpha_symbolic()})"
    
    matrix = [
        [cos_theta, f"-{sin_theta}*{cos_alpha}", f"{sin_theta}*{sin_alpha}", f"{dh.a}*{cos_theta}"],
        [sin_theta, f"{cos_theta}*{cos_alpha}", f"-{cos_theta}*{sin_alpha}", f"{dh.a}*{sin_theta}"],
        ["0", sin_alpha, cos_alpha, str(dh.d)],
        ["0", "0", "0", "1"]
    ]
    
    proof = ProofObject(
        rule="ForwardKinematics_Symbolic",
        premises=[f"n_joints={n}", f"last_joint_a={dh.a}, d={dh.d}"],
        conclusion=f"4x4 symbolic transformation matrix"
    )
    
    return matrix, proof


def workspace_reachability(arm_lengths: List[Fraction], target_distance_sq: Fraction) -> Tuple[bool, ProofObject]:
    """Check if target is within robot workspace using conservative bounds.
    
    Conservative check: if sum of arm lengths squared >= target distance squared,
    the target might be reachable. This avoids square roots (which would give floats).
    
    Args:
        arm_lengths: List of link lengths
        target_distance_sq: Squared distance from base to target
    
    Returns:
        (possibly_reachable, proof)
    """
    max_reach_sq = sum(l * l for l in arm_lengths)
    
    # Conservative: if target is farther than fully extended arm, definitely not reachable
    # But being closer doesn't guarantee reachability due to joint limits
    possibly_reachable = target_distance_sq <= max_reach_sq * len(arm_lengths)
    
    proof = ProofObject(
        rule="WorkspaceReachability",
        premises=[
            f"arm_lengths={arm_lengths}",
            f"max_reach²={max_reach_sq}",
            f"target_dist²={target_distance_sq}"
        ],
        conclusion=f"possibly_reachable={possibly_reachable}"
    )
    
    return possibly_reachable, proof


def joint_limit_check(joint: JointState, min_pos: Fraction, max_pos: Fraction) -> Tuple[bool, ProofObject]:
    """Verify joint position is within limits.
    
    Args:
        joint: Joint state to check
        min_pos: Minimum allowed position
        max_pos: Maximum allowed position
    
    Returns:
        (within_limits, proof)
    """
    within_limits = min_pos <= joint.position <= max_pos
    
    proof = ProofObject(
        rule="JointLimitCheck",
        premises=[
            f"joint_id={joint.joint_id}",
            f"position={joint.position}",
            f"limits=[{min_pos}, {max_pos}]"
        ],
        conclusion=f"within_limits={within_limits}"
    )
    
    return within_limits, proof


def velocity_jacobian_rank(num_joints: int, num_dof: int) -> Tuple[bool, ProofObject]:
    """Check if Jacobian has full rank (sufficient degrees of freedom).
    
    For a manipulator to have full control authority, the velocity Jacobian
    must have rank equal to the task space dimension (num_dof).
    
    A necessary condition: num_joints >= num_dof
    
    Args:
        num_joints: Number of joints (columns of Jacobian)
        num_dof: Degrees of freedom in task space (rows of Jacobian)
    
    Returns:
        (can_have_full_rank, proof)
    """
    can_have_full_rank = num_joints >= num_dof
    
    proof = ProofObject(
        rule="JacobianRank",
        premises=[
            f"num_joints={num_joints}",
            f"num_dof={num_dof}"
        ],
        conclusion=f"can_have_full_rank={can_have_full_rank}"
    )
    
    return can_have_full_rank, proof


@dataclass(frozen=True)
class CartesianPose:
    """End-effector pose in Cartesian space."""
    x: Fraction
    y: Fraction
    z: Fraction
    # Orientation could be added as roll/pitch/yaw or quaternion


def inverse_kinematics_analytic_2link(l1: Fraction, l2: Fraction, 
                                       target: CartesianPose) -> Tuple[List[Tuple[Fraction, Fraction]], ProofObject]:
    """Analytic IK for 2-link planar arm.
    
    For a 2-link arm with lengths l1, l2 reaching to (x, y):
    
    c2 = (x² + y² - l1² - l2²) / (2*l1*l2)
    
    If |c2| > 1: no solution (target unreachable)
    If |c2| <= 1: two solutions (elbow up/down)
    
    Returns list of (theta1, theta2) solutions.
    """
    x, y = target.x, target.y
    r_sq = x * x + y * y
    
    # Check reachability
    max_reach = l1 + l2
    min_reach = abs(l1 - l2)
    
    if r_sq > max_reach * max_reach or r_sq < min_reach * min_reach:
        return [], ProofObject(
            rule="InverseKinematics_2Link",
            premises=[
                f"l1={l1}, l2={l2}",
                f"target=({x},{y})",
                f"r²={r_sq}",
                f"reach=[{min_reach},{max_reach}]"
            ],
            conclusion="no solution (target unreachable)"
        )
    
    # Compute c2 = cos(theta2)
    # Note: We'd need sqrt for s2, so we work with squared terms
    c2_numerator = r_sq - l1*l1 - l2*l2
    c2_denominator = 2 * l1 * l2
    c2 = c2_numerator / c2_denominator
    
    # For exact arithmetic without sqrt, we note when solutions exist
    c2_sq = c2 * c2
    solutions_exist = c2_sq <= Fraction(1)
    
    if not solutions_exist:
        return [], ProofObject(
            rule="InverseKinematics_2Link",
            premises=[
                f"c2={c2}",
                f"c2²={c2_sq}"
            ],
            conclusion="no solution (|c2| > 1)"
        )
    
    # Solutions exist (would need sqrt for exact angles)
    # Return symbolic indication
    proof = ProofObject(
        rule="InverseKinematics_2Link",
        premises=[
            f"l1={l1}, l2={l2}",
            f"target=({x},{y})",
            f"c2={c2}"
        ],
        conclusion="solutions exist (elbow-up and elbow-down)"
    )
    
    # Placeholder for solutions (exact values require sqrt)
    return [(Fraction(0), Fraction(0))], proof  # Symbolic solutions


def manipulability_measure(joint_angles: List[Fraction], dh_params: List[DHParameter]) -> Tuple[Fraction, ProofObject]:
    """Compute manipulability measure (simplified).
    
    The Yoshikawa manipulability measure is sqrt(det(J * J^T)).
    Without computing J explicitly, we use a proxy based on arm configuration.
    
    Returns a Fraction representing relative manipulability.
    """
    # Simplified: count how far joints are from singular configurations
    # A common singularity is when joints are fully extended or folded
    
    score = Fraction(1)
    for angle in joint_angles:
        # Penalize angles near 0 (fully extended) or π (folded)
        # Using squared distance from singularities
        dist_from_0 = angle * angle
        dist_from_pi = (angle - Fraction(1)) * (angle - Fraction(1))
        
        # Keep the larger of the two distances (farther from singularity)
        # This is a simplified metric
        if dist_from_0 > dist_from_pi:
            score = score * dist_from_0
        else:
            score = score * dist_from_pi
    
    proof = ProofObject(
        rule="ManipulabilityMeasure",
        premises=[f"joint_angles={joint_angles}"],
        conclusion=f"manipulability_score={score}"
    )
    
    return score, proof
