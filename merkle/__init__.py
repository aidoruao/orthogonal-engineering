"""merkle package — Global Merkle Root generation and Merkle tree utilities"""
from merkle.global_merkle import build_global_merkle, write_global_root


def __getattr__(name):
    """Lazy import merkle.tree symbols to avoid hasher dependency at package load time."""
    _tree_names = {"MerkleNode", "MerkleTree", "MerkleTreeBuilder", "verify_inclusion_proof"}
    if name in _tree_names:
        from merkle import tree as _tree
        return getattr(_tree, name)
    raise AttributeError(f"module 'merkle' has no attribute {name}")
