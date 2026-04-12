"""oe_engine.cli — Terminal entry point for the OE Engine.

Usage:
  python -m oe_engine.cli "query text"
  python -m oe_engine.cli --interactive
  python -m oe_engine.cli "query" --context '{"domain": "value"}' --json

falsifies_if: CLI produces different output for identical query + context.
"""

from __future__ import annotations

import argparse
import json
import sys

from oe_engine.engine import OrthogonalEngine


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
        help="Interactive REPL mode",
    )
    args = parser.parse_args()

    engine = OrthogonalEngine()

    if args.interactive:
        print("Orthogonal Engine v0.1.0 — type 'exit' to quit")
        print(f"Loaded {engine._manifest.domain_count} domains")
        while True:
            try:
                line = input("oe> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if line.strip().lower() in ("exit", "quit"):
                break
            result = engine.query(line.strip())
            if args.json:
                print(json.dumps({
                    "text": result.text,
                    "confidence": str(result.confidence),
                    "thinker_hash": result.thinker_hash,
                    "speaker_hash": result.speaker_hash,
                    "proof_count": len(result.proof_chain),
                }, indent=2))
            else:
                print(result.text)
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    context = json.loads(args.context)
    result = engine.query(args.query, context)

    if args.json:
        print(json.dumps({
            "text": result.text,
            "confidence": str(result.confidence),
            "thinker_hash": result.thinker_hash,
            "speaker_hash": result.speaker_hash,
            "proof_count": len(result.proof_chain),
        }, indent=2))
    else:
        print(result.text)


if __name__ == "__main__":
    main()
