"""
COMPREHENSIVE TEST SUITE FOR MATHEMATICAL THEOLOGY V60

Tests the fully non-abstract, mathematically irreducible, Popperian, immutable
mathematical theology system implemented in mathematical_theology_v60.py
"""

import os
import sys
from decimal import Decimal, getcontext

import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mathematical_theology_v60 import (
    ConcreteContractionMap,
    ConcreteNecessityOperator,
    ConcreteSalvationOperator,
    ConcreteVectorSpace,
    ConstraintType,
    MathematicalTheologyV60,
    V60Constraint,
)


class TestConcreteVectorSpace:
    """Test concrete vector space implementation"""

    def test_initialization(self):
        """Test space initialization"""
        space = ConcreteVectorSpace(dimension=3)
        assert space.dimension == 3
        assert len(space.vectors) == 0
        assert space.norm_type == "euclidean"
        assert space.complete is True

    def test_add_vector(self):
        """Test adding vectors to space"""
        space = ConcreteVectorSpace(dimension=2)
        v1 = np.array([1.0, 2.0])
        v2 = np.array([3.0, 4.0])

        space1 = space.add_vector(v1)
        assert len(space1.vectors) == 1
        assert np.array_equal(space1.vectors[0], v1)

        space2 = space1.add_vector(v2)
        assert len(space2.vectors) == 2
        assert np.array_equal(space2.vectors[0], v1)
        assert np.array_equal(space2.vectors[1], v2)

    def test_norm_calculations(self):
        """Test norm calculations"""
        space = ConcreteVectorSpace(dimension=3)

        # Euclidean norm
        v = np.array([3.0, 4.0, 0.0])
        assert abs(space.norm(v) - 5.0) < 1e-12

        # Manhattan norm
        space_manhattan = ConcreteVectorSpace(dimension=3, norm_type="manhattan")
        assert abs(space_manhattan.norm(v) - 7.0) < 1e-12

        # Max norm
        space_max = ConcreteVectorSpace(dimension=3, norm_type="max")
        assert abs(space_max.norm(v) - 4.0) < 1e-12

    def test_distance_calculation(self):
        """Test distance calculation"""
        space = ConcreteVectorSpace(dimension=2)
        v1 = np.array([0.0, 0.0])
        v2 = np.array([3.0, 4.0])

        distance = space.distance(v1, v2)
        assert abs(distance - 5.0) < 1e-12

    def test_validation(self):
        """Test validation of vector dimensions"""
        space = ConcreteVectorSpace(dimension=2)

        # Valid vector
        v_valid = np.array([1.0, 2.0])
        space_valid = space.add_vector(v_valid)
        assert len(space_valid.vectors) == 1

        # Invalid vector should raise error
        v_invalid = np.array([1.0, 2.0, 3.0])
        try:
            space.add_vector(v_invalid)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "dimension" in str(e)


class TestConcreteContractionMap:
    """Test concrete contraction map implementation"""

    def setup_space(self):
        """Setup test space"""
        return ConcreteVectorSpace(dimension=3)

    def test_initialization(self):
        """Test contraction map initialization"""
        space = self.setup_space()
        H = np.array([1.0, 1.0, 1.0])
        alpha = 0.6

        contraction = ConcreteContractionMap(H=H, alpha=alpha, space=space)

        assert np.array_equal(contraction.H, H)
        assert contraction.alpha == alpha
        assert contraction.space == space
        assert abs(contraction.lambda_val - 0.4) < 1e-12

    def test_validation(self):
        """Test validation of contraction parameters"""
        space = self.setup_space()
        H = np.array([1.0, 1.0, 1.0])

        # Valid alpha
        contraction_valid = ConcreteContractionMap(H=H, alpha=0.5, space=space)
        assert contraction_valid.alpha == 0.5

        # Invalid alpha should raise error
        try:
            ConcreteContractionMap(H=H, alpha=1.5, space=space)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "alpha" in str(e) or "lambda" in str(e)

    def test_application(self):
        """Test contraction map application"""
        space = self.setup_space()
        H = np.array([1.0, 1.0, 1.0])
        contraction = ConcreteContractionMap(H=H, alpha=0.6, space=space)

        x = np.array([0.0, 0.0, 0.0])
        result = contraction(x)

        # f(x) = αH + (1-α)x = 0.6*[1,1,1] + 0.4*[0,0,0] = [0.6,0.6,0.6]
        expected = np.array([0.6, 0.6, 0.6])
        assert np.allclose(result, expected, rtol=1e-12, atol=1e-12)

    def test_iteration(self):
        """Test contraction map iteration"""
        space = self.setup_space()
        H = np.array([1.0, 1.0, 1.0])
        contraction = ConcreteContractionMap(H=H, alpha=0.5, space=space)

        x0 = np.array([0.0, 0.0, 0.0])
        x1 = contraction.iterate(x0, n=10)

        # After many iterations, should be close to H
        assert np.allclose(x1, H, rtol=0.01, atol=0.01)

    def test_contraction_verification(self):
        """Test concrete contraction verification"""
        space = self.setup_space()
        H = np.array([1.0, 1.0, 1.0])
        contraction = ConcreteContractionMap(H=H, alpha=0.6, space=space)

        # Create test pairs
        test_pairs = [
            (np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])),
            (np.array([0.5, 0.5, 0.5]), np.array([1.0, 1.0, 1.0])),
        ]

        verification = contraction.verify_contraction_concrete(test_pairs)

        assert verification["contraction_verified"] is True
        assert verification["lambda"] == 0.4
        assert verification["test_pairs_count"] == 2
        assert verification["violations_count"] == 0
        assert verification["falsifiable"] is True


class TestConcreteSalvationOperator:
    """Test concrete salvation operator implementation"""

    def setup(self):
        """Setup test environment"""
        space = ConcreteVectorSpace(dimension=3)
        H = np.array([1.0, 1.0, 1.0])
        space = space.add_vector(H)

        def merit_function(x):
            return space.norm(x)

        theta = 0.8
        salvation = ConcreteSalvationOperator(
            theta=theta, merit_function=merit_function, space=space
        )

        return space, salvation, H

    def test_initialization(self):
        """Test salvation operator initialization"""
        space, salvation, H = self.setup()

        assert salvation.theta == 0.8
        assert salvation.space == space
        assert callable(salvation.merit_function)

    def test_salvation_decision(self):
        """Test salvation decisions"""
        space, salvation, H = self.setup()

        # Test vectors
        x_below = np.array([0.5, 0.5, 0.5])  # norm ≈ 0.866 > 0.8
        x_above = np.array([1.0, 0.0, 0.0])  # norm = 1.0 > 0.8
        x_below2 = np.array([0.4, 0.4, 0.4])  # norm ≈ 0.693 < 0.8

        # M(x_below) ≈ 0.866 > 0.8 → saved
        assert salvation(x_below) == 1

        # M(x_above) = 1.0 > 0.8 → saved
        assert salvation(x_above) == 1

        # M(x_below2) ≈ 0.693 < 0.8 → not saved
        assert salvation(x_below2) == 0

    def test_partition(self):
        """Test concrete partition"""
        space, salvation, H = self.setup()

        vectors = [
            np.array([1.0, 1.0, 1.0]),  # norm ≈ 1.732 > 0.8 → elect
            np.array([0.5, 0.5, 0.5]),  # norm ≈ 0.866 > 0.8 → elect
            np.array([0.4, 0.4, 0.4]),  # norm ≈ 0.693 < 0.8 → reprobate
            np.array([0.0, 0.0, 0.0]),  # norm = 0.0 < 0.8 → reprobate
        ]

        partition = salvation.partition_concrete(vectors)

        assert partition["theta"] == 0.8
        assert partition["total_vectors"] == 4
        assert partition["elect_count"] == 2  # First two vectors
        assert partition["reprobate_count"] == 2  # Last two vectors
        assert partition["partition_complete"] is True
        assert partition["falsifiable"] is True


class TestConcreteNecessityOperator:
    """Test concrete necessity operator implementation"""

    def setup(self):
        """Setup test environment"""
        space = ConcreteVectorSpace(dimension=3)

        H = np.array([1.0, 1.0, 1.0])
        space = space.add_vector(H)

        alpha = 0.6
        contraction = ConcreteContractionMap(H=H, alpha=alpha, space=space)

        def merit_function(x):
            return space.norm(x)

        theta = 0.8
        salvation = ConcreteSalvationOperator(
            theta=theta, merit_function=merit_function, space=space
        )

        necessity = ConcreteNecessityOperator(
            contraction_map=contraction, salvation_operator=salvation
        )

        return space, contraction, salvation, necessity, H

    def test_initialization(self):
        """Test necessity operator initialization"""
        space, contraction, salvation, necessity, H = self.setup()

        assert necessity.contraction_map == contraction
        assert necessity.salvation_operator == salvation

    def test_necessity_verification(self):
        """Test necessity verification"""
        space, contraction, salvation, necessity, H = self.setup()

        initial_points = [
            np.array([0.0, 0.0, 0.0]),
            np.array([0.5, 0.5, 0.5]),
            np.array([2.0, 2.0, 2.0]),
        ]

        verification = necessity.verify_necessity_concrete(
            initial_points=initial_points, iterations=30
        )

        # M(H) = √3 ≈ 1.732 > 0.8 = θ
        assert verification["M(H)"] > verification["theta"]
        assert verification["M(H) > theta"] is True

        # All should converge to H
        assert verification["all_converge_to_H"] is True

        # Necessity should hold
        assert verification["necessity_verified"] is True

        assert verification["falsifiable"] is True
        assert "falsification_condition" in verification


class TestV60Constraint:
    """Test V60 constraint system"""

    def test_constraint_creation(self):
        """Test constraint creation"""

        def test_predicate(state):
            return True

        constraint = V60Constraint(
            constraint_id="TEST_001",
            constraint_type=ConstraintType.AXIOM,
            description="Test constraint",
            predicate=test_predicate,
            falsification_condition="Test falsification",
            priority=5,
        )

        assert constraint.constraint_id == "TEST_001"
        assert constraint.constraint_type == ConstraintType.AXIOM
        assert constraint.description == "Test constraint"
        assert constraint.predicate == test_predicate
        assert constraint.falsification_condition == "Test falsification"
        assert constraint.priority == 5
        assert constraint.immutable is True

    def test_constraint_execution(self):
        """Test constraint execution"""

        def test_predicate(state):
            return state.get("valid", False)

        constraint = V60Constraint(
            constraint_id="TEST_002",
            constraint_type=ConstraintType.THEOREM,
            description="Test theorem",
            predicate=test_predicate,
            falsification_condition="State not valid",
            priority=7,
        )

        # Test with valid state
        valid_state = {"valid": True}
        result_valid = constraint.execute(valid_state)
        assert result_valid["satisfied"] is True
        assert result_valid["constraint_id"] == "TEST_002"
        assert (
            result_valid["can_be_falsified"] is True
        )  # All constraints are falsifiable by design

        # Test with invalid state
        invalid_state = {"valid": False}
        result_invalid = constraint.execute(invalid_state)
        assert result_invalid["satisfied"] is False
        assert (
            result_invalid["can_be_falsified"] is True
        )  # All constraints are falsifiable by design

    def test_priority_validation(self):
        """Test priority validation"""

        def test_predicate(state):
            return True

        # Valid priority
        constraint_valid = V60Constraint(
            constraint_id="TEST_003",
            constraint_type=ConstraintType.AXIOM,
            description="Test",
            predicate=test_predicate,
            falsification_condition="Test",
            priority=10,
        )
        assert constraint_valid.priority == 10

        # Invalid priority should raise error
        try:
            V60Constraint(
                constraint_id="TEST_004",
                constraint_type=ConstraintType.AXIOM,
                description="Test",
                predicate=test_predicate,
                falsification_condition="Test",
                priority=15,  # Invalid
            )
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Priority" in str(e)


class TestMathematicalTheologyV60:
    """Test complete V60 mathematical theology system"""

    def test_system_initialization(self):
        """Test system initialization"""
        system = MathematicalTheologyV60()

        assert len(system.constraints) == 0
        assert len(system.verification_history) == 0
        assert isinstance(system.constraints, dict)

    def test_constraint_registration(self):
        """Test constraint registration"""
        system = MathematicalTheologyV60()

        def test_predicate(state):
            return True

        constraint = V60Constraint(
            constraint_id="TEST_REG_001",
            constraint_type=ConstraintType.AXIOM,
            description="Test registration",
            predicate=test_predicate,
            falsification_condition="Test",
            priority=5,
        )

        system.register_constraint(constraint)

        assert "TEST_REG_001" in system.constraints
        assert system.constraints["TEST_REG_001"] == constraint

        # Test duplicate registration
        try:
            system.register_constraint(constraint)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already registered" in str(e)

    def test_constraint_execution_all(self):
        """Test execution of all constraints"""
        system = MathematicalTheologyV60()

        # Register multiple constraints
        for i in range(3):

            def make_predicate(value):
                return lambda state: state.get("value", 0) == value

            constraint = V60Constraint(
                constraint_id=f"TEST_EXEC_{i}",
                constraint_type=ConstraintType.THEOREM,
                description=f"Test constraint {i}",
                predicate=make_predicate(i),
                falsification_condition=f"State value != {i}",
                priority=i,
            )
            system.register_constraint(constraint)

        # Test execution
        state = {"value": 1}
        results = system.execute_all_constraints(state)

        assert "execution_summary" in results
        assert "detailed_results" in results

        summary = results["execution_summary"]
        assert summary["total_constraints"] == 3
        assert (
            summary["satisfied_constraints"] == 1
        )  # Only TEST_EXEC_1 should be satisfied
        assert summary["violated_constraints"] == 2
        assert 0 <= summary["falsifiability_score"] <= 1

        # Check history
        assert len(system.verification_history) == 1

    def test_concrete_demonstration(self):
        """Test complete concrete demonstration"""
        system = MathematicalTheologyV60()
        results = system.create_concrete_demonstration()

        # Check structure
        assert "system_metadata" in results
        assert "mathematical_objects" in results
        assert "constraint_execution" in results
        assert "concrete_verifications" in results
        assert "popperian_analysis" in results

        # Check metadata
        metadata = results["system_metadata"]
        assert metadata["system_name"] == "Mathematical Theology V60"
        assert metadata["version"] == "1.0.0"
        assert metadata["immutable"] is True
        assert metadata["popperian"] is True
        assert metadata["concrete"] is True
        assert metadata["falsifiable"] is True

        # Check mathematical objects
        math_objs = results["mathematical_objects"]
        assert math_objs["space_dimension"] == 3
        assert math_objs["vectors_count"] == 4
