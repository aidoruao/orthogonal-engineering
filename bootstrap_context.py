#!/usr/bin/env python3
"""
bootstrap_context.py — Copilot/AI Agent Context Bootstrap

Generates a consolidated CONTEXT BLOCK suitable for pasting into a Copilot or LLM prompt.

Usage:
    python bootstrap_context.py [--chat-dir <dir>] [--max-chat-lines <n>]

Exit codes:
    0  — success; context block printed to stdout
    1  — one or more continuity artifacts missing

Standard library only — no pip install required.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
REQUIRED_ARTIFACTS = ["STATE.md", "MEMORY.md"]
CHAT_LOG_DIR = REPO_ROOT / "chat_logs"
DEFAULT_MAX_CHAT_LINES = 120  # trim large chat logs to this many lines

# Required headings in each artifact (used for a basic sanity check)
REQUIRED_HEADINGS = {
    "MEMORY.md": ["## Architectural Decisions", "## Constraints", "## Open Questions"],
    "STATE.md": ["## ", ],  # STATE.md just needs at least one heading
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_file(path: Path, max_lines: Optional[int] = None) -> str:
    """Read a file and optionally truncate to max_lines."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return f"[ERROR reading {path.name}: {exc}]"
    if max_lines is not None:
        lines = text.splitlines()
        if len(lines) > max_lines:
            text = "\n".join(lines[:max_lines]) + f"\n[... truncated to {max_lines} lines]"
    return text


def _find_latest_handoff(chat_dir: Path) -> Optional[Path]:
    """Return the most recently modified handoff_*.md in chat_dir, or None."""
    if not chat_dir.is_dir():
        return None
    candidates = sorted(
        chat_dir.glob("handoff_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _find_latest_jsonl(chat_dir: Path) -> Optional[Path]:
    """Return the most recently modified *.jsonl in chat_dir, or None."""
    if not chat_dir.is_dir():
        return None
    candidates = sorted(
        chat_dir.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _check_venv() -> str:
    """Return a short venv status message."""
    venv_dir = REPO_ROOT / ".venv"
    if venv_dir.is_dir():
        return f"✅  .venv found at {venv_dir}"
    # Also check if we're already inside any venv
    if os.environ.get("VIRTUAL_ENV"):
        return f"✅  Active venv: {os.environ['VIRTUAL_ENV']}"
    return (
        "⚠️  No .venv detected. Create one with:\n"
        "      python -m venv .venv\n"
        "      source .venv/bin/activate   # Linux/macOS\n"
        "      .venv\\Scripts\\Activate.ps1  # Windows PowerShell"
    )


def _section(title: str, body: str) -> str:
    bar = "=" * 70
    return f"{bar}\n## {title}\n{bar}\n{body}\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_context(chat_dir: Path, max_chat_lines: int) -> Tuple[str, int]:
    """
    Build the consolidated context block.

    Returns (context_text, exit_code).
    exit_code 0 = success, 1 = missing artifacts.
    """
    exit_code = 0
    sections: list[str] = []

    # -- Header --
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections.append(
        _section(
            "ORTHOGONAL ENGINEERING — COPILOT CONTEXT BLOCK",
            f"Generated: {now}\nRepo:      {REPO_ROOT}\nPython:    {sys.version.split()[0]}",
        )
    )

    # -- Venv status --
    sections.append(_section("VENV STATUS", _check_venv()))

    # -- Continuity artifacts --
    for artifact_name in REQUIRED_ARTIFACTS:
        artifact_path = REPO_ROOT / artifact_name
        if not artifact_path.exists():
            sections.append(
                _section(
                    f"ARTIFACT: {artifact_name}",
                    f"❌  MISSING — run continuity_check.py for details",
                )
            )
            exit_code = 1
        else:
            content = _read_file(artifact_path)
            sections.append(_section(f"ARTIFACT: {artifact_name}", content))

    # -- Latest handoff --
    handoff_path = _find_latest_handoff(chat_dir)
    if handoff_path:
        handoff_content = _read_file(handoff_path, max_lines=max_chat_lines)
        sections.append(
            _section(
                f"LATEST HANDOFF: {handoff_path.name}",
                f"(from {handoff_path})\n\n{handoff_content}",
            )
        )
    else:
        sections.append(
            _section(
                "LATEST HANDOFF",
                f"No handoff_*.md found in {chat_dir}\n"
                "This may be a fresh start. Begin by reading MEMORY.md and STATE.md.",
            )
        )

    # -- Latest chat log (jsonl) --
    jsonl_path = _find_latest_jsonl(chat_dir)
    if jsonl_path:
        chat_content = _read_file(jsonl_path, max_lines=max_chat_lines)
        sections.append(
            _section(
                f"LATEST CHAT LOG: {jsonl_path.name}",
                f"(showing last {max_chat_lines} lines)\n\n{chat_content}",
            )
        )

    # -- Tail instructions --
    sections.append(
        _section(
            "NEXT STEPS FOR AI AGENT",
            "1. Read MEMORY.md (durable facts — do not re-derive).\n"
            "2. Read STATE.md (current phase and open questions).\n"
            "3. Review the latest handoff (if present) to find the exact resume point.\n"
            "4. Declare your starting context before doing any work:\n"
            "   CONTEXT LOADED: MEMORY.md ✅ | STATE.md ✅ | Handoff: <date or 'none'>\n"
            "5. When you finish, fill out HANDOFF_TEMPLATE.md and save to chat_logs/.",
        )
    )

    return "\n".join(sections), exit_code


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a consolidated context block for Copilot/LLM prompt."
    )
    parser.add_argument(
        "--chat-dir",
        default=str(CHAT_LOG_DIR),
        help=f"Directory containing chat logs and handoff summaries (default: {CHAT_LOG_DIR})",
    )
    parser.add_argument(
        "--max-chat-lines",
        type=int,
        default=DEFAULT_MAX_CHAT_LINES,
        help=f"Maximum lines to include from chat logs (default: {DEFAULT_MAX_CHAT_LINES})",
    )
    args = parser.parse_args()

    chat_dir = Path(args.chat_dir)
    context, exit_code = build_context(chat_dir, args.max_chat_lines)
    print(context)

    if exit_code != 0:
        print(
            "\n⚠️  Some continuity artifacts are missing. Run `python continuity_check.py` "
            "for a detailed report.",
            file=sys.stderr,
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
