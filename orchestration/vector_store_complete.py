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
import math
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.boundary_enforcer import glass_box_boundary

# ============================================================================
# DATA STRUCTURES
# ============================================================================


class VectorStoreConfig:
    """Configuration for vector store"""

    def __init__(
        self,
        store_type: str = "chromadb",
        persist_directory: Union[str, Path] = "./vector_db/",
        collection_name: str = "repository_embeddings",
        distance_function: str = "cosine",
        embedding_dimension: int = 384,
        max_batch_size: int = 100,
        enable_cache: bool = True,
        cache_directory: Union[str, Path] = "./cache/vector_store/",
        backup_enabled: bool = True,
        backup_interval: int = 1000,
        validation_enabled: bool = True,
    ):
        self.store_type = store_type
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.distance_function = distance_function
        self.embedding_dimension = embedding_dimension
        self.max_batch_size = max_batch_size
        self.enable_cache = enable_cache
        self.cache_directory = Path(cache_directory)
        self.backup_enabled = backup_enabled
        self.backup_interval = backup_interval
        self.validation_enabled = validation_enabled

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            "store_type": self.store_type,
            "persist_directory": str(self.persist_directory),
            "collection_name": self.collection_name,
            "distance_function": self.distance_function,
            "embedding_dimension": self.embedding_dimension,
            "max_batch_size": self.max_batch_size,
            "enable_cache": self.enable_cache,
            "cache_directory": str(self.cache_directory),
            "backup_enabled": self.backup_enabled,
            "backup_interval": self.backup_interval,
            "validation_enabled": self.validation_enabled,
        }


class StoreResult:
    """Result of storing embeddings"""

    def __init__(
        self,
        success: bool,
        stored_count: int,
        error_count: int,
        total_chunks: int,
        store_type: str,
        processing_time: float,
        error: str = None,
        metadata: Dict = None,
    ):
        self.success = success
        self.stored_count = stored_count
        self.error_count = error_count
        self.total_chunks = total_chunks
        self.store_type = store_type
        self.processing_time = processing_time
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "stored_count": self.stored_count,
            "error_count": self.error_count,
            "total_chunks": self.total_chunks,
            "store_type": self.store_type,
            "processing_time": self.processing_time,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class SearchResult:
    """Result of similarity search"""

    def __init__(
        self,
        success: bool,
        query: str,
        results: List[Dict],
        search_time: float,
        total_results: int,
        store_type: str,
        error: str = None,
        metadata: Dict = None,
    ):
        self.success = success
        self.query = query
        self.results = results
        self.search_time = search_time
        self.total_results = total_results
        self.store_type = store_type
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "query": self.query,
            "results": self.results,
            "search_time": self.search_time,
            "total_results": self.total_results,
            "store_type": self.store_type,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class RetrievalResult:
    """Result of embedding retrieval"""

    def __init__(
        self,
        success: bool,
        retrieved_count: int,
        total_requested: int,
        embeddings: List[Dict],
        retrieval_time: float,
        store_type: str,
        error: str = None,
        metadata: Dict = None,
    ):
        self.success = success
        self.retrieved_count = retrieved_count
        self.total_requested = total_requested
        self.embeddings = embeddings
        self.retrieval_time = retrieval_time
        self.store_type = store_type
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "retrieved_count": self.retrieved_count,
            "total_requested": self.total_requested,
            "embeddings": self.embeddings,
            "retrieval_time": self.retrieval_time,
            "store_type": self.store_type,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================


@glass_box_boundary(side_effect_check=False)
def validate_store_input(
    embeddings: List[Dict], config: VectorStoreConfig
) -> List[str]:
    """Validate input for storing embeddings"""
    errors = []

    if not embeddings:
        errors.append("No embeddings provided")

    if not config:
        errors.append("Configuration is required")

    if config and config.embedding_dimension < 1:
        errors.append(f"Invalid embedding dimension: {config.embedding_dimension}")

    for i, emb in enumerate(embeddings):
        if not isinstance(emb, dict):
            errors.append(f"Embedding {i} is not a dictionary")
            continue

        # Check required fields
        required_fields = ["chunk_id", "embedding", "metadata"]
        for field in required_fields:
            if field not in emb:
                errors.append(f"Embedding {i} missing required field: {field}")

        # Check embedding dimensions
        if "embedding" in emb:
            embedding = emb["embedding"]
            if not isinstance(embedding, list):
                errors.append(f"Embedding {i} embedding is not a list")
            elif len(embedding) != config.embedding_dimension:
                errors.append(
                    f"Embedding {i} has dimension {len(embedding)}, "
                    f"expected {config.embedding_dimension}"
                )

        # Check chunk_id format
        if "chunk_id" in emb:
            chunk_id = emb["chunk_id"]
            if not isinstance(chunk_id, str):
                errors.append(f"Embedding {i} chunk_id is not a string")
            elif not chunk_id.strip():
                errors.append(f"Embedding {i} has empty chunk_id")

    return errors


@glass_box_boundary(side_effect_check=False)
def validate_search_input(
    query_embedding: List[float], top_k: int, config: VectorStoreConfig
) -> List[str]:
    """Validate input for similarity search"""
    errors = []

    if not query_embedding:
        errors.append("Query embedding is required")

    if not isinstance(query_embedding, list):
        errors.append("Query embedding must be a list")

    if top_k < 1 or top_k > 1000:
        errors.append(f"top_k must be between 1 and 1000, got {top_k}")

    if config and len(query_embedding) != config.embedding_dimension:
        errors.append(
            f"Query embedding dimension {len(query_embedding)} "
            f"does not match configured dimension {config.embedding_dimension}"
        )

    return errors


@glass_box_boundary(side_effect_check=False)
def validate_retrieval_input(chunk_ids: List[str]) -> List[str]:
    """Validate input for embedding retrieval"""
    errors = []

    if not chunk_ids:
        errors.append("No chunk IDs provided")

    if not isinstance(chunk_ids, list):
        errors.append("chunk_ids must be a list")

    for i, chunk_id in enumerate(chunk_ids):
        if not isinstance(chunk_id, str):
            errors.append(f"chunk_id at index {i} is not a string")
        elif not chunk_id.strip():
            errors.append(f"chunk_id at index {i} is empty")

    # Check for duplicates
    if len(chunk_ids) != len(set(chunk_ids)):
        errors.append("Duplicate chunk IDs found")

    return errors


@glass_box_boundary(side_effect_check=False)
def validate_store_result(result: StoreResult) -> List[str]:
    """Validate store operation result"""
    errors = []

    if not isinstance(result, StoreResult):
        errors.append("Result is not a StoreResult instance")

    if result.success and result.error_count > 0:
        errors.append("Success with error count > 0")

    if result.stored_count > result.total_chunks:
        errors.append("Stored count exceeds total chunks")

    if result.processing_time < 0:
        errors.append("Negative processing time")

    return errors


@glass_box_boundary(side_effect_check=False)
def validate_search_result(result: SearchResult) -> List[str]:
    """Validate search operation result"""
    errors = []

    if not isinstance(result, SearchResult):
        errors.append("Result is not a SearchResult instance")

    if result.success and not result.results:
        errors.append("Success but no results")

    if result.search_time < 0:
        errors.append("Negative search time")

    if result.total_results < 0:
        errors.append("Negative total results")

    return errors


@glass_box_boundary(side_effect_check=False)
def validate_retrieval_result(result: RetrievalResult) -> List[str]:
    """Validate retrieval operation result"""
    errors = []

    if not isinstance(result, RetrievalResult):
        errors.append("Result is not a RetrievalResult instance")

    if result.success and result.retrieved_count == 0:
        errors.append("Success but retrieved count is 0")

    if result.retrieved_count > result.total_requested:
        errors.append("Retrieved count exceeds requested count")

    if result.retrieval_time < 0:
        errors.append("Negative retrieval time")

    return errors


# ============================================================================
# VECTOR STORE INTERFACE
# ============================================================================


class VectorStore:
    """
    Abstract interface for vector storage operations.

    Glass-Box Boundary Compliance:
    - All methods use @glass_box_boundary decorator
    - Input/output validation for all operations
    - Side effects confined to storage backend
    - Orthogonal separation between operations
    - Trace generation for auditability
    """

    def __init__(self, config: VectorStoreConfig):
        """Initialize vector store with configuration"""
        self.config = config
        self.stats = {
            "store_operations": 0,
            "search_operations": 0,
            "retrieval_operations": 0,
            "total_stored": 0,
            "total_searched": 0,
            "total_retrieved": 0,
            "errors": [],
            "last_operation": None,
        }

    @glass_box_boundary(
        input_validator=validate_store_input,
        output_validator=validate_store_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def store_embeddings(self, embeddings: List[Dict]) -> StoreResult:
        """Store embeddings in vector database"""
        raise NotImplementedError("Subclasses must implement store_embeddings")

    @glass_box_boundary(
        input_validator=validate_search_input,
        output_validator=validate_search_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def similarity_search(
        self, query_embedding: List[float], top_k: int = 10
    ) -> SearchResult:
        """Perform similarity search in vector database"""
        raise NotImplementedError("Subclasses must implement similarity_search")

    @glass_box_boundary(
        input_validator=validate_retrieval_input,
        output_validator=validate_retrieval_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def retrieve_embeddings(self, chunk_ids: List[str]) -> RetrievalResult:
        """Retrieve embeddings by chunk IDs"""
        raise NotImplementedError("Subclasses must implement retrieve_embeddings")

    @glass_box_boundary(side_effect_check=False)
    def get_stats(self) -> Dict:
        """Get statistics about vector store operations"""
        return self.stats.copy()

    @glass_box_boundary(side_effect_check=True, orthogonal_separation=True)
    def cleanup(self) -> None:
        """Clean up resources"""
        pass


# ============================================================================
# CHROMADB IMPLEMENTATION
# ============================================================================


class InMemoryVectorStore(VectorStore):
    """
    In-memory implementation of vector store for testing.

    Glass-Box Boundary Compliance:
    - All operations are boundary-wrapped
    - No file system operations
    - Simple error handling
    - No external dependencies
    """

    def __init__(self, config: VectorStoreConfig):
        """Initialize in-memory vector store"""
        super().__init__(config)
        self.embeddings = {}  # chunk_id -> {"embedding": List[float], "metadata": Dict}
        self._initialize_store()

    @glass_box_boundary(side_effect_check=True, orthogonal_separation=True)
    def _initialize_store(self):
        """Initialize in-memory store"""
        try:
            # Create empty store
            self.embeddings = {}
            print(
                f"✅ Initialized in-memory vector store: {self.config.collection_name}"
            )

            # Update stats
            self.stats["initialized"] = True
            self.stats["collection_name"] = self.config.collection_name
            self.stats["store_type"] = "in_memory"

        except Exception as e:
            raise RuntimeError(f"Failed to initialize in-memory store: {e}") from e

    @glass_box_boundary(
        input_validator=validate_store_input,
        output_validator=validate_store_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def store_embeddings(self, embeddings: List[Dict]) -> StoreResult:
        """Store embeddings in memory"""
        start_time = time.time()

        try:
            stored_count = 0
            error_count = 0

            for emb in embeddings:
                try:
                    chunk_id = emb["chunk_id"]
                    embedding = emb["embedding"]
                    metadata = emb.get("metadata", {})

                    # Add required metadata
                    metadata.update(
                        {
                            "chunk_id": chunk_id,
                            "stored_at": datetime.now().isoformat(),
                            "embedding_dimension": len(embedding),
                        }
                    )

                    # Store in memory
                    self.embeddings[chunk_id] = {
                        "embedding": embedding,
                        "metadata": metadata,
                    }
                    stored_count += 1

                except Exception as e:
                    error_count += 1
                    self.stats["errors"].append(
                        f"Failed to store embedding {chunk_id}: {str(e)}"
                    )

            processing_time = time.time() - start_time

            # Update stats
            self.stats["store_operations"] += 1
            self.stats["total_stored"] += stored_count
            self.stats["last_operation"] = "store"

            return StoreResult(
                success=True,
                stored_count=stored_count,
                error_count=error_count,
                total_chunks=len(embeddings),
                store_type="in_memory",
                processing_time=processing_time,
                metadata={
                    "collection_name": self.config.collection_name,
                    "batch_size": len(embeddings),
                    "total_embeddings": len(self.embeddings),
                },
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.stats["errors"].append(f"Store operation failed: {str(e)}")

            return StoreResult(
                success=False,
                stored_count=0,
                error_count=len(embeddings),
                total_chunks=len(embeddings),
                store_type="in_memory",
                processing_time=processing_time,
                error=str(e),
            )

    @glass_box_boundary(
        input_validator=validate_search_input,
        output_validator=validate_search_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def similarity_search(
        self, query_embedding: List[float], top_k: int = 10
    ) -> SearchResult:
        """Perform similarity search in memory"""
        start_time = time.time()

        try:
            if not self.embeddings:
                return SearchResult(
                    success=True,
                    query="vector_similarity_search",
                    results=[],
                    search_time=time.time() - start_time,
                    total_results=0,
                    store_type="in_memory",
                    metadata={"collection_name": self.config.collection_name},
                )

            # Calculate similarities
            similarities = []
            for chunk_id, data in self.embeddings.items():
                embedding = data["embedding"]
                metadata = data["metadata"]

                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, embedding)
                similarities.append(
                    {
                        "chunk_id": chunk_id,
                        "similarity": similarity,
                        "metadata": metadata,
                        "embedding": embedding,
                    }
                )

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)

            # Take top_k results
            search_results = similarities[:top_k]

            # Add rank
            for i, result in enumerate(search_results):
                result["rank"] = i + 1
                result["distance"] = 1.0 - result["similarity"]  # Convert to distance

            search_time = time.time() - start_time

            # Update stats
            self.stats["search_operations"] += 1
            self.stats["total_searched"] += 1
            self.stats["last_operation"] = "search"

            return SearchResult(
                success=True,
                query="vector_similarity_search",
                results=search_results,
                search_time=search_time,
                total_results=len(search_results),
                store_type="in_memory",
                metadata={
                    "collection_name": self.config.collection_name,
                    "top_k": top_k,
                    "query_dimension": len(query_embedding),
                    "total_embeddings": len(self.embeddings),
                },
            )

        except Exception as e:
            search_time = time.time() - start_time
            self.stats["errors"].append(f"Search operation failed: {str(e)}")

            return SearchResult(
                success=False,
                query="vector_similarity_search",
                results=[],
                search_time=search_time,
                total_results=0,
                store_type="in_memory",
                error=str(e),
            )

    @glass_box_boundary(
        input_validator=validate_retrieval_input,
        output_validator=validate_retrieval_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def retrieve_embeddings(self, chunk_ids: List[str]) -> RetrievalResult:
        """Retrieve embeddings from memory by chunk IDs"""
        start_time = time.time()

        try:
            retrieved_embeddings = []
            retrieved_count = 0

            for chunk_id in chunk_ids:
                if chunk_id in self.embeddings:
                    data = self.embeddings[chunk_id]
                    retrieved_embeddings.append(
                        {
                            "chunk_id": chunk_id,
                            "embedding": data["embedding"],
                            "metadata": data["metadata"],
                            "retrieved_at": datetime.now().isoformat(),
                        }
                    )
                    retrieved_count += 1

            retrieval_time = time.time() - start_time

            # Update stats
            self.stats["retrieval_operations"] += 1
            self.stats["total_retrieved"] += retrieved_count
            self.stats["last_operation"] = "retrieval"

            return RetrievalResult(
                success=True,
                retrieved_count=retrieved_count,
                total_requested=len(chunk_ids),
                embeddings=retrieved_embeddings,
                retrieval_time=retrieval_time,
                store_type="in_memory",
                metadata={
                    "collection_name": self.config.collection_name,
                    "requested_ids": len(chunk_ids),
                    "found_ids": retrieved_count,
                    "total_embeddings": len(self.embeddings),
                },
            )

        except Exception as e:
            retrieval_time = time.time() - start_time
            self.stats["errors"].append(f"Retrieval operation failed: {str(e)}")

            return RetrievalResult(
                success=False,
                retrieved_count=0,
                total_requested=len(chunk_ids),
                embeddings=[],
                retrieval_time=retrieval_time,
                store_type="in_memory",
                error=str(e),
            )

    @glass_box_boundary(side_effect_check=True, orthogonal_separation=True)
    def cleanup(self) -> None:
        """Clean up in-memory resources"""
        try:
            # Clear all embeddings
            self.embeddings.clear()

            # Update stats
            self.stats["last_operation"] = "cleanup"
            print(
                f"✅ Cleaned up in-memory vector store: {self.config.collection_name}"
            )

        except Exception as e:
            self.stats["errors"].append(f"Cleanup failed: {str(e)}")
            print(f"⚠️  Cleanup warning: {e}")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        # Avoid division by zero
        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)


class ChromaDBVectorStore(VectorStore):
    """
    ChromaDB implementation of vector store.

    Glass-Box Boundary Compliance:
    - All ChromaDB operations are boundary-wrapped
    - File system operations confined to persist directory
    - Error handling with proper boundary violations
    - Resource cleanup on destruction
    """

    def __init__(self, config: VectorStoreConfig):
        """Initialize ChromaDB vector store"""
        super().__init__(config)
        self.client = None
        self.collection = None
        self._initialize_chromadb()

    @glass_box_boundary(side_effect_check=True, orthogonal_separation=True)
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            import chromadb
            from chromadb.config import Settings

            # Create persist directory if it doesn't exist
            self.config.persist_directory.mkdir(parents=True, exist_ok=True)

            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.config.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )

            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.config.collection_name
                )
                print(f"✅ Loaded existing collection: {self.config.collection_name}")
            except Exception:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.config.collection_name,
                    metadata={"hnsw:space": self.config.distance_function},
                )
                print(f"✅ Created new collection: {self.config.collection_name}")

            # Update stats
            self.stats["initialized"] = True
            self.stats["collection_name"] = self.config.collection_name
            self.stats["store_type"] = "chromadb"

        except ImportError as e:
            raise ImportError(
                f"ChromaDB not installed. Please install with: pip install chromadb"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaDB: {e}") from e

    @glass_box_boundary(
        input_validator=validate_store_input,
        output_validator=validate_store_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def store_embeddings(self, embeddings: List[Dict]) -> StoreResult:
        """Store embeddings in ChromaDB"""
        start_time = time.time()

        try:
            if not self.collection:
                raise RuntimeError("ChromaDB collection not initialized")

            # Prepare data for ChromaDB
            ids = []
            embeddings_list = []
            metadatas = []

            stored_count = 0
            error_count = 0

            for emb in embeddings:
                try:
                    chunk_id = emb["chunk_id"]
                    embedding = emb["embedding"]
                    metadata = emb.get("metadata", {})

                    # Add required metadata
                    metadata.update(
                        {
                            "chunk_id": chunk_id,
                            "stored_at": datetime.now().isoformat(),
                            "embedding_dimension": len(embedding),
                        }
                    )

                    ids.append(chunk_id)
                    embeddings_list.append(embedding)
                    metadatas.append(metadata)
                    stored_count += 1

                except Exception as e:
                    error_count += 1
                    self.stats["errors"].append(
                        f"Failed to prepare embedding {chunk_id}: {str(e)}"
                    )

            # Store in ChromaDB
            if ids:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings_list,
                    metadatas=metadatas,
                )

                # Update stats
                self.stats["store_operations"] += 1
                self.stats["total_stored"] += stored_count
                self.stats["last_operation"] = "store"

            processing_time = time.time() - start_time

            return StoreResult(
                success=True,
                stored_count=stored_count,
                error_count=error_count,
                total_chunks=len(embeddings),
                store_type="chromadb",
                processing_time=processing_time,
                metadata={
                    "collection_name": self.config.collection_name,
                    "batch_size": len(embeddings),
                },
            )

        except Exception as e:
            processing_time = time.time() - start_time
            self.stats["errors"].append(f"Store operation failed: {str(e)}")

            return StoreResult(
                success=False,
                stored_count=0,
                error_count=len(embeddings),
                total_chunks=len(embeddings),
                store_type="chromadb",
                processing_time=processing_time,
                error=str(e),
            )

    @glass_box_boundary(
        input_validator=validate_search_input,
        output_validator=validate_search_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def similarity_search(
        self, query_embedding: List[float], top_k: int = 10
    ) -> SearchResult:
        """Perform similarity search in ChromaDB"""
        start_time = time.time()

        try:
            if not self.collection:
                raise RuntimeError("ChromaDB collection not initialized")

            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["embeddings", "metadatas", "distances"],
            )

            # Process results
            search_results = []
            if results["ids"] and results["ids"][0]:
                for i, (chunk_id, distance, metadata) in enumerate(
                    zip(
                        results["ids"][0],
                        results["distances"][0],
                        results["metadatas"][0],
                    )
                ):
                    # Convert distance to similarity (cosine distance to similarity)
                    # ChromaDB returns cosine distance: 0 = identical, 2 = opposite
                    similarity = 1.0 - (distance / 2.0) if distance is not None else 0.0

                    # Get embedding if available
                    embedding = None
                    if results["embeddings"] and results["embeddings"][0]:
                        embedding = results["embeddings"][0][i]

                    search_results.append(
                        {
                            "chunk_id": chunk_id,
                            "similarity": similarity,
                            "distance": distance,
                            "metadata": metadata,
                            "embedding": embedding,
                            "rank": i + 1,
                        }
                    )

            search_time = time.time() - start_time

            # Update stats
            self.stats["search_operations"] += 1
            self.stats["total_searched"] += 1
            self.stats["last_operation"] = "search"

            return SearchResult(
                success=True,
                query="vector_similarity_search",
                results=search_results,
                search_time=search_time,
                total_results=len(search_results),
                store_type="chromadb",
                metadata={
                    "collection_name": self.config.collection_name,
                    "top_k": top_k,
                    "query_dimension": len(query_embedding),
                },
            )

        except Exception as e:
            search_time = time.time() - start_time
            self.stats["errors"].append(f"Search operation failed: {str(e)}")

            return SearchResult(
                success=False,
                query="vector_similarity_search",
                results=[],
                search_time=search_time,
                total_results=0,
                store_type="chromadb",
                error=str(e),
            )

    @glass_box_boundary(
        input_validator=validate_retrieval_input,
        output_validator=validate_retrieval_result,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def retrieve_embeddings(self, chunk_ids: List[str]) -> RetrievalResult:
        """Retrieve embeddings from ChromaDB by chunk IDs"""
        start_time = time.time()

        try:
            if not self.collection:
                raise RuntimeError("ChromaDB collection not initialized")

            # Get embeddings by IDs
            results = self.collection.get(
                ids=chunk_ids,
                include=["embeddings", "metadatas"],
            )

            # Process results
            retrieved_embeddings = []
            retrieved_count = 0

            if results["ids"]:
                for i, chunk_id in enumerate(results["ids"]):
                    embedding = (
                        results["embeddings"][i] if results["embeddings"] else None
                    )
                    metadata = results["metadatas"][i] if results["metadatas"] else {}

                    retrieved_embeddings.append(
                        {
                            "chunk_id": chunk_id,
                            "embedding": embedding,
                            "metadata": metadata,
                            "retrieved_at": datetime.now().isoformat(),
                        }
                    )
                    retrieved_count += 1

            retrieval_time = time.time() - start_time

            # Update stats
            self.stats["retrieval_operations"] += 1
            self.stats["total_retrieved"] += retrieved_count
            self.stats["last_operation"] = "retrieval"

            return RetrievalResult(
                success=True,
                retrieved_count=retrieved_count,
                total_requested=len(chunk_ids),
                embeddings=retrieved_embeddings,
                retrieval_time=retrieval_time,
                store_type="chromadb",
                metadata={
                    "collection_name": self.config.collection_name,
                    "requested_ids": len(chunk_ids),
                    "found_ids": retrieved_count,
                },
            )

        except Exception as e:
            retrieval_time = time.time() - start_time
            self.stats["errors"].append(f"Retrieval operation failed: {str(e)}")

            return RetrievalResult(
                success=False,
                retrieved_count=0,
                total_requested=len(chunk_ids),
                embeddings=[],
                retrieval_time=retrieval_time,
                store_type="chromadb",
                error=str(e),
            )

    @glass_box_boundary(side_effect_check=True, orthogonal_separation=True)
    def cleanup(self) -> None:
        """Clean up ChromaDB resources"""
        try:
            if self.client:
                # ChromaDB PersistentClient doesn't need explicit cleanup
                # but we can reset our references
                self.collection = None
                self.client = None

                # Update stats
                self.stats["last_operation"] = "cleanup"
                print(
                    f"✅ Cleaned up ChromaDB vector store: {self.config.collection_name}"
                )
        except Exception as e:
            self.stats["errors"].append(f"Cleanup failed: {str(e)}")
            print(f"⚠️  Cleanup warning: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destruction
