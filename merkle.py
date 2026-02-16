"""
Merkle tree implementation for content verification.

Provides hierarchical hashing for efficient content verification.
"""

from typing import List, Optional
from hasher import hash_data


class MerkleNode:
    """Node in a Merkle tree."""
    
    def __init__(self, hash_value: str, left: Optional['MerkleNode'] = None, right: Optional['MerkleNode'] = None):
        """
        Initialize Merkle node.
        
        Args:
            hash_value: Hash value for this node
            left: Left child node
            right: Right child node
        """
        self.hash = hash_value
        self.left = left
        self.right = right
    
    def is_leaf(self) -> bool:
        """Check if node is a leaf."""
        return self.left is None and self.right is None


class MerkleTree:
    """Merkle tree for hierarchical content verification."""
    
    def __init__(self, leaves: List[str]):
        """
        Build Merkle tree from leaf hashes.
        
        Args:
            leaves: List of leaf hash values
            
        Raises:
            ValueError: If leaves list is empty
        """
        if not leaves:
            raise ValueError("Cannot create Merkle tree with no leaves")
        
        self.leaves = leaves
        self.root = self._build_tree(leaves)
    
    def _build_tree(self, hashes: List[str]) -> MerkleNode:
        """
        Recursively build Merkle tree.
        
        Args:
            hashes: List of hash values
            
        Returns:
            Root node of the tree
        """
        if len(hashes) == 1:
            return MerkleNode(hashes[0])
        
        # Build leaf nodes
        nodes = [MerkleNode(h) for h in hashes]
        
        # Build tree bottom-up
        while len(nodes) > 1:
            next_level = []
            
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                
                # Combine hashes
                combined = left.hash + right.hash
                parent_hash = hash_data(combined)
                
                parent = MerkleNode(parent_hash, left, right)
                next_level.append(parent)
            
            nodes = next_level
        
        return nodes[0]
    
    def get_root_hash(self) -> str:
        """Get root hash of the tree."""
        return self.root.hash
    
    def get_proof(self, index: int) -> List[tuple[str, str]]:
        """
        Get Merkle proof for leaf at index.
        
        Args:
            index: Index of leaf to prove
            
        Returns:
            List of (hash, position) tuples for proof path
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.leaves):
            raise IndexError(f"Index {index} out of range for {len(self.leaves)} leaves")
        
        proof = []
        nodes = [MerkleNode(h) for h in self.leaves]
        
        # Track current index as we go up the tree
        current_index = index
        
        while len(nodes) > 1:
            next_level = []
            
            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else left
                
                # If this pair contains our node, add sibling to proof
                if i == current_index or i + 1 == current_index:
                    if i == current_index and i + 1 < len(nodes):
                        # Our node is on left, add right sibling
                        proof.append((right.hash, 'right'))
                    elif i + 1 == current_index:
                        # Our node is on right, add left sibling
                        proof.append((left.hash, 'left'))
                
                combined = left.hash + right.hash
                parent_hash = hash_data(combined)
                parent = MerkleNode(parent_hash, left, right)
                next_level.append(parent)
            
            # Update current index for next level
            current_index = current_index // 2
            nodes = next_level
        
        return proof
    
    def verify_proof(self, leaf_hash: str, index: int, proof: List[tuple[str, str]]) -> bool:
        """
        Verify Merkle proof for a leaf.
        
        Args:
            leaf_hash: Hash of the leaf to verify
            index: Index of the leaf
            proof: Proof path from get_proof()
            
        Returns:
            True if proof is valid
        """
        current_hash = leaf_hash
        
        for sibling_hash, position in proof:
            if position == 'left':
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash
            
            current_hash = hash_data(combined)
        
        return current_hash == self.root.hash
