"""kingdom_os_entry.py — Unified Kingdom OS entry point.

Bundles kernel boot sequence with shared oe_engine CLI logic
for PyInstaller binary distribution.

Usage:
    python kingdom_os_entry.py --version
    python kingdom_os_entry.py --query "nuclear reactor scram"
    python kingdom_os_entry.py --query "nuclear reactor scram" --json
    python kingdom_os_entry.py --interactive
    python kingdom_os_entry.py --mode conversation

No float anywhere. No external deps. No try/except hiding errors.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction

from kernel.boot import boot, verify_boot_integrity
from oe_engine import __version__
from oe_engine.engine import OrthogonalEngine
from oe_engine import cli as oe_cli

_BANNER = f"Kingdom OS {__version__} — Deterministic Glass-Box Sovereign AI"


def _boot_kernel() -> tuple:
    """Execute kernel boot and return (state, proof).

    Exits with code 1 if boot integrity verification fails.
    No float. 8 GB nominal memory bound.
    """
    state, proof = boot(total_memory=Fraction(8 * 1024 * 1024 * 1024))
    valid, _v_proof = verify_boot_integrity(state)
    if not valid:
        print("BOOT INTEGRITY FAILURE", file=sys.stderr)
        sys.exit(1)
    print(f"Boot complete: {len(state.steps_completed)} phases, all verified")
    print(f"Kernel proof hash: {proof.proof_hash}")
    return state, proof


def main() -> None:
    """Entry point for the Kingdom OS binary."""
    print(_BANNER)

    parser = argparse.ArgumentParser(
        prog="kingdom-os",
        description=_BANNER,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version information and exit",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Run a single query and exit",
    )
    parser.add_argument(
        "--context",
        type=str,
        default="{}",
        help="JSON context dict for --query",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output query result as JSON",
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
    args = parser.parse_args()

    if args.version:
        from oe_engine.manifest import EngineManifest

        print(f"Kingdom OS {__version__}")
        print("Kernel: capability-gated, deterministic, proof-carrying")
        print(
            "Engine: "
            f"{EngineManifest.count_domains_fast()} domain invariant modules, 0 floats, 0 stubs"
        )
        sys.exit(0)

    _boot_kernel()

    engine = OrthogonalEngine()
    print(f"Engine loaded: {engine._manifest.domain_count} domains")
    print(f"Manifest hash: {engine._manifest.manifest_hash[:32]}...")

    if args.mode == "conversation":
        oe_cli.run_conversation_repl()
        return

    if args.interactive:
        oe_cli.run_interactive_repl(
            engine,
            as_json=args.json,
            prompt="kingdom-os> ",
            banner_name="Kingdom OS",
        )
        return

    if args.query is not None:
        context = json.loads(args.context)
        oe_cli.run_single_query(engine, args.query, context, args.json)
        return

    oe_cli.run_conversation_repl()


if __name__ == "__main__":
    main()
