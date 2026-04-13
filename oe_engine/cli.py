"""oe_engine.cli — Terminal entry point for the OE Engine.

Usage:
  python -m oe_engine.cli "query text"
  python -m oe_engine.cli --interactive
  python -m oe_engine.cli --mode conversation
  python -m oe_engine.cli "query" --context '{"domain": "value"}' --json

Interactive conversation commands:
  /export   — save transcript as JSON with Merkle proof
  /quit     — exit the conversation REPL

falsifies_if: CLI produces different output for identical query + context.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from oe_engine import __version__
from oe_engine.engine import OrthogonalEngine


def _print_result(result: Any, as_json: bool) -> None:
    """Print an engine result in text or JSON format."""
    if as_json:
        print(json.dumps({
            "text": result.text,
            "confidence": str(result.confidence),
            "thinker_hash": result.thinker_hash,
            "speaker_hash": result.speaker_hash,
            "proof_count": len(result.proof_chain),
        }, indent=2))
    else:
        print(result.text)


def run_single_query(
    engine: OrthogonalEngine,
    query: str,
    context: Dict[str, Any],
    as_json: bool,
) -> None:
    """Run one query through a provided engine instance."""
    result = engine.query(query, context)
    _print_result(result, as_json)


def run_interactive_repl(
    engine: OrthogonalEngine,
    as_json: bool,
    prompt: str = "oe> ",
    banner_name: str = "Orthogonal Engine",
) -> None:
    """Run single-turn interactive REPL using the provided engine."""
    print(f"{banner_name} {__version__} — type 'exit' to quit")
    print(f"Loaded {engine._manifest.domain_count} domains")
    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip().lower() in ("exit", "quit"):
            break
        if not line.strip():
            continue
        result = engine.query(line.strip())
        _print_result(result, as_json)


def run_conversation_repl() -> None:
    """Run the stateful multi-turn conversation REPL.

    Imports ConversationEngine on demand so the base CLI remains importable
    without the conversation module.

    falsifies_if: /export produces a different merkle_root for the same turns.
    """
    from oe_engine.conversation import ConversationEngine  # noqa: PLC0415

    engine = ConversationEngine()
    print("Orthogonal Engine — Conversation Mode")
    print("Commands: /export <file.json>  /quit")
    print("─" * 50)

    while True:
        try:
            line = input("conv> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        if line.lower() in ("/quit", "/exit"):
            break

        if line.lower().startswith("/export"):
            parts = line.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else "transcript.json"
            transcript = engine.export_transcript()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(transcript, f, indent=2)
            print(f"Transcript saved to {filename}")
            print(f"  state_hash:  {transcript['state_hash']}")
            print(f"  merkle_root: {transcript['merkle_root']}")
            continue

        text, new_state = engine.process_turn(line)
        print(text)
        print(f"  [state_hash: {new_state.state_hash[:16]}...]")


def main() -> None:
    """Entry point for the OE Engine CLI."""
    parser = argparse.ArgumentParser(
        prog="oe-engine",
        description="Orthogonal Engine — deterministic invariant-locked AI",
    )
    parser.add_argument("query", nargs="?", help="Query text")
    parser.add_argument(
        "--context",
        "-c",
        type=str,
        default="{}",
        help="JSON context dict (e.g. '{\"reactor_id\": \"R1\"}')",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output raw JSON instead of natural language",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive REPL mode (single-turn engine)",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["conversation"],
        help="Extended mode: 'conversation' for stateful multi-turn REPL",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"Orthogonal Engine {__version__}",
    )
    args = parser.parse_args()

    if args.mode == "conversation":
        run_conversation_repl()
        return

    engine = OrthogonalEngine()

    if args.interactive:
        run_interactive_repl(engine, as_json=args.json)
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    context = json.loads(args.context)
    run_single_query(engine, args.query, context, args.json)


if __name__ == "__main__":
    main()
