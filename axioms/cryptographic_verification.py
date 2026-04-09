"""Cryptographic verification — hash chains, Merkle proofs, commitment schemes.

Extends the existing SHA-256 infrastructure with formal proof objects.
All operations return (result, ProofObject) pairs.

Mathematical foundation: Menezes, Oorschot, Vanstone — "Handbook of Applied Cryptography"
Biblical: Proverbs 25:2 — "It is the glory of God to conceal a matter;
to search out a matter is the glory of kings."
"""

import hashlib
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class HashChainLink:
    index: int
    data: str
    previous_hash: str
    current_hash: str


def sha256_hex(data: str) -> str:
    """Deterministic SHA-256 hex digest."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def build_hash_chain(entries: List[str]) -> Tuple[List[HashChainLink], ProofObject]:
    """Build a hash chain from a list of string entries.

    Each link's hash = SHA-256(previous_hash + data).
    Returns the chain and a proof of construction.
    """
    chain: List[HashChainLink] = []
    prev = "0" * 64  # Genesis hash

    for i, entry in enumerate(entries):
        current = sha256_hex(prev + entry)
        chain.append(HashChainLink(
            index=i, data=entry,
            previous_hash=prev, current_hash=current,
        ))
        prev = current

    proof = ProofObject(
        conclusion=f"Hash chain of length {len(chain)} constructed",
        premises=[f"Link {c.index}: {c.current_hash[:16]}..." for c in chain],
        rule="hash_chain_construction",
    )
    return chain, proof


def verify_hash_chain(chain: List[HashChainLink]) -> Tuple[bool, ProofObject]:
    """Verify integrity of a hash chain."""
    for i, link in enumerate(chain):
        expected = sha256_hex(link.previous_hash + link.data)
        if expected != link.current_hash:
            proof = ProofObject(
                conclusion=f"Chain BROKEN at link {i}",
                premises=[f"Expected: {expected[:16]}...", f"Got: {link.current_hash[:16]}..."],
                rule="hash_chain_verification",
            )
            return False, proof

        if i > 0 and link.previous_hash != chain[i - 1].current_hash:
            proof = ProofObject(
                conclusion=f"Chain BROKEN: link {i} previous_hash mismatch",
                premises=[f"Link {i}.prev: {link.previous_hash[:16]}...",
                          f"Link {i-1}.curr: {chain[i-1].current_hash[:16]}..."],
                rule="hash_chain_verification",
            )
            return False, proof

    proof = ProofObject(
        conclusion=f"Hash chain of length {len(chain)} verified intact",
        premises=[f"All {len(chain)} links validated"],
        rule="hash_chain_verification",
    )
    return True, proof


@dataclass
class MerkleNode:
    hash_val: str
    left: Optional["MerkleNode"] = None
    right: Optional["MerkleNode"] = None
    data: Optional[str] = None


def build_merkle_tree(leaves: List[str]) -> Tuple[MerkleNode, ProofObject]:
    """Build a Merkle tree from leaf data strings."""
    if not leaves:
        empty = MerkleNode(hash_val=sha256_hex("EMPTY"))
        proof = ProofObject(
            conclusion="Empty Merkle tree",
            premises=[], rule="merkle_construction",
        )
        return empty, proof

    nodes = [MerkleNode(hash_val=sha256_hex(leaf), data=leaf) for leaf in leaves]

    while len(nodes) > 1:
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else left
            parent_hash = sha256_hex(left.hash_val + right.hash_val)
            next_level.append(MerkleNode(
                hash_val=parent_hash, left=left, right=right,
            ))
        nodes = next_level

    root = nodes[0]
    proof = ProofObject(
        conclusion=f"Merkle root: {root.hash_val[:16]}...",
        premises=[f"Leaf count: {len(leaves)}"],
        rule="merkle_construction",
    )
    return root, proof


def commitment_scheme(secret: str, nonce: str) -> Tuple[str, ProofObject]:
    """Create a cryptographic commitment: C = SHA-256(secret || nonce)."""
    commitment = sha256_hex(secret + nonce)
    proof = ProofObject(
        conclusion=f"Commitment: {commitment[:16]}...",
        premises=["Hiding: commitment reveals nothing about secret",
                   "Binding: cannot open to different secret"],
        rule="commitment_scheme",
    )
    return commitment, proof


def verify_commitment(secret: str, nonce: str, commitment: str) -> Tuple[bool, ProofObject]:
    """Verify a commitment opening."""
    recomputed = sha256_hex(secret + nonce)
    valid = recomputed == commitment
    proof = ProofObject(
        conclusion=f"Commitment {'valid' if valid else 'INVALID'}",
        premises=[f"Recomputed: {recomputed[:16]}...", f"Expected: {commitment[:16]}..."],
        rule="commitment_verification",
    )
    return valid, proof
