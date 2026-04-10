"""Logos IDE Formal Specification — Fixed-Point Rendering Pipeline

Every UI state transition returns ProofObject.
Deterministic layout (no floating point in layout math).
Capability-gated editor actions (EditCap, ViewCap, DebugCap).

Mathematical foundation: Fixed-point arithmetic (Fraction-based).
Standard: IEEE 754 excluded — all coordinates are Fractions.
Biblical: Colossians 1:17 — "In him all things hold together."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict, Any, FrozenSet
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from axioms.capability_security import Capability, Permission


class ComponentType(Enum):
    """Types of UI components."""
    EDITOR = auto()       # Code editor pane
    TERMINAL = auto()     # Terminal/output pane
    FILE_TREE = auto()    # File explorer
    STATUS_BAR = auto()   # Status display
    MENU_BAR = auto()     # Menu bar
    DIALOG = auto()       # Modal dialog
    TOOLBAR = auto()      # Tool buttons


class LayoutConstraint(Enum):
    """Layout constraint types (all Fraction-based)."""
    FIXED_WIDTH = auto()      # Exact width in pixels (Fraction)
    FIXED_HEIGHT = auto()     # Exact height in pixels (Fraction)
    MIN_WIDTH = auto()        # Minimum width
    MIN_HEIGHT = auto()       # Minimum height
    MAX_WIDTH = auto()        # Maximum width
    MAX_HEIGHT = auto()       # Maximum height
    ASPECT_RATIO = auto()     # Width/height ratio as Fraction
    PERCENT_WIDTH = auto()    # Percentage of parent width
    PERCENT_HEIGHT = auto()   # Percentage of parent height


@dataclass(frozen=True)
class FractionalRect:
    """Rectangle using Fraction coordinates (no floats).
    
    x, y: Top-left corner
    width, height: Dimensions
    All values are Fractions for deterministic precision.
    """
    x: Fraction
    y: Fraction
    width: Fraction
    height: Fraction
    
    def contains_point(self, px: Fraction, py: Fraction) -> bool:
        """Check if point is inside rect."""
        return (
            self.x <= px < self.x + self.width and
            self.y <= py < self.y + self.height
        )
    
    def intersects(self, other: FractionalRect) -> bool:
        """Check if this rect intersects another."""
        return not (
            self.x + self.width <= other.x or
            other.x + other.width <= self.x or
            self.y + self.height <= other.y or
            other.y + other.height <= self.y
        )


@dataclass(frozen=True)
class LayoutConstraintSpec:
    """A single layout constraint with Fraction value."""
    constraint_type: LayoutConstraint
    value: Fraction  # Constraint value (never float)


@dataclass
class UIComponent:
    """A single UI component with Fraction-based layout.
    
    All positioning uses Fraction arithmetic for determinism.
    No floating point anywhere in layout calculations.
    """
    component_id: str
    component_type: ComponentType
    
    # Layout (all Fractions)
    bounds: FractionalRect
    constraints: Tuple[LayoutConstraintSpec, ...]
    
    # Content
    content_hash: str  # Content-addressed
    content_type: str  # MIME type equivalent
    
    # State
    is_visible: bool
    is_enabled: bool
    is_focused: bool
    z_index: int
    
    # Children (tree structure)
    children: Tuple[str, ...] = field(default_factory=tuple)  # Child component IDs
    parent_id: Optional[str] = None
    
    def get_area(self) -> Fraction:
        """Calculate component area (Fraction)."""
        return self.bounds.width * self.bounds.height


@dataclass
class EditCap:
    """Capability for editor actions.
    
    Grants permission to:
    - Modify content (WRITE)
    - Save files (WRITE)
    - Execute commands (EXECUTE)
    - Delegate to others (DELEGATE)
    """
    editor_id: str
    holder_id: str
    permissions: frozenset
    delegator: str
    file_paths: FrozenSet[str]  # Which files can be edited
    
    def can_edit_file(self, path: str) -> bool:
        """Check if capability allows editing specific file."""
        return path in self.file_paths
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions


@dataclass
class ViewCap:
    """Capability for view actions.
    
    Grants permission to:
    - View content (READ)
    - Navigate (READ)
    - Search (READ)
    """
    view_id: str
    holder_id: str
    permissions: frozenset
    delegator: str
    view_scope: str  # "file", "project", "workspace"
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions


@dataclass
class DebugCap:
    """Capability for debug actions.
    
    Grants permission to:
    - Set breakpoints (WRITE)
    - Step execution (EXECUTE)
    - Inspect variables (READ)
    - Modify memory (WRITE)
    """
    debug_session_id: str
    holder_id: str
    permissions: frozenset
    delegator: str
    target_process: str
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        return perm in self.permissions


@dataclass
class UIState:
    """Complete UI state snapshot.
    
    State is content-addressed: hash of all components
defines the complete UI state.
    """
    components: Dict[str, UIComponent]
    root_component_id: str
    focused_component_id: Optional[str]
    
    # Viewport (all Fractions)
    viewport_width: Fraction
    viewport_height: Fraction
    dpi_scale: Fraction  # e.g., 2 for Retina (never float)
    
    # History for undo/redo
    undo_stack: Tuple[str, ...] = field(default_factory=tuple)  # State hashes
    redo_stack: Tuple[str, ...] = field(default_factory=tuple)
    
    def compute_state_hash(self) -> str:
        """Compute content-addressed hash of this state."""
        import hashlib
        # Deterministic serialization
        components_str = "|".join(
            f"{cid}:{comp.content_hash}"
            for cid, comp in sorted(self.components.items())
        )
        state_input = f"{components_str}:{self.focused_component_id}:{self.viewport_width}:{self.viewport_height}"
        return hashlib.sha256(state_input.encode()).hexdigest()
    
    def get_component_at(self, x: Fraction, y: Fraction) -> Optional[UIComponent]:
        """Get component at fractional coordinates."""
        # Search in reverse z-order (top first)
        sorted_components = sorted(
            self.components.values(),
            key=lambda c: c.z_index,
            reverse=True
        )
        for comp in sorted_components:
            if comp.is_visible and comp.bounds.contains_point(x, y):
                return comp
        return None


def transition_state(
    current_state: UIState,
    action: str,
    action_params: Dict[str, Any],
    capability: Any,  # EditCap, ViewCap, or DebugCap
    timestamp: Fraction
) -> Tuple[UIState, ProofObject]:
    """Execute a UI state transition.
    
    Every transition returns a ProofObject witness.
    All coordinates and dimensions use Fraction (no float).
    
    Args:
        current_state: Current UI state
        action: Action type ("focus", "edit", "resize", etc.)
        action_params: Action parameters (all Fraction or str)
        capability: Capability authorizing this action
        timestamp: Transition timestamp
        
    Returns:
        (new_state, proof)
    """
    # Verify capability
    if hasattr(capability, 'has_permission'):
        if not capability.has_permission(Permission.WRITE) and action in ("edit", "save", "modify"):
            return current_state, ProofObject(
                rule="UIStateTransition",
                premises=[
                    f"action={action}",
                    f"capability={type(capability).__name__}"
                ],
                conclusion="transition denied: no WRITE permission"
            )
    
    # Execute transition based on action type
    if action == "focus":
        return _transition_focus(current_state, action_params, timestamp)
    elif action == "resize":
        return _transition_resize(current_state, action_params, timestamp)
    elif action == "edit":
        return _transition_edit(current_state, action_params, capability, timestamp)
    elif action == "create_component":
        return _transition_create(current_state, action_params, timestamp)
    elif action == "destroy_component":
        return _transition_destroy(current_state, action_params, timestamp)
    else:
        return current_state, ProofObject(
            rule="UIStateTransition",
            premises=[f"action={action}"],
            conclusion=f"unknown action: {action}"
        )


def _transition_focus(
    state: UIState,
    params: Dict[str, Any],
    timestamp: Fraction
) -> Tuple[UIState, ProofObject]:
    """Execute focus transition."""
    target_id = params.get("component_id")
    
    if target_id not in state.components:
        return state, ProofObject(
            rule="FocusTransition",
            premises=[f"target={target_id}"],
            conclusion="focus failed: component not found"
        )
    
    # Update focused component
    new_state = UIState(
        components=state.components,
        root_component_id=state.root_component_id,
        focused_component_id=target_id,
        viewport_width=state.viewport_width,
        viewport_height=state.viewport_height,
        dpi_scale=state.dpi_scale,
        undo_stack=state.undo_stack,
        redo_stack=state.redo_stack
    )
    
    return new_state, ProofObject(
        rule="FocusTransition",
        premises=[
            f"previous_focus={state.focused_component_id}",
            f"new_focus={target_id}"
        ],
        conclusion=f"focus changed to {target_id}"
    )


def _transition_resize(
    state: UIState,
    params: Dict[str, Any],
    timestamp: Fraction
) -> Tuple[UIState, ProofObject]:
    """Execute resize transition (all Fraction parameters)."""
    component_id = params.get("component_id")
    new_width = params.get("width")  # Must be Fraction
    new_height = params.get("height")  # Must be Fraction
    
    if component_id not in state.components:
        return state, ProofObject(
            rule="ResizeTransition",
            premises=[f"component={component_id}"],
            conclusion="resize failed: component not found"
        )
    
    # Ensure Fraction types
    if not isinstance(new_width, Fraction):
        return state, ProofObject(
            rule="ResizeTransition",
            premises=[f"width_type={type(new_width).__name__}"],
            conclusion="resize failed: width must be Fraction"
        )
    
    if not isinstance(new_height, Fraction):
        return state, ProofObject(
            rule="ResizeTransition",
            premises=[f"height_type={type(new_height).__name__}"],
            conclusion="resize failed: height must be Fraction"
        )
    
    # Update component bounds
    old_comp = state.components[component_id]
    new_bounds = FractionalRect(
        x=old_comp.bounds.x,
        y=old_comp.bounds.y,
        width=new_width,
        height=new_height
    )
    
    new_comp = UIComponent(
        component_id=old_comp.component_id,
        component_type=old_comp.component_type,
        bounds=new_bounds,
        constraints=old_comp.constraints,
        content_hash=old_comp.content_hash,
        content_type=old_comp.content_type,
        is_visible=old_comp.is_visible,
        is_enabled=old_comp.is_enabled,
        is_focused=old_comp.is_focused,
        z_index=old_comp.z_index,
        children=old_comp.children,
        parent_id=old_comp.parent_id
    )
    
    new_components = state.components.copy()
    new_components[component_id] = new_comp
    
    new_state = UIState(
        components=new_components,
        root_component_id=state.root_component_id,
        focused_component_id=state.focused_component_id,
        viewport_width=state.viewport_width,
        viewport_height=state.viewport_height,
        dpi_scale=state.dpi_scale,
        undo_stack=state.undo_stack,
        redo_stack=state.redo_stack
    )
    
    return new_state, ProofObject(
        rule="ResizeTransition",
        premises=[
            f"component={component_id}",
            f"old_size=({old_comp.bounds.width},{old_comp.bounds.height})",
            f"new_size=({new_width},{new_height})"
        ],
        conclusion="resize completed"
    )


def _transition_edit(
    state: UIState,
    params: Dict[str, Any],
    capability: EditCap,
    timestamp: Fraction
) -> Tuple[UIState, ProofObject]:
    """Execute edit transition."""
    component_id = params.get("component_id")
    new_content_hash = params.get("content_hash")
    
    if component_id not in state.components:
        return state, ProofObject(
            rule="EditTransition",
            premises=[f"component={component_id}"],
            conclusion="edit failed: component not found"
        )
    
    # Verify file access if editing a file
    file_path = params.get("file_path")
    if file_path and not capability.can_edit_file(file_path):
        return state, ProofObject(
            rule="EditTransition",
            premises=[
                f"component={component_id}",
                f"file={file_path}",
                f"allowed={capability.file_paths}"
            ],
            conclusion="edit failed: file not in capability scope"
        )
    
    # Save state to undo stack
    state_hash = state.compute_state_hash()
    new_undo = state.undo_stack + (state_hash,)
    
    # Update component
    old_comp = state.components[component_id]
    new_comp = UIComponent(
        component_id=old_comp.component_id,
        component_type=old_comp.component_type,
        bounds=old_comp.bounds,
        constraints=old_comp.constraints,
        content_hash=new_content_hash,
        content_type=old_comp.content_type,
        is_visible=old_comp.is_visible,
        is_enabled=old_comp.is_enabled,
        is_focused=old_comp.is_focused,
        z_index=old_comp.z_index,
        children=old_comp.children,
        parent_id=old_comp.parent_id
    )
    
    new_components = state.components.copy()
    new_components[component_id] = new_comp
    
    new_state = UIState(
        components=new_components,
        root_component_id=state.root_component_id,
        focused_component_id=state.focused_component_id,
        viewport_width=state.viewport_width,
        viewport_height=state.viewport_height,
        dpi_scale=state.dpi_scale,
        undo_stack=new_undo,
        redo_stack=tuple()  # Clear redo on new action
    )
    
    return new_state, ProofObject(
        rule="EditTransition",
        premises=[
            f"component={component_id}",
            f"old_hash={old_comp.content_hash[:16]}...",
            f"new_hash={new_content_hash[:16]}..."
        ],
        conclusion="edit completed"
    )


def _transition_create(
    state: UIState,
    params: Dict[str, Any],
    timestamp: Fraction
) -> Tuple[UIState, ProofObject]:
    """Execute create component transition."""
    component_id = params.get("component_id")
    component_type = params.get("component_type")
    bounds = params.get("bounds")  # FractionalRect
    
    if component_id in state.components:
        return state, ProofObject(
            rule="CreateTransition",
            premises=[f"component={component_id}"],
            conclusion="create failed: component already exists"
        )
    
    new_comp = UIComponent(
        component_id=component_id,
        component_type=component_type,
        bounds=bounds,
        constraints=tuple(),
        content_hash="",
        content_type="text/plain",
        is_visible=True,
        is_enabled=True,
        is_focused=False,
        z_index=0
    )
    
    new_components = state.components.copy()
    new_components[component_id] = new_comp
    
    new_state = UIState(
        components=new_components,
        root_component_id=state.root_component_id,
        focused_component_id=state.focused_component_id,
        viewport_width=state.viewport_width,
        viewport_height=state.viewport_height,
        dpi_scale=state.dpi_scale,
        undo_stack=state.undo_stack,
        redo_stack=state.redo_stack
    )
    
    return new_state, ProofObject(
        rule="CreateTransition",
        premises=[
            f"component={component_id}",
            f"type={component_type.name}",
            f"bounds=({bounds.x},{bounds.y},{bounds.width},{bounds.height})"
        ],
        conclusion="component created"
    )


def _transition_destroy(
    state: UIState,
    params: Dict[str, Any],
    timestamp: Fraction
) -> Tuple[UIState, ProofObject]:
    """Execute destroy component transition."""
    component_id = params.get("component_id")
    
    if component_id not in state.components:
        return state, ProofObject(
            rule="DestroyTransition",
            premises=[f"component={component_id}"],
            conclusion="destroy failed: component not found"
        )
    
    new_components = {k: v for k, v in state.components.items() if k != component_id}
    
    new_state = UIState(
        components=new_components,
        root_component_id=state.root_component_id,
        focused_component_id=state.focused_component_id if state.focused_component_id != component_id else None,
        viewport_width=state.viewport_width,
        viewport_height=state.viewport_height,
        dpi_scale=state.dpi_scale,
        undo_stack=state.undo_stack,
        redo_stack=state.redo_stack
    )
    
    return new_state, ProofObject(
        rule="DestroyTransition",
        premises=[f"component={component_id}"],
        conclusion="component destroyed"
    )


def verify_deterministic_layout(
    state: UIState
) -> Tuple[bool, ProofObject]:
    """Verify that all layout values use Fraction (no floats).
    
    Args:
        state: UI state to verify
        
    Returns:
        (is_deterministic, proof)
    """
    violations = []
    
    for comp_id, comp in state.components.items():
        # Check bounds are Fractions
        if not isinstance(comp.bounds.x, Fraction):
            violations.append(f"{comp_id}: bounds.x is {type(comp.bounds.x).__name__}")
        if not isinstance(comp.bounds.y, Fraction):
            violations.append(f"{comp_id}: bounds.y is {type(comp.bounds.y).__name__}")
        if not isinstance(comp.bounds.width, Fraction):
            violations.append(f"{comp_id}: bounds.width is {type(comp.bounds.width).__name__}")
        if not isinstance(comp.bounds.height, Fraction):
            violations.append(f"{comp_id}: bounds.height is {type(comp.bounds.height).__name__}")
        
        # Check constraints use Fractions
        for constraint in comp.constraints:
            if not isinstance(constraint.value, Fraction):
                violations.append(f"{comp_id}: constraint {constraint.constraint_type.name} value is {type(constraint.value).__name__}")
    
    # Check viewport
    if not isinstance(state.viewport_width, Fraction):
        violations.append("viewport_width is not Fraction")
    if not isinstance(state.viewport_height, Fraction):
        violations.append("viewport_height is not Fraction")
    if not isinstance(state.dpi_scale, Fraction):
        violations.append("dpi_scale is not Fraction")
    
    is_deterministic = len(violations) == 0
    
    return is_deterministic, ProofObject(
        rule="VerifyDeterministicLayout",
        premises=[
            f"components={len(state.components)}",
            f"violations={len(violations)}"
        ],
        conclusion=f"deterministic={is_deterministic}"
    )


def check_proof_object_return(
    transition_result: Tuple[UIState, ProofObject]
) -> Tuple[bool, ProofObject]:
    """Verify that a transition returned a valid ProofObject.
    
    This is a meta-check for the specification requirement that
    every UI state transition returns ProofObject.
    
    Args:
        transition_result: Result from transition_state()
        
    Returns:
        (is_valid, check_proof)
    """
    new_state, proof = transition_result
    
    # Verify proof object structure
    has_rule = hasattr(proof, 'rule') and isinstance(proof.rule, str)
    has_premises = hasattr(proof, 'premises') and isinstance(proof.premises, list)
    has_conclusion = hasattr(proof, 'conclusion') and isinstance(proof.conclusion, str)
    has_hash = hasattr(proof, 'proof_hash') and isinstance(proof.proof_hash, str)
    
    is_valid = has_rule and has_premises and has_conclusion and has_hash
    
    return is_valid, ProofObject(
        rule="CheckProofObjectReturn",
        premises=[
            f"has_rule={has_rule}",
            f"has_premises={has_premises}",
            f"has_conclusion={has_conclusion}",
            f"has_hash={has_hash}"
        ],
        conclusion=f"valid_proof_object={is_valid}"
    )
