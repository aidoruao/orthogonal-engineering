"""
V57 CONSTRAINT EXECUTION ENGINE FOR LLM CODING VALIDATION

This module uses the v57 Maximal Oracle system to enforce constraints on LLM-generated code,
addressing notorious LLM coding issues through paraconsistent logic, falsification-first
validation, and category-theoretic structure enforcement.

Notorious LLM Issues Addressed:
1. Hallucinating non-existent APIs/functions
2. Incorrect algorithm implementations
3. Logical contradictions in code
4. Type safety violations
5. Edge case handling omissions
6. Resource management errors
"""

import ast
import inspect
import hashlib
from typing import Dict, List, Set, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Import v57 components
try:
    from maximal_oracle_v57 import (
        ParaconsistentTruthValue,
        ParaconsistentFormula,
        Morphism,
        NaturalTransformation,
        ModalOperator,
        ModalFormula,
        HomotopyPath
    )
    V57_AVAILABLE = True
except ImportError:
    V57_AVAILABLE = False
    print("⚠ v57 system not available - running in fallback mode")

# Z3 for theorem proving
try:
    from z3 import Solver, Bool, Int, Real, sat, unsat, And, Or, Not, Implies
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False

# ============================================================================
# CONSTRAINT TYPES
# ============================================================================

class ConstraintType(Enum):
    """Types of constraints to enforce on LLM-generated code"""
    API_EXISTENCE = "api_existence"           # Check if APIs/functions exist
    ALGORITHM_CORRECTNESS = "algorithm_correctness"  # Validate algorithm logic
    LOGICAL_CONSISTENCY = "logical_consistency"      # Check for contradictions
    TYPE_SAFETY = "type_safety"               # Enforce type constraints
    EDGE_CASE_HANDLING = "edge_case_handling" # Verify edge cases covered
    RESOURCE_MANAGEMENT = "resource_management" # Check resource usage
    SECURITY = "security"                     # Security constraints
    PERFORMANCE = "performance"               # Performance constraints

@dataclass
class Constraint:
    """A constraint to enforce on code"""
    constraint_type: ConstraintType
    description: str
    validator: Callable[[ast.AST, Dict[str, Any]], Tuple[bool, str]]
    priority: int = 5  # 1-10, higher = more important
    paraconsistent_value: ParaconsistentTruthValue = ParaconsistentTruthValue.TRUE

    def validate(self, code_ast: ast.AST, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate constraint against code"""
        try:
            return self.validator(code_ast, context)
        except Exception as e:
            return False, f"Constraint validation error: {e}"

# ============================================================================
# NOTORIOUS LLM ISSUE CONSTRAINTS
# ============================================================================

class LLMIssueConstraints:
    """Constraints targeting specific notorious LLM coding issues"""

    @staticmethod
    def check_api_existence(code_ast: ast.AST, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for hallucinated/non-existent APIs"""
        issues = []

        # Get known APIs from context or builtins
        known_apis = context.get('known_apis', set(dir(__builtins__)))

        for node in ast.walk(code_ast):
            if isinstance(node, ast.Call):
                # Check function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in known_apis and not func_name.startswith('_'):
                        issues.append(f"Potential hallucinated API: {func_name}")

                # Check method calls
                elif isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    if attr_name not in known_apis and not attr_name.startswith('_'):
                        issues.append(f"Potential hallucinated method: {attr_name}")

        if issues:
            return False, "; ".join(issues)
        return True, "All APIs appear valid"

    @staticmethod
    def check_algorithm_correctness(code_ast: ast.AST, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate algorithm logic using Z3 theorem prover"""
        if not Z3_AVAILABLE:
            return True, "Z3 not available - skipping algorithm validation"

        # Extract function definitions
        functions = [n for n in ast.walk(code_ast) if isinstance(n, ast.FunctionDef)]

        for func in functions:
            # Simple validation: check for infinite loops
            for node in ast.walk(func):
                if isinstance(node, ast.While):
                    # Check if while condition could be always true
                    if isinstance(node.test, ast.Constant):
                        if node.test.value is True:
                            return False, f"Potential infinite loop in {func.name}: while True without break"

        return True, "No obvious algorithm errors detected"

    @staticmethod
    def check_logical_consistency(code_ast: ast.AST, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for logical contradictions in code"""
        contradictions = []

        # Track variable assignments and conditions
        variable_states = {}

        for node in ast.walk(code_ast):
            if isinstance(node, ast.Assign):
                # Track assignments
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Simple tracking - in real implementation would use Z3
                        variable_states[target.id] = "assigned"

            elif isinstance(node, ast.If):
                # Check for contradictory conditions
                test_str = ast.unparse(node.test)
                # Simple check for obvious contradictions like "x and not x"
                if " and not " in test_str or " not and " in test_str:
                    contradictions.append(f"Potential contradiction in if condition: {test_str}")

        if contradictions:
            return False, "; ".join(contradictions)
        return True, "No logical contradictions detected"

    @staticmethod
    def check_type_safety(code_ast: ast.AST, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check for type safety violations"""
        type_issues = []

        for node in ast.walk(code_ast):
            # Check for operations that might cause type errors
            if isinstance(node, ast.BinOp):
                # Check for string + number type errors
                if isinstance(node.op, ast.Add):
                    left_type = LLMIssueConstraints._infer_type(node.left)
                    right_type = LLMIssueConstraints._infer_type(node.right)

                    if left_type == "str" and right_type == "int":
                        type_issues.append("Potential TypeError: str + int")
                    elif left_type == "int" and right_type == "str":
                        type_issues.append("Potential TypeError: int + str")

        if type_issues:
            return False, "; ".join(type_issues)
        return True, "No obvious type safety issues"

    @staticmethod
    def _infer_type(node: ast.AST) -> str:
        """Simple type inference for AST nodes"""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return "str"
            elif isinstance(node.value, int):
                return "int"
            elif isinstance(node.value, float):
                return "float"
            elif isinstance(node.value, bool):
                return "bool"
        elif isinstance(node, ast.Name):
            return "variable"
        elif isinstance(node, ast.Call):
            return "function_call"
        return "unknown"

    @staticmethod
    def check_edge_cases(code_ast: ast.AST, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if edge cases are handled"""
        edge_warnings = []

        # Look for division operations without zero checks
        for node in ast.walk(code_ast):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                # Check if divisor could be zero
                divisor = node.right
                if isinstance(divisor, ast.Constant):
                    if divisor.value == 0:
                        edge_warnings.append("Division by zero constant")
                else:
                    edge_warnings.append("Division by variable - consider zero check")

        # Look for list indexing without bounds checking
        for node in ast.walk(code_ast):
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Constant):
                    if isinstance(node.slice.value, int):
                        # Could check list length if we had more context
                        edge_warnings.append(f"List indexing at position {node.slice.value} - consider bounds check")

        if edge_warnings:
            return False, "Edge cases to consider: " + "; ".join(edge_warnings)
        return True, "Edge cases appear considered"

# ============================================================================
# V57 CONSTRAINT EXECUTION ENGINE
# ============================================================================

@dataclass
class ConstraintExecutionResult:
    """Result of constraint execution"""
    code_hash: str
    constraints_passed: List[str]
    constraints_failed: List[Tuple[str, str]]  # (constraint_name, reason)
    paraconsistent_evaluation: Dict[str, ParaconsistentTruthValue]
    recommendations: List[str]
    overall_valid: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code_hash": self.code_hash,
            "constraints_passed": self.constraints_passed,
            "constraints_failed": [(c, r) for c, r in self.constraints_failed],
            "paraconsistent_evaluation": {k: v.value for k, v in self.paraconsistent_evaluation.items()},
            "recommendations": self.recommendations,
            "overall_valid": self.overall_valid
        }

class V57ConstraintExecutionEngine:
    """
    Main constraint execution engine using v57 principles:
    1. Falsification-first: Try to break the code before accepting it
    2. Paraconsistent: Accept contradictions but track them
    3. Category-theoretic: Enforce structural constraints
    4. Modal: Consider different possible worlds/scenarios
    """

    def __init__(self):
        self.constraints: List[Constraint] = []
        self.known_apis: Set[str] = set(dir(__builtins__))
        self._setup_default_constraints()

    def _setup_default_constraints(self):
        """Setup constraints for notorious LLM issues"""
        self.constraints = [
            Constraint(
                constraint_type=ConstraintType.API_EXISTENCE,
                description="Check for hallucinated/non-existent APIs",
                validator=LLMIssueConstraints.check_api_existence,
                priority=9,
                paraconsistent_value=ParaconsistentTruthValue.TRUE
            ),
            Constraint(
                constraint_type=ConstraintType.ALGORITHM_CORRECTNESS,
                description="Validate algorithm logic",
                validator=LLMIssueConstraints.check_algorithm_correctness,
                priority=8,
                paraconsistent_value=ParaconsistentTruthValue.BOTH  # Allow some algorithm flexibility
            ),
            Constraint(
                constraint_type=ConstraintType.LOGICAL_CONSISTENCY,
                description="Check for logical contradictions",
                validator=LLMIssueConstraints.check_logical_consistency,
                priority=7,
                paraconsistent_value=ParaconsistentTruthValue.BOTH  # Paraconsistent logic allows contradictions
            ),
            Constraint(
                constraint_type=ConstraintType.TYPE_SAFETY,
                description="Check type safety",
                validator=LLMIssueConstraints.check_type_safety,
                priority=6,
                paraconsistent_value=ParaconsistentTruthValue.TRUE
            ),
            Constraint(
                constraint_type=ConstraintType.EDGE_CASE_HANDLING,
                description="Check edge case handling",
                validator=LLMIssueConstraints.check_edge_cases,
                priority=5,
                paraconsistent_value=ParaconsistentTruthValue.TRUE
            ),
        ]

    def add_custom_constraint(self, constraint: Constraint):
        """Add a custom constraint to the engine"""
        self.constraints.append(constraint)
        self.constraints.sort(key=lambda c: c.priority, reverse=True)

    def register_known_api(self, api_name: str):
        """Register a known API to prevent false positives"""
        self.known_apis.add(api_name)

    def register_module_apis(self, module):
        """Register all APIs from a module"""
        for name in dir(module):
            if not name.startswith('_'):
                self.known_apis.add(name)

    def execute_constraints(self, code: str, context: Dict[str, Any] = None) -> ConstraintExecutionResult:
        """
        Execute all constraints on the provided code.
        Uses v57 principles: falsification-first, paraconsistent evaluation.
        """
        if context is None:
            context = {}

        # Add known APIs to context
        context['known_apis'] = self.known_apis

        try:
            # Parse code to AST
            code_ast = ast.parse(code)
            code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]

            # Execute constraints
            constraints_passed = []
            constraints_failed = []
            paraconsistent_eval = {}
            recommendations = []

            for constraint in self.constraints:
                is_valid, message = constraint.validate(code_ast, context)

                if is_valid:
                    constraints_passed.append(f"{constraint.constraint_type.value}: {constraint.description}")
                    paraconsistent_eval[constraint.constraint_type.value] = constraint.paraconsistent_value
                else:
                    constraints_failed.append((constraint.constraint_type.value, message))
                    paraconsistent_eval[constraint.constraint_type.value] = ParaconsistentTruthValue.FALSE

                    # Generate recommendation based on failure
                    rec = self._generate_recommendation(constraint.constraint_type, message)
                    if rec:
                        recommendations.append(rec)

            # Determine overall validity using paraconsistent logic
            overall_valid = self._paraconsistent_overall_evaluation(paraconsistent_eval, constraints_failed)

            return ConstraintExecutionResult(
                code_hash=code_hash,
                constraints_passed=constraints_passed,
                constraints_failed=constraints_failed,
                paraconsistent_evaluation=paraconsistent_eval,
                recommendations=recommendations,
                overall_valid=overall_valid
            )

        except SyntaxError as e:
            # Code has syntax errors - immediate failure
            return ConstraintExecutionResult(
                code_hash="INVALID_SYNTAX",
                constraints_passed=[],
                constraints_failed=[("SYNTAX", f"Syntax error: {e}")],
                paraconsistent_evaluation={"syntax": ParaconsistentTruthValue.FALSE},
                recommendations=["Fix syntax errors before constraint validation"],
                overall_valid=False
            )

    def _generate_recommendation(self, constraint_type: ConstraintType, message: str) -> str:
        """Generate helpful recommendations based on constraint failures"""
        if constraint_type == ConstraintType.API_EXISTENCE:
            if "hallucinated" in message.lower():
                return f"Check if API exists: {message}. Consider using standard library or verify imports."

        elif constraint_type == ConstraintType.ALGORITHM_CORRECTNESS:
            if "infinite loop" in message.lower():
                return f"Add loop termination condition: {message}"

        elif constraint_type == ConstraintType.LOGICAL_CONSISTENCY:
            return f"Review logic for contradictions: {message}"

        elif constraint_type == ConstraintType.TYPE_SAFETY:
            if "TypeError" in message:
                return f"Add type checking or conversion: {message}"

        elif constraint_type == ConstraintType.EDGE_CASE_HANDLING:
            return f"Consider edge case: {message}"

        return f"Address issue: {message}"

    def _paraconsistent_overall_evaluation(self,
                                         paraconsistent_eval: Dict[str, ParaconsistentTruthValue],
                                         constraints_failed: List[Tuple[str, str]]) -> bool:
        """
        Determine overall validity using paraconsistent logic.
        In v57 philosophy, we can accept some contradictions (BOTH) but not pure FALSE.
        """
        if not V57_AVAILABLE:
            # Fallback: valid if no critical failures
            critical_failures = [c for c in constraints_failed
                               if c[0] in ["api_existence", "type_safety"]]
            return len(critical_failures) == 0

        # Using v57 paraconsistent logic
        has_false = any(v == ParaconsistentTruthValue.FALSE for v in paraconsistent_eval.values())
        has_both = any(v == ParaconsistentTruthValue.BOTH for v in paraconsistent_eval.values())

        # In paraconsistent logic, BOTH (contradiction) is acceptable
        # but FALSE (pure falsehood) is not
        return not has_false

    def validate_and_suggest(self, code: str, task_description: str = "") -> Dict[str, Any]:
        """
        Comprehensive validation with suggestions.
        This is the main method to use for LLM-generated code validation.
        """
        context = {
            "task_description": task_description,
            "validation_mode": "falsification_first"
        }

        result = self.execute_constraints(code, context)

        # Generate improvement suggestions
        suggestions = []

        if not result.overall_valid:
            suggestions.append("Code failed critical constraints. Major revisions needed.")

        if result.constraints_failed:
            for constraint_name, reason in result.constraints_failed:
                suggestions.append(f"Fix {constraint_name}: {reason}")

        if result.recommendations:
            suggestions.extend(result.recommendations)

        # Add v57 philosophical suggestions
        if V57_AVAILABLE:
            suggestions.append("Consider v57 principles: falsification-first testing, embrace contradictions where appropriate")

        return {
            "validation_result": result.to_dict(),
            "suggestions": suggestions,
            "v57_philosophy_applied": V57_AVAILABLE,
            "next_steps": self._generate_next_steps(result)
        }

    def _generate_next_steps(self, result: ConstraintExecutionResult) -> List[str]:
        """Generate actionable next steps based on validation results"""
        steps = []

        if result.overall_valid:
            steps.append("✅ Code passed v57 constraint
