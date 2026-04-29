"""Tests for Logos IDE Formal Specification

Test coverage:
- Fixed-point layout (no floats)
- UI state transitions with ProofObject
- Content-addressed rendering
- Capability-gated actions
- Pixel determinism verification

All tests use Fraction arithmetic and verify ProofObject returns.
"""

import pytest
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Permission

from spec.logos_ide.formal_spec import (
    UIState, UIComponent, ComponentType, LayoutConstraintSpec, LayoutConstraint,
    EditCap, ViewCap, DebugCap, FractionalRect,
    transition_state, verify_deterministic_layout, check_proof_object_return
)

from spec.logos_ide.renderer import (
    RenderTarget, RenderCommand, CommandType, Color,
    content_addressed_render, execute_render_command,
    verify_pixel_determinism, compare_render_outputs,
    fraction_to_pixel, pixel_to_fraction
)


class TestFractionalLayout:
    """Test Fraction-based layout (no floats)."""
    
    def test_fractional_rect_contains_point(self):
        """Test point containment with Fraction coordinates."""
        rect = FractionalRect(
            x=Fraction(10),
            y=Fraction(20),
            width=Fraction(100),
            height=Fraction(50)
        )
        
        # Point inside
        assert rect.contains_point(Fraction(50), Fraction(40)) is True
        
        # Point outside
        assert rect.contains_point(Fraction(200), Fraction(40)) is False
        
        # Point on edge (inclusive of min, exclusive of max)
        assert rect.contains_point(Fraction(10), Fraction(20)) is True
        assert rect.contains_point(Fraction(110), Fraction(20)) is False
    
    def test_fractional_rect_intersects(self):
        """Test rectangle intersection."""
        rect1 = FractionalRect(
            x=Fraction(0), y=Fraction(0),
            width=Fraction(100), height=Fraction(100)
        )
        rect2 = FractionalRect(
            x=Fraction(50), y=Fraction(50),
            width=Fraction(100), height=Fraction(100)
        )
        rect3 = FractionalRect(
            x=Fraction(200), y=Fraction(200),
            width=Fraction(100), height=Fraction(100)
        )
        
        assert rect1.intersects(rect2) is True
        assert rect2.intersects(rect1) is True
        assert rect1.intersects(rect3) is False
    
    def test_component_area_fraction(self):
        """Test component area calculation with Fraction."""
        comp = UIComponent(
            component_id="test",
            component_type=ComponentType.EDITOR,
            bounds=FractionalRect(
                x=Fraction(0), y=Fraction(0),
                width=Fraction(100, 3),  # 33.333... as Fraction
                height=Fraction(50, 2)   # 25 as Fraction
            ),
            constraints=tuple(),
            content_hash="abc",
            content_type="text/plain",
            is_visible=True,
            is_enabled=True,
            is_focused=False,
            z_index=0
        )
        
        area = comp.get_area()
        # 100/3 * 50/2 = 5000/6 = 2500/3
        assert area == Fraction(2500, 3)


class EditCap:
    """Capability for editor actions."""
    
    def __init__(self, editor_id: str, holder_id: str, permissions: frozenset,
                 delegator: str, file_paths: frozenset):
        self.editor_id = editor_id
        self.holder_id = holder_id
        self.permissions = permissions
        self.delegator = delegator
        self.file_paths = file_paths

    def can_edit_file(self, path: str) -> bool:
        """Check if capability allows editing specific file."""
        return path in self.file_paths

    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has specific permission."""
        # TODO: Expand has_permission() - stub detected by Yeshua Agent
        return perm in self.permissions


class TestUICapabilities:
    """Test UI capability system."""
    
    def test_edit_cap_file_access(self):
        """Test EditCap file access control."""
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.READ, Permission.WRITE]),
            delegator="root",
            file_paths=frozenset(["/project/file1.py", "/project/file2.py"])
        )
        
        assert cap.can_edit_file("/project/file1.py") is True
        assert cap.can_edit_file("/project/file2.py") is True
        assert cap.can_edit_file("/project/file3.py") is False
    
    def test_edit_cap_permissions(self):
        """Test EditCap permission checking."""
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            file_paths=frozenset(["/project/file1.py"])
        )
        
        assert cap.has_permission(Permission.READ) is True
        assert cap.has_permission(Permission.WRITE) is False


class TestUIStateTransitions:
    """Test UI state transitions."""
    
    def _create_test_state(self) -> UIState:
        """Create a test UI state."""
        comp1 = UIComponent(
            component_id="editor1",
            component_type=ComponentType.EDITOR,
            bounds=FractionalRect(
                x=Fraction(0), y=Fraction(0),
                width=Fraction(800), height=Fraction(600)
            ),
            constraints=tuple(),
            content_hash="hash1",
            content_type="text/plain",
            is_visible=True,
            is_enabled=True,
            is_focused=False,
            z_index=1
        )
        
        return UIState(
            components={"editor1": comp1},
            root_component_id="editor1",
            focused_component_id=None,
            viewport_width=Fraction(1920),
            viewport_height=Fraction(1080),
            dpi_scale=Fraction(1)
        )
    
    def test_transition_focus(self):
        """Test focus transition."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            file_paths=frozenset()
        )
        
        new_state, proof = transition_state(
            state, "focus",
            {"component_id": "editor1"},
            cap, Fraction(1000)
        )
        
        assert new_state.focused_component_id == "editor1"
        assert proof.rule == "FocusTransition"
        assert "focus changed" in proof.conclusion
    
    def test_transition_focus_not_found(self):
        """Test focus transition with non-existent component."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            file_paths=frozenset()
        )
        
        new_state, proof = transition_state(
            state, "focus",
            {"component_id": "nonexistent"},
            cap, Fraction(1000)
        )
        
        assert new_state.focused_component_id is None  # Unchanged
        assert "not found" in proof.conclusion
    
    def test_transition_resize_fraction(self):
        """Test resize transition with Fraction dimensions."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            file_paths=frozenset()
        )
        
        new_state, proof = transition_state(
            state, "resize",
            {
                "component_id": "editor1",
                "width": Fraction(1024),
                "height": Fraction(768)
            },
            cap, Fraction(1000)
        )
        
        assert new_state.components["editor1"].bounds.width == Fraction(1024)
        assert new_state.components["editor1"].bounds.height == Fraction(768)
        assert "resize completed" in proof.conclusion
    
    def test_transition_resize_rejects_float(self):
        """Test that resize rejects float dimensions."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            file_paths=frozenset()
        )
        
        new_state, proof = transition_state(
            state, "resize",
            {
                "component_id": "editor1",
                "width": 1024.5,  # Float! Should reject
                "height": 768.0
            },
            cap, Fraction(1000)
        )
        
        # State should be unchanged
        assert new_state.components["editor1"].bounds.width == Fraction(800)
        assert "must be Fraction" in proof.conclusion
    
    def test_transition_edit_saves_undo(self):
        """Test that edit saves state to undo stack."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            file_paths=frozenset(["/project/file1.py"])
        )
        
        new_state, proof = transition_state(
            state, "edit",
            {
                "component_id": "editor1",
                "content_hash": "new_hash",
                "file_path": "/project/file1.py"
            },
            cap, Fraction(1000)
        )
        
        assert new_state.components["editor1"].content_hash == "new_hash"
        assert len(new_state.undo_stack) == 1
        assert len(new_state.redo_stack) == 0  # Cleared on new action
    
    def test_transition_edit_no_permission(self):
        """Test edit fails without WRITE permission."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.READ]),  # No WRITE
            delegator="root",
            file_paths=frozenset(["/project/file1.py"])
        )
        
        new_state, proof = transition_state(
            state, "edit",
            {
                "component_id": "editor1",
                "content_hash": "new_hash",
                "file_path": "/project/file1.py"
            },
            cap, Fraction(1000)
        )
        
        assert new_state.components["editor1"].content_hash == "hash1"  # Unchanged
        assert "no WRITE permission" in proof.conclusion
    
    def test_transition_create_component(self):
        """Test create component transition."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            file_paths=frozenset()
        )
        
        new_state, proof = transition_state(
            state, "create_component",
            {
                "component_id": "status_bar",
                "component_type": ComponentType.STATUS_BAR,
                "bounds": FractionalRect(
                    x=Fraction(0), y=Fraction(580),
                    width=Fraction(800), height=Fraction(20)
                )
            },
            cap, Fraction(1000)
        )
        
        assert "status_bar" in new_state.components
        assert new_state.components["status_bar"].component_type == ComponentType.STATUS_BAR
        assert "component created" in proof.conclusion
    
    def test_transition_destroy_component(self):
        """Test destroy component transition."""
        state = self._create_test_state()
        cap = EditCap(
            editor_id="editor1",
            holder_id="user1",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            file_paths=frozenset()
        )
        
        new_state, proof = transition_state(
            state, "destroy_component",
            {"component_id": "editor1"},
            cap, Fraction(1000)
        )
        
        assert "editor1" not in new_state.components
        assert "component destroyed" in proof.conclusion


class TestDeterminismVerification:
    """Test determinism verification."""
    
    def test_verify_deterministic_layout_pass(self):
        """Test layout verification passes with all Fractions."""
        comp = UIComponent(
            component_id="test",
            component_type=ComponentType.EDITOR,
            bounds=FractionalRect(
                x=Fraction(10),
                y=Fraction(20),
                width=Fraction(100),
                height=Fraction(50)
            ),
            constraints=(
                LayoutConstraintSpec(LayoutConstraint.FIXED_WIDTH, Fraction(100)),
            ),
            content_hash="abc",
            content_type="text/plain",
            is_visible=True,
            is_enabled=True,
            is_focused=False,
            z_index=0
        )
        
        state = UIState(
            components={"test": comp},
            root_component_id="test",
            focused_component_id=None,
            viewport_width=Fraction(1920),
            viewport_height=Fraction(1080),
            dpi_scale=Fraction(1)
        )
        
        is_deterministic, proof = verify_deterministic_layout(state)
        
        assert is_deterministic is True
        assert "deterministic=True" in proof.conclusion
    
    def test_check_proof_object_return(self):
        """Test proof object return verification."""
        state = UIState(
            components={},
            root_component_id="root",
            focused_component_id=None,
            viewport_width=Fraction(1920),
            viewport_height=Fraction(1080),
            dpi_scale=Fraction(1)
        )
        
        # Create a valid transition result
        proof = ProofObject(
            rule="TestTransition",
            premises=["test"],
            conclusion="test"
        )
        result = (state, proof)
        
        is_valid, check_proof = check_proof_object_return(result)
        
        assert is_valid is True
        assert "valid_proof_object=True" in check_proof.conclusion


class TestColorSystem:
    """Test Color system (Fraction-based)."""
    
    def test_color_from_bytes(self):
        """Test color creation from bytes."""
        color = Color.from_bytes(255, 128, 64, 255)
        
        assert color.r == Fraction(255, 255)  # 1.0
        assert color.g == Fraction(128, 255)
        assert color.b == Fraction(64, 255)
        assert color.a == Fraction(1)
    
    def test_color_to_bytes(self):
        """Test color conversion to bytes."""
        color = Color(
            r=Fraction(1),      # 255
            g=Fraction(1, 2),   # 127.5 -> 127
            b=Fraction(1, 4),   # 63.75 -> 63
            a=Fraction(1)
        )
        
        r, g, b, a = color.to_bytes()
        assert r == 255
        assert g == 127  # 255 * 0.5 = 127.5 -> 127
        assert b == 63   # 255 * 0.25 = 63.75 -> 63
        assert a == 255


class TestCoordinateConversion:
    """Test Fraction <-> pixel conversion."""
    
    def test_fraction_to_pixel(self):
        """Test Fraction to pixel conversion."""
        # 10.5 at scale 2 = 21
        pixel = fraction_to_pixel(Fraction(21, 2), Fraction(2))
        assert pixel == 21
        
        # 5.3 at scale 1 = 5 (rounded)
        pixel = fraction_to_pixel(Fraction(53, 10), Fraction(1))
        assert pixel == 5  # 5.3 rounds to 5
    
    def test_pixel_to_fraction(self):
        """Test pixel to Fraction conversion."""
        frac = pixel_to_fraction(100, Fraction(2))
        assert frac == Fraction(50)
        
        frac = pixel_to_fraction(50, Fraction(1))
        assert frac == Fraction(50)


class TestRenderCommands:
    """Test render command generation."""
    
    def test_render_command_hash(self):
        """Test that render commands have deterministic hashes."""
        cmd1 = RenderCommand(
            command_type=CommandType.DRAW_RECT,
            x=Fraction(10),
            y=Fraction(20),
            width=Fraction(100),
            height=Fraction(50),
            color=Color.from_bytes(255, 0, 0, 255)
        )
        
        cmd2 = RenderCommand(
            command_type=CommandType.DRAW_RECT,
            x=Fraction(10),
            y=Fraction(20),
            width=Fraction(100),
            height=Fraction(50),
            color=Color.from_bytes(255, 0, 0, 255)
        )
        
        # Same commands should have same hash
        assert cmd1.compute_hash() == cmd2.compute_hash()
    
    def test_content_addressed_render(self):
        """Test content-addressed rendering."""
        comp = UIComponent(
            component_id="editor1",
            component_type=ComponentType.EDITOR,
            bounds=FractionalRect(
                x=Fraction(0), y=Fraction(0),
                width=Fraction(100), height=Fraction(100)
            ),
            constraints=tuple(),
            content_hash="content_abc",
            content_type="text/plain",
            is_visible=True,
            is_enabled=True,
            is_focused=False,
            z_index=0
        )
        
        state = UIState(
            components={"editor1": comp},
            root_component_id="editor1",
            focused_component_id=None,
            viewport_width=Fraction(100),
            viewport_height=Fraction(100),
            dpi_scale=Fraction(1)
        )
        
        target = RenderTarget(
            target_id="framebuffer1",
            width=100,
            height=100,
            pixel_format="RGBA8"
        )
        
        output, commands = content_addressed_render(state, target)
        
        assert output.command_count > 0
        assert len(output.content_hash) == 64  # SHA-256 hex
        assert len(commands) == output.command_count
        assert "ContentAddressedRender" in output.proof.rule
    
    def test_deterministic_render_output(self):
        """Test that same state produces same output hash."""
        comp = UIComponent(
            component_id="editor1",
            component_type=ComponentType.EDITOR,
            bounds=FractionalRect(
                x=Fraction(0), y=Fraction(0),
                width=Fraction(100), height=Fraction(100)
            ),
            constraints=tuple(),
            content_hash="content_abc",
            content_type="text/plain",
            is_visible=True,
            is_enabled=True,
            is_focused=False,
            z_index=0
        )
        
        state = UIState(
            components={"editor1": comp},
            root_component_id="editor1",
            focused_component_id=None,
            viewport_width=Fraction(100),
            viewport_height=Fraction(100),
            dpi_scale=Fraction(1)
        )
        
        target = RenderTarget(
            target_id="framebuffer1",
            width=100,
            height=100,
            pixel_format="RGBA8"
        )
        
        # Render twice
        output1, _ = content_addressed_render(state, target)
        output2, _ = content_addressed_render(state, target)
        
        # Same state → same hash
        assert output1.content_hash == output2.content_hash


class TestRenderExecution:
    """Test render command execution."""
    
    def test_execute_clear_command(self):
        """Test CLEAR command execution."""
        target = RenderTarget(
            target_id="fb1",
            width=10,
            height=10,
            pixel_format="RGBA8"
        )
        
        cmd = RenderCommand(
            command_type=CommandType.CLEAR,
            color=Color.from_bytes(255, 0, 0, 255)  # Red
        )
        
        new_target, proof = execute_render_command(target, cmd, Fraction(1))
        
        # All pixels should be set
        assert len(new_target.pixel_content_map) == 100  # 10x10
        # All should have same hash (red color)
        unique_hashes = set(new_target.pixel_content_map.values())
        assert len(unique_hashes) == 1
    
    def test_execute_draw_rect_command(self):
        """Test DRAW_RECT command execution."""
        target = RenderTarget(
            target_id="fb1",
            width=100,
            height=100,
            pixel_format="RGBA8"
        )
        
        cmd = RenderCommand(
            command_type=CommandType.DRAW_RECT,
            x=Fraction(10),
            y=Fraction(10),
            width=Fraction(20),
            height=Fraction(20),
            color=Color.from_bytes(0, 255, 0, 255)  # Green
        )
        
        new_target, proof = execute_render_command(target, cmd, Fraction(1))
        
        # Should have drawn pixels
        assert len(new_target.pixel_content_map) == 400  # 20x20 rect
    
    def test_verify_pixel_determinism(self):
        """Test pixel determinism verification."""
        target = RenderTarget(
            target_id="fb1",
            width=10,
            height=10,
            pixel_format="RGBA8",
            pixel_content_map={(x, y): "hash_abc" for x in range(10) for y in range(10)}
        )
        
        # Compute expected hash
        import hashlib
        pixel_data = []
        for y in range(10):
            for x in range(10):
                pixel_data.append(f"{x},{y}:hash_abc")
        expected_hash = hashlib.sha256("|".join(pixel_data).encode()).hexdigest()
        
        matches, proof = verify_pixel_determinism(target, expected_hash)
        
        assert matches is True
        assert "deterministic_match=True" in proof.conclusion


class TestRenderComparison:
    """Test render output comparison."""
    
    def test_compare_equal_outputs(self):
        """Test comparing equal render outputs."""
        target = RenderTarget(
            target_id="fb1",
            width=10,
            height=10,
            pixel_format="RGBA8"
        )
        
        output1 = RenderOutput(
            target=target,
            command_count=5,
            content_hash="abc123" * 8,  # 64 chars
            proof=ProofObject(rule="Test", premises=[], conclusion="test")
        )
        
        output2 = RenderOutput(
            target=target,
            command_count=5,
            content_hash="abc123" * 8,
            proof=ProofObject(rule="Test", premises=[], conclusion="test")
        )
        
        equal, proof = compare_render_outputs(output1, output2)
        
        assert equal is True
        assert "outputs_equal=True" in proof.conclusion
    
    def test_compare_different_outputs(self):
        """Test comparing different render outputs."""
        target = RenderTarget(
            target_id="fb1",
            width=10,
            height=10,
            pixel_format="RGBA8"
        )
        
        output1 = RenderOutput(
            target=target,
            command_count=5,
            content_hash="abc123" * 8,
            proof=ProofObject(rule="Test", premises=[], conclusion="test")
        )
        
        output2 = RenderOutput(
            target=target,
            command_count=5,
            content_hash="xyz789" * 8,
            proof=ProofObject(rule="Test", premises=[], conclusion="test")
        )
        
        equal, proof = compare_render_outputs(output1, output2)
        
        assert equal is False
        assert "outputs_equal=False" in proof.conclusion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
