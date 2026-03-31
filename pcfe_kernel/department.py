"""
pcfe_kernel/department.py — Department dataclass + registry.

Each Department is a typed rule-space overlay on the core kernel loop.
It feeds into the existing OrthoKernel loop at a specific injection point.

Kernel Injection Points:
    state_input       → populates OrthoState.manifest (D_bio, D_sense, D_train)
    action_constraint → filters SigmaTheoOperators (D_chem)
    rule_filter       → constrains OrthoKernel.transition() (D_fdacs)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Department:
    """Typed rule-space overlay on the core kernel loop.

    Each department injects domain knowledge at a specific point in:
        S → R → A → S' → O → H → F*

    Attributes:
        id:                 Unique identifier, e.g. "D_bio", "D_chem".
        name:               Human-readable name.
        ontology:           Structured domain data (not prose).
        constraint_keys:    Maps to covenant.yaml constraint IDs.
        kernel_role:        One of "state_input", "action_constraint",
                            or "rule_filter".
        falsification_ids:  Maps to ontology/falsification_tests.json IDs.
    """

    id: str
    name: str
    ontology: Dict[str, Any]
    constraint_keys: List[str]
    kernel_role: str
    falsification_ids: List[str]

    def __post_init__(self) -> None:
        valid_roles = {"state_input", "action_constraint", "rule_filter"}
        if self.kernel_role not in valid_roles:
            raise ValueError(
                f"Department {self.id!r}: kernel_role must be one of "
                f"{sorted(valid_roles)}, got {self.kernel_role!r}"
            )

    def is_action_allowed(self, action: str) -> bool:
        """Return True iff action is not blocked by this department's ontology.

        For action-constraint departments (D_chem), the ontology includes a
        "prohibited_actions" list.  Any other department always returns True.
        """
        if self.kernel_role != "action_constraint":
            return True
        prohibited: List[str] = self.ontology.get("prohibited_actions", [])
        return action not in prohibited

    def manifest_entries(self) -> List[str]:
        """Return domain manifest strings for state injection.

        For state-input departments (D_bio, D_sense, D_train), the ontology
        includes an "entities" list whose items are injected into
        OrthoState.manifest.
        """
        if self.kernel_role != "state_input":
            return []
        return list(self.ontology.get("entities", []))

    def rule_keys(self) -> List[str]:
        """Return hard-constraint rule keys for rule-filter departments.

        For rule-filter departments (D_fdacs), returns constraint_keys that
        must all be satisfied before OrthoKernel.transition() is accepted.
        """
        if self.kernel_role != "rule_filter":
            return []
        return list(self.constraint_keys)


class DepartmentRegistry:
    """Registry of all active departments for a PCFE kernel session.

    Usage::

        registry = DepartmentRegistry()
        registry.register(D_BIO)
        registry.register(D_CHEM)
        dept = registry.get("D_bio")
    """

    def __init__(self) -> None:
        self._departments: Dict[str, Department] = {}

    def register(self, dept: Department) -> None:
        """Register a department. Raises ValueError on ID collision."""
        if dept.id in self._departments:
            raise ValueError(f"Department {dept.id!r} is already registered.")
        self._departments[dept.id] = dept

    def get(self, dept_id: str) -> Department:
        """Retrieve a department by ID. Raises KeyError if not found."""
        if dept_id not in self._departments:
            raise KeyError(f"No department registered with id={dept_id!r}")
        return self._departments[dept_id]

    def all(self) -> List[Department]:
        """Return all registered departments in registration order."""
        return list(self._departments.values())

    def by_role(self, role: str) -> List[Department]:
        """Return all departments with the given kernel_role."""
        return [d for d in self._departments.values() if d.kernel_role == role]

    def all_manifest_entries(self) -> List[str]:
        """Aggregate manifest entries from every state-input department."""
        entries: List[str] = []
        for dept in self.by_role("state_input"):
            entries.extend(dept.manifest_entries())
        return entries

    def is_action_allowed(self, action: str) -> bool:
        """Return True iff no action-constraint department blocks the action."""
        for dept in self.by_role("action_constraint"):
            if not dept.is_action_allowed(action):
                return False
        return True
