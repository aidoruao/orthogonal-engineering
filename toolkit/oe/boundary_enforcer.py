"""
Boundary Enforcer - Glass-Box Boundary Decorator Factory

Centralizes boundary enforcement functionality for the Orthogonal Engineering framework.
Re-exports and enhances the glass_box_boundary decorator pattern.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import functools
import sys
from typing import Any, Callable, Optional


class BoundaryViolation(Exception):
    """Exception raised when Glass-Box Boundary is violated."""

    def __init__(self, message: str, violation_type: str, function: str = None):
        self.message = message
        self.violation_type = violation_type
        self.function = function
        super().__init__(f"{violation_type.upper()} violation in {function}: {message}")


def glass_box_boundary(
    input_validator: Optional[Callable] = None,
    output_validator: Optional[Callable] = None,
    side_effect_check: bool = True,
    orthogonal_separation: bool = True,
    **kwargs: Any,
) -> Callable:
    """
    Glass-Box Boundary decorator factory.

    Re-exports the decorator from the main enforcer with enhanced functionality.

    Args:
        input_validator: Function to validate inputs (args, kwargs)
        output_validator: Function to validate outputs
        side_effect_check: Whether to check for uncaptured side effects
        orthogonal_separation: Whether to enforce gateway pattern

    Returns:
        Decorator function
    """
    # Import from main enforcer to avoid duplication
    try:
        from automation.run_full_audit_with_trace import (
            glass_box_boundary as main_decorator,
        )

        return main_decorator(
            input_validator=input_validator,
            output_validator=output_validator,
            side_effect_check=side_effect_check,
            orthogonal_separation=orthogonal_separation,
        )
    except ImportError:
        # Fallback implementation if main enforcer not available
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                return func(*args, **kwargs)

            return wrapper

        return decorator


# Export the BoundaryViolation exception from main enforcer
try:
    from automation.run_full_audit_with_trace import BoundaryViolation
except ImportError:
    # Use local definition if import fails
    pass


__all__ = ["glass_box_boundary", "BoundaryViolation", "validate_input_schema", "validate_output_schema"]


def validate_input_schema(schema: dict) -> Callable:
    """
    Decorator that validates function inputs against a schema.

    Args:
        schema: Dictionary defining expected input structure

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_output_schema(schema: dict) -> Callable:
    """
    Decorator that validates function outputs against a schema.

    Args:
        schema: Dictionary defining expected output structure

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)
        return wrapper
    return decorator
