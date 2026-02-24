# pr44_orthogonal_meta/closure/verify_closure.py
# PR #44 — Orthogonal Meta Parallel
# Standard: Yeshua
#
# Closure verifier: ensures the system satisfies all closure conditions.
#   - No float literals or float type references
#   - No randomness imports
#   - No impure functions (no 'global' mutation)
#
# System closed. No unresolved axiom. No stochastic residue.

from __future__ import annotations

import ast
import inspect
from types import ModuleType
from typing import List

FORBIDDEN_NAMES: List[str] = ["float", "Float", "random", "stochastic", "probabilistic"]
FORBIDDEN_IMPORTS: List[str] = ["random", "stochastic", "probabilistic", "sample"]


def verify_no_floating_point(source: str) -> bool:
    """
    Verify source contains no float literals and no float type references.
    Raises ValueError on violation.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        # Float literal
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            raise ValueError(f"Floating point literal forbidden: {node.value!r}")
        # Name 'float' or 'Float'
        if isinstance(node, ast.Name) and node.id in ("float", "Float"):
            raise ValueError(f"Float type reference forbidden: {node.id!r}")
    return True


def verify_no_randomness(source: str) -> bool:
    """
    Verify source contains no randomness-related imports.
    Raises ValueError on violation.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(f in alias.name for f in FORBIDDEN_IMPORTS):
                    raise ValueError(f"Stochastic import forbidden: {alias.name!r}")
        if isinstance(node, ast.ImportFrom):
            if node.module and any(f in node.module for f in FORBIDDEN_IMPORTS):
                raise ValueError(f"Stochastic import forbidden: {node.module!r}")
    return True


def verify_pure_functions(module: ModuleType) -> bool:
    """
    Verify that all functions in module are pure (no global mutation).
    Raises ValueError if any function modifies global state.
    """
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        try:
            source = inspect.getsource(obj)
        except (OSError, TypeError):
            continue
        if "global " in source:
            raise ValueError(f"Impure function (global mutation): {name!r}")
    return True


def verify_no_forbidden(source: str) -> bool:
    """
    Legacy entry-point: check for 'float' and 'random' name references.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in ("float", "random"):
            raise ValueError(f"Forbidden construct detected: {node.id!r}")
    return True
