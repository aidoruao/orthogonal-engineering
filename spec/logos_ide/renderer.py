"""Logos IDE Renderer — Content-Addressed Rendering

Content-addressed rendering: same state → same pixels.
Fraction-based coordinate system (no floating point).
Deterministic rendering pipeline.

Mathematical foundation: Content-addressing + fixed-point rasterization.
Standard: IEEE 754 excluded — all coordinates are Fractions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict, Any
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject
from .formal_spec import UIState, UIComponent, FractionalRect


class CommandType(Enum):
    """Types of render commands."""
    CLEAR = auto()           # Clear target
    DRAW_RECT = auto()       # Draw rectangle
    DRAW_TEXT = auto()       # Draw text
    DRAW_LINE = auto()       # Draw line
    DRAW_IMAGE = auto()      # Draw image (content-addressed)
    SET_CLIP = auto()        # Set clipping region
    PUSH_TRANSFORM = auto()  # Push coordinate transform
    POP_TRANSFORM = auto()   # Pop coordinate transform


@dataclass(frozen=True)
class Color:
    """RGBA color using Fraction components (0-1 range).
    
    All components are Fractions, never floats.
    """
    r: Fraction  # Red: 0-1
    g: Fraction  # Green: 0-1
    b: Fraction  # Blue: 0-1
    a: Fraction  # Alpha: 0-1
    
    def to_bytes(self) -> Tuple[int, int, int, int]:
        """Convert to 8-bit per channel bytes."""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255),
            int(self.a * 255)
        )
    
    @staticmethod
    def from_bytes(r: int, g: int, b: int, a: int = 255) -> Color:
        """Create color from 8-bit bytes."""
        return Color(
            r=Fraction(r, 255),
            g=Fraction(g, 255),
            b=Fraction(b, 255),
            a=Fraction(a, 255)
        )


@dataclass(frozen=True)
class RenderCommand:
    """A single render command.
    
    All coordinates and dimensions use Fraction.
    """
    command_type: CommandType
    
    # Geometry (all Fractions)
    x: Fraction = Fraction(0)
    y: Fraction = Fraction(0)
    width: Fraction = Fraction(0)
    height: Fraction = Fraction(0)
    x2: Optional[Fraction] = None  # For lines: end x
    y2: Optional[Fraction] = None  # For lines: end y
    
    # Styling
    color: Optional[Color] = None
    background_color: Optional[Color] = None
    
    # Content (content-addressed)
    content_hash: Optional[str] = None  # For images/text
    text_content: Optional[str] = None  # For text rendering
    font_hash: Optional[str] = None     # Content-addressed font
    font_size: Fraction = Fraction(12)  # Font size in points
    
    def compute_hash(self) -> str:
        """Compute content hash of this command."""
        import hashlib
        # Deterministic serialization
        parts = [
            self.command_type.name,
            str(self.x), str(self.y),
            str(self.width), str(self.height),
            str(self.x2) if self.x2 else "",
            str(self.y2) if self.y2 else "",
            self.content_hash or "",
            self.text_content or ""
        ]
        data = "|".join(parts)
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class RenderTarget:
    """A render target (framebuffer).
    
    Dimensions in pixels (integers), but all rendering
    uses Fraction coordinates internally.
    """
    target_id: str
    width: int
    height: int
    pixel_format: str  # "RGBA8", "RGB8", etc.
    
    # Content-addressed pixel storage
    # Each "pixel" is a content hash of its value
    pixel_content_map: Dict[Tuple[int, int], str] = field(default_factory=dict)
    
    def get_pixel_content_hash(self, x: int, y: int) -> Optional[str]:
        """Get content hash of pixel at coordinates."""
        return self.pixel_content_map.get((x, y))


@dataclass
class RenderOutput:
    """Output of rendering operation."""
    target: RenderTarget
    command_count: int
    content_hash: str  # Hash of complete render output
    proof: ProofObject


def fraction_to_pixel(value: Fraction, scale: Fraction) -> int:
    """Convert Fraction coordinate to pixel coordinate.
    
    Uses proper rounding for deterministic results.
    """
    scaled = value * scale
    # Round to nearest integer: floor(x + 0.5)
    return int(scaled + Fraction(1, 2))


def pixel_to_fraction(pixel: int, scale: Fraction) -> Fraction:
    """Convert pixel coordinate to Fraction."""
    return Fraction(pixel) / scale


def content_addressed_render(
    state: UIState,
    target: RenderTarget
) -> Tuple[RenderOutput, List[RenderCommand]]:
    """Render UI state to target using content-addressing.
    
    Same UI state always produces:
    1. Same render command sequence
    2. Same pixel content hashes
    3. Same output content hash
    
    Args:
        state: UI state to render
        target: Render target
        
    Returns:
        (output, commands)
    """
    commands: List[RenderCommand] = []
    
    # Generate clear command
    clear_cmd = RenderCommand(
        command_type=CommandType.CLEAR,
        color=Color.from_bytes(30, 30, 30, 255)  # Dark gray background
    )
    commands.append(clear_cmd)
    
    # Render each visible component
    # Sort by z-index (back to front)
    sorted_components = sorted(
        state.components.values(),
        key=lambda c: c.z_index
    )
    
    for component in sorted_components:
        if not component.is_visible:
            continue
        
        comp_commands = _render_component(component, state)
        commands.extend(comp_commands)
    
    # Compute output content hash
    import hashlib
    command_hashes = [cmd.compute_hash() for cmd in commands]
    output_hash_input = "|".join(sorted(command_hashes))
    output_hash = hashlib.sha256(output_hash_input.encode()).hexdigest()
    
    proof = ProofObject(
        rule="ContentAddressedRender",
        premises=[
            f"state_hash={state.compute_state_hash()[:16]}...",
            f"components_rendered={len([c for c in sorted_components if c.is_visible])}",
            f"commands_generated={len(commands)}"
        ],
        conclusion=f"render_output_hash={output_hash[:16]}..."
    )
    
    output = RenderOutput(
        target=target,
        command_count=len(commands),
        content_hash=output_hash,
        proof=proof
    )
    
    return output, commands


def _render_component(
    component: UIComponent,
    state: UIState
) -> List[RenderCommand]:
    """Generate render commands for a single component."""
    commands = []
    
    # Background rect
    bg_cmd = RenderCommand(
        command_type=CommandType.DRAW_RECT,
        x=component.bounds.x,
        y=component.bounds.y,
        width=component.bounds.width,
        height=component.bounds.height,
        color=Color.from_bytes(50, 50, 50, 255)
    )
    commands.append(bg_cmd)
    
    # Border
    border_color = Color.from_bytes(100, 100, 100, 255)
    if component.is_focused:
        border_color = Color.from_bytes(0, 120, 212, 255)  # Blue focus
    
    # Top border
    commands.append(RenderCommand(
        command_type=CommandType.DRAW_LINE,
        x=component.bounds.x,
        y=component.bounds.y,
        x2=component.bounds.x + component.bounds.width,
        y2=component.bounds.y,
        color=border_color
    ))
    
    # Bottom border
    commands.append(RenderCommand(
        command_type=CommandType.DRAW_LINE,
        x=component.bounds.x,
        y=component.bounds.y + component.bounds.height,
        x2=component.bounds.x + component.bounds.width,
        y2=component.bounds.y + component.bounds.height,
        color=border_color
    ))
    
    # Left border
    commands.append(RenderCommand(
        command_type=CommandType.DRAW_LINE,
        x=component.bounds.x,
        y=component.bounds.y,
        x2=component.bounds.x,
        y2=component.bounds.y + component.bounds.height,
        color=border_color
    ))
    
    # Right border
    commands.append(RenderCommand(
        command_type=CommandType.DRAW_LINE,
        x=component.bounds.x + component.bounds.width,
        y=component.bounds.y,
        x2=component.bounds.x + component.bounds.width,
        y2=component.bounds.y + component.bounds.height,
        color=border_color
    ))
    
    # Component-specific rendering
    if component.component_type.name == "EDITOR":
        # Editor: add text content placeholder
        text_cmd = RenderCommand(
            command_type=CommandType.DRAW_TEXT,
            x=component.bounds.x + Fraction(5),
            y=component.bounds.y + Fraction(20),
            text_content=f"[Editor: {component.content_hash[:16]}...]",
            font_size=Fraction(14),
            color=Color.from_bytes(200, 200, 200, 255)
        )
        commands.append(text_cmd)
    
    elif component.component_type.name == "STATUS_BAR":
        # Status bar text
        status_cmd = RenderCommand(
            command_type=CommandType.DRAW_TEXT,
            x=component.bounds.x + Fraction(5),
            y=component.bounds.y + Fraction(15),
            text_content="Ready",
            font_size=Fraction(12),
            color=Color.from_bytes(200, 200, 200, 255)
        )
        commands.append(status_cmd)
    
    return commands


def execute_render_command(
    target: RenderTarget,
    command: RenderCommand,
    dpi_scale: Fraction
) -> Tuple[RenderTarget, ProofObject]:
    """Execute a single render command on target.
    
    Updates pixel content map with content-addressed values.
    
    Args:
        target: Render target
        command: Command to execute
        dpi_scale: DPI scale factor
        
    Returns:
        (updated_target, proof)
    """
    new_pixel_map = target.pixel_content_map.copy()
    
    if command.command_type == CommandType.CLEAR:
        # Clear all pixels to background color
        color_bytes = command.color.to_bytes() if command.color else (0, 0, 0, 255)
        import hashlib
        color_hash = hashlib.sha256(bytes(color_bytes)).hexdigest()
        
        for y in range(target.height):
            for x in range(target.width):
                new_pixel_map[(x, y)] = color_hash
    
    elif command.command_type == CommandType.DRAW_RECT:
        # Draw rectangle
        x1 = fraction_to_pixel(command.x, dpi_scale)
        y1 = fraction_to_pixel(command.y, dpi_scale)
        x2 = fraction_to_pixel(command.x + command.width, dpi_scale)
        y2 = fraction_to_pixel(command.y + command.height, dpi_scale)
        
        color_bytes = command.color.to_bytes() if command.color else (255, 255, 255, 255)
        import hashlib
        color_hash = hashlib.sha256(bytes(color_bytes)).hexdigest()
        
        for y in range(max(0, y1), min(target.height, y2)):
            for x in range(max(0, x1), min(target.width, x2)):
                new_pixel_map[(x, y)] = color_hash
    
    elif command.command_type == CommandType.DRAW_LINE:
        # Simple line drawing (Bresenham-like with Fraction precision)
        if command.x2 is None or command.y2 is None:
            return target, ProofObject(
                rule="ExecuteRenderCommand",
                premises=["command=DRAW_LINE", "missing_endpoints"],
                conclusion="execution failed: missing endpoints"
            )
        
        x1 = fraction_to_pixel(command.x, dpi_scale)
        y1 = fraction_to_pixel(command.y, dpi_scale)
        x2 = fraction_to_pixel(command.x2, dpi_scale)
        y2 = fraction_to_pixel(command.y2, dpi_scale)
        
        color_bytes = command.color.to_bytes() if command.color else (255, 255, 255, 255)
        import hashlib
        color_hash = hashlib.sha256(bytes(color_bytes)).hexdigest()
        
        # Simple DDA line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy)
        
        if steps > 0:
            x_inc = Fraction(x2 - x1, steps)
            y_inc = Fraction(y2 - y1, steps)
            
            x, y = Fraction(x1), Fraction(y1)
            for _ in range(steps + 1):
                px, py = int(x + Fraction(1, 2)), int(y + Fraction(1, 2))
                if 0 <= px < target.width and 0 <= py < target.height:
                    new_pixel_map[(px, py)] = color_hash
                x += x_inc
                y += y_inc
    
    new_target = RenderTarget(
        target_id=target.target_id,
        width=target.width,
        height=target.height,
        pixel_format=target.pixel_format,
        pixel_content_map=new_pixel_map
    )
    
    proof = ProofObject(
        rule="ExecuteRenderCommand",
        premises=[
            f"command={command.command_type.name}",
            f"target={target.target_id}"
        ],
        conclusion="command executed"
    )
    
    return new_target, proof


def verify_pixel_determinism(
    target: RenderTarget,
    expected_content_hash: str
) -> Tuple[bool, ProofObject]:
    """Verify that target pixels match expected content hash.
    
    This verifies the key property: same state → same pixels.
    
    Args:
        target: Render target to verify
        expected_content_hash: Expected content hash
        
    Returns:
        (matches, proof)
    """
    # Compute actual content hash
    import hashlib
    pixel_data = []
    for y in range(target.height):
        for x in range(target.width):
            pixel_hash = target.pixel_content_map.get((x, y), "")
            pixel_data.append(f"{x},{y}:{pixel_hash}")
    
    actual_hash = hashlib.sha256("|".join(pixel_data).encode()).hexdigest()
    
    matches = actual_hash == expected_content_hash
    
    return matches, ProofObject(
        rule="VerifyPixelDeterminism",
        premises=[
            f"target={target.target_id}",
            f"pixels={len(target.pixel_content_map)}",
            f"expected_hash={expected_content_hash[:16]}...",
            f"actual_hash={actual_hash[:16]}..."
        ],
        conclusion=f"deterministic_match={matches}"
    )


def compare_render_outputs(
    output1: RenderOutput,
    output2: RenderOutput
) -> Tuple[bool, ProofObject]:
    """Compare two render outputs for equality.
    
    Two outputs are equal if their content hashes match.
    
    Args:
        output1: First render output
        output2: Second render output
        
    Returns:
        (equal, proof)
    """
    equal = output1.content_hash == output2.content_hash
    
    return equal, ProofObject(
        rule="CompareRenderOutputs",
        premises=[
            f"hash1={output1.content_hash[:16]}...",
            f"hash2={output2.content_hash[:16]}..."
        ],
        conclusion=f"outputs_equal={equal}"
    )
