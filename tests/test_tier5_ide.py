"""
tests/test_tier5_ide.py — Tier 5 IDE Integration verification tests

Verifies: .vscode/launch.json, .vscode/tasks.json, pyrightconfig.json,
mcp/oe-basic.mcp.json, .ai_registry.json, alert_on_failure.py,
docs/AGENT_FEED_NOTES.md.

All tests follow the Popperian pattern: each has a Falsifies if: condition.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# 1. .vscode/launch.json
# ---------------------------------------------------------------------------


class TestVSCodeLaunch:
    """Tests for .vscode/launch.json (Gap #21)."""

    def test_launch_json_exists(self) -> None:
        """
        Invariant: .vscode/launch.json must exist.

        Falsifies if: file not found at .vscode/launch.json.
        falsifies_if: file_not_found
        """
        assert (REPO_ROOT / ".vscode" / "launch.json").exists()

    def test_launch_json_valid_json(self) -> None:
        """
        Invariant: .vscode/launch.json must be valid JSON.

        Falsifies if: json.JSONDecodeError raised on parse.
        falsifies_if: json_parse_error
        """
        content = (REPO_ROOT / ".vscode" / "launch.json").read_text()
        data = json.loads(content)
        assert isinstance(data, dict)

    def test_launch_json_has_minimum_configs(self) -> None:
        """
        Invariant: .vscode/launch.json must have at least 8 debug configurations.

        Falsifies if: configurations array has fewer than 8 entries.
        falsifies_if: fewer_than_8_configurations
        """
        data = json.loads((REPO_ROOT / ".vscode" / "launch.json").read_text())
        configs = data.get("configurations", [])
        assert len(configs) >= 8, f"Expected ≥8 configs, got {len(configs)}"

    def test_launch_json_all_python_type(self) -> None:
        """
        Invariant: All launch configs must use type 'python'.

        Falsifies if: any config has type != 'python'.
        falsifies_if: non_python_type_config
        """
        data = json.loads((REPO_ROOT / ".vscode" / "launch.json").read_text())
        for cfg in data.get("configurations", []):
            assert cfg.get("type") == "python", f"Non-python type: {cfg.get('name')}"

    def test_launch_json_has_health_check(self) -> None:
        """
        Invariant: .vscode/launch.json must include an Agent Health Check config.

        Falsifies if: no config name contains 'health' (case-insensitive).
        falsifies_if: no_health_check_config
        """
        data = json.loads((REPO_ROOT / ".vscode" / "launch.json").read_text())
        names = [c.get("name", "").lower() for c in data.get("configurations", [])]
        assert any("health" in n for n in names), "No health check config found"

    def test_launch_json_has_tests_config(self) -> None:
        """
        Invariant: .vscode/launch.json must include a 'Run All Tests' config.

        Falsifies if: no config name contains 'test' (case-insensitive).
        falsifies_if: no_tests_config
        """
        data = json.loads((REPO_ROOT / ".vscode" / "launch.json").read_text())
        names = [c.get("name", "").lower() for c in data.get("configurations", [])]
        assert any("test" in n for n in names), "No tests config found"


# ---------------------------------------------------------------------------
# 2. .vscode/tasks.json
# ---------------------------------------------------------------------------


class TestVSCodeTasks:
    """Tests for .vscode/tasks.json (Gap #22)."""

    def test_tasks_json_exists(self) -> None:
        """
        Invariant: .vscode/tasks.json must exist.

        Falsifies if: file not found at .vscode/tasks.json.
        falsifies_if: file_not_found
        """
        assert (REPO_ROOT / ".vscode" / "tasks.json").exists()

    def test_tasks_json_valid_json(self) -> None:
        """
        Invariant: .vscode/tasks.json must be valid JSON.

        Falsifies if: json.JSONDecodeError raised on parse.
        falsifies_if: json_parse_error
        """
        data = json.loads((REPO_ROOT / ".vscode" / "tasks.json").read_text())
        assert isinstance(data, dict)

    def test_tasks_json_has_minimum_tasks(self) -> None:
        """
        Invariant: .vscode/tasks.json must have at least 8 tasks.

        Falsifies if: tasks array has fewer than 8 entries.
        falsifies_if: fewer_than_8_tasks
        """
        data = json.loads((REPO_ROOT / ".vscode" / "tasks.json").read_text())
        tasks = data.get("tasks", [])
        assert len(tasks) >= 8, f"Expected ≥8 tasks, got {len(tasks)}"

    def test_tasks_json_has_test_group(self) -> None:
        """
        Invariant: At least one task must belong to the 'test' group.

        Falsifies if: no task has group 'test' or group.kind 'test'.
        falsifies_if: no_test_group_task
        """
        data = json.loads((REPO_ROOT / ".vscode" / "tasks.json").read_text())
        has_test_group = False
        for task in data.get("tasks", []):
            g = task.get("group", "")
            if g == "test" or (isinstance(g, dict) and g.get("kind") == "test"):
                has_test_group = True
                break
        assert has_test_group, "No task with group 'test' found"


# ---------------------------------------------------------------------------
# 3. pyrightconfig.json
# ---------------------------------------------------------------------------


class TestPyrightConfig:
    """Tests for pyrightconfig.json (Gap #23)."""

    def test_pyrightconfig_exists(self) -> None:
        """
        Invariant: pyrightconfig.json must exist at repo root.

        Falsifies if: file not found.
        falsifies_if: file_not_found
        """
        assert (REPO_ROOT / "pyrightconfig.json").exists()

    def test_pyrightconfig_valid_json(self) -> None:
        """
        Invariant: pyrightconfig.json must be valid JSON.

        Falsifies if: json.JSONDecodeError raised on parse.
        falsifies_if: json_parse_error
        """
        data = json.loads((REPO_ROOT / "pyrightconfig.json").read_text())
        assert isinstance(data, dict)

    def test_pyrightconfig_strict_mode(self) -> None:
        """
        Invariant: pyrightconfig.json must set typeCheckingMode to 'strict'.

        Falsifies if: typeCheckingMode is absent or not 'strict'.
        falsifies_if: typeCheckingMode_not_strict
        """
        data = json.loads((REPO_ROOT / "pyrightconfig.json").read_text())
        assert data.get("typeCheckingMode") == "strict", (
            f"Expected typeCheckingMode='strict', got {data.get('typeCheckingMode')!r}"
        )

    def test_pyrightconfig_has_include(self) -> None:
        """
        Invariant: pyrightconfig.json must have an 'include' array covering source dirs.

        Falsifies if: 'include' key is absent or empty.
        falsifies_if: include_absent_or_empty
        """
        data = json.loads((REPO_ROOT / "pyrightconfig.json").read_text())
        include = data.get("include", [])
        assert len(include) >= 3, f"Expected ≥3 include paths, got {len(include)}"


# ---------------------------------------------------------------------------
# 4. mcp/oe-basic.mcp.json
# ---------------------------------------------------------------------------


class TestMCPDescriptor:
    """Tests for mcp/oe-basic.mcp.json (Gap #24)."""

    def test_mcp_json_exists(self) -> None:
        """
        Invariant: mcp/oe-basic.mcp.json must exist.

        Falsifies if: file not found.
        falsifies_if: file_not_found
        """
        assert (REPO_ROOT / "mcp" / "oe-basic.mcp.json").exists()

    def test_mcp_json_valid_json(self) -> None:
        """
        Invariant: mcp/oe-basic.mcp.json must be valid JSON.

        Falsifies if: json.JSONDecodeError raised on parse.
        falsifies_if: json_parse_error
        """
        data = json.loads((REPO_ROOT / "mcp" / "oe-basic.mcp.json").read_text())
        assert isinstance(data, dict)

    def test_mcp_json_has_minimum_tools(self) -> None:
        """
        Invariant: mcp/oe-basic.mcp.json must define at least 5 tools.

        Falsifies if: tools array has fewer than 5 entries.
        falsifies_if: fewer_than_5_tools
        """
        data = json.loads((REPO_ROOT / "mcp" / "oe-basic.mcp.json").read_text())
        tools = data.get("tools", [])
        assert len(tools) >= 5, f"Expected ≥5 tools, got {len(tools)}"

    def test_mcp_json_has_required_tools(self) -> None:
        """
        Invariant: mcp/oe-basic.mcp.json must include health_check and popperian_audit tools.

        Falsifies if: either 'run_health_check' or 'run_popperian_audit' tool name absent.
        falsifies_if: required_tool_names_absent
        """
        data = json.loads((REPO_ROOT / "mcp" / "oe-basic.mcp.json").read_text())
        tool_names = {t.get("name") for t in data.get("tools", [])}
        assert "run_health_check" in tool_names
        assert "run_popperian_audit" in tool_names

    def test_mcp_json_has_resources(self) -> None:
        """
        Invariant: mcp/oe-basic.mcp.json must define at least 3 resources.

        Falsifies if: resources array has fewer than 3 entries.
        falsifies_if: fewer_than_3_resources
        """
        data = json.loads((REPO_ROOT / "mcp" / "oe-basic.mcp.json").read_text())
        resources = data.get("resources", [])
        assert len(resources) >= 3, f"Expected ≥3 resources, got {len(resources)}"


# ---------------------------------------------------------------------------
# 5. .ai_registry.json
# ---------------------------------------------------------------------------


class TestAIRegistry:
    """Tests for .ai_registry.json (Gap #25)."""

    def test_ai_registry_exists(self) -> None:
        """
        Invariant: .ai_registry.json must exist at repo root.

        Falsifies if: file not found.
        falsifies_if: file_not_found
        """
        assert (REPO_ROOT / ".ai_registry.json").exists()

    def test_ai_registry_valid_json(self) -> None:
        """
        Invariant: .ai_registry.json must be valid JSON.

        Falsifies if: json.JSONDecodeError raised on parse.
        falsifies_if: json_parse_error
        """
        data = json.loads((REPO_ROOT / ".ai_registry.json").read_text())
        assert isinstance(data, dict)

    def test_ai_registry_has_wardens(self) -> None:
        """
        Invariant: .ai_registry.json must have a 'wardens' key with ≥1 entry.

        Falsifies if: 'wardens' key absent or empty.
        falsifies_if: wardens_absent_or_empty
        """
        data = json.loads((REPO_ROOT / ".ai_registry.json").read_text())
        wardens = data.get("wardens", {})
        assert len(wardens) >= 1, "No wardens found in .ai_registry.json"

    def test_ai_registry_has_agents(self) -> None:
        """
        Invariant: .ai_registry.json must have an 'agents' array with ≥10 entries.

        Falsifies if: 'agents' key absent or has fewer than 10 entries.
        falsifies_if: agents_absent_or_fewer_than_10
        """
        data = json.loads((REPO_ROOT / ".ai_registry.json").read_text())
        agents = data.get("agents", [])
        assert len(agents) >= 10, f"Expected ≥10 agents, got {len(agents)}"

    def test_ai_registry_has_standards_registry_ref(self) -> None:
        """
        Invariant: .ai_registry.json must reference STANDARDS_REGISTRY.json.

        Falsifies if: 'standards_registry' key absent.
        falsifies_if: standards_registry_ref_absent
        """
        data = json.loads((REPO_ROOT / ".ai_registry.json").read_text())
        assert "standards_registry" in data


# ---------------------------------------------------------------------------
# 6. tools/state_witness/alert_on_failure.py
# ---------------------------------------------------------------------------


class TestAlertOnFailure:
    """Tests for tools/state_witness/alert_on_failure.py (P3)."""

    def test_alert_on_failure_exists(self) -> None:
        """
        Invariant: tools/state_witness/alert_on_failure.py must exist.

        Falsifies if: file not found.
        falsifies_if: file_not_found
        """
        assert (REPO_ROOT / "tools" / "state_witness" / "alert_on_failure.py").exists()

    def test_alert_on_failure_importable(self) -> None:
        """
        Invariant: alert_on_failure module must be importable.

        Falsifies if: ImportError raised.
        falsifies_if: import_error
        """
        sys.path.insert(0, str(REPO_ROOT))
        try:
            import tools.state_witness.alert_on_failure as m  # noqa: F401
            assert hasattr(m, "build_alert")
            assert hasattr(m, "maybe_alert")
        finally:
            sys.path.pop(0)

    def test_build_alert_returns_required_keys(self) -> None:
        """
        Invariant: build_alert must return dict with all required keys.

        Falsifies if: any required key is missing from returned dict.
        falsifies_if: required_key_missing
        """
        sys.path.insert(0, str(REPO_ROOT))
        try:
            from tools.state_witness.alert_on_failure import build_alert
            alert = build_alert(exit_code=1, stderr_content="chain break detected")
            required_keys = {
                "timestamp", "failure_type", "exit_code",
                "stderr_excerpt", "last_known_good_row", "recommended_action"
            }
            assert required_keys.issubset(set(alert.keys())), (
                f"Missing keys: {required_keys - set(alert.keys())}"
            )
        finally:
            sys.path.pop(0)

    def test_maybe_alert_no_alert_on_zero_exit(self) -> None:
        """
        Invariant: maybe_alert must return (False, proof) when exit_code=0.

        Falsifies if: returns True when exit_code == 0.
        falsifies_if: alert_emitted_for_zero_exit
        """
        sys.path.insert(0, str(REPO_ROOT))
        try:
            from tools.state_witness.alert_on_failure import maybe_alert
            emitted, proof = maybe_alert(exit_code=0, stderr_content="")
            assert emitted is False
        finally:
            sys.path.pop(0)

    def test_maybe_alert_emits_on_nonzero_exit(self, capsys: pytest.CaptureFixture[str]) -> None:
        """
        Invariant: maybe_alert must return (True, proof) and print JSON when exit_code!=0.

        Falsifies if: returns False or prints nothing when exit_code != 0.
        falsifies_if: no_alert_for_nonzero_exit
        """
        sys.path.insert(0, str(REPO_ROOT))
        try:
            from tools.state_witness.alert_on_failure import maybe_alert
            emitted, proof = maybe_alert(exit_code=1, stderr_content="chain hash mismatch")
            assert emitted is True
            captured = capsys.readouterr()
            data = json.loads(captured.out.strip())
            assert data["failure_type"] == "chain_break"
        finally:
            sys.path.pop(0)


# ---------------------------------------------------------------------------
# 7. docs/AGENT_FEED_NOTES.md
# ---------------------------------------------------------------------------


class TestAgentFeedNotes:
    """Tests for docs/AGENT_FEED_NOTES.md (P4)."""

    def test_agent_feed_notes_exists(self) -> None:
        """
        Invariant: docs/AGENT_FEED_NOTES.md must exist.

        Falsifies if: file not found.
        falsifies_if: file_not_found
        """
        assert (REPO_ROOT / "docs" / "AGENT_FEED_NOTES.md").exists()

    def test_agent_feed_notes_mentions_genesis(self) -> None:
        """
        Invariant: docs/AGENT_FEED_NOTES.md must document the genesis row.

        Falsifies if: word 'genesis' absent from file content.
        falsifies_if: genesis_not_mentioned
        """
        content = (REPO_ROOT / "docs" / "AGENT_FEED_NOTES.md").read_text().lower()
        assert "genesis" in content

    def test_agent_feed_notes_mentions_gap(self) -> None:
        """
        Invariant: docs/AGENT_FEED_NOTES.md must document timestamp gaps.

        Falsifies if: word 'gap' absent from file content.
        falsifies_if: gap_not_mentioned
        """
        content = (REPO_ROOT / "docs" / "AGENT_FEED_NOTES.md").read_text().lower()
        assert "gap" in content
