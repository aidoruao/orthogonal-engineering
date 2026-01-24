# ENVIRONMENT VARIABLE TEMPLATE
# Orthogonal Engineering Orchestration System

# Copy this file to `.env` and fill in your values
# DO NOT commit `.env` to version control

## ============================================================================
## CORE CONFIGURATION
## ============================================================================

# Workspace Configuration
WORKSPACE_ROOT=.
OUTPUT_DIRECTORY=./orchestration_output
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
CHECKPOINT_ENABLED=true
PARALLEL_PROCESSING=true
MAX_WORKERS=4
MEMORY_LIMIT_MB=4096

# Boundary Compliance
BOUNDARY_COMPLIANCE_ENFORCED=true
TRACE_GENERATION_ENABLED=true
EXIT_CODE_2_ON_VIOLATION=true
VALIDATION_STRICTNESS=high  # low, medium, high

## ============================================================================
## EMBEDDING CONFIGURATION
## ============================================================================

# Local Embedding Models (SentenceTransformers)
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
# Options: all-MiniLM-L6-v2, all-mpnet-base-v2, codebert-base
LOCAL_EMBEDDING_DEVICE=cpu  # cpu or cuda
LOCAL_EMBEDDING_BATCH_SIZE=32
LOCAL_EMBEDDING_NORMALIZE=true
LOCAL_EMBEDDING_CACHE_DIR=./cache/embeddings/

# Cloud Embedding Services (Optional)

# OpenAI Embeddings
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_RATE_LIMIT_REQUESTS_PER_MINUTE=3000
OPENAI_RATE_LIMIT_TOKENS_PER_MINUTE=1000000

# Cohere Embeddings
COHERE_API_KEY=your_cohere_api_key_here
COHERE_EMBEDDING_MODEL=embed-english-v3.0
COHERE_RATE_LIMIT_REQUESTS_PER_MINUTE=1000
COHERE_RATE_LIMIT_TOKENS_PER_MINUTE=50000

# Embedding Selection Strategy
EMBEDDING_STRATEGY_DEFAULT=local
EMBEDDING_FALLBACK_CHAIN=local,openai,cohere
EMBEDDING_SIZE_THRESHOLD_LOCAL_MB=10
EMBEDDING_SIZE_THRESHOLD_CLOUD_MB=100

## ============================================================================
## VECTOR DATABASE CONFIGURATION
## ============================================================================

# Vector Database Selection
VECTOR_DATABASE_TYPE=chromadb  # chromadb, faiss, pinecone, weaviate
VECTOR_DATABASE_PERSIST_DIRECTORY=./vector_db/
VECTOR_DATABASE_COLLECTION_NAME=repository_embeddings

# ChromaDB Specific
CHROMADB_PERSIST_DIRECTORY=./vector_db/chromadb/
CHROMADB_COLLECTION_NAME=orthogonal_engineering
CHROMADB_DISTANCE_FUNCTION=cosine  # cosine, l2, ip

# FAISS Specific
FAISS_INDEX_TYPE=IVF  # IVF, Flat, HNSW
FAISS_METRIC_TYPE=cosine  # cosine, l2, ip
FAISS_NLIST=100
FAISS_NPROBE=10

# Pinecone Specific (Cloud)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=orthogonal-engineering
PINECONE_DIMENSION=384  # Must match embedding dimension

# Weaviate Specific (Cloud)
WEAVIATE_API_KEY=your_weaviate_api_key_here
WEAVIATE_URL=https://your-weaviate-cluster.weaviate.network
WEAVIATE_CLASS_NAME=DocumentChunk

## ============================================================================
## MEDIA PROCESSING CONFIGURATION
## ============================================================================

# Audio Transcription (Whisper)
WHISPER_MODEL=base  # tiny, base, small, medium, large
WHISPER_DEVICE=cpu  # cpu or cuda
WHISPER_LANGUAGE=en
WHISPER_TASK=transcribe  # transcribe or translate
WHISPER_TIMESTAMP_RESOLUTION=word  # word or segment

# AssemblyAI (Cloud Alternative)
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
ASSEMBLYAI_LANGUAGE_CODE=en
ASSEMBLYAI_SPEAKER_LABELS=true

# Media Processing Limits
MAX_AUDIO_DURATION_HOURS=10
MAX_VIDEO_DURATION_HOURS=5
MEDIA_PROCESSING_PARALLEL=true
MEDIA_CACHE_DIRECTORY=./cache/media/

## ============================================================================
## CHUNKING CONFIGURATION
## ============================================================================

# Token and Size Limits
MAX_CHUNK_TOKENS=50000
MAX_CHUNK_BYTES=250000
MIN_CHUNK_SIZE=100
OVERLAP_PERCENTAGE=10
TOKEN_RATIO=0.75
CHARS_PER_TOKEN=4

# File Type Specific
PYTHON_CHUNKING_STRATEGY=function_based
MARKDOWN_CHUNKING_STRATEGY=section_based
JSON_CHUNKING_STRATEGY=structured
HTML_CHUNKING_STRATEGY=tag_based
TEXT_CHUNKING_STRATEGY=line_based

# Performance Settings
CHUNKING_PARALLEL=true
CHUNKING_BUFFER_SIZE=100
CHUNKING_CHECKPOINT_FREQUENCY=100

## ============================================================================
## PROMPT GENERATION CONFIGURATION
## ============================================================================

# Sora Prompt Templates
PROMPT_TEMPLATE_NAME=atomic_sora_prompt_v1
PROMPT_OUTPUT_FORMAT=markdown  # markdown, json, yaml
PROMPT_COMPRESSION_ENABLED=true
PROMPT_COMPRESSION_ALGORITHM=gzip
PROMPT_SPLIT_LARGE_PROMPTS=false
PROMPT_MAX_TOKENS=1000000
PROMPT_MAX_CHUNKS=10000

# Prompt Content Options
INCLUDE_EMBEDDINGS_REFERENCE=true
INCLUDE_SEARCH_CAPABILITIES=true
INCLUDE_CROSS_REFERENCES=true
INCLUDE_VALIDATION_REPORT=true
INCLUDE_TRACE_DOCUMENTS=true

## ============================================================================
## API RATE LIMITING AND RETRY
## ============================================================================

# General API Settings
API_RETRY_COUNT=3
API_RETRY_DELAY_SECONDS=1
API_TIMEOUT_SECONDS=30
API_BACKOFF_FACTOR=2

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_MAX_REQUESTS=1000

## ============================================================================
## SECURITY AND PRIVACY
## ============================================================================

# Data Privacy
PROCESS_SENSITIVE_DATA_LOCALLY=true
CLOUD_PROCESSING_OPT_IN=false
DATA_ENCRYPTION_ENABLED=true
ENCRYPTION_ALGORITHM=AES-256-GCM

# Access Control
REQUIRE_AUTHENTICATION=false
ALLOWED_FILE_PATTERNS=**/*
DENIED_FILE_PATTERNS=**/secrets/**,**/private/**,**/confidential/**
FILE_PERMISSION_CHECK=true

## ============================================================================
## LOGGING AND MONITORING
## ============================================================================

# Logging Configuration
LOG_DIRECTORY=./logs/orchestration/
LOG_ROTATION_ENABLED=true
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=10
LOG_COMPRESSION_ENABLED=true

# Monitoring
METRICS_COLLECTION_ENABLED=true
METRICS_OUTPUT_DIRECTORY=./metrics/
METRICS_UPDATE_INTERVAL_SECONDS=60
PERFORMANCE_ALERTS_ENABLED=true

# Alerting
ALERT_ON_BOUNDARY_VIOLATION=true
ALERT_ON_API_ERROR=true
ALERT_ON_MEMORY_LIMIT=true
ALERT_ON_PROCESSING_ERROR=true

## ============================================================================
## ADVANCED SETTINGS
## ============================================================================

# Cache Configuration
CACHE_ENABLED=true
CACHE_DIRECTORY=./cache/
CACHE_MAX_SIZE_MB=1000
CACHE_TTL_SECONDS=86400  # 24 hours
CACHE_COMPRESSION_ENABLED=true

# Memory Management
MEMORY_MONITORING_ENABLED=true
MEMORY_WARNING_THRESHOLD_PERCENT=80
MEMORY_CRITICAL_THRESHOLD_PERCENT=90
MEMORY_CLEANUP_INTERVAL_SECONDS=300

# Parallel Processing
PARALLEL_MAX_WORKERS=4
PARALLEL_CHUNK_SIZE=100
PARALLEL_TIMEOUT_SECONDS=3600
PARALLEL_RETRY_ON_FAILURE=true

# Validation Settings
VALIDATE_EMBEDDING_DIMENSIONS=true
VALIDATE_CHUNK_SIZE=true
VALIDATE_METADATA_COMPLETENESS=true
VALIDATE_BOUNDARY_COMPLIANCE=true
VALIDATION_STRICTNESS_LEVEL=high

## ============================================================================
## DEVELOPMENT AND DEBUGGING
## ============================================================================

# Debug Mode
DEBUG_MODE_ENABLED=false
DEBUG_LOG_LEVEL=DEBUG
DEBUG_OUTPUT_DIRECTORY=./debug/
DEBUG_TRACE_EXECUTION=true
DEBUG_PROFILE_PERFORMANCE=false

# Testing
TEST_MODE_ENABLED=false
TEST_DATA_DIRECTORY=./test_data/
TEST_MAX_FILES=100
TEST_SKIP_LARGE_FILES=true

# Development
DEVELOPMENT_MODE=false
SKIP_VALIDATION_IN_DEV=false
FAST_MODE_IN_DEV=true
DEV_MAX_FILES=1000

## ============================================================================
## DEPLOYMENT ENVIRONMENT
## ============================================================================

# Environment Detection
ENVIRONMENT=development  # development, staging, production
DEPLOYMENT_TYPE=local  # local, docker, kubernetes, cloud

# Docker/Kubernetes
CONTAINER_MEMORY_LIMIT=4G
CONTAINER_CPU_LIMIT=2
CONTAINER_STORAGE_LIMIT=10G

# Cloud Deployment
CLOUD_PROVIDER=none  # aws, azure, gcp, none
CLOUD_REGION=us-east-1
CLOUD_STORAGE_BUCKET=

## ============================================================================
## NOTES AND INSTRUCTIONS
## ============================================================================

# 1. Copy this file to `.env` in the project root
# 2. Fill in your API keys and configuration values
# 3. Never commit `.env` to version control
# 4. Use environment-specific files for different deployments:
#    - `.env.development`
#    - `.env.staging`
#    - `.env.production`
#
# 5. Required variables for basic operation:
#    - WORKSPACE_ROOT
#    - OUTPUT_DIRECTORY
#    - LOG_LEVEL
#    - LOCAL_EMBEDDING_MODEL
#    - VECTOR_DATABASE_TYPE
#
# 6. Optional variables for advanced features:
#    - OPENAI_API_KEY (for cloud embeddings)
#    - COHERE_API_KEY (for alternative embeddings)
#    - WHISPER_MODEL (for media processing)
#    - PINECONE_API_KEY (for cloud vector DB)
#
# 7. Security best practices:
#    - Use different API keys for different environments
#    - Rotate API keys regularly
#    - Monitor usage and set budget alerts
#    - Process sensitive data locally when possible
#
# 8. Performance tuning:
#    - Adjust MAX_WORKERS based on CPU cores
#    - Adjust MEMORY_LIMIT_MB based on available RAM
#    - Adjust batch sizes for optimal throughput
#    - Enable caching for repeated operations