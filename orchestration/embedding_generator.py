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
                 vector: List[float],
                 chunk: TextChunk,
                 model_info: EmbeddingModelInfo,
                 generated_at: datetime = None,
                 processing_time_ms: int = None,
                 metadata: Dict = None):
        self.vector = vector
        self.chunk = chunk
        self.model_info = model_info
        self.generated_at = generated_at or datetime.now()
        self.processing_time_ms = processing_time_ms or 0
        self.metadata = metadata or {}

    @property
    def dimensions(self) -> int:
        return len(self.vector)

    @property
    def norm(self) -> float:
        """Calculate L2 norm of the vector"""
        import math
        return math.sqrt(sum(x * x for x in self.vector))

    def cosine_similarity(self, other: 'EmbeddingResult') -> float:
        """Calculate cosine similarity with another embedding"""
        if self.dimensions != other.dimensions:
            raise ValueError(f"Embedding dimensions must match: {self.dimensions} != {other.dimensions}")

        import math

        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        norm_product = self.norm * other.norm

        if norm_product == 0:
            return 0.0

        return dot_product / norm_product

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "vector": self.vector,
            "chunk_id": self.chunk.chunk_id,
            "model": self.model_info.name,
            "dimensions": self.dimensions,
            "generated_at": self.generated_at.isoformat(),
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata,
            "chunk_metadata": self.chunk.metadata
        }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_chunks(chunks: List[TextChunk]) -> None:
    """Validate list of text chunks for embedding"""
    if not chunks:
        raise ValueError("Chunks list cannot be empty")

    errors = []
    for i, chunk in enumerate(chunks):
        chunk_errors = chunk.validate()
        if chunk_errors:
            errors.append(f"Chunk {i} ({chunk.chunk_id}): {', '.join(chunk_errors)}")

    if errors:
        raise ValueError(f"Chunk validation failed: {'; '.join(errors)}")


def validate_embeddings(embeddings: List[EmbeddingResult]) -> None:
    """Validate embedding results"""
    if not embeddings:
        raise ValueError("Embeddings list cannot be empty")

    # Check all embeddings have same dimensions
    dimensions = set(embedding.dimensions for embedding in embeddings)
    if len(dimensions) > 1:
        raise ValueError(f"Inconsistent embedding dimensions: {dimensions}")

    # Check dimensions are reasonable
    dim = next(iter(dimensions))
    if dim < 1 or dim > 10000:
        raise ValueError(f"Invalid embedding dimension: {dim}")

    # Check vectors are not all zeros
    for i, embedding in enumerate(embeddings):
        if all(abs(x) < 1e-10 for x in embedding.vector):
            raise ValueError(f"Embedding {i} is all zeros")


def validate_model_params(model: str, batch_size: int, normalize: bool) -> None:
    """Validate embedding model parameters"""
    if not model:
        raise ValueError("Model name is required")

    if batch_size < 1 or batch_size > 1000:
        raise ValueError(f"Batch size must be between 1 and 1000: {batch_size}")

    if not isinstance(normalize, bool):
        raise ValueError(f"Normalize must be boolean: {normalize}")


# ============================================================================
# EMBEDDING GENERATOR CLASS
# ============================================================================

class EmbeddingGenerator:
    """
    Generates vector embeddings for text chunks using local models.

    Glass-Box Boundary Compliance:
    - All public methods use @glass_box_boundary decorator
    - Input validation before processing
    - Output validation after processing
    - Side effects confined to model loading/generation
    - Orthogonal separation between model types
    - Trace generation for auditability
    """

    def __init__(self,
                 config_path: Union[str, Path] = None,
                 cache_dir: Union[str, Path] = None):
        """
        Initialize embedding generator.

        Args:
            config_path: Path to configuration file
            cache_dir: Directory for model cache
        """
        self.config_path = Path(config_path) if config_path else None
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache/embeddings/")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Initialize models dictionary (lazy loading)
        self.models: Dict[str, any] = {}
        self.model_info: Dict[str, EmbeddingModelInfo] = {}

        # Initialize local models info
        self._init_local_models()

        # Statistics
        self.stats = {
            "embeddings_generated": 0,
            "total_processing_time_ms": 0,
            "errors": [],
            "cache_hits": 0,
            "cache_misses": 0
        }

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _load_config(self) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "local_models": {
                "default": "all-MiniLM-L6-v2",
                "device": "cpu",
                "batch_size": 32,
                "normalize": True,
                "show_progress_bar": True
            },
            "cache": {
                "enabled": True,
                "max_size_mb": 1000,
                "ttl_hours": 24
            },
            "validation": {
                "dimension_validation": True,
                "similarity_threshold": 0.85,
                "min_chunk_length": 10,
                "max_chunk_length": 10000
            }
        }

        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                # Merge with defaults
                import copy
                merged = copy.deepcopy(default_config)
                self._merge_dicts(merged, file_config)
                return merged
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")
                return default_config

        return default_config

    def _merge_dicts(self, target: Dict, source: Dict) -> None:
        """Recursively merge source dict into target dict"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dicts(target[key], value)
            else:
                target[key] = value

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _init_local_models(self) -> None:
        """Initialize information about available local models"""
        local_models = {
            "all-MiniLM-L6-v2": EmbeddingModelInfo(
                name="all-MiniLM-L6-v2",
                provider="local",
                dimensions=384,
                max_tokens=256,
                description="Fast, lightweight model good for general text",
                url="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"
            ),
            "all-mpnet-base-v2": EmbeddingModelInfo(
                name="all-mpnet-base-v2",
                provider="local",
                dimensions=768,
                max_tokens=384,
                description="Higher quality but slower, good for semantic search",
                url="https://huggingface.co/sentence-transformers/all-mpnet-base-v2"
            ),
            "codebert-base": EmbeddingModelInfo(
                name="codebert-base",
                provider="local",
                dimensions=768,
                max_tokens=512,
                description="Specialized for code understanding",
                url="https://huggingface.co/microsoft/codebert-base"
            )
        }

        self.model_info.update(local_models)

    @glass_box_boundary(
        input_validator=validate_model_params,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def _load_local_model(self, model_name: str) -> any:
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

            load_time = int((time.time() - start_time) * 1000)
            print(f"Model loaded in {load_time}ms")

            return model

        except ImportError:
            raise ImportError(
                "SentenceTransformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model {model_name}: {str(e)}")

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
                show_progress_bar=self.config["local_models"]["show_progress_bar"],
                normalize_embeddings=normalize,
                convert_to_numpy=True
            )
        except Exception as e:
            self.stats["errors"].append(f"Embedding generation failed: {str(e)}")
            raise RuntimeError(f"
