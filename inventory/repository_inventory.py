#!/usr/bin/env python3
"""
Repository inventory for Yeshua Mathematics domain mapping.
Maps every Python file to its Yeshua domain(s) based on content analysis.
Author: Orthogonal Engineering
"""

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Foundation files exempt from self-audit (they define the system)
EXEMPT_FILES = {
    "mathematical_core.py",
    "peano_kernel.py",
    "repository_inventory.py",
    "verify_yeshua_standard.py",
    "test_peano_axioms.py",
    "test_boolean_algebra.py",
}

# Domain signatures: what to look for in each file
DOMAIN_SIGNATURES = {
    "PEANO-001": [
        r"\bsuccessor\(",
        r"\bpredecessor\(",
        r"\bpeano_add\(",
        r"\bpeano_mul\(",
    ],
    "BOOL-001": [r"\bbool_and\(", r"\bbool_or\(", r"\bbool_not\(", r"\bbool_xor\("],
    "MOD-001": [r"\bmodular_multiply\(", r"\bmod_add\(", r"\bmod_mul\("],
    "ARITH-001": [r"\bint64\(", r"\buint64\(", r"_MASK64", r"_SIGN_BIT"],
    "BIN-001": [r"\blogical_shift_left\(", r"\blogical_shift_right\("],
    "HASH-001": [r"hashlib\.sha256", r"sha256\(", r"hexdigest\("],
    "MERKLE-001": [r"merkle_root", r"leaf_hash", r"node_hash", r"merkle_proof"],
    "CRYPTO-001": [r"hashlib", r"sha256", r"hmac\(", r"pbkdf2"],
    "CHAIN-001": [r"AttestationChain", r"chain_hash", r"append_attestation"],
    "ISA-001": [r"UVM", r"universal_virtual_machine", r"fetch_decode_execute"],
    "BIT-001": [
        r"bitwise_and_emulated",
        r"bitwise_xor_emulated",
        r"bitwise_or_emulated",
    ],
    "ENDIAN-001": [r"struct\.pack", r"little-endian", r"endianness"],
    "WORD-001": [r"_WORD_BITS", r"int64", r"uint64", r"MASK64"],
    "TREE-001": [r"binary_tree", r"BinaryNode", r"tree_", r"root\."],
    "INDUCT-001": [r"induction", r"base_case", r"inductive_step"],
    "INVAR-001": [r"invariant", r"INVAR-", r"preserve_invariant"],
    "FALSIF-001": [r"falsification", r"test_falsification", r"designed_to_fail"],
    "ATTEST-001": [r"attestation", r"witness", r"signature", r"verify_attestation"],
    "ONTOL-001": [r"ontological", r"OI-", r"ontology"],
    "CORRESP-001": [r"correspondence", r"merkle_root.*==", r"truth test"],
    "TRUTH-001": [r"truth inelasticity", r"environmental", r"bend"],
    "AXIOM-001": [r"axiom", r"self-evident", r"primitive"],
}


def hash_file(path: Path) -> str:
    """Return SHA-256 hash of file contents."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def detect_domains(content: str) -> Set[str]:
    """Detect which Yeshua domains are used in a file."""
    domains = set()
    for domain, patterns in DOMAIN_SIGNATURES.items():
        for pattern in patterns:
            if re.search(pattern, content):
                domains.add(domain)
                break
    return domains


def inventory_repository(repo_root: Path) -> Dict:
    """Generate complete inventory of all Python files."""
    inventory = {
        "files": {},
        "domains": {domain: [] for domain in DOMAIN_SIGNATURES},
        "unclassified": [],
        "exempt": [],
        "merkle_root": "",
    }

    all_hashes = []

    for py_file in sorted(repo_root.rglob("*.py")):
        rel_path = str(py_file.relative_to(repo_root))

        # Skip exempt files
        if any(exempt in rel_path for exempt in EXEMPT_FILES):
            inventory["exempt"].append(rel_path)
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            file_hash = hash_file(py_file)
            all_hashes.append(file_hash)

            domains = detect_domains(content)

            file_entry = {
                "path": rel_path,
                "hash": file_hash,
                "size": py_file.stat().st_size,
                "domains": list(domains),
            }
            inventory["files"][rel_path] = file_entry

            if domains:
                for domain in domains:
                    inventory["domains"][domain].append(rel_path)
            else:
                inventory["unclassified"].append(rel_path)

        except Exception as e:
            print(f"Warning: Could not process {rel_path}: {e}")

    # Compute Merkle root of all file hashes
    if all_hashes:
        all_hashes.sort()
        combined = "".join(all_hashes).encode()
        inventory["merkle_root"] = hashlib.sha256(combined).hexdigest()

    return inventory


def main():
    repo_root = Path(__file__).parent.parent
    inventory = inventory_repository(repo_root)

    output_path = repo_root / "inventory" / "domain_map.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)

    print(f"Inventory complete:")
    print(f"  Files: {len(inventory['files'])}")
    print(
        f"  Domains: {len([d for d in inventory['domains'] if inventory['domains'][d]])}"
    )
    print(f"  Unclassified: {len(inventory['unclassified'])}")
    print(f"  Exempt: {len(inventory['exempt'])}")
    print(f"  Merkle root: {inventory['merkle_root']}")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
