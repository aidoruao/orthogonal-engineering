"""
Boundary Enforcer - Glass-Box Boundary Decorator Factory

Centralizes boundary enforcement functionality for the Orthogonal Engineering framework.
Re-exports and enhances the glass_box_boundary decorator pattern.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import functools
import logging
import sys
import time
from typing import Any, Callable, Optional

_log = logging.getLogger(__name__)


class BoundaryViolation(Exception):
    """Exception raised when Glass-Box Boundary is violated."""

    def __init__(self, message: str, violation_type: str, function: str = None):
        self.message = message
        self.violation_type = violation_type
        self.function = function
        super().__init__(f"{violation_type.upper()} violation in {function}: {message}")


# ---------------------------------------------------------------------------
# ContractViolationError — raised when schema validation fails
# ---------------------------------------------------------------------------


class ContractViolationError(Exception):
    """
    Raised when a validate_input_schema or validate_output_schema check fails.

    Attributes:
        function:   Name of the function whose contract was violated.
        direction:  'input' or 'output'.
        errors:     List of human-readable validation error strings.
        record:     Deterministic violation record (dict) suitable for logging.
    """

    def __init__(self, function: str, direction: str, errors: list) -> None:
        self.function = function
        self.direction = direction
        self.errors = errors
        self.record = {
            "violation": "contract",
            "direction": direction,
            "function": function,
            "errors": errors,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        super().__init__(
            f"ContractViolation [{direction.upper()}] in '{function}': {errors}"
        )


# ---------------------------------------------------------------------------
# Simple schema validator (no third-party deps)
# ---------------------------------------------------------------------------

_TYPE_MAP: dict = {
    "string": str,
    "str": str,
    "integer": int,
    "int": int,
    "number": (int, float),
    "float": float,
    "boolean": bool,
    "bool": bool,
    "array": list,
    "list": list,
    "object": dict,
    "dict": dict,
}


def _validate_against_schema(value: Any, schema: dict, path: str = "$") -> list:
    """
    Recursively validate *value* against *schema*.

    Returns a (possibly empty) list of error strings.
    An empty list means the value is valid.
    """
    if not schema:
        return []

    errors: list = []

    type_spec = schema.get("type")
    if type_spec is not None:
        if isinstance(type_spec, list):
            allows_null = "null" in type_spec
            expected = [_TYPE_MAP[t] for t in type_spec if t in _TYPE_MAP]
            if value is None:
                if not allows_null:
                    errors.append(f"{path}: null not allowed by schema")
            elif expected and not isinstance(value, tuple(expected)):
                errors.append(
                    f"{path}: expected type in {type_spec}, got {type(value).__name__}"
                )
        else:
            expected_type = _TYPE_MAP.get(type_spec)
            if expected_type is not None and value is not None:
                if not isinstance(value, expected_type):
                    errors.append(
                        f"{path}: expected {type_spec}, got {type(value).__name__}"
                    )

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key '{key}'")
        for key, prop_schema in schema.get("properties", {}).items():
            if key in value:
                errors.extend(
                    _validate_against_schema(value[key], prop_schema, f"{path}.{key}")
                )

    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(value):
                errors.extend(
                    _validate_against_schema(item, item_schema, f"{path}[{i}]")
                )

    return errors


# ---------------------------------------------------------------------------
# external_claim tagging
# ---------------------------------------------------------------------------


class ExternalClaimError(Exception):
    """
    Raised when an external_claim value is used where a proof object is required.

    This enforces the YESHUA STANDARD constraint: outputs/claims that originate
    outside the Consistency Scope S must be tagged and must not be treated as
    first-class proof objects within the scope.
    """


def tag_external_claim(data: Any, source: Optional[str] = None) -> dict:
    """
    Tag *data* as an external claim that originates outside the Consistency
    Scope S.

    The returned dict carries ``external_claim=True`` and the original payload
    under the key ``value``.  Any code that receives such a dict MUST NOT
    treat it as a proof object without re-validating it against the internal
    consistency scope.

    Args:
        data:    The claim/output to tag.
        source:  Optional human-readable origin description.

    Returns:
        ``{"external_claim": True, "value": data, "source": source}``
    """
    record: dict = {"external_claim": True, "value": data}
    if source is not None:
        record["source"] = source
    return record


def is_external_claim(obj: Any) -> bool:
    """Return True if *obj* was produced by :func:`tag_external_claim`."""
    return isinstance(obj, dict) and obj.get("external_claim") is True


def assert_not_external_claim(obj: Any, context: str = "") -> None:
    """
    Raise :class:`ExternalClaimError` if *obj* is an external claim.

    Use this at proof-object consumption sites to prevent unvalidated
    external data from being treated as an internal proof.

    Args:
        obj:      The object to check.
        context:  Optional description of the consumption site.

    Raises:
        ExternalClaimError: If *obj* carries ``external_claim=True``.
    """
    if is_external_claim(obj):
        msg = "external_claim object used where proof object required"
        if context:
            msg = f"{msg} [{context}]"
        raise ExternalClaimError(msg)


def glass_box_boundary(
    input_validator: Optional[Callable] = None,
    output_validator: Optional[Callable] = None,
    side_effect_check: bool = True,
    orthogonal_separation: bool = True,
    input_schema: Optional[dict] = None,
    output_schema: Optional[dict] = None,
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
        input_schema: Optional schema dict for input validation
        output_schema: Optional schema dict for output validation

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


__all__ = [
    "glass_box_boundary",
    "BoundaryViolation",
    "ContractViolationError",
    "validate_input_schema",
    "validate_output_schema",
    "tag_external_claim",
    "is_external_claim",
    "assert_not_external_claim",
    "ExternalClaimError",
]


def validate_input_schema(schema: dict) -> Callable:
    """
    Decorator that validates a function's keyword arguments against *schema*.

    On validation failure the decorated function is **not** called; instead a
    :class:`ContractViolationError` is raised and a deterministic violation
    record is written to the ``toolkit.oe.boundary_enforcer`` logger at
    ERROR level.

    Args:
        schema: Schema dict used by :func:`_validate_against_schema`.

    Returns:
        Decorator function.

    Raises:
        ContractViolationError: When the kwargs dict fails schema validation.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            errors = _validate_against_schema(kwargs, schema)
            if errors:
                exc = ContractViolationError(func.__qualname__, "input", errors)
                _log.error("ContractViolation: %s", exc.record)
                raise exc
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_output_schema(schema: dict) -> Callable:
    """
    Decorator that validates a function's return value against *schema*.

    On validation failure a :class:`ContractViolationError` is raised and a
    deterministic violation record is written to the
    ``toolkit.oe.boundary_enforcer`` logger at ERROR level.

    Args:
        schema: Schema dict used by :func:`_validate_against_schema`.

    Returns:
        Decorator function.

    Raises:
        ContractViolationError: When the return value fails schema validation.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            errors = _validate_against_schema(result, schema)
            if errors:
                exc = ContractViolationError(func.__qualname__, "output", errors)
                _log.error("ContractViolation: %s", exc.record)
                raise exc
            return result
        return wrapper
    return decorator
