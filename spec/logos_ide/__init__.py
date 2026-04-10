"""Logos IDE Formal Specification

Fixed-point rendering pipeline for deterministic UI.
Every UI state transition returns ProofObject.
Content-addressed rendering: same state → same pixels.

Mathematical foundation: Fixed-point arithmetic + content-addressing.
Standard: Yeshua (determinism, verifiability, no hidden state).
"""

from __future__ import annotations

from .formal_spec import (
    UIState,
    UIComponent,
    ComponentType,
    EditCap,
    ViewCap,
    DebugCap,
    transition_state,
    verify_deterministic_layout,
    check_proof_object_return,
)

from .renderer import (
    RenderTarget,
    RenderCommand,
    CommandType,
    content_addressed_render,
    execute_render_command,
    verify_pixel_determinism,
)

__all__ = [
    # Formal spec
    "UIState",
    "UIComponent",
    "ComponentType",
    "EditCap",
    "ViewCap",
    "DebugCap",
    "transition_state",
    "verify_deterministic_layout",
    "check_proof_object_return",
    # Renderer
    "RenderTarget",
    "RenderCommand",
    "CommandType",
    "content_addressed_render",
    "execute_render_command",
    "verify_pixel_determinism",
]
