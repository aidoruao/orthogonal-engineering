#!/usr/bin/env python3
"""
Embedding Generator - Orthogonal Engineering Glass-Box Boundary Compliant

Generates vector embeddings for text chunks using local models (SentenceTransformers)
with optional cloud API fallback. Maintains full Glass-Box Boundary compliance.

Version: 1.0.0
Schema ID: GB-EMBEDDING-1.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Framework

Glass Box Boundary Compliance:
- @glass_box_boundary decorator on all functions
- Input/output validation schemas
- Side effect confinement through gateway patterns
- Orthogonal separation between local and cloud operations
- Exit code 2 on boundary violations
- Trace generation for embedding operations
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from toolkit.oe.boundary_enforcer import glass_box_boundary


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class EmbeddingModelInfo:
    """Information about an embedding model"""

    def __init__(self,
                 name: str,
                 provider: str,
                 dimensions: int,
                 max_tokens: int,
                 description: str,
                 url: str = None,
                 rate_limits: Dict = None,
                 pricing: Dict = None):
        self.name = name
        self.provider = provider  # "local", "openai", "cohere"
        self.dimensions = dimensions
        self.max_tokens = max_tokens
        self.description = description
        self.url = url
        self.rate_limits = rate_limits or {}
        self.pricing = pricing or {}

    @property
    def is_local(self) -> bool:
        return self.provider == "local"

    @property
    def is_cloud(self) -> bool:
        return self.provider in ["openai", "cohere"]

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "provider": self.provider,
            "dimensions": self.dimensions,
            "max_tokens": self.max_tokens,
            "description": self.description,
            "url": self.url,
            "rate_limits": self.rate_limits,
            "pricing": self.pricing,
            "is_local": self.is_local,
            "is_cloud": self.is_cloud
        }


class TextChunk:
    """A chunk of text with metadata for embedding"""

    def __init__(self,
                 text: str,
                 chunk_id: str,
                 source_file: Union[str, Path],
                 chunk_index: int,
                 total_chunks: int,
                 line_range: Tuple[int, int] = None,
                 timestamp_range: Tuple[str, str] = None,
                 speaker: str = None,
                 tokens_estimated: int = None,
                 boundary_context: Dict = None):
        self.text = text
        self.chunk_id = chunk_id  # Format: "X{index}" or "A{index}"
        self.source_file = Path(source_file) if source_file else None
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks
        self.line_range = line_range
        self.timestamp_range = timestamp_range
        self.speaker = speaker
        self.tokens_estimated = tokens_estimated
        self.boundary_context = boundary_context or {}
        self.sha256_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA256 hash of text content"""
        text_bytes = self.text.encode('utf-8')
        return hashlib.sha256(text_bytes).hexdigest()

    @property
    def metadata(self) -> Dict:
        """Get chunk metadata as dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "source_file": str(self.source_file) if self.source_file else None,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "line_range": self.line_range,
            "timestamp_range": self.timestamp_range,
            "speaker": self.speaker,
            "tokens_estimated": self.tokens_estimated,
            "sha256_hash": self.sha256_hash,
            "boundary_context": self.boundary_context,
            "text_length": len(self.text)
        }

    def validate(self) -> List[str]:
        """Validate chunk for embedding generation"""
        errors = []

        if not self.text or not self.text.strip():
            errors.append("Text cannot be empty")

        if len(self.text) > 1000000:  # 1MB limit
            errors.append(f"Text too long: {len(self.text)} characters")

        if not self.chunk_id:
            errors.append("Chunk ID is required")

        if self.tokens_estimated and self.tokens_estimated > 100000:
            errors.append(f"Token estimate too high: {self.tokens_estimated}")

        return errors


class EmbeddingResult:
    """Result of embedding generation"""

    def __init__(self,
                 chunk: TextChunk,
                 embedding: List[float],
                 model: str,
                 dimensions: int,
                 generation_time: float,
                 cache_hit: bool = False,
                 error: str = None):
        self.chunk = chunk
        self.embedding = embedding
        self.model = model
        self.dimensions = dimensions
        self.generation_time = generation_time
        self.cache_hit = cache_hit
        self.error = error
        self.timestamp = datetime.now().isoformat()

    @property
    def chunk_id(self) -> str:
        return self.chunk.chunk_id

    @property
    def source_file(self) -> str:
        return str(self.chunk.source_file) if self.chunk.source_file else None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "chunk_id": self.chunk_id,
            "source_file": self.source_file,
            "model": self.model,
            "dimensions": self.dimensions,
            "generation_time": self.generation_time,
            "cache_hit": self.cache_hit,
            "error": self.error,
            "timestamp": self.timestamp,
            "embedding_length": len(self.embedding),
            "chunk_metadata": self.chunk.metadata
        }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_chunks(chunks: List[TextChunk]) -> List[str]:
    """Validate list of text chunks for embedding generation"""
    errors = []

    if not chunks:
        errors.append("No chunks provided")

    for i, chunk in enumerate(chunks):
        chunk_errors = chunk.validate()
        if chunk_errors:
            errors.extend([f"Chunk {i} ({chunk.chunk_id}): {err}" for err in chunk_errors])

    # Check for duplicate chunk IDs
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    duplicates = set([cid for cid in chunk_ids if chunk_ids.count(cid) > 1])
    if duplicates:
        errors.append(f"Duplicate chunk IDs: {duplicates}")

    return errors


def validate_embeddings(results: List[EmbeddingResult]) -> List[str]:
    """Validate embedding results"""
    errors = []

    if not results:
        errors.append("No embedding results")

    for i, result in enumerate(results):
        if result.error:
            errors.append(f"Result {i} ({result.chunk_id}): {result.error}")
            continue

        if not result.embedding:
            errors.append(f"Result {i} ({result.chunk_id}): Empty embedding")

        if len(result.embedding) != result.dimensions:
            errors.append(f"Result {i} ({result.chunk_id}): Embedding length {len(result.embedding)} "
                         f"does not match dimensions {result.dimensions}")

        if result.generation_time < 0:
            errors.append(f"Result {i} ({result.chunk_id}): Negative generation time")

    return errors


# ============================================================================
# EMBEDDING GENERATOR
# ============================================================================

class EmbeddingGenerator:
    """
    Generates vector embeddings for text chunks using local models.

    Glass-Box Boundary Compliance:
    - All operations use @glass_box_boundary decorator
    - Input/output validation for all methods
    - Side effects confined to cache directory
    - Orthogonal separation between local and cloud operations
    - Trace generation for embedding operations
    """

    def __init__(self, config_path: Union[str, Path] = None):
        """
        Initialize embedding generator.

        Args:
            config_path: Path to configuration file (defaults to orchestration/config/embedding_models.json)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "embedding_models.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.models = {}  # Cache for loaded models
        self.cache_dir = self._setup_cache_directory()
        self.stats = {
            "embeddings_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": []
        }
        self.model_info = self._load_model_info()

    @glass_box_boundary(
        input_validator=lambda config_path: [] if config_path else ["Config path is required"],
        side_effect_check=True
    )
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

    @glass_box_boundary(
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _setup_cache_directory(self) -> Path:
        """Setup cache directory for embeddings"""
        cache_dir = Path(self.config["cache"]["directory"])
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @glass_box_boundary(
        side_effect_check=False  # Pure function
    )
    def _load_model_info(self) -> Dict[str, EmbeddingModelInfo]:
        """Load model information from configuration"""
        model_info = {}

        # Local models
        for model_name, model_config in self.config["local_models"]["models"].items():
            model_info[model_name] = EmbeddingModelInfo(
                name=model_name,
                provider="local",
                dimensions=model_config["dimensions"],
                max_tokens=model_config["max_tokens"],
                description=model_config["description"],
                url=model_config.get("url")
            )

        # Cloud models (OpenAI)
        for model_name, model_config in self.config["cloud_models"]["openai"].items():
            model_info[model_name] = EmbeddingModelInfo(
                name=model_name,
                provider="openai",
                dimensions=model_config["dimensions"],
                max_tokens=model_config["max_tokens"],
                description=model_config["description"],
                url=model_config.get("url"),
                rate_limits=model_config.get("rate_limits"),
                pricing=model_config.get("pricing")
            )

        # Cloud models (Cohere)
        for model_name, model_config in self.config["cloud_models"]["cohere"].items():
            model_info[model_name] = EmbeddingModelInfo(
                name=model_name,
                provider="cohere",
                dimensions=model_config["dimensions"],
                max_tokens=model_config["max_tokens"],
                description=model_config["description"],
                url=model_config.get("url"),
                rate_limits=model_config.get("rate_limits"),
                pricing=model_config.get("pricing")
            )

        return model_info

    @glass_box_boundary(
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _load_local_model(self, model_name: str):
        """
        Load a local SentenceTransformers model.

        Note: This method has side effects (downloads model, loads into memory)
        but is confined by the boundary decorator.
        """
        try:
            # Import here to avoid dependency if not using local models
            from sentence_transformers import SentenceTransformer

            print(f"Loading local model: {model_name}")
            start_time = time.time()

            model = SentenceTransformer(
                model_name,
                device=self.config["local_models"]["device"],
                cache_folder=str(self.cache_dir)
            )

            load_time = time.time() - start_time
            print(f"Model loaded in {load_time:.2f} seconds")

            return model
        except ImportError:
            raise ImportError(
                "SentenceTransformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model {model_name}: {str(e)}")

    @glass_box_boundary(
        side_effect_check=False  # Pure function
    )
    def _get_cached_embedding(self, chunk: TextChunk, model: str) -> Optional[EmbeddingResult]:
        """Get embedding from cache if available"""
        if not self.config["cache"]["enabled"]:
            return None

        cache_key = f"{chunk.sha256_hash}_{model}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # Validate cache data
                if (cache_data["chunk_hash"] == chunk.sha256_hash and
                    cache_data["model"] == model):

                    return EmbeddingResult(
                        chunk=chunk,
                        embedding=cache_data["embedding"],
                        model=model,
                        dimensions=cache_data["dimensions"],
                        generation_time=cache_data["generation_time"],
                        cache_hit=True
                    )
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, ignore it
                pass

        return None

    @glass_box_boundary(
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _cache_embedding(self, result: EmbeddingResult):
        """Cache embedding result"""
        if not self.config["cache"]["enabled"]:
            return

        cache_key = f"{result.chunk.sha256_hash}_{result.model}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_data = {
            "chunk_hash": result.chunk.sha256_hash,
            "model": result.model,
            "embedding": result.embedding,
            "dimensions": result.dimensions,
            "generation_time": result.generation_time,
            "timestamp": result.timestamp
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to cache embedding: {str(e)}")

    @glass_box_boundary(
        input_validator=validate_chunks,
        output_validator=validate_embeddings,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def generate_embeddings(self,
                           chunks: List[TextChunk],
                           model: str = "local",
                           batch_size: int = None,
                           normalize: bool = None) -> List[EmbeddingResult]:
        """
        Generate embeddings for text chunks using local model.

        Args:
            chunks: List of TextChunk objects to embed
            model: Model name (defaults to config default)
            batch_size: Batch size for processing (defaults to config)
            normalize: Whether to normalize embeddings (defaults to config)

        Returns:
            List of EmbeddingResult objects
        """
        # Use defaults from config if not specified
        if model == "local":
            model = self.config["local_models"]["default"]

        if batch_size is None:
            batch_size = self.config["local_models"]["batch_size"]

        if normalize is None:
            normalize = self.config["local_models"]["normalize"]

        # Validate model
        if model not in self.model_info:
            raise ValueError(f"Unknown model: {model}. Available: {list(self.model_info.keys())}")

        model_info = self.model_info[model]
        if not model_info.is_local:
            raise ValueError(f"Model {model} is not a local model. Use cloud embedding API.")

        # Check cache first
        cached_results = []
        remaining_chunks = []

        if self.config["cache"]["enabled"]:
            for chunk in chunks:
                cached = self._get_cached_embedding(chunk, model)
                if cached:
                    cached_results.append(cached)
                    self.stats["cache_hits"] += 1
                else:
                    remaining_chunks.append(chunk)
                    self.stats["cache_misses"] += 1
        else:
            remaining_chunks = chunks

        # Generate embeddings for remaining chunks
        new_results = []
        if remaining_chunks:
            new_results = self._generate_new_embeddings(
                remaining_chunks, model, model_info, batch_size, normalize
            )

            # Cache new results
            if self.config["cache"]["enabled"]:
                for result in new_results:
                    self._cache_embedding(result)

        # Combine and return all results
        all_results = cached_results + new_results

        # Update statistics
        self.stats["embeddings_generated"] += len(all_results)

        return all_results

    @glass_box_boundary(
        input_validator=validate_chunks,
        output_validator=validate_embeddings,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _generate_new_embeddings(self,
                                chunks: List[TextChunk],
                                model_name: str,
                                model_info: EmbeddingModelInfo,
                                batch_size: int,
                                normalize: bool) -> List[EmbeddingResult]:
        """Generate new embeddings (not from cache)"""
        # Load model if not already loaded
        if model_name not in self.models:
            self.models[model_name] = self._load_local_model(model_name)

        model = self.models[model_name]
        texts = [chunk.text for chunk in chunks]

        # Generate embeddings
        start_time = time.time()

        try:
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
