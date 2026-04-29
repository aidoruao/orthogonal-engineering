"""
Crusader Combat Refrigerator - Hash Utilities
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Cryptographic hash utilities for SHA-256, Merkle trees, and integrity verification.
"""

import hashlib
import hmac
import json
import os
import time
from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4


class HashAlgorithm(Enum):
    """Supported hash algorithms."""

    SHA256 = auto()
    SHA512 = auto()
    SHA3_256 = auto()
    SHA3_512 = auto()
    BLAKE2B = auto()
    BLAKE2S = auto()


class HashFormat(Enum):
    """Hash output formats."""

    HEX = auto()
    BASE64 = auto()
    BINARY = auto()
    INT = auto()


@dataclass
class HashResult:
    """Result of a hash operation."""

    algorithm: str
    hash_value: str
    format: str
    timestamp: datetime
    input_size_bytes: int
    computation_time_ms: float
    salt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        # TODO: Expand to_json() - stub detected by Yeshua Agent
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class MerkleNode:
    """Merkle tree node."""

    node_id: str
    hash_value: str
    level: int
    position: int
    is_leaf: bool
    left_child: Optional[str] = None
    right_child: Optional[str] = None
    parent: Optional[str] = None
    data_reference: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HashEngine:
    """
    Cryptographic hash engine with support for multiple algorithms.
    Provides secure hashing, HMAC, and salt generation.
    """

    ALGORITHM_MAP = {
        HashAlgorithm.SHA256: hashlib.sha256,
        HashAlgorithm.SHA512: hashlib.sha512,
        HashAlgorithm.SHA3_256: hashlib.sha3_256,
        HashAlgorithm.SHA3_512: hashlib.sha3_512,
        HashAlgorithm.BLAKE2B: hashlib.blake2b,
        HashAlgorithm.BLAKE2S: hashlib.blake2s,
    }

    DEFAULT_ALGORITHM = HashAlgorithm.SHA256
    DEFAULT_SALT_SIZE = 16  # 128-bit salt
    DEFAULT_ITERATIONS = 100000  # For key derivation

    def __init__(self):
        """Initialize the hash engine."""
        self.algorithm = self.DEFAULT_ALGORITHM
        self.salt_size = self.DEFAULT_SALT_SIZE
        self.iterations = self.DEFAULT_ITERATIONS
        self.hash_cache: Dict[str, HashResult] = {}
        self.cache_max_size = 1000

        # Statistics
        self.statistics = {
            "total_hashes": 0,
            "hashes_by_algorithm": {alg.name: 0 for alg in HashAlgorithm},
            "cache_hits": 0,
            "cache_misses": 0,
            "average_hash_time_ms": 0.0,
            "total_hash_time_ms": 0.0,
        }

    def initialize(self):
        """Initialize the hash engine."""
        print("🔧 Initializing Hash Engine...")
        self.hash_cache.clear()
        print(f"✅ Hash Engine initialized with {self.algorithm.name}")

    def set_algorithm(self, algorithm: HashAlgorithm):
        """Set the default hash algorithm."""
        if algorithm in self.ALGORITHM_MAP:
            self.algorithm = algorithm
            print(f"🔧 Hash algorithm set to {algorithm.name}")
        else:
            print(f"❌ Unsupported algorithm: {algorithm}")

    def generate_salt(self, size: Optional[int] = None) -> str:
        """Generate cryptographically secure salt."""
        salt_size = size or self.salt_size
        salt = os.urandom(salt_size)
        return b64encode(salt).decode("utf-8")

    def hash_data(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        algorithm: Optional[HashAlgorithm] = None,
        salt: Optional[str] = None,
        format: HashFormat = HashFormat.HEX,
        cache_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HashResult:
        """
        Hash data with optional salt.

        Args:
            data: Data to hash (string, bytes, or dictionary)
            algorithm: Hash algorithm to use
            salt: Optional salt for the hash
            format: Output format
            cache_key: Optional cache key for reuse
            metadata: Optional metadata for the hash result

        Returns:
            HashResult object
        """
        start_time = time.time()

        # Use specified algorithm or default
        algo = algorithm or self.algorithm
        hash_func = self.ALGORITHM_MAP.get(algo)

        if not hash_func:
            raise ValueError(f"Unsupported algorithm: {algo}")

        # Prepare data
        if isinstance(data, dict):
            data_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
        elif isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        input_size = len(data_bytes)

        # Check cache
        if cache_key and cache_key in self.hash_cache:
            self.statistics["cache_hits"] += 1
            cached_result = self.hash_cache[cache_key]
            # Update timestamp
            cached_result.timestamp = datetime.now()
            return cached_result

        self.statistics["cache_misses"] += 1

        # Apply salt if provided
        if salt:
            salt_bytes = b64decode(salt.encode("utf-8"))
            data_bytes = salt_bytes + data_bytes

        # Compute hash
        hash_obj = hash_func(data_bytes)
        hash_bytes = hash_obj.digest()

        # Format output
        if format == HashFormat.HEX:
            hash_value = hash_obj.hexdigest()
        elif format == HashFormat.BASE64:
            hash_value = b64encode(hash_bytes).decode("utf-8")
        elif format == HashFormat.BINARY:
            hash_value = hash_bytes
        elif format == HashFormat.INT:
            hash_value = str(int.from_bytes(hash_bytes, byteorder="big"))
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Calculate computation time
        computation_time = (time.time() - start_time) * 1000

        # Create result
        result = HashResult(
            algorithm=algo.name,
            hash_value=hash_value,
            format=format.name,
            timestamp=datetime.now(),
            input_size_bytes=input_size,
            computation_time_ms=computation_time,
            salt=salt,
            metadata=metadata,
        )

        # Update statistics
        self.statistics["total_hashes"] += 1
        self.statistics["hashes_by_algorithm"][algo.name] += 1
        self.statistics["total_hash_time_ms"] += computation_time
        self.statistics["average_hash_time_ms"] = (
            self.statistics["total_hash_time_ms"] / self.statistics["total_hashes"]
        )

        # Cache result
        if cache_key:
            self._add_to_cache(cache_key, result)

        return result

    def _add_to_cache(self, key: str, result: HashResult):
        """Add hash result to cache."""
        if len(self.hash_cache) >= self.cache_max_size:
            # Remove oldest entry (FIFO)
            oldest_key = next(iter(self.hash_cache))
            del self.hash_cache[oldest_key]

        self.hash_cache[key] = result

    def hmac_hash(
        self,
        data: Union[str, bytes],
        key: Union[str, bytes],
        algorithm: Optional[HashAlgorithm] = None,
        format: HashFormat = HashFormat.HEX,
    ) -> HashResult:
        """
        Compute HMAC hash.

        Args:
            data: Data to hash
            key: HMAC key
            algorithm: Hash algorithm to use
            format: Output format

        Returns:
            HashResult object
        """
        start_time = time.time()

        # Use specified algorithm or default
        algo = algorithm or self.algorithm
        hash_name = algo.name.lower().replace("_", "-")

        # Prepare data and key
        if isinstance(data, str):
            data_bytes = data.encode("utf-8")
        else:
            data_bytes = data

        if isinstance(key, str):
            key_bytes = key.encode("utf-8")
        else:
            key_bytes = key

        input_size = len(data_bytes)

        # Compute HMAC
        hmac_obj = hmac.new(key_bytes, data_bytes, digestmod=hash_name)
        hmac_bytes = hmac_obj.digest()

        # Format output
        if format == HashFormat.HEX:
            hash_value = hmac_obj.hexdigest()
        elif format == HashFormat.BASE64:
            hash_value = b64encode(hmac_bytes).decode("utf-8")
        elif format == HashFormat.BINARY:
            hash_value = hmac_bytes
        elif format == HashFormat.INT:
            hash_value = str(int.from_bytes(hmac_bytes, byteorder="big"))
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Calculate computation time
        computation_time = (time.time() - start_time) * 1000

        # Create result
        return HashResult(
            algorithm=f"HMAC-{algo.name}",
            hash_value=hash_value,
            format=format.name,
            timestamp=datetime.now(),
            input_size_bytes=input_size,
            computation_time_ms=computation_time,
            metadata={"key_size": len(key_bytes)},
        )

    def verify_hash(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        expected_hash: str,
        algorithm: Optional[HashAlgorithm] = None,
        salt: Optional[str] = None,
        format: HashFormat = HashFormat.HEX,
    ) -> Tuple[bool, Optional[HashResult]]:
        """
        Verify data against expected hash.

        Returns:
            Tuple of (is_valid, hash_result)
        """
        # Compute hash of data
        hash_result = self.hash_data(
            data=data,
            algorithm=algorithm,
            salt=salt,
            format=format,
        )

        # Compare hashes
        is_valid = hash_result.hash_value == expected_hash

        if not is_valid:
            print(f"❌ Hash verification failed")
            print(f"   Expected: {expected_hash}")
            print(f"   Got: {hash_result.hash_value}")

        return is_valid, hash_result

    def verify_hmac(
        self,
        data: Union[str, bytes],
        key: Union[str, bytes],
        expected_hmac: str,
        algorithm: Optional[HashAlgorithm] = None,
        format: HashFormat = HashFormat.HEX,
    ) -> Tuple[bool, Optional[HashResult]]:
        """
        Verify HMAC.

        Returns:
            Tuple of (is_valid, hmac_result)
        """
        # Compute HMAC
        hmac_result = self.hmac_hash(
            data=data,
            key=key,
            algorithm=algorithm,
            format=format,
        )

        # Compare
        is_valid = hmac_result.hash_value == expected_hmac

        if not is_valid:
            print(f"❌ HMAC verification failed")
            print(f"   Expected: {expected_hmac}")
            print(f"   Got: {hmac_result.hash_value}")

        return is_valid, hmac_result

    def hash_file(
        self,
        file_path: str,
        algorithm: Optional[HashAlgorithm] = None,
        chunk_size: int = 8192,
        format: HashFormat = HashFormat.HEX,
    ) -> HashResult:
        """
        Hash a file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm to use
            chunk_size: Chunk size for reading large files
            format: Output format

        Returns:
            HashResult object
        """
        start_time = time.time()

        # Use specified algorithm or default
        algo = algorithm or self.algorithm
        hash_func = self.ALGORITHM_MAP.get(algo)

        if not hash_func:
            raise ValueError(f"Unsupported algorithm: {algo}")

        # Initialize hash object
        hash_obj = hash_func()

        # Get file size
        file_size = os.path.getsize(file_path)

        # Hash file in chunks
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)

        hash_bytes = hash_obj.digest()

        # Format output
        if format == HashFormat.HEX:
            hash_value = hash_obj.hexdigest()
        elif format == HashFormat.BASE64:
            hash_value = b64encode(hash_bytes).decode("utf-8")
        elif format == HashFormat.BINARY:
            hash_value = hash_bytes
        elif format == HashFormat.INT:
            hash_value = str(int.from_bytes(hash_bytes, byteorder="big"))
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Calculate computation time
        computation_time = (time.time() - start_time) * 1000

        # Create result
        return HashResult(
            algorithm=algo.name,
            hash_value=hash_value,
            format=format.name,
            timestamp=datetime.now(),
            input_size_bytes=file_size,
            computation_time_ms=computation_time,
            metadata={
                "file_path": file_path,
                "chunk_size": chunk_size,
            },
        )

    def generate_key_derivation(
        self,
        password: str,
        salt: Optional[str] = None,
        iterations: Optional[int] = None,
        key_length: int = 32,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    ) -> Tuple[str, str]:
        """
        Generate key from password using PBKDF2.

        Returns:
            Tuple of (derived_key, salt_used)
        """
        # Generate salt if not provided
        if not salt:
            salt = self.generate_salt()

        # Convert to bytes
        password_bytes = password.encode("utf-8")
        salt_bytes = b64decode(salt.encode("utf-8"))

        # Use specified iterations or default
        iters = iterations or self.iterations

        # Derive key
        hash_name = algorithm.name.lower().replace("_", "-")
        derived_key = hashlib.pbkdf2_hmac(
            hash_name,
            password_bytes,
            salt_bytes,
            iters,
            dklen=key_length,
        )

        # Encode result
        key_b64 = b64encode(derived_key).decode("utf-8")

        return key_b64, salt

    def get_statistics(self) -> Dict[str, Any]:
        """Get hash engine statistics."""
        stats = self.statistics.copy()
        stats["cache_size"] = len(self.hash_cache)
        stats["cache_max_size"] = self.cache_max_size
        stats["current_algorithm"] = self.algorithm.name
        return stats

    def clear_cache(self):
        """Clear hash cache."""
        self.hash_cache.clear()
        print("🧹 Hash cache cleared")


class MerkleTree:
    """
    Merkle tree implementation for efficient data integrity verification.
    Supports incremental updates and proof generation.
    """

    def __init__(self, algorithm: HashAlgorithm = HashAlgorithm.SHA256):
        """Initialize Merkle tree."""
        self.algorithm = algorithm
        self.hash_engine = HashEngine()
        self.hash_engine.set_algorithm(algorithm)
        self.root: Optional[MerkleNode] = None
        self.leaves: Dict[str, MerkleNode] = {}
        self.nodes: Dict[str, MerkleNode] = {}
        self.leaf_count = 0

    def build_from_data(
        self, data_items: List[Union[str, bytes, Dict[str, Any]]]
    ) -> MerkleNode:
        """Build Merkle tree from list of data items."""
        print(f"🌳 Building Merkle tree with {len(data_items)} items...")

        # Clear existing tree
        self.leaves.clear()
        self.nodes.clear()

        # Create leaf nodes
        leaves = []
        for i, data in enumerate(data_items):
            leaf_id = f"leaf_{i}"
            hash_result = self.hash_engine.hash_data(data, algorithm=self.algorithm)

            leaf_node = MerkleNode(
                node_id=leaf_id,
                hash_value=hash_result.hash_value,
                level=0,
                position=i,
                is_leaf=True,
                data_reference=f"data_{i}",
                metadata={"hash_result": hash_result.to_dict()},
            )

            leaves.append(leaf_node)
            self.leaves[leaf_id] = leaf_node
            self.nodes[leaf_id] = leaf_node

        self.leaf_count = len(leaves)

        # Build tree from leaves
        self.root = self._build_tree(leaves, level=1)

        print(f"✅ Merkle tree built. Root hash: {self.root.hash_value}")
        return self.root

    def _build_tree(self, nodes: List[MerkleNode], level: int) -> MerkleNode:
        """Recursively build tree from nodes."""
        if len(nodes) == 1:
            return nodes[0]

        parent_nodes = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else left  # Duplicate if odd

            # Combine hashes
            combined = left.hash_value + right.hash_value
            hash_result = self.hash_engine.hash_data(combined, algorithm=self.algorithm)

            parent_id = f"node_{level}_{i // 2}"
            parent_node = MerkleNode(
                node_id=parent_id,
                hash_value=hash_result.hash_value,
                level=level,
                position=i // 2,
                is_leaf=False,
                left_child=left.node_id,
                right_child=right.node_id if i + 1 < len(nodes) else None,
                data_reference=None,
            )
            parent_nodes.append(parent_node)

        # Recursively build next level
        return self._build_tree(parent_nodes, level + 1)

    def _create_merkle_proof(self, leaf_index: int) -> List[Dict[str, Any]]:
        """Create a Merkle proof for a leaf node."""
        proof = []
        current_index = leaf_index
        current_level = 0

        while current_level < len(self.levels) - 1:
            level_nodes = self.levels[current_level]

            # Determine sibling position
            if current_index % 2 == 0:  # Left child
                sibling_index = current_index + 1
            else:  # Right child
                sibling_index = current_index - 1

            # Add sibling to proof if it exists
            if sibling_index < len(level_nodes):
                sibling = level_nodes[sibling_index]
                proof.append(
                    {
                        "position": "left"
                        if sibling_index < current_index
                        else "right",
                        "hash": sibling.hash_value,
                        "level": current_level,
                        "index": sibling_index,
                    }
                )

            # Move to parent level
            current_index = current_index // 2
            current_level += 1

        return proof

    def verify_merkle_proof(
        self,
        leaf_hash: str,
        proof: List[Dict[str, Any]],
        root_hash: str,
    ) -> bool:
        """Verify a Merkle proof."""
        current_hash = leaf_hash

        for proof_item in proof:
            sibling_hash = proof_item["hash"]
            position = proof_item["position"]

            # Combine hashes based on position
            if position == "left":
                combined = sibling_hash + current_hash
            else:  # right
                combined = current_hash + sibling_hash

            # Hash the combination
            hash_result = self.hash_engine.hash_data(combined, algorithm=self.algorithm)
            current_hash = hash_result.hash_value

        return current_hash == root_hash

    def get_tree_summary(self) -> Dict[str, Any]:
        """Get summary of the Merkle tree."""
        return {
            "root_hash": self.root_hash,
            "leaf_count": self.leaf_count,
            "tree_height": len(self.levels),
            "levels": len(self.levels),
            "algorithm": self.algorithm.name,
            "timestamp": datetime.now().isoformat(),
        }

    def export_tree(self) -> Dict[str, Any]:
        """Export the entire Merkle tree structure."""
        exported_levels = []
        for level_idx, level_nodes in enumerate(self.levels):
            level_data = []
            for node in level_nodes:
                level_data.append(
                    {
                        "node_id": node.node_id,
                        "hash": node.hash_value,
                        "level": node.level,
                        "position": node.position,
                        "is_leaf": node.is_leaf,
                        "left_child": node.left_child,
                        "right_child": node.right_child,
                        "data_reference": node.data_reference,
                    }
                )
            exported_levels.append(level_data)

        return {
            "root_hash": self.root_hash,
            "leaf_count": self.leaf_count,
            "levels": exported_levels,
            "algorithm": self.algorithm.name,
            "timestamp": datetime.now().isoformat(),
        }


# Convenience functions for common hashing operations
def hash_file(
    file_path: str, algorithm: HashAlgorithm = HashAlgorithm.SHA256
) -> HashResult:
    """Hash a file."""
    engine = HashEngine()
    return engine.hash_file(file_path, algorithm)


def hash_string(
    # TODO: Expand hash_string() - stub detected by Yeshua Agent
    data: str, algorithm: HashAlgorithm = HashAlgorithm.SHA256
) -> HashResult:
    """Hash a string."""
    engine = HashEngine()
    return engine.hash_data(data.encode("utf-8"), algorithm)


def create_merkle_tree(
    # TODO: Expand create_merkle_tree() - stub detected by Yeshua Agent
    data_items: List[bytes], algorithm: HashAlgorithm = HashAlgorithm.SHA256
) -> MerkleTree:
    """Create a Merkle tree from data items."""
    tree = MerkleTree(algorithm=algorithm)
    tree.build_tree(data_items)
    return tree


if __name__ == "__main__":
    # Test the hash utilities
    print("Testing Hash Utilities...")

    # Test basic hashing
    engine = HashEngine()
    test_data = b"test data for hashing"
    result = engine.hash_data(test_data, HashAlgorithm.SHA256)
    print(f"SHA256 hash: {result.hash_value}")

    # Test Merkle tree
    data_items = [b"item1", b"item2", b"item3", b"item4"]
    tree = MerkleTree()
    tree.build_tree(data_items)
    print(f"Merkle root: {tree.root_hash}")
    print(f"Tree height: {len(tree.levels)}")

    # Test proof generation and verification
    proof = tree._create_merkle_proof(0)
    print(f"Proof for leaf 0: {len(proof)} items")

    leaf_hash = tree.levels[0][0].hash_value
    is_valid = tree.verify_merkle_proof(leaf_hash, proof, tree.root_hash)
    print(f"Proof valid: {is_valid}")

    print("✅ Hash utilities test completed")
