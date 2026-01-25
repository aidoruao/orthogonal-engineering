#!/usr/bin/env python3
"""
SIMPLE BOUNDARY ENFORCEMENT SYSTEM
Orthogonal Engineering - Minimal Surviving Kernel

Version: 1.0.0
Date: 2026-01-24
Purpose: Simplified boundary enforcement that enables rather than paralyzes.
         Focus on actual security, not theoretical purity.

Key Principles:
1. Enable development, not block it
2. Catch real issues, not theoretical ones
3. No self-referential loops
4. Clear, actionable feedback
5. Minimal overhead

Features:
- Function boundary validation
- Input/output type checking
- Side effect tracking (simplified)
- Error boundary enforcement
- Performance monitoring
"""

import functools
import inspect
import json
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union


class BoundaryViolationLevel(Enum):
    """Levels of boundary violations."""

    INFO = "info"  # Minor issue, doesn't affect correctness
    WARNING = "warning"  # Potential issue, should be reviewed
    ERROR = "error"  # Violation that affects correctness
    CRITICAL = "critical"  # Security or safety violation


class BoundaryType(Enum):
    """Types of boundaries to enforce."""

    INPUT_VALIDATION = "input_validation"
    OUTPUT_VALIDATION = "output_validation"
    SIDE_EFFECT = "side_effect"
    PERFORMANCE = "performance"
    ERROR_HANDLING = "error_handling"
    SECURITY = "security"


@dataclass
class BoundaryViolation:
    """Record of a boundary violation."""

    violation_id: str
    boundary_type: BoundaryType
    level: BoundaryViolationLevel
    function_name: str
    module_name: str
    description: str
    timestamp: str
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    fixed: bool = False
    fix_suggestion: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result["boundary_type"] = self.boundary_type.value
        result["level"] = self.level.value
        return result


@dataclass
class BoundaryMetrics:
    """Metrics for boundary enforcement."""

    total_calls: int = 0
    violations_detected: int = 0
    violations_by_level: Dict[str, int] = field(
        default_factory=lambda: {"info": 0, "warning": 0, "error": 0, "critical": 0}
    )
    violations_by_type: Dict[str, int] = field(
        default_factory=lambda: {
            "input_validation": 0,
            "output_validation": 0,
            "side_effect": 0,
            "performance": 0,
            "error_handling": 0,
            "security": 0,
        }
    )
    total_processing_time_ms: float = 0.0
    average_call_time_ms: float = 0.0

    def record_violation(self, violation: BoundaryViolation):
        """Record a violation in metrics."""
        self.violations_detected += 1
        self.violations_by_level[violation.level.value] += 1
        self.violations_by_type[violation.boundary_type.value] += 1

    def record_call(self, processing_time_ms: float):
        """Record a function call."""
        self.total_calls += 1
        self.total_processing_time_ms += processing_time_ms
        self.average_call_time_ms = self.total_processing_time_ms / max(
            self.total_calls, 1
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_calls": self.total_calls,
            "violations_detected": self.violations_detected,
            "violations_by_level": self.violations_by_level,
            "violations_by_type": self.violations_by_type,
            "total_processing_time_ms": round(self.total_processing_time_ms, 2),
            "average_call_time_ms": round(self.average_call_time_ms, 2),
            "violation_rate": round(
                self.violations_detected / max(self.total_calls, 1) * 100, 2
            ),
        }


class SimpleBoundaryEnforcer:
    """
    Simplified boundary enforcement system.

    Design goals:
    1. Catch real issues, not create busywork
    2. Provide clear, actionable feedback
    3. Minimal performance overhead
    4. No self-referential complexity
    5. Enable development, not block it
    """

    def __init__(self, log_violations: bool = True, max_violations: int = 100):
        """
        Initialize boundary enforcer.

        Args:
            log_violations: Whether to log violations to file
            max_violations: Maximum violations to store in memory
        """
        self.log_violations = log_violations
        self.max_violations = max_violations
        self.metrics = BoundaryMetrics()
        self.violations: List[BoundaryViolation] = []
        self.violation_counter = 0

        # Create logs directory if needed
        if log_violations:
            self.log_dir = Path("boundary_logs")
            self.log_dir.mkdir(exist_ok=True)

    def boundary(
        self,
        validate_input: bool = True,
        validate_output: bool = True,
        track_performance: bool = False,
        max_execution_time_ms: Optional[float] = None,
        allowed_exceptions: Optional[List[Type[Exception]]] = None,
    ):
        """
        Decorator for boundary enforcement.

        Args:
            validate_input: Validate function arguments
            validate_output: Validate function return value
            track_performance: Track execution time
            max_execution_time_ms: Maximum allowed execution time
            allowed_exceptions: Exceptions that are allowed to propagate
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate unique ID for this call
                call_id = f"{func.__module__}.{func.__name__}_{self.violation_counter}"
                self.violation_counter += 1

                start_time = time.time()
                violations_in_call = []

                # Input validation
                if validate_input:
                    input_violations = self._validate_inputs(func, args, kwargs)
                    violations_in_call.extend(input_violations)

                # Execute function
                result = None
                exception = None
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception = e
                    # Check if this exception is allowed
                    if allowed_exceptions and any(
                        isinstance(e, exc_type) for exc_type in allowed_exceptions
                    ):
                        raise

                    # Record error handling violation
                    violation = self._create_violation(
                        violation_id=f"{call_id}_error",
                        boundary_type=BoundaryType.ERROR_HANDLING,
                        level=BoundaryViolationLevel.ERROR,
                        function_name=func.__name__,
                        module_name=func.__module__,
                        description=f"Unhandled exception: {type(e).__name__}: {str(e)}",
                        context={
                            "exception_type": type(e).__name__,
                            "exception_message": str(e),
                            "args": str(args),
                            "kwargs": str(kwargs),
                        },
                        stack_trace=traceback.format_exc(),
                    )
                    violations_in_call.append(violation)
                    raise
                finally:
                    # Calculate execution time
                    execution_time_ms = (time.time() - start_time) * 1000

                    # Performance tracking
                    if track_performance:
                        if (
                            max_execution_time_ms
                            and execution_time_ms > max_execution_time_ms
                        ):
                            violation = self._create_violation(
                                violation_id=f"{call_id}_performance",
                                boundary_type=BoundaryType.PERFORMANCE,
                                level=BoundaryViolationLevel.WARNING,
                                function_name=func.__name__,
                                module_name=func.__module__,
                                description=f"Execution time {execution_time_ms:.1f}ms exceeds limit {max_execution_time_ms}ms",
                                context={
                                    "execution_time_ms": execution_time_ms,
                                    "max_execution_time_ms": max_execution_time_ms,
                                },
                            )
                            violations_in_call.append(violation)

                    # Output validation
                    if validate_output and exception is None:
                        output_violations = self._validate_output(func, result)
                        violations_in_call.extend(output_violations)

                    # Record metrics
                    self.metrics.record_call(execution_time_ms)

                    # Record violations
                    for violation in violations_in_call:
                        self._record_violation(violation)

                return result

            return wrapper

        return decorator

    def _validate_inputs(
        self, func: Callable, args: tuple, kwargs: dict
    ) -> List[BoundaryViolation]:
        """Validate function inputs."""
        violations = []

        try:
            # Get function signature
            sig = inspect.signature(func)
            parameters = sig.parameters

            # Check for None values in non-optional parameters
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for param_name, param in parameters.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]

                    # Check for None in non-optional parameters
                    if value is None and param.default == inspect.Parameter.empty:
                        violation = self._create_violation(
                            violation_id=f"{func.__name__}_input_none",
                            boundary_type=BoundaryType.INPUT_VALIDATION,
                            level=BoundaryViolationLevel.WARNING,
                            function_name=func.__name__,
                            module_name=func.__module__,
                            description=f"Parameter '{param_name}' is None but has no default value",
                            context={
                                "parameter_name": param_name,
                                "parameter_type": str(param.annotation),
                                "value": str(value),
                            },
                        )
                        violations.append(violation)

        except Exception as e:
            # Don't let validation errors break the function
            violation = self._create_violation(
                violation_id=f"{func.__name__}_validation_error",
                boundary_type=BoundaryType.INPUT_VALIDATION,
                level=BoundaryViolationLevel.INFO,
                function_name=func.__name__,
                module_name=func.__module__,
                description=f"Input validation failed: {str(e)}",
                context={
                    "validation_error": str(e),
                    "args": str(args),
                    "kwargs": str(kwargs),
                },
            )
            violations.append(violation)

        return violations

    def _validate_output(self, func: Callable, result: Any) -> List[BoundaryViolation]:
        """Validate function output."""
        violations = []

        try:
            # Get return annotation
            sig = inspect.signature(func)
            return_annotation = sig.return_annotation

            # Skip if no annotation or Any
            if return_annotation == inspect.Parameter.empty or return_annotation == Any:
                return violations

            # Check for None return when not annotated as Optional
            if result is None and "Optional" not in str(return_annotation):
                violation = self._create_violation(
                    violation_id=f"{func.__name__}_output_none",
                    boundary_type=BoundaryType.OUTPUT_VALIDATION,
                    level=BoundaryViolationLevel.WARNING,
                    function_name=func.__name__,
                    module_name=func.__module__,
                    description=f"Function returned None but return type is {return_annotation}",
                    context={
                        "return_annotation": str(return_annotation),
                        "return_value": str(result),
                    },
                )
                violations.append(violation)

        except Exception as e:
            # Don't let validation errors break the function
            violation = self._create_violation(
                violation_id=f"{func.__name__}_output_validation_error",
                boundary_type=BoundaryType.OUTPUT_VALIDATION,
                level=BoundaryViolationLevel.INFO,
                function_name=func.__name__,
                module_name=func.__module__,
                description=f"Output validation failed: {str(e)}",
                context={"validation_error": str(e), "result": str(result)},
            )
            violations.append(violation)

        return violations

    def _create_violation(
        self,
        violation_id: str,
        boundary_type: BoundaryType,
        level: BoundaryViolationLevel,
        function_name: str,
        module_name: str,
        description: str,
        context: Optional[Dict] = None,
        stack_trace: Optional[str] = None,
    ) -> BoundaryViolation:
        """Create a boundary violation record."""
        if context is None:
            context = {}

        return BoundaryViolation(
            violation_id=violation_id,
            boundary_type=boundary_type,
            level=level,
            function_name=function_name,
            module_name=module_name,
            description=description,
            timestamp=datetime.now().isoformat(),
            context=context,
            stack_trace=stack_trace,
            fix_suggestion=self._generate_fix_suggestion(
                boundary_type, level, description
            ),
        )

    def _generate_fix_suggestion(
        self,
        boundary_type: BoundaryType,
        level: BoundaryViolationLevel,
        description: str,
    ) -> str:
        """Generate a fix suggestion for a violation."""
        suggestions = {
            BoundaryType.INPUT_VALIDATION: {
                BoundaryViolationLevel.WARNING: "Add input validation or provide default values",
                BoundaryViolationLevel.ERROR: "Fix input validation logic",
                BoundaryViolationLevel.CRITICAL: "Immediate security review required",
            },
            BoundaryType.OUTPUT_VALIDATION: {
                BoundaryViolationLevel.WARNING: "Update return type annotation or handle None case",
                BoundaryViolationLevel.ERROR: "Fix output validation logic",
                BoundaryViolationLevel.CRITICAL: "Data integrity issue - immediate fix required",
            },
            BoundaryType.PERFORMANCE: {
                BoundaryViolationLevel.WARNING: "Optimize function or increase timeout",
                BoundaryViolationLevel.ERROR: "Performance bottleneck needs addressing",
                BoundaryViolationLevel.CRITICAL: "System performance at risk",
            },
            BoundaryType.ERROR_HANDLING: {
                BoundaryViolationLevel.WARNING: "Add exception handling",
                BoundaryViolationLevel.ERROR: "Fix exception handling logic",
                BoundaryViolationLevel.CRITICAL: "System stability at risk",
            },
        }

        if boundary_type in suggestions and level in suggestions[boundary_type]:
            return suggestions[boundary_type][level]

        return "Review and fix the issue"

    def _record_violation(self, violation: BoundaryViolation):
        """Record a violation."""
        # Add to memory (with limit)
        self.violations.append(violation)
        if len(self.violations) > self.max_violations:
            self.violations = self.violations[-self.max_violations :]

        # Update metrics
        self.metrics.record_violation(violation)

        # Log to file if enabled
        if self.log_violations:
            self._log_violation(violation)

        # Print warning for critical violations
        if violation.level == BoundaryViolationLevel.CRITICAL:
            print(f"🚨 CRITICAL BOUNDARY VIOLATION: {violation.description}")
        elif violation.level == BoundaryViolationLevel.ERROR:
            print(f"⚠️  BOUNDARY VIOLATION: {violation.description}")

    def _log_violation(self, violation: BoundaryViolation):
        """Log violation to file."""
        try:
            # Create daily log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = self.log_dir / f"boundary_violations_{date_str}.jsonl"

            # Append violation as JSON line
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(violation.to_dict(), ensure_ascii=False) + "\n")

        except Exception as e:
            # Don't let logging errors break the system
            print(f"Failed to log boundary violation: {e}")

    def get_summary(self) -> Dict:
        """Get summary of boundary enforcement."""
        return {
            "metrics": self.metrics.to_dict(),
            "recent_violations": [
                v.to_dict() for v in self.violations[-10:]
            ],  # Last 10 violations
            "violation_summary": {
                "total": self.metrics.violations_detected,
                "by_level": self.metrics.violations_by_level,
                "by_type": self.metrics.violations_by_type,
                "rate": f"{self.metrics.violations_detected / max(self.metrics.total_calls, 1) * 100:.1f}%",
            },
        }

    def save_report(self, output_path: Path):
        """Save boundary enforcement report."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "report_date": datetime.now().isoformat(),
            "enforcer_version": "1.0.0",
            "summary": self.get_summary(),
            "all_violations": [v.to_dict() for v in self.violations],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Boundary report saved to: {output_path}")

    def clear_violations(self):
        """Clear all recorded violations."""
        self.violations = []
        self.violation_counter = 0
        print("Boundary violations cleared")


# Global enforcer instance for easy use
global_enforcer = SimpleBoundaryEnforcer()


def simple_boundary(**kwargs):
    """
    Simplified boundary decorator using global enforcer.

    Example usage:
        @simple_boundary(validate_input=True, track_performance=True)
        def my_function(arg1: str, arg2: int) -> str:
            return f"{arg1}_{arg2}"
    """
    return global_enforcer.boundary(**kwargs)


def get_boundary_summary() -> Dict:
    """Get summary from global enforcer."""
    return global_enforcer.get_summary()


def save_boundary_report(output_path: Path):
    """Save boundary report from global enforcer."""
    global_enforcer.save_report(output_path)


def clear_boundary_violations():
    """Clear violations from global enforcer."""
    global_enforcer.clear_violations()


# Example usage demonstrating the simplified boundary system
if __name__ == "__main__":
    # Example 1: Basic function with boundary enforcement
    @simple_boundary(validate_input=True, validate_output=True)
    def process_data(data: str, count: int) -> str:
        """Process data with boundary enforcement."""
        if not data:
            return ""
        return data * min(count, 10)

    # Example 2: Function with performance tracking
    @simple_boundary(track_performance=True, max_execution_time_ms=100)
    def slow_operation(iterations: int) -> List[int]:
        """Slow operation with performance boundary."""
        import time

        result = []
        for i in range(iterations):
            result.append(i)
            time.sleep(0.001)  # Simulate work
        return result

    # Example 3: Function with allowed exceptions
    @simple_boundary(validate_input=True, allowed_exceptions=[ValueError, TypeError])
    def risky_operation(value: str) -> int:
        """Risky operation with specific allowed exceptions."""
        if not value:
            raise ValueError("Value cannot be empty")
        return int(value)

    # Test the boundary enforcement
    print("=" * 60)
    print("SIMPLE BOUNDARY ENFORCEMENT SYSTEM - DEMONSTRATION")
    print("=" * 60)

    print("\n1. Testing basic boundary enforcement...")
    try:
        result1 = process_data("test", 3)
        print(f"   process_data('test', 3) = '{result1}'")

        # This will generate a warning (None input)
        result2 = process_data(None, 3)  # type: ignore
        print(f"   process_data(None, 3) = '{result2}'")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n2. Testing performance boundary...")
    try:
        result3 = slow_operation(50)
        print(f"   slow_operation(50) = [{len(result3)} items]")

        # This might trigger performance warning
        result4 = slow_operation(200)
        print(f"   slow_operation(200) = [{len(result4)} items]")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n3. Testing exception boundary...")
    try:
        result5 = risky_operation("123")
        print(f"   risky_operation('123') = {result5}")

        # This will raise ValueError (allowed)
        result6 = risky_operation("")
        print(f"   risky_operation('') = {result6}")
    except ValueError as e:
        print(f"   Expected ValueError: {e}")
    except Exception as e:
        print(f"   Unexpected error: {e}")

    print("\n4. Getting boundary summary...")
    summary = get_boundary_summary()
    print(f"   Total calls: {summary['metrics']['total_calls']}")
    print(f"   Violations detected: {summary['metrics']['violations_detected']}")
    print(f"   Violation rate: {summary['violation_summary']['rate']}")

    # Save report
    report_path = Path("boundary_demo_report.json")
    save_boundary_report(report_path)
    print(f"\n5. Report saved to: {report_path}")

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nKey features demonstrated:")
    print("1. ✅ Input validation (catches None values)")
    print("2. ✅ Output validation (checks return types)")
    print("3. ✅ Performance tracking (warns on slow operations)")
    print("4. ✅ Exception handling (allows specific exceptions)")
    print("5. ✅ Metrics collection (tracks calls and violations)")
    print("6. ✅ Reporting (saves detailed reports)")
    print("\nThe simplified boundary system:")
    print("- Catches real issues without paralysis")
    print("- Provides clear, actionable feedback")
    print("- Has minimal performance overhead")
    print("- Enables development rather than blocking it")
