#!/usr/bin/env python3
"""
tools/context_window_estimator.py — Token Cost Estimator

Estimates the token cost of reading files or directories, using the
4 characters-per-token heuristic (or tiktoken if available).

Agents with limited context windows use this to plan what to read before
starting a session:
    Kimi    220k tokens
    Claude  200k tokens
    Copilot 128k tokens

Usage:
    python tools/context_window_estimator.py --path src/domains/d_aerospace/
    python tools/context_window_estimator.py --path COPILOT_ONBOARDING.md
    python tools/context_window_estimator.py --path src/domains/ --budget 50000
    python tools/context_window_estimator.py --list-agents

Exit codes:
    0   Estimate produced; within budget (if --budget given)
    1   Budget exceeded
    2   Path not found

Author: Orthogonal Engineering
Gap: #14 (gap analysis 2026-04-17)
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

# Context window sizes in tokens (conservative upper bounds)
AGENT_CONTEXT_WINDOWS: dict[str, int] = {
    "copilot":  128_000,
    "claude":   200_000,
    "devin":    200_000,
    "kimi":     220_000,
    "aider":    128_000,
    "cursor":   128_000,
    "windsurf": 128_000,
    "cline":    128_000,
    "continue": 128_000,
}

# Extensions considered readable text (binary files are skipped)
TEXT_EXTENSIONS = frozenset({
    ".py", ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml",
    ".html", ".css", ".js", ".ts", ".sh", ".toml", ".cfg", ".ini",
    ".rst", ".tex", ".csv",
})

# Heuristic: 4 chars per token
CHARS_PER_TOKEN = Fraction(4)


# ---------------------------------------------------------------------------
# Estimation logic
# ---------------------------------------------------------------------------

def _is_text_file(path: Path) -> bool:
    """Return True if the file extension is in TEXT_EXTENSIONS.

    Falsifies if: returns True for a binary file extension.
    falsifies_if: returns True for a binary file extension.
    """
    return path.suffix.lower() in TEXT_EXTENSIONS


def estimate_file_tokens(path: Path) -> tuple[int, Fraction]:
    """Estimate token count for a single file.

    Returns (char_count, token_estimate_fraction).

    Falsifies if: token_estimate_fraction != char_count / CHARS_PER_TOKEN.
    falsifies_if: token_estimate_fraction != char_count / CHARS_PER_TOKEN.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        chars = Fraction(len(content))
        tokens = chars / CHARS_PER_TOKEN
        return len(content), tokens
    except OSError:
        return 0, Fraction(0)


def _try_tiktoken(text: str) -> int | None:
    """Attempt to use tiktoken for exact token counting. Returns None if unavailable.

    Falsifies if: returns a count that doesn't match tiktoken's actual count.
    falsifies_if: returns a count that doesn't match tiktoken's actual count.
    """
    try:
        import tiktoken  # type: ignore[import-not-found]

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:  # noqa: BLE001
        return None


def estimate_path(
    path: Path,
    *,
    use_tiktoken: bool = False,
    recursive: bool = True,
) -> list[dict[str, Any]]:
    """Estimate token cost for a file or directory.

    Returns a list of per-file result dicts with keys:
        path, chars, tokens, method

    Falsifies if: a result dict has tokens < 0.
    falsifies_if: a result dict has tokens < 0.
    """
    results: list[dict[str, Any]] = []

    if path.is_file():
        files = [path]
    elif path.is_dir():
        if recursive:
            files = sorted(path.rglob("*"))
        else:
            files = sorted(path.iterdir())
        files = [f for f in files if f.is_file() and _is_text_file(f)]
    else:
        return results

    for fpath in files:
        if not _is_text_file(fpath):
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        method = "heuristic"
        if use_tiktoken:
            exact = _try_tiktoken(content)
            if exact is not None:
                tokens = exact
                method = "tiktoken"
            else:
                tokens = int(Fraction(len(content)) / CHARS_PER_TOKEN)
        else:
            tokens = int(Fraction(len(content)) / CHARS_PER_TOKEN)

        try:
            rel = fpath.relative_to(REPO_ROOT)
        except ValueError:
            rel = fpath

        results.append({
            "path": str(rel),
            "chars": len(content),
            "tokens": tokens,
            "method": method,
        })

    return results


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate file-level results into a summary.

    Falsifies if: total_tokens != sum of individual token counts.
    falsifies_if: total_tokens != sum of individual token counts.
    """
    total_chars = sum(r["chars"] for r in results)
    total_tokens = sum(r["tokens"] for r in results)
    return {
        "file_count": len(results),
        "total_chars": total_chars,
        "total_tokens": total_tokens,
        "largest_file": max(results, key=lambda r: r["tokens"])["path"] if results else None,
        "largest_file_tokens": max(r["tokens"] for r in results) if results else 0,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Entry point for the context window estimator.

    Falsifies if: --budget N causes exit 0 when total_tokens > N.
    falsifies_if: --budget N causes exit 0 when total_tokens > N.
    """
    parser = argparse.ArgumentParser(
        description="Estimate token cost of reading files/directories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--path",
        metavar="PATH",
        help="File or directory path to estimate (relative to repo root or absolute).",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=None,
        help="Token budget. Exit 1 if total_tokens exceeds this value.",
    )
    parser.add_argument(
        "--agent",
        choices=sorted(AGENT_CONTEXT_WINDOWS),
        default=None,
        help="Use a named agent's context window as the budget.",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List known agents and their context window sizes.",
    )
    parser.add_argument(
        "--tiktoken",
        action="store_true",
        help="Use tiktoken for exact counts (falls back to heuristic if unavailable).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON.",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not recurse into subdirectories.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Show top N files by token count (default: 10).",
    )

    args = parser.parse_args(argv)

    if args.list_agents:
        for agent, tokens in sorted(AGENT_CONTEXT_WINDOWS.items(), key=lambda x: -x[1]):
            print(f"  {agent:12s}  {tokens:>9,} tokens")
        return 0

    if not args.path:
        parser.print_help()
        return 2

    target = Path(args.path)
    if not target.is_absolute():
        target = REPO_ROOT / target

    if not target.exists():
        print(f"ERROR: Path not found: {target}", file=sys.stderr)
        return 2

    results = estimate_path(
        target,
        use_tiktoken=args.tiktoken,
        recursive=not args.no_recursive,
    )

    summary = summarize_results(results)

    budget = args.budget
    if args.agent:
        budget = AGENT_CONTEXT_WINDOWS[args.agent]

    if args.json:
        output = {
            "path": str(target),
            "summary": summary,
            "budget": budget,
            "budget_exceeded": (budget is not None and summary["total_tokens"] > budget),
            "top_files": sorted(results, key=lambda r: -r["tokens"])[: args.top],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Path: {target}")
        print(f"Files: {summary['file_count']}")
        print(f"Total chars : {summary['total_chars']:>12,}")
        print(f"Total tokens: {summary['total_tokens']:>12,}")
        if budget is not None:
            pct = Fraction(summary["total_tokens"] * 100) / Fraction(max(budget, 1))
            print(f"Budget      : {budget:>12,}  ({int(pct)}% used)")
        top = sorted(results, key=lambda r: -r["tokens"])[: args.top]
        if top:
            print(f"\nTop {min(args.top, len(top))} files by token count:")
            for r in top:
                print(f"  {r['tokens']:>8,}  {r['path']}")

    if budget is not None and summary["total_tokens"] > budget:
        if not args.json:
            print(
                f"\nWARNING: Exceeds budget of {budget:,} tokens by "
                f"{summary['total_tokens'] - budget:,}.",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
