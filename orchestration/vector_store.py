#!/usr/bin/env python3
"""
Vector Store - Orthogonal Engineering Glass-Box Boundary Compliant

Stores and retrieves vector embeddings with metadata using ChromaDB
with fallback to file-based storage. Maintains full Glass-Box Boundary compliance.

Version: 1.0.0
Schema ID: GB-VECTORSTORE-1.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Framework

Glass Box Boundary Compliance:
- @glass_box_boundary decorator on all functions
- Input/output validation schemas
- Side effect confinement through gateway patterns
- Orthogonal separation between storage backends
- Exit code 2 on boundary violations
- Trace generation for all operations
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.boundary_enforcer import glass_box_boundary


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class VectorStoreConfig:
    """Configuration for vector store"""

    def __init__(self,
                 store_type: str = "chromadb",
                 persist_directory: Union[str, Path] = "./vector_db/",
                 collection_name: str = "repository_embeddings",
                 distance_function: str = "cosine",
                 metadata_fields: List[str] = None,
                 cache_enabled: bool = True,
                 cache_size_mb: int = 1000):
        self.store_type = store_type  # "chromadb", "faiss", "file", "memory"
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.distance_function = distance_function
        self.metadata_fields = metadata_fields or [
            "source_file", "file_type", "chunk_index", "line_range",
            "sha256_hash", "boundary_compliance"
        ]
        self.cache_enabled = cache_enabled
        self.cache_size_mb = cache_size_mb

    def to_dict(self) -> Dict:
        return {
            "store_type": self.store_type,
            "persist_directory": str(self.persist_directory),
            "collection_name": self.collection_name,
            "distance_function": self.distance_function,
            "metadata_fields": self.metadata_fields,
            "cache_enabled": self.cache_enabled,
            "cache_size_mb": self.cache_size_mb
        }

    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'VectorStoreConfig':
        return cls(
            store_type=config_dict.get("store_type", "chromadb"),
            persist_directory=config_dict.get("persist_directory", "./vector_db/"),
            collection_name=config_dict.get("collection_name", "repository_embeddings"),
            distance_function=config_dict.get("distance_function", "cosine"),
            metadata_fields=config_dict.get("metadata_fields"),
            cache_enabled=config_dict.get("cache_enabled", True),
            cache_size_mb=config_dict.get("cache_size_mb", 1000)
        )


class StoreResult:
    """Result of storing embeddings"""

    def __init__(self,
                 success: bool,
                 chunks_stored: int,
                 collection_name: str,
                 storage_size_bytes: int,
                 operation_id: str,
                 store_type: str,
                 errors: List[str] = None,
                 warnings: List[str] = None):
        self.success = success
        self.chunks_stored = chunks_stored
        self.collection_name = collection_name
        self.storage_size_bytes = storage_size_bytes
        self.operation_id = operation_id
        self.store_type = store_type
        self.errors = errors or []
        self.warnings = warnings or []
        self.timestamp = datetime.now()

    @property
    def storage_size_mb(self) -> float:
        return self.storage_size_bytes / (1024 * 1024)

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "chunks_stored": self.chunks_stored,
            "collection_name": self.collection_name,
            "storage_size_bytes": self.storage_size_bytes,
            "storage_size_mb": self.storage_size_mb,
            "operation_id": self.operation_id,
            "store_type": self.store_type,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat()
        }


class SearchResult:
    """Result of similarity search"""

    def __init__(self,
                 chunk_id: str,
                 text: str,
                 vector: List[float],
                 similarity_score: float,
                 rank: int,
                 metadata: Dict = None):
        self.chunk_id = chunk_id
        self.text = text
        self.vector = vector
        self.similarity_score = similarity_score
        self.rank = rank
        self.metadata = metadata or {}

    @property
    def dimensions(self) -> int:
        return len(self.vector)

    def to_dict(self) -> Dict:
        return {
            "chunk_id": self.chunk_id,
            "text_preview": self.text[:200] + "..." if len(self.text) > 200 else self.text,
            "text_length": len(self.text),
            "similarity_score": self.similarity_score,
            "rank": self.rank,
            "dimensions": self.dimensions,
            "metadata": self.metadata
        }


class RetrievalResult:
    """Result of retrieving by chunk_id"""

    def __init__(self,
                 chunk_id: str,
                 found: bool,
                 text: str = None,
                 vector: List[float] = None,
                 metadata: Dict = None,
                 retrieval_time_ms: int = 0,
                 error: str = None):
        self.chunk_id = chunk_id
        self.found = found
        self.text = text
        self.vector = vector
        self.metadata = metadata or {}
        self.retrieval_time_ms = retrieval_time_ms
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "chunk_id": self.chunk_id,
            "found": self.found,
            "text": self.text,
            "text_length": len(self.text) if self.text else 0,
            "vector_dimensions": len(self.vector) if self.vector else 0,
            "metadata": self.metadata,
            "retrieval_time_ms": self.retrieval_time_ms,
            "error": self.error
        }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_store_params(chunks: List[Any],
                         vectors: List[List[float]],
                         metadata_list: List[Dict]) -> None:
    """Validate parameters for storing embeddings"""
    if not chunks:
        raise ValueError("Chunks list cannot be empty")

    if not vectors:
        raise ValueError("Vectors list cannot be empty")

    if len(chunks) != len(vectors):
        raise ValueError(f"Chunks and vectors must have same length: {len(chunks)} != {len(vectors)}")

    if metadata_list and len(chunks) != len(metadata_list):
        raise ValueError(f"Chunks and metadata must have same length: {len(chunks)} != {len(metadata_list)}")

    # Validate vectors
    dimensions = set(len(v) for v in vectors)
    if len(dimensions) > 1:
        raise ValueError(f"Inconsistent vector dimensions: {dimensions}")

    dim = next(iter(dimensions))
    if dim < 1 or dim > 10000:
        raise ValueError(f"Invalid vector dimension: {dim}")

    # Validate vectors are not all zeros
    for i, vector in enumerate(vectors):
        if all(abs(x) < 1e-10 for x in vector):
            raise ValueError(f"Vector {i} is all zeros")


def validate_query_params(query_vector: List[float],
                         top_k: int,
                         filters: Dict = None) -> None:
    """Validate parameters for similarity search"""
    if not query_vector:
        raise ValueError("Query vector cannot be empty")

    if len(query_vector) < 1 or len(query_vector) > 10000:
        raise ValueError(f"Invalid query vector dimension: {len(query_vector)}")

    if top_k < 1 or top_k > 1000:
        raise ValueError(f"top_k must be between 1 and 1000: {top_k}")

    if filters and not isinstance(filters, dict):
        raise ValueError(f"Filters must be a dictionary: {type(filters)}")


def validate_search_results(results: List[SearchResult]) -> None:
    """Validate search results"""
    if not results:
        return  # Empty results are valid

    # Check all results have same dimensions
    dimensions = set(result.dimensions for result in results)
    if len(dimensions) > 1:
        raise ValueError(f"Inconsistent result dimensions: {dimensions}")

    # Check similarity scores are in valid range
    for i, result in enumerate(results):
        if not -1.0 <= result.similarity_score <= 1.0:
            raise ValueError(f"Invalid similarity score at index {i}: {result.similarity_score}")


# ============================================================================
# VECTOR STORE CLASS
# ============================================================================

class VectorStore:
    """
    Stores and retrieves vector embeddings with metadata.

    Supports multiple backends:
    - ChromaDB (primary, persistent)
    - File-based (fallback, JSON files)
    - In-memory (testing)

    Glass-Box Boundary Compliance:
    - All public methods use @glass_box_boundary decorator
    - Input validation before operations
    - Output validation after operations
    - Side effects confined to storage operations
    - Orthogonal separation between backends
    - Trace generation for auditability
    """

    def __init__(self,
                 config: Union[Dict, VectorStoreConfig] = None,
                 auto_init: bool = True):
        """
        Initialize vector store.

        Args:
            config: Configuration dictionary or VectorStoreConfig object
            auto_init: Whether to automatically initialize the store
        """
        # Parse configuration
        if isinstance(config, VectorStoreConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = VectorStoreConfig.from_dict(config)
        else:
            self.config = VectorStoreConfig()

        # Create persist directory
        self.config.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize store based on type
        self.store = None
        self.initialized = False

        # Statistics
        self.stats = {
            "operations": {
                "store": 0,
                "search": 0,
                "retrieve": 0,
                "delete": 0
            },
            "chunks_stored": 0,
            "total_storage_bytes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": []
        }

        # Cache for frequent operations
        self.cache = {}

        # Initialize if requested
        if auto_init:
            self.initialize()

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def initialize(self) -> bool:
        """Initialize the vector store backend"""
        try:
            if self.config.store_type == "chromadb":
                self._init_chromadb()
            elif self.config.store_type == "file":
                self._init_file_based()
            elif self.config.store_type == "memory":
                self._init_memory()
            else:
                raise ValueError(f"Unsupported store type: {self.config.store_type}")

            self.initialized = True
            print(f"Vector store initialized: {self.config.store_type}")
            return True

        except Exception as e:
            self.stats["errors"].append(f"Initialization failed: {str(e)}")
            print(f"Warning: Failed to initialize {self.config.store_type} store: {e}")

            # Fall back to file-based storage
            if self.config.store_type != "file":
                print("Falling back to file-based storage")
                self.config.store_type = "file"
                return self.initialize()

            return False

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _init_chromadb(self) -> None:
        """Initialize ChromaDB backend"""
        try:
            import chromadb
            from chromadb.config import Settings

            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.config.persist_directory / "chromadb"),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.config.collection_name
                )
                print(f"Using existing collection: {self.config.collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=self.config.collection_name,
                    metadata={"hnsw:space": self.config.distance_function}
                )
                print(f"Created new collection: {self.config.collection_name}")

            self.store = "chromadb"

        except ImportError:
            raise ImportError(
                "ChromaDB not installed. "
                "Install with: pip install chromadb"
            )

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _init_file_based(self) -> None:
        """Initialize file-based backend (JSON files)"""
        self.data_dir = self.config.persist_directory / "file_store"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self.file_data = {}
        self.file_vectors = {}

        data_file = self.data_dir / "vectors.json"
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.file_data = data.get("metadata", {})
                    self.file_vectors = data.get("vectors", {})
                print(f"Loaded {len(self.file_data)} chunks from file store")
            except Exception as e:
                print(f"Warning: Failed to load file store data: {e}")

        self.store = "file"

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True
    )
    def _init_memory(self) -> None:
        """Initialize in-memory backend (for testing)"""
        self.memory_data = {}
        self.memory_vectors = {}
        self.store = "memory"
        print("Initialized in-memory vector store (testing only)")

    @glass_box_boundary(
        input_validator=validate_store_params,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def store_embeddings(self,
                        chunks: List[Any],
                        vectors: List[List[float]],
                        metadata_list: List[Dict] = None,
                        operation_id: str = None) -> StoreResult:
        """
        Store embeddings with metadata.

        Args:
            chunks: List of chunk objects or chunk IDs
            vectors: List of embedding vectors
            metadata_list: List of metadata dictionaries
            operation_id: Optional operation ID for tracking

        Returns:
            StoreResult object
        """
        if not self.initialized:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        operation_id = operation_id or str(uuid.uuid4())
        start_time = time.time()

        try:
            # Prepare metadata
            if metadata_list is None:
                metadata_list = [{} for _ in range(len(chunks))]

            # Convert chunks to IDs if needed
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                if hasattr(chunk, 'chunk_id'):
                    chunk_ids.append(chunk.chunk_id)
                elif isinstance(chunk, str):
                    chunk_ids.append(chunk)
                else:
                    chunk_ids.append(f"chunk_{i}_{hash(str(chunk))}")

            # Store based on backend
            if self.store == "chromadb":
                result = self._store_chromadb(chunk_ids, vectors, metadata_list)
            elif self.store == "file":
                result = self._store_file_based(chunk_ids, vectors, metadata_list)
            elif self.store == "memory":
                result = self._store_memory(chunk_ids, vectors, metadata_list)
            else:
                raise ValueError(f"Unknown store type: {self.store}")

            # Update statistics
            self.stats["operations"]["store"] += 1
            self.stats["chunks_stored"] += result.chunks_stored

            processing_time = int((time.time() - start_time) * 1000)

            return StoreResult(
                success=True,
                chunks_stored=result.chunks_stored,
                collection_name=self.config.collection_name,
                storage_size_bytes=result.storage_size_bytes,
                operation_id=operation_id,
                store_type=self.store
            )

        except Exception as e:
            self.stats["errors"].append(f"Store operation failed: {str(e)}")

            return StoreResult(
                success=False,
                chunks_stored=0,
                collection_name=self.config.collection_name,
                storage_size_bytes=0,
                operation_id=operation_id,
                store_type=self.store,
                errors=[str(e)]
            )

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True
    )
    def _store_chromadb(self,
                       chunk_ids: List[str],
                       vectors: List[List[float]],
                       metadata_list: List[Dict]) -> Dict:
        """Store embeddings in ChromaDB"""
        # Prepare documents (text representations)
        documents = [f"chunk_{cid}" for cid in chunk_ids]

        # Add to collection
        self.collection.add(
            embeddings=vectors,
            documents=documents,
            metadatas=metadata_list,
            ids=chunk_ids
        )

        # Estimate storage size (rough approximation)
        storage_size = sum(
            len(json.dumps(m).encode('utf-8')) + len(v) * 8  # 8 bytes per float
            for m, v in zip(metadata_list
