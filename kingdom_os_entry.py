"""kingdom_os_entry.py — Unified Kingdom OS entry point.

Bundles kernel boot sequence + OrthogonalEngine + ConversationEngine
into a single executable for PyInstaller binary distribution.

Usage:
    python kingdom_os_entry.py --version
    python kingdom_os_entry.py --query "nuclear reactor scram"
    python kingdom_os_entry.py --query "nuclear reactor scram" --json
    python kingdom_os_entry.py               # interactive conversation REPL

REPL commands:
    /status               — print domain count, turn count, state_hash
    /export <file.json>   — save transcript as JSON with Merkle proof
    /quit                 — print boot proof hash + conversation merkle root, exit

No float anywhere. No external deps. No try/except hiding errors.
"""

import sys
import json
import argparse
import traceback
from fractions import Fraction
from kernel.boot import boot, verify_boot_integrity
from oe_engine.engine import OrthogonalEngine
from oe_engine.conversation import ConversationEngine

_VERSION = "v2.0.0"
_BANNER = "Kingdom OS v2.0.0 — Deterministic Glass-Box Sovereign AI"


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
        "--json",
        action="store_true",
        help="Output query result as JSON (requires --query)",
    )
    args = parser.parse_args()

    if args.version:
        from oe_engine.manifest import EngineManifest
        manifest = EngineManifest()
        print(f"Kingdom OS {_VERSION}")
        print("Kernel: capability-gated, deterministic, proof-carrying")
        print(f"Engine: {manifest.domain_count} domain invariant modules, 0 floats, 0 stubs")
        sys.exit(0)

    # Boot kernel for all modes
    state, boot_proof = _boot_kernel()

    # Initialize engine
    engine = OrthogonalEngine()
    print(f"Engine loaded: {engine._manifest.domain_count} domains")
    print(f"Manifest hash: {engine._manifest.manifest_hash[:32]}...")

    if args.query is not None:
        # Single-query mode
        result = engine.query(args.query)
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
        sys.exit(0)

    # Interactive conversation REPL
    conversation_engine = ConversationEngine()
    print("Conversation mode — commands: /status  /export <file>  /quit")
    print("─" * 60)

    while True:
        try:
            line = input("kingdom-os> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            _exit_repl(boot_proof, conversation_engine)

        if not line:
            continue

        if line.lower() in ("/quit", "/exit"):
            _exit_repl(boot_proof, conversation_engine)

        if line.lower() == "/status":
            state_info = conversation_engine.state
            print(f"domains: {engine._manifest.domain_count}")
            print(f"turns: {len(state_info.turns)}")
            print(f"state_hash: {state_info.state_hash}")
            continue

        if line.lower().startswith("/export"):
            parts = line.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else "transcript.json"
            transcript = conversation_engine.export_transcript()
            with open(filename, "w", encoding="utf-8") as fh:
                json.dump(transcript, fh, indent=2)
            print(f"Transcript saved to {filename}")
            print(f"  state_hash:  {transcript['state_hash']}")
            print(f"  merkle_root: {transcript['merkle_root']}")
            continue

        text, new_state = conversation_engine.process_turn(line)
        print(text)
        print(f"  [turn {len(new_state.turns) - 1} | state: {new_state.state_hash[:16]}...]")


def _exit_repl(boot_proof: object, conversation_engine: "ConversationEngine") -> None:
    """Print final hashes and exit cleanly."""
    transcript = conversation_engine.export_transcript()
    print(f"\nBoot proof hash:         {boot_proof.proof_hash}")  # type: ignore[attr-defined]
    print(f"Conversation Merkle root: {transcript['merkle_root']}")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}", file=sys.stderr)
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
