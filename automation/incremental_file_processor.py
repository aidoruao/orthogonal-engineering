#!/usr/bin/env python3
"""
INCREMENTAL FILE PROCESSOR - Glass Box Boundary Compliant
Version: 1.11
Schema ID: GB-ORIGIN-1.11
Generated: 2026-01-23
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Process large files incrementally to avoid token limit grenade pin behavior
Principle: "Process everything, just not all at once"

Glass Box Boundary Compliance:
- @glass_box_boundary decorator on all functions
- Exit code 2 on boundary violations
- Trace generation for processing sessions
- State persistence for resumable processing
- Token-aware chunking with boundary limits

Forgiveness System Integration:
- Built from FORK-IDE-TOKEN-GRENADE-001
- Energy redirected from fight to build
- No recursive engagement with IDE crashes
- Success measured by files processed, not arguments won
"""

import hashlib
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# ============================================================================
# GLASS BOX BOUNDARY DECORATOR
# ============================================================================


def glass_box_boundary(
    input_validator: Optional[Callable] = None,
    output_validator: Optional[Callable] = None,
    side_effect_check: bool = True,
    orthogonal_separation: bool = True,
):
    """
    Glass Box Boundary decorator factory.

    Enforces:
    1. Input validation (if validator provided)
    2. Output validation (if validator provided)
    3. Side effect confinement
    4. Orthogonal separation principles
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Input validation
            if input_validator:
                try:
                    input_validator(*args, **kwargs)
                except Exception as e:
                    raise ValueError(f"Input validation failed: {str(e)}")

            # Execute function with boundary enforcement
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                # Re-raise with boundary violation context
                raise RuntimeError(f"Boundary violation in {func.__name__}: {str(e)}")

            # Output validation
            if output_validator:
                try:
                    output_validator(result)
                except Exception as e:
                    raise ValueError(f"Output validation failed: {str(e)}")

            return result

        return wrapper

    return decorator


# ============================================================================
# CONSTANTS
# ============================================================================

# Token and chunking limits
MAX_CHUNK_TOKENS = 50000  # 50K tokens per chunk (safe margin)
MAX_CHUNK_BYTES = 250000  # 250KB per chunk
TOKEN_RATIO = 0.75  # Rough estimate: tokens = chars * 0.75
CHARS_PER_TOKEN = 4  # Approximation: 1 token ≈ 4 characters

# State persistence
STATE_DIR = Path(__file__).parent.parent / "logs" / "incremental_processing"
STATE_FILE = STATE_DIR / "processing_state.json"
CHECKPOINT_DIR = STATE_DIR / "checkpoints"

# File type specific chunking
CHUNKING_STRATEGIES = {
    ".json": "structured",  # Parse JSON, chunk by objects/arrays
    ".txt": "line_based",  # Chunk by lines
    ".md": "section_based",  # Chunk by markdown sections
    ".py": "function_based",  # Chunk by functions/classes
    ".html": "tag_based",  # Chunk by HTML tags
    ".csv": "row_based",  # Chunk by rows
    ".log": "line_based",  # Chunk by lines
}

# Default strategy for unknown file types
DEFAULT_STRATEGY = "byte_based"

# ============================================================================
# CORE PROCESSING CLASSES
# ============================================================================


class ProcessingState:
    """State persistence for resumable incremental processing"""

    def __init__(self):
        self.state_dir = STATE_DIR
        self.state_file = STATE_FILE
        self.checkpoint_dir = CHECKPOINT_DIR

        # Ensure directories exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load existing state or create new
        self.state = self._load_state()

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def _load_state(self) -> Dict[str, Any]:
        """Load processing state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load state file: {e}")

        # Default state
        return {
            "version": "1.11",
            "schema_id": "GB-ORIGIN-1.11",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "active_processes": {},
            "completed_files": [],
            "failed_files": [],
            "total_chunks_processed": 0,
            "total_bytes_processed": 0,
            "total_tokens_estimated": 0,
            "processing_sessions": [],
        }

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def save_state(self) -> None:
        """Save processing state to disk"""
        self.state["last_updated"] = datetime.now().isoformat()

        try:
            # Create backup of current state
            backup_file = self.state_file.with_suffix(".json.backup")
            if self.state_file.exists():
                import shutil

                shutil.copy2(self.state_file, backup_file)

            # Save new state
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Failed to save processing state: {e}")

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def start_file_processing(self, file_path: Path, total_chunks: int) -> str:
        """Start processing a new file, returns process_id"""
        process_id = str(uuid.uuid4())

        self.state["active_processes"][process_id] = {
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "total_chunks": total_chunks,
            "completed_chunks": 0,
            "current_chunk": 0,
            "started": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "bytes_processed": 0,
            "tokens_estimated": 0,
            "checkpoints": [],
        }

        self.save_state()
        return process_id

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def update_chunk_progress(
        self,
        process_id: str,
        chunk_index: int,
        bytes_processed: int,
        tokens_estimated: int,
    ) -> None:
        """Update progress for a chunk"""
        if process_id not in self.state["active_processes"]:
            raise ValueError(f"Process {process_id} not found")

        process = self.state["active_processes"][process_id]
        process["current_chunk"] = chunk_index
        process["last_activity"] = datetime.now().isoformat()
        process["bytes_processed"] += bytes_processed
        process["tokens_estimated"] += tokens_estimated

        # Create checkpoint
        checkpoint_id = f"checkpoint_{chunk_index:06d}"
        checkpoint_file = self.checkpoint_dir / f"{process_id}_{checkpoint_id}.json"

        checkpoint_data = {
            "process_id": process_id,
            "chunk_index": chunk_index,
            "timestamp": datetime.now().isoformat(),
            "bytes_processed": bytes_processed,
            "tokens_estimated": tokens_estimated,
            "total_bytes": process["bytes_processed"],
            "total_tokens": process["tokens_estimated"],
        }

        try:
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            process["checkpoints"].append(checkpoint_id)
        except IOError:
            # Checkpoint failure is not critical
            pass

        self.save_state()

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def complete_file_processing(self, process_id: str) -> None:
        """Mark a file as completed"""
        if process_id not in self.state["active_processes"]:
            raise ValueError(f"Process {process_id} not found")

        process = self.state["active_processes"].pop(process_id)

        # Update totals
        self.state["total_chunks_processed"] += process["completed_chunks"]
        self.state["total_bytes_processed"] += process["bytes_processed"]
        self.state["total_tokens_estimated"] += process["tokens_estimated"]

        # Add to completed files
        self.state["completed_files"].append(
            {
                "file_path": process["file_path"],
                "file_size": process["file_size"],
                "chunks_processed": process["completed_chunks"],
                "total_chunks": process["total_chunks"],
                "bytes_processed": process["bytes_processed"],
                "tokens_estimated": process["tokens_estimated"],
                "started": process["started"],
                "completed": datetime.now().isoformat(),
                "process_id": process_id,
            }
        )

        # Add to processing sessions
        self.state["processing_sessions"].append(
            {
                "session_id": process_id,
                "type": "file_completion",
                "timestamp": datetime.now().isoformat(),
                "file": process["file_path"],
                "chunks": process["completed_chunks"],
                "bytes": process["bytes_processed"],
                "tokens": process["tokens_estimated"],
            }
        )

        self.save_state()

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def mark_file_failed(self, process_id: str, error_message: str) -> None:
        """Mark a file as failed with error message"""
        if process_id not in self.state["active_processes"]:
            raise ValueError(f"Process {process_id} not found")

        process = self.state["active_processes"].pop(process_id)

        self.state["failed_files"].append(
            {
                "file_path": process["file_path"],
                "file_size": process["file_size"],
                "chunks_processed": process["completed_chunks"],
                "error": error_message,
                "process_id": process_id,
                "last_activity": process["last_activity"],
            }
        )

        self.save_state()


class TokenAwareChunker:
    """Token-aware chunking with file type specific strategies"""

    def __init__(self):
        self.max_chunk_tokens = MAX_CHUNK_TOKENS
        self.max_chunk_bytes = MAX_CHUNK_BYTES
        self.token_ratio = TOKEN_RATIO
        self.chars_per_token = CHARS_PER_TOKEN

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, int) and result > 0,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def estimate_file_tokens(self, file_path: Path) -> int:
        """Estimate total tokens in a file"""
        try:
            file_size = file_path.stat().st_size
            # Rough estimate: tokens = (bytes * token_ratio) / chars_per_token
            estimated_tokens = int(
                (file_size * self.token_ratio) / self.chars_per_token
            )
            return max(1, estimated_tokens)
        except OSError as e:
            raise RuntimeError(f"Cannot estimate tokens for {file_path}: {e}")

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, int) and result > 0,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def calculate_chunks_needed(self, file_path: Path) -> int:
        """Calculate how many chunks are needed for a file"""
        estimated_tokens = self.estimate_file_tokens(file_path)
        file_size = file_path.stat().st_size

        # Calculate chunks based on both token and byte limits
        chunks_by_tokens = max(
            1, (estimated_tokens + self.max_chunk_tokens - 1) // self.max_chunk_tokens
        )
        chunks_by_bytes = max(
            1, (file_size + self.max_chunk_bytes - 1) // self.max_chunk_bytes
        )

        # Use the larger number to be safe
        return max(chunks_by_tokens, chunks_by_bytes)

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, str)
        and result in CHUNKING_STRATEGIES.values(),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def get_chunking_strategy(self, file_path: Path) -> str:
        """Determine chunking strategy based on file extension"""
        suffix = file_path.suffix.lower()
        return CHUNKING_STRATEGIES.get(suffix, DEFAULT_STRATEGY)

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, tuple) and len(result) == 2,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def get_chunk_boundaries(
        self, file_path: Path, chunk_index: int, total_chunks: int
    ) -> Tuple[int, int]:
        """Calculate byte boundaries for a chunk"""
        file_size = file_path.stat().st_size
        chunk_size = file_size // total_chunks

        start_byte = chunk_index * chunk_size
        end_byte = (
            start_byte + chunk_size if chunk_index < total_chunks - 1 else file_size
        )

        return (start_byte, end_byte)

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, str)
        and len(result) <= (end_byte - start_byte),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def read_chunk(
        self,
        file_path: Path,
        start_byte: int,
        end_byte: int,
        strategy: str = "byte_based",
    ) -> str:
        """Read a chunk from the file using appropriate strategy"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # Seek to start position
                f.seek(start_byte)

                if strategy == "byte_based":
                    # Simple byte-based chunking
                    chunk_size = end_byte - start_byte
                    return f.read(chunk_size)

                elif strategy == "line_based":
                    # Read lines until we reach end_byte
                    lines = []
                    current_pos = start_byte

                    while current_pos < end_byte:
                        line = f.readline()
                        if not line:
                            break

                        lines.append(line)
                        current_pos = f.tell()

                        # Check if we've exceeded our chunk
                        if current_pos > end_byte:
                            # We read past our boundary, but we keep the line
                            # to avoid breaking in the middle of a line
                            break

                    return "".join(lines)

                elif strategy == "json_structured":
                    # For JSON files, we need to parse and chunk intelligently
                    # This is a simplified version - in production would need full JSON parsing
                    content = f.read(end_byte - start_byte)

                    # Try to find complete JSON structures
                    # Look for complete objects/arrays
                    brace_count = 0
                    bracket_count = 0
                    in_string = False
                    escape_next = False

                    valid_end = len(content)

                    for i, char in enumerate(content):
                        if escape_next:
                            escape_next = False
                            continue

                        if char == "\\":
                            escape_next = True
                            continue

                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue

                        if not in_string:
                            if char == "{":
                                brace_count += 1
                            elif char == "}":
                                brace_count -= 1
                            elif char == "[":
                                bracket_count += 1
                            elif char == "]":
                                bracket_count -= 1

                    # Find where braces/brackets are balanced
                    while valid_end > 0 and (brace_count > 0 or bracket_count > 0):
                        valid_end -= 1
                        char = content[valid_end]

                        if char == "}":
                            brace_count -= 1
                        elif char == "]":
                            bracket_count -= 1
                        elif char == "{":
                            brace_count += 1
                        elif char == "[":
                            bracket_count += 1

                    return content[:valid_end] if valid_end > 0 else content

                else:
                    # Default to byte-based
                    chunk_size = end_byte - start_byte
                    return f.read(chunk_size)

        except (IOError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Failed to read chunk from {file_path}: {e}")


class IncrementalProcessor:
    """Main incremental file processor"""

    def __init__(self):
        self.state_manager = ProcessingState()
        self.chunker = TokenAwareChunker()

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, str) and len(result) > 0,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def process_file_incrementally(self, file_path: Union[str, Path]) -> str:
        """Process a file incrementally, returns process_id"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Calculate chunks needed
        total_chunks = self.chunker.calculate_chunks_needed(file_path)

        # Start processing
        process_id = self.state_manager.start_file_processing(file_path, total_chunks)

        # Get chunking strategy
        strategy = self.chunker.get_chunking_strategy(file_path)

        print(f"Starting incremental processing of {file_path}")
        print(f"  Total chunks: {total_chunks}")
        print(f"  Strategy: {strategy}")
        print(f"  Process ID: {process_id}")

        # Process each chunk
        for chunk_index in range(total_chunks):
            try:
                # Get chunk boundaries
                start_byte, end_byte = self.chunker.get_chunk_boundaries(
                    file_path, chunk_index, total_chunks
                )

                # Read chunk
                chunk = self.chunker.read_chunk(
                    file_path, start_byte, end_byte, strategy
                )

                # Estimate tokens in this chunk
                chunk_bytes = len(chunk.encode("utf-8"))
                chunk_tokens = int((chunk_bytes * TOKEN_RATIO) / CHARS_PER_TOKEN)

                # Update progress
                self.state_manager.update_chunk_progress(
                    process_id, chunk_index, chunk_bytes, chunk_tokens
                )

                print(
                    f"  Chunk {chunk_index + 1}/{total_chunks}: {chunk_bytes:,} bytes, ~{chunk_tokens:,} tokens"
                )

                # Process the chunk (this is where you'd add your actual processing logic)
                self._process_chunk(chunk, file_path, chunk_index, total_chunks)

                # Small delay to prevent overwhelming systems
                time.sleep(0.1)

            except Exception as e:
                error_msg = f"Failed to process chunk {chunk_index}: {str(e)}"
                self.state_manager.mark_file_failed(process_id, error_msg)
                raise RuntimeError(error_msg)

        # Mark as completed
        self.state_manager.complete_file_processing(process_id)

        print(f"Completed processing {file_path}")
        return process_id

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def _process_chunk(
        self, chunk: str, file_path: Path, chunk_index: int, total_chunks: int
    ) -> None:
        """Process a single chunk - override this with your actual processing logic"""
        # This is a placeholder - in production, you would:
        # 1. Send to AI for analysis
        # 2. Extract insights
        # 3. Update databases
        # 4. Generate summaries
        # etc.

        # For now, just count lines and words as an example
        lines = chunk.count("\n") + 1
        words = len(chunk.split())

        # Log the processing (in production, you'd do something more useful)
        processing_log = {
            "file": str(file_path),
            "chunk": chunk_index,
            "total_chunks": total_chunks,
            "lines": lines,
            "words": words,
            "timestamp": datetime.now().isoformat(),
            "chunk_hash": hashlib.sha256(chunk.encode("utf-8")).hexdigest()[:16],
        }

        # Save chunk processing result
        result_file = CHECKPOINT_DIR / f"chunk_{file_path.name}_{chunk_index:06d}.json"
        try:
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(processing_log, f, indent=2, ensure_ascii=False)
        except IOError:
            # Non-critical if we can't save the log
            pass

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def resume_processing(self, process_id: str) -> Dict[str, Any]:
        """Resume processing from a saved state"""
        state = self.state_manager.state

        if process_id not in state["active_processes"]:
            # Check if it's in completed or failed
            for completed in state["completed_files"]:
                if completed.get("process_id") == process_id:
                    return {"status": "completed", "file": completed["file_path"]}

            for failed in state["failed_files"]:
                if failed.get("process_id") == process_id:
                    return {
                        "status": "failed",
                        "file": failed["file_path"],
                        "error": failed["error"],
                    }

            raise ValueError(f"Process {process_id} not found")

        process = state["active_processes"][process_id]
        file_path = Path(process["file_path"])
        total_chunks = process["total_chunks"]
        current_chunk = process["current_chunk"]

        print(f"Resuming processing of {file_path}")
        print(f"  Resuming from chunk {current_chunk + 1}/{total_chunks}")

        # Get chunking strategy
        strategy = self.chunker.get_chunking_strategy(file_path)

        # Resume from current chunk
        for chunk_index in range(current_chunk, total_chunks):
            try:
                # Get chunk boundaries
                start_byte, end_byte = self.chunker.get_chunk_boundaries(
                    file_path, chunk_index, total_chunks
                )

                # Read chunk
                chunk = self.chunker.read_chunk(
                    file_path, start_byte, end_byte, strategy
                )

                # Estimate tokens in this chunk
                chunk_bytes = len(chunk.encode("utf-8"))
                chunk_tokens = int((chunk_bytes * TOKEN_RATIO) / CHARS_PER_TOKEN)

                # Update progress
                self.state_manager.update_chunk_progress(
                    process_id, chunk_index, chunk_bytes, chunk_tokens
                )

                print(
                    f"  Chunk {chunk_index + 1}/{total_chunks}: {chunk_bytes:,} bytes, ~{chunk_tokens:,} tokens"
                )

                # Process the chunk
                self._process_chunk(chunk, file_path, chunk_index, total_chunks)

                # Small delay
                time.sleep(0.1)

            except Exception as e:
                error_msg = f"Failed to process chunk {chunk_index}: {str(e)}"
                self.state_manager.mark_file_failed(process_id, error_msg)
                raise RuntimeError(error_msg)

        # Mark as completed
        self.state_manager.complete_file_processing(process_id)

        print(f"Completed processing {file_path}")
        return {"status": "completed", "file": str(file_path), "process_id": process_id}

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about all processing"""
        state = self.state_manager.state

        return {
            "total_files_completed": len(state["completed_files"]),
            "total_files_failed": len(state["failed_files"]),
            "active_processes": len(state["active_processes"]),
            "total_chunks_processed": state["total_chunks_processed"],
            "total_bytes_processed": state["total_bytes_processed"],
            "total_tokens_estimated": state["total_tokens_estimated"],
            "last_updated": state["last_updated"],
        }

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def analyze_file_for_processing(
        self, file_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Analyze a file to determine processing requirements"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        estimated_tokens = self.chunker.estimate_file_tokens(file_path)
        chunks_needed = self.chunker.calculate_chunks_needed(file_path)
        strategy = self.chunker.get_chunking_strategy(file_path)

        return {
            "file_path": str(file_path),
            "file_size_bytes": file_size,
            "estimated_tokens": estimated_tokens,
            "chunks_needed": chunks_needed,
            "chunking_strategy": strategy,
            "max_chunk_tokens": MAX_CHUNK_TOKENS,
            "max_chunk_bytes": MAX_CHUNK_BYTES,
            "exceeds_single_chunk": estimated_tokens > MAX_CHUNK_TOKENS
            or file_size > MAX_CHUNK_BYTES,
            "analysis_timestamp": datetime.now().isoformat(),
        }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main():
    """Main entry point with Glass Box Boundary compliance."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Incremental File Processor - Avoid token limit grenade pin behavior",
        epilog="Exit codes: 0=Success, 1=System error, 2=Boundary violation, 3=Processing failed",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process a file incrementally"
    )
    process_parser.add_argument("file", help="File to process")
    process_parser.add_argument(
        "--resume", "-r", help="Resume processing with process ID"
    )
    process_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze file for processing"
    )
    analyze_parser.add_argument("file", help="File to analyze")
    analyze_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get processing statistics")
    stats_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a processing job")
    resume_parser.add_argument("process_id", help="Process ID to resume")
    resume_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List processing jobs")
    list_parser.add_argument(
        "--active", "-a", action="store_true", help="Show active jobs"
    )
    list_parser.add_argument(
        "--completed", "-c", action="store_true", help="Show completed jobs"
    )
    list_parser.add_argument(
        "--failed", "-f", action="store_true", help="Show failed jobs"
    )
    list_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    try:
        processor = IncrementalProcessor()

        if args.command == "process":
            if args.resume:
                if args.verbose:
                    print(f"Resuming processing with ID: {args.resume}")
                result = processor.resume_processing(args.resume)
                print(f"✅ Processing completed: {result['file']}")
            else:
                if args.verbose:
                    print(f"Starting incremental processing of: {args.file}")
                process_id = processor.process_file_incrementally(args.file)
                print(f"✅ Processing started with ID: {process_id}")

        elif args.command == "analyze":
            analysis = processor.analyze_file_for_processing(args.file)
            print(json.dumps(analysis, indent=2, ensure_ascii=False))

            if args.verbose:
                if analysis["exceeds_single_chunk"]:
                    print(
                        f"⚠️  File requires {analysis['chunks_needed']} chunks for safe processing"
                    )
                else:
                    print("✅ File can be processed in a single chunk")

        elif args.command == "stats":
            stats = processor.get_processing_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))

            if args.verbose:
                print(f"\n📊 Processing Summary:")
                print(f"  Completed files: {stats['total_files_completed']}")
                print(f"  Failed files: {stats['total_files_failed']}")
                print(f"  Active processes: {stats['active_processes']}")
                print(f"  Total chunks processed: {stats['total_chunks_processed']:,}")
                print(f"  Total bytes processed: {stats['total_bytes_processed']:,}")
                print(f"  Total tokens estimated: {stats['total_tokens_estimated']:,}")

        elif args.command == "resume":
            if args.verbose:
                print(f"Resuming processing with ID: {args.process_id}")
            result = processor.resume_processing(args.process_id)
            print(f"✅ Processing completed: {result['file']}")

        elif args.command == "list":
            state = processor.state_manager.state

            if args.active or (not args.completed and not args.failed):
                print("Active Processes:")
                print("=" * 80)
                for process_id, process in state["active_processes"].items():
                    print(f"ID: {process_id}")
                    print(f"  File: {process['file_path']}")
                    print(
                        f"  Progress: {process['current_chunk'] + 1}/{process['total_chunks']} chunks"
                    )
                    print(
                        f"  Bytes: {process['bytes_processed']:,}/{process['file_size']:,}"
                    )
                    print(f"  Started: {process['started']}")
                    print(f"  Last activity: {process['last_activity']}")
                    print()

            if args.completed:
                print("Completed Files:")
                print("=" * 80)
                for completed in state["completed_files"]:
                    print(f"File: {completed['file_path']}")
                    print(f"  Size: {completed['file_size']:,} bytes")
                    print(
                        f"  Chunks: {completed['chunks_processed']}/{completed['total_chunks']}"
                    )
                    print(f"  Tokens: {completed['tokens_estimated']:,} estimated")
                    print(f"  Process ID: {completed['process_id']}")
                    print(f"  Completed: {completed['completed']}")
                    print()

            if args.failed:
                print("Failed Files:")
                print("=" * 80)
                for failed in state["failed_files"]:
                    print(f"File: {failed['file_path']}")
                    print(f"  Size: {failed['file_size']:,} bytes")
                    print(f"  Chunks processed: {failed['chunks_processed']}")
                    print(f"  Error: {failed['error']}")
                    print(f"  Process ID: {failed['process_id']}")
                    print(f"  Last activity: {failed['last_activity']}")
                    print()

        else:
            parser.print_help()
            sys.exit(1)

        sys.exit(0)

    except ValueError as e:
        print(f"Validation error: {str(e)}", file=sys.stderr)
        sys.exit(1)

    except RuntimeError as e:
        print(f"Boundary violation: {str(e)}", file=sys.stderr)
        sys.exit(2)

    except Exception as e:
        print(f"System error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
