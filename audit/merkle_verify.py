"""audit/merkle_verify.py — Merkle Root Comparator.

Recomputes the global and per-domain Merkle roots and compares them against
stored snapshots in merkle/global_root.json and merkle/domain_roots.json.

If the global root mismatches, the tool recomputes per-domain roots to identify
which domains changed.

Run as:
    python3 audit/merkle_verify.py [--output <path>]

Exit code: 0 if match, 1 if stale (informational — stale is expected after changes).
Persists JSON report to audit/MERKLE_VERIFY_REPORT.json by default.

Standard: MERK-001
Falsifies if: reports match when roots differ.
falsifies_if: reports match when roots differ.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject
from merkle.global_merkle import build_global_merkle
from merkle.domain_merkle import build_all_domain_roots

GLOBAL_ROOT_PATH = REPO_ROOT / "merkle" / "global_root.json"
DOMAIN_ROOTS_PATH = REPO_ROOT / "merkle" / "domain_roots.json"
DEFAULT_REPORT_PATH = Path(__file__).parent / "MERKLE_VERIFY_REPORT.json"


def _load_stored_global_root() -> Tuple[Optional[str], Optional[int]]:
    """Load stored global root hash and file count."""
    if not GLOBAL_ROOT_PATH.exists():
        return None, None
    try:
        data = json.loads(GLOBAL_ROOT_PATH.read_text(encoding="utf-8"))
        return data.get("root_hash"), data.get("file_count")
    except (json.JSONDecodeError, OSError):
        return None, None


def _load_stored_domain_roots() -> Dict[str, dict]:
    """Load stored per-domain roots."""
    if not DOMAIN_ROOTS_PATH.exists():
        return {}
    try:
        return json.loads(DOMAIN_ROOTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def run_merkle_verify(
    output_path: Path = DEFAULT_REPORT_PATH,
) -> Tuple[bool, ProofObject]:
    """Run Merkle root verification.

    Falsifies if: reports match when computed and stored roots differ.
    falsifies_if: reports match when computed and stored roots differ.
    """
    computed_root, computed_file_count = build_global_merkle()
    stored_root, stored_file_count = _load_stored_global_root()

    global_match = False
    changed_domains: List[str] = []

    if stored_root is None:
        stale = True
        global_match = False
    else:
        global_match = computed_root == stored_root
        stale = not global_match

    if stale:
        computed_domains = build_all_domain_roots()
        stored_domains = _load_stored_domain_roots()
        for domain, cdata in computed_domains.items():
            sdata = stored_domains.get(domain)
            if sdata is None:
                changed_domains.append(domain)
            elif cdata.get("root_hash") != sdata.get("root_hash"):
                changed_domains.append(domain)
        # Also report domains that were removed
        for domain in stored_domains:
            if domain not in computed_domains:
                changed_domains.append(domain)

    result: Dict[str, Any] = {
        "global_root_match": global_match,
        "computed_root": computed_root,
        "stored_root": stored_root,
        "file_count_computed": computed_file_count,
        "file_count_stored": stored_file_count,
        "changed_domains": sorted(set(changed_domains)),
        "stale": stale,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    conclusion = (
        "PASS: Global Merkle root matches stored snapshot"
        if global_match
        else f"STALE: Global Merkle root differs ({len(changed_domains)} domains changed)"
    )
    proof = ProofObject(
        rule="run_merkle_verify",
        premises=[
            f"computed_root={computed_root}",
            f"stored_root={stored_root}",
        ],
        conclusion=conclusion,
    )
    return global_match, proof


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Merkle root verification"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path for the JSON report",
    )
    args = parser.parse_args(argv)

    passed, proof = run_merkle_verify(output_path=args.output)
    print(proof.conclusion)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
