# COMPONENT INTERFACES SPECIFICATION
## Sora Pipeline System - Orthogonal Engineering Glass-Box Boundary Compliant

**Version:** 1.0.0  
**Schema ID:** GB-INTERFACES-1.0  
**Generated:** 2026-01-24  
**Authority:** Orthogonal Engineering Framework  
**Status:** 🚀 ACTIVE DEVELOPMENT

---

## 🎯 EXECUTIVE SUMMARY

This document defines the component interfaces for the IDE-orchestrated Sora pipeline system. All interfaces follow Glass-Box Boundary principles with `@glass_box_boundary` decorators, input/output validation, and orthogonal separation. Interfaces are designed for extensibility, testability, and maintainability.

---

## 🏗️ ARCHITECTURAL OVERVIEW

### **Component Hierarchy:**
```
┌─────────────────────────────────────────────┐
│           ORCHESTRATION ENGINE              │
│   (coordinates all components)              │
├─────────────────────────────────────────────┤
│  • PipelineOrchestrator                     │
│  • ComponentCoordinator                     │
│  • ProgressTracker                          │
└─────────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────────┐
│ CHUNKING│   │EMBEDDING│   │   MEDIA     │
│ ENGINE  │   │ SYSTEM  │   │ PROCESSOR   │
├─────────┤   ├─────────┤   ├─────────────┤
│• File   │   │• Local  │   │• Audio      │
│  Scanner│   │  Models │   │  Transcribe │
│• Chunker│   │• Cloud  │   │• Video      │
│• State  │   │  APIs   │   │  Process    │
│  Manager│   │• Vector │   │• Transcript │
└─────────┘   │  Store  │   │  Chunker    │
              └─────────┘   └─────────────┘
                    │               │
                    └───────┬───────┘
                            ▼
                    ┌─────────────┐
                    │   PROMPT    │
                    │  GENERATOR  │
                    ├─────────────┤
                    │• Template   │
                    │  Engine     │
                    │• Metadata   │
                    │  Aggregator │
                    │• Validator  │
                    └─────────────┘
```

---

## 🔧 CORE INTERFACE DEFINITIONS

### **1. CHUNKING ENGINE INTERFACE**

#### **FileScanner Interface:**
```python
class FileScanner:
    """Scans repository for files to process"""
    
    @glass_box_boundary(
        input_validator=validate_scan_params,
        output_validator=validate_file_list,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def scan_repository(self, 
                       root_path: Path,
                       include_patterns: List[str] = None,
                       exclude_patterns: List[str] = None,
                       max_file_size_mb: int = 100) -> List[FileInfo]:
        """
        Scan repository for files matching patterns.
        
        Args:
            root_path: Root directory to scan
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
            max_file_size_mb: Maximum file size in MB
            
        Returns:
            List of FileInfo objects with metadata
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_file_path,
        output_validator=validate_file_info,
        side_effect_check=True
    )
    def get_file_info(self, file_path: Path) -> FileInfo:
        """Get detailed information about a file"""
        pass
```

#### **FileInfo Data Structure:**
```python
@dataclass
class FileInfo:
    """Metadata for a file to be processed"""
    path: Path
    size_bytes: int
    modified_time: datetime
    file_type: str
    encoding: str = "utf-8"
    sha256_hash: str = None
    boundary_compliance: str = "unknown"
    
    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)
    
    @property
    def extension(self) -> str:
        return self.path.suffix.lower()
```

#### **Chunker Interface:**
```python
class Chunker:
    """Chunks files based on file type and strategy"""
    
    @glass_box_boundary(
        input_validator=validate_chunking_params,
        output_validator=validate_chunks,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def chunk_file(self, 
                  file_info: FileInfo,
                  strategy: str = None,
                  max_chunk_tokens: int = 50000,
                  overlap_percentage: int = 10) -> List[TextChunk]:
        """
        Chunk a file into processable segments.
        
        Args:
            file_info: File metadata
            strategy: Chunking strategy (auto-detected from file type)
            max_chunk_tokens: Maximum tokens per chunk
            overlap_percentage: Percentage overlap between chunks
            
        Returns:
            List of TextChunk objects
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_text_input,
        output_validator=validate_chunks,
        side_effect_check=False
    )
    def chunk_text(self, 
                  text: str,
                  file_type: str = "txt",
                  strategy: str = "line_based",
                  **kwargs) -> List[TextChunk]:
        """Chunk raw text using specified strategy"""
        pass
```

#### **TextChunk Data Structure:**
```python
@dataclass
class TextChunk:
    """A chunk of text with metadata"""
    id: str  # Format: "X{index}" or "A{index}" for audio
    text: str
    source_file: Path
    chunk_index: int
    total_chunks: int
    line_range: Tuple[int, int] = None
    timestamp_range: Tuple[str, str] = None  # For media: "00:00-05:00"
    speaker: str = None  # For transcripts
    tokens_estimated: int = None
    sha256_hash: str = None
    boundary_context: Dict = None  # @glass_box_boundary context
    
    @property
    def metadata(self) -> Dict:
        """Get chunk metadata as dictionary"""
        return {
            "chunk_id": self.id,
            "source_file": str(self.source_file),
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "line_range": self.line_range,
            "timestamp_range": self.timestamp_range,
            "speaker": self.speaker,
            "tokens_estimated": self.tokens_estimated,
            "sha256_hash": self.sha256_hash,
            "boundary_context": self.boundary_context
        }
```

---

### **2. EMBEDDING SYSTEM INTERFACE**

#### **EmbeddingGenerator Interface:**
```python
class EmbeddingGenerator:
    """Generates vector embeddings for text chunks"""
    
    @glass_box_boundary(
        input_validator=validate_embedding_params,
        output_validator=validate_embeddings,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def generate_embeddings(self,
                           chunks: List[TextChunk],
                           model: str = "local",
                           batch_size: int = 32,
                           normalize: bool = True) -> List[Embedding]:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of TextChunk objects
            model: Embedding model to use
            batch_size: Batch size for processing
            normalize: Whether to normalize embeddings
            
        Returns:
            List of Embedding objects
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_model_query,
        output_validator=validate_model_info,
        side_effect_check=False
    )
    def get_model_info(self, model: str) -> ModelInfo:
        """Get information about an embedding model"""
        pass
    
    @glass_box_boundary(
        input_validator=validate_text_input,
        output_validator=validate_embedding,
        side_effect_check=True
    )
    def embed_text(self, text: str, model: str = None) -> Embedding:
        """Generate embedding for single text string"""
        pass
```

#### **Embedding Data Structure:**
```python
@dataclass
class Embedding:
    """Vector embedding with metadata"""
    vector: List[float]  # The actual embedding vector
    chunk_id: str  # Reference to TextChunk.id
    model: str  # Model used for generation
    dimensions: int  # Vector dimensions
    generated_at: datetime
    metadata: Dict = None
    
    @property
    def norm(self) -> float:
        """Calculate L2 norm of the vector"""
        return math.sqrt(sum(x * x for x in self.vector))
    
    def cosine_similarity(self, other: 'Embedding') -> float:
        """Calculate cosine similarity with another embedding"""
        if self.dimensions != other.dimensions:
            raise ValueError("Embedding dimensions must match")
        
        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        norm_product = self.norm * other.norm
        
        if norm_product == 0:
            return 0.0
        
        return dot_product / norm_product
```

#### **ModelInfo Data Structure:**
```python
@dataclass
class ModelInfo:
    """Information about an embedding model"""
    name: str
    provider: str  # "local", "openai", "cohere"
    dimensions: int
    max_tokens: int
    description: str
    url: str = None
    rate_limits: Dict = None
    pricing: Dict = None
    
    @property
    def is_local(self) -> bool:
        return self.provider == "local"
    
    @property
    def is_cloud(self) -> bool:
        return self.provider in ["openai", "cohere"]
```

---

#### **VectorStore Interface:**
```python
class VectorStore:
    """Stores and retrieves vector embeddings"""
    
    @glass_box_boundary(
        input_validator=validate_store_params,
        output_validator=validate_store_result,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def store_embeddings(self,
                        chunks: List[TextChunk],
                        embeddings: List[Embedding],
                        collection_name: str = "default",
                        metadata_fields: List[str] = None) -> StoreResult:
        """
        Store embeddings with associated metadata.
        
        Args:
            chunks: TextChunk objects
            embeddings: Corresponding Embedding objects
            collection_name: Name of collection/table
            metadata_fields: Which metadata fields to index
            
        Returns:
            StoreResult with operation details
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_query_params,
        output_validator=validate_query_results,
        side_effect_check=True
    )
    def similarity_search(self,
                         query_embedding: Embedding,
                         top_k: int = 10,
                         filters: Dict = None,
                         collection_name: str = "default") -> List[SearchResult]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Embedding to compare against
            top_k: Number of results to return
            filters: Metadata filters (e.g., {"file_type": "py"})
            collection_name: Collection to search
            
        Returns:
            List of SearchResult objects
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_chunk_id,
        output_validator=validate_retrieval_result,
        side_effect_check=True
    )
    def get_chunk_by_id(self, chunk_id: str, collection_name: str = "default") -> RetrievalResult:
        """Retrieve chunk and embedding by chunk_id"""
        pass
```

#### **Vector Store Data Structures:**
```python
@dataclass
class StoreResult:
    """Result of storing embeddings"""
    success: bool
    chunks_stored: int
    collection_name: str
    storage_size_bytes: int
    operation_id: str
    errors: List[str] = None
    
    @property
    def storage_size_mb(self) -> float:
        return self.storage_size_bytes / (1024 * 1024)

@dataclass
class SearchResult:
    """Result of similarity search"""
    chunk: TextChunk
    embedding: Embedding
    similarity_score: float
    rank: int
    metadata: Dict = None

@dataclass
class RetrievalResult:
    """Result of retrieving by chunk_id"""
    chunk: TextChunk
    embedding: Embedding
    found: bool
    retrieval_time_ms: int
```

---

### **3. MEDIA PROCESSOR INTERFACE**

#### **MediaProcessor Interface:**
```python
class MediaProcessor:
    """Processes audio and video files"""
    
    @glass_box_boundary(
        input_validator=validate_media_file,
        output_validator=validate_transcript,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def transcribe_audio(self,
                        audio_path: Path,
                        engine: str = "whisper",
                        model: str = "base",
                        language: str = "en",
                        timestamp_resolution: str = "word") -> Transcript:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            engine: Transcription engine ("whisper", "assemblyai")
            model: Model size/quality
            language: Language code
            timestamp_resolution: "word" or "segment"
            
        Returns:
            Transcript object
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_video_file,
        output_validator=validate_video_processing_result,
        side_effect_check=True
    )
    def process_video(self,
                     video_path: Path,
                     extract_audio: bool = True,
                     extract_frames: bool = False,
                     frames_per_second: int = 1) -> VideoProcessingResult:
        """
        Process video file.
        
        Args:
            video_path: Path to video file
            extract_audio: Whether to extract and transcribe audio
            extract_frames: Whether to extract key frames
            frames_per_second: Frames to extract per second
            
        Returns:
            VideoProcessingResult object
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_transcript,
        output_validator=validate_transcript_chunks,
        side_effect_check=False
    )
    def chunk_transcript(self,
                        transcript: 'Transcript',
                        strategy: str = "timestamp_based",
                        seconds_per_chunk: int = 300,
                        speaker_aware: bool = True) -> List[TextChunk]:
        """Chunk transcript into processable segments"""
        pass
```

#### **Media Data Structures:**
```python
@dataclass
class Transcript:
    """Audio/video transcript"""
    source_path: Path
    text: str
    segments: List[TranscriptSegment]
    language: str
    duration_seconds: float
    word_error_rate: float = None
    speaker_labels: List[str] = None
    
    @property
    def word_count(self) -> int:
        return len(self.text.split())

@dataclass
class TranscriptSegment:
    """Segment of a transcript"""
    text: str
    start_time: float  # seconds
    end_time: float    # seconds
    speaker: str = None
    confidence: float = None

@dataclass
class VideoProcessingResult:
    """Result of video processing"""
    audio_transcript: Transcript = None
    extracted_frames: List[Path] = None
    video_metadata: Dict = None
    processing_time_seconds: float = None
```

---

### **4. PROMPT GENERATOR INTERFACE**

#### **PromptGenerator Interface:**
```python
class PromptGenerator:
    """Generates Sora/LLM prompts from processed content"""
    
    @glass_box_boundary(
        input_validator=validate_prompt_params,
        output_validator=validate_prompt,
        side_effect_check=True,
        orthogonal_separation=True
    )
    def generate_sora_prompt(self,
                            chunks: List[TextChunk],
                            embeddings: List[Embedding] = None,
                            vector_store: VectorStore = None,
                            template: str = "atomic_sora_prompt_v1",
                            task_instructions: str = None) -> SoraPrompt:
        """
        Generate Sora prompt from processed content.
        
        Args:
            chunks: TextChunk objects
            embeddings: Optional embeddings for reference
            vector_store: Optional vector store for search capabilities
            template: Prompt template to use
            task_instructions: Specific task instructions
            
        Returns:
            SoraPrompt object
        """
        pass
    
    @glass_box_boundary(
        input_validator=validate_template_params,
        output_validator=validate_template,
        side_effect_check=False
    )
    def get_template(self, template_name: str) -> PromptTemplate:
        """Get prompt template by name"""
        pass
    
    @glass_box_boundary(
        input_validator=validate_prompt,
        output_validator=validate_validation_result,
        side_effect_check=True
    )
    def validate_prompt(self, prompt: 'SoraPrompt') -> ValidationResult:
        """Validate prompt completeness and correctness"""
        pass
```

#### **Prompt Data Structures:**
```python
@dataclass
class SoraPrompt:
    """Complete Sora prompt with all components"""
    header: str
    repository_metadata: Dict
    chunk_manifest: List[Dict]  # List of chunk metadata
    media_transcripts: List[Dict] = None
    embedding_references: Dict = None
    task_instructions: str = None
    boundary_constraints: List[str] = None
    search_capabilities: Dict = None
    generated_at: datetime = None
    prompt_id: str = None
    
    @property
    def total_chunks(self) -> int:
        return len(self.chunk_manifest)
    
    @property
    def estimated_tokens(self) -> int:
        # Estimate tokens based on text content
        total_text = self.header + (self.task_instructions or "")
        if self.chunk_manifest:
            total_text += " ".join(str(c) for c in self.chunk_manifest