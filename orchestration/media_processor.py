#!/usr/bin/env python3
"""
MEDIA PROCESSOR - Orthogonal Engineering Glass-Box Boundary Compliant

Audio and video file processing component for the Sora Pipeline.
Handles transcription, chunking, and metadata extraction from media files.

Version: 1.0.0
Schema ID: GB-MEDIA-PROCESSOR-1.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Framework with Subtractive Clarity Canon

Glass-Box Boundary Compliance:
- All functions use @glass_box_boundary decorator
- Input/output validation for all media operations
- Trace generation for transcription and processing
- Exit code 2 on boundary violations
- Subtractive Clarity Canon compliance (removes ambiguity from media processing)
"""

import argparse
import json
import os
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from toolkit.oe.boundary_enforcer import glass_box_boundary
    from toolkit.oe.evidence_store import EvidenceStore
    from toolkit.oe.ide_orchestration import IDEOrchestrationLayer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure Glass-Box Boundary toolkit is available.")
    sys.exit(1)

# Try to import Whisper for transcription (optional dependency)
try:
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️  Whisper not available. Transcription will be simulated.")

# Try to import moviepy for video processing (optional dependency)
try:
    from moviepy.editor import VideoFileClip

    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠️  MoviePy not available. Video metadata extraction will be limited.")

# Try to import pydub for audio processing (optional dependency)
try:
    from pydub import AudioSegment

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("⚠️  Pydub not available. Audio processing will be limited.")


class MediaProcessor:
    """
    Media processing component for the Sora Pipeline.
    Handles audio/video transcription, chunking, and metadata extraction.
    """

    def __init__(self, workspace_root: Union[str, Path] = "."):
        """
        Initialize the Media Processor.

        Args:
            workspace_root: Root directory for media processing
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.evidence_store = EvidenceStore()
        self.orchestration = None
        self.statistics = self._initialize_statistics()

        # Supported media formats
        self.supported_formats = {
            "audio": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"],
            "video": [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"],
        }

        # Transcription configuration
        self.transcription_config = {
            "engine": "whisper" if WHISPER_AVAILABLE else "simulated",
            "model": "base",
            "language": "en",
            "task": "transcribe",
            "timestamp_resolution": "word",
            "compute_type": "float32" if WHISPER_AVAILABLE else None,
        }

        # Chunking configuration
        self.chunking_config = {
            "strategy": "timestamp_based",
            "seconds_per_chunk": 300,  # 5 minutes
            "speaker_aware": True,
            "preserve_speaker_labels": True,
            "overlap_seconds": 30,
        }

        print(f"✅ Media Processor initialized")
        print(f"   Workspace: {self.workspace_root}")
        print(f"   Whisper available: {WHISPER_AVAILABLE}")
        print(f"   MoviePy available: {MOVIEPY_AVAILABLE}")
        print(f"   Pydub available: {PYDUB_AVAILABLE}")

    @glass_box_boundary()
    def _initialize_statistics(self) -> Dict[str, Any]:
        """Initialize statistics tracking for media processing."""
        return {
            "media_files_processed": 0,
            "audio_files": 0,
            "video_files": 0,
            "total_duration_seconds": 0,
            "transcription_seconds": 0,
            "chunks_generated": 0,
            "errors_encountered": 0,
            "execution_time_seconds": 0,
            "boundary_checks": 0,
        }

    @glass_box_boundary()
    def initialize_orchestration(
        self, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize the orchestration layer for media processing.

        Args:
            session_id: Optional session ID for continuity

        Returns:
            Initialization result
        """
        try:
            self.orchestration = IDEOrchestrationLayer(
                workspace_root=str(self.workspace_root), session_id=session_id
            )

            print(
                f"✅ Media orchestration initialized: {self.orchestration.session_id}"
            )

            return {
                "initialized": True,
                "session_id": self.orchestration.session_id,
                "workspace_root": str(self.workspace_root),
            }
        except Exception as e:
            print(f"❌ Failed to initialize media orchestration: {e}")
            return {"initialized": False, "error": str(e)}

    @glass_box_boundary()
    def scan_media_files(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_duration_hours: float = 10.0,
        extract_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Scan for media files in the workspace.

        Args:
            include_patterns: File patterns to include
            exclude_patterns: File patterns to exclude
            max_duration_hours: Maximum media duration to process
            extract_metadata: Whether to extract metadata from files

        Returns:
            Media inventory with file information
        """
        start_time = time.time()

        if include_patterns is None:
            include_patterns = list(
                self.supported_formats["audio"] + self.supported_formats["video"]
            )

        if exclude_patterns is None:
            exclude_patterns = ["**/__pycache__/**", "**/.git/**", "**/node_modules/**"]

        print("=" * 70)
        print("MEDIA SCAN: Discovering Audio/Video Files")
        print("=" * 70)
        print(f"   Include patterns: {include_patterns}")
        print(f"   Max duration: {max_duration_hours} hours")
        print(f"   Extract metadata: {extract_metadata}")

        media_files = []
        audio_files = []
        video_files = []
        skipped_files = []

        # Start workflow if orchestration is available
        workflow_result = {"status": "not_started"}
        if self.orchestration:
            workflow_result = self.orchestration.start_workflow(
                workflow_name="media_processing",
                components=["media_processor"],
                parameters={
                    "include_patterns": include_patterns,
                    "max_duration_hours": max_duration_hours,
                    "extract_metadata": extract_metadata,
                },
            )

        try:
            # Scan for files
            for pattern in include_patterns:
                for file_path in self.workspace_root.rglob(pattern.lstrip("./")):
                    # Check exclusions
                    skip = False
                    for exclude in exclude_patterns:
                        if file_path.match(exclude):
                            skip = True
                            break

                    if skip:
                        skipped_files.append(str(file_path))
                        continue

                    # Classify file type
                    file_info = self._analyze_media_file(
                        file_path,
                        extract_metadata=extract_metadata,
                        max_duration_hours=max_duration_hours,
                    )

                    if file_info.get("skipped", False):
                        skipped_files.append(str(file_path))
                        continue

                    media_files.append(file_info)

                    if file_info["file_type"] == "audio":
                        audio_files.append(file_info)
                    elif file_info["file_type"] == "video":
                        video_files.append(file_info)

            execution_time = time.time() - start_time

            # Update statistics
            self.statistics["media_files_processed"] = len(media_files)
            self.statistics["audio_files"] = len(audio_files)
            self.statistics["video_files"] = len(video_files)
            self.statistics["execution_time_seconds"] += execution_time
            self.statistics["boundary_checks"] += 1

            # Log evidence
            self.evidence_store.log_evidence(
                evidence_type="media_scan_completed",
                content={
                    "media_files_found": len(media_files),
                    "audio_files": len(audio_files),
                    "video_files": len(video_files),
                    "skipped_files": len(skipped_files),
                    "execution_time": execution_time,
                },
                source="media_processor.scan_media_files",
                metadata={"workspace_root": str(self.workspace_root)},
            )

            print(f"\n✅ Media scan completed:")
            print(f"   Total media files: {len(media_files)}")
            print(f"   Audio files: {len(audio_files)}")
            print(f"   Video files: {len(video_files)}")
            print(f"   Skipped files: {len(skipped_files)}")
            print(f"   Execution time: {execution_time:.2f}s")

            result = {
                "media_files": media_files,
                "audio_files": audio_files,
                "video_files": video_files,
                "skipped_files": skipped_files,
                "total_files": len(media_files),
                "execution_time": execution_time,
                "workspace_root": str(self.workspace_root),
            }

            # Complete workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="media_processing",
                    status="completed",
                    summary={
                        "media_files_processed": len(media_files),
                        "execution_time": execution_time,
                        "scan_results": result,
                    },
                )

            return result

        except Exception as e:
            print(f"❌ Media scan failed: {e}")

            # Fail workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="media_processing",
                    status="failed",
                    summary={"error": str(e)},
                )

            return {"error": f"Media scan failed: {e}"}

    @glass_box_boundary()
    def _analyze_media_file(
        self,
        file_path: Path,
        extract_metadata: bool = True,
        max_duration_hours: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Analyze a single media file and extract metadata.

        Args:
            file_path: Path to the media file
            extract_metadata: Whether to extract detailed metadata
            max_duration_hours: Maximum duration to allow

        Returns:
            File information dictionary
        """
        file_info = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "file_type": None,
            "duration_seconds": None,
            "format": file_path.suffix.lower(),
            "sha256_hash": None,
            "metadata": {},
            "skipped": False,
            "skip_reason": None,
        }

        # Determine file type
        if file_path.suffix.lower() in self.supported_formats["audio"]:
            file_info["file_type"] = "audio"
        elif file_path.suffix.lower() in self.supported_formats["video"]:
            file_info["file_type"] = "video"
        else:
            file_info["skipped"] = True
            file_info["skip_reason"] = "unsupported_format"
            return file_info

        # Calculate SHA256 hash
        try:
            import hashlib

            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
                file_info["sha256_hash"] = file_hash.hexdigest()
        except Exception as e:
            print(f"⚠️ Could not calculate hash for {file_path}: {e}")

        # Extract duration and metadata
        if extract_metadata:
            try:
                if file_info["file_type"] == "audio" and PYDUB_AVAILABLE:
                    audio = AudioSegment.from_file(file_path)
                    file_info["duration_seconds"] = len(audio) / 1000.0
                    file_info["metadata"]["audio_channels"] = audio.channels
                    file_info["metadata"]["sample_rate"] = audio.frame_rate
                    file_info["metadata"]["sample_width"] = audio.sample_width

                elif file_info["file_type"] == "video" and MOVIEPY_AVAILABLE:
                    with VideoFileClip(str(file_path)) as video:
                        file_info["duration_seconds"] = video.duration
                        file_info["metadata"]["video_resolution"] = (
                            f"{video.size[0]}x{video.size[1]}"
                        )
                        file_info["metadata"]["video_fps"] = video.fps

                        if video.audio:
                            file_info["metadata"]["has_audio"] = True
                            file_info["metadata"]["audio_fps"] = video.audio.fps
                        else:
                            file_info["metadata"]["has_audio"] = False

                else:
                    # Simulate duration for demonstration
                    # Handle zero file size to avoid division by zero
                    if file_info["file_size_bytes"] > 0:
                        file_info["duration_seconds"] = min(
                            file_info["file_size_bytes"]
                            / (1024 * 1024),  # 1MB ≈ 1 second
                            3600 * max_duration_hours,  # Cap at max duration
                        )
                    else:
                        # Default to 60 seconds for empty files
                        file_info["duration_seconds"] = min(
                            60.0, 3600 * max_duration_hours
                        )
                    file_info["metadata"]["simulated"] = True

                # Check duration limit
                if (
                    file_info["duration_seconds"] is not None
                    and file_info["duration_seconds"] > max_duration_hours * 3600
                ):
                    file_info["skipped"] = True
                    file_info["skip_reason"] = (
                        f"duration_exceeds_limit_{max_duration_hours}h"
                    )

                # Update total duration statistics
                if file_info["duration_seconds"]:
                    self.statistics["total_duration_seconds"] += file_info[
                        "duration_seconds"
                    ]

            except Exception as e:
                print(f"⚠️ Could not extract metadata from {file_path}: {e}")
                file_info["metadata"]["extraction_error"] = str(e)

        return file_info

    @glass_box_boundary()
    def transcribe_media(
        self,
        media_files: List[Dict[str, Any]],
        engine: str = "whisper",
        model: str = "base",
        language: str = "en",
        task: str = "transcribe",
        timestamp_resolution: str = "word",
    ) -> Dict[str, Any]:
        """
        Transcribe audio from media files.

        Args:
            media_files: List of media file information from scan
            engine: Transcription engine to use
            model: Model to use for transcription
            language: Language for transcription
            task: "transcribe" or "translate"
            timestamp_resolution: "word" or "segment"

        Returns:
            Transcription results
        """
        start_time = time.time()

        print("=" * 70)
        print("MEDIA TRANSCRIPTION: Converting Audio to Text")
        print("=" * 70)
        print(f"   Engine: {engine}")
        print(f"   Model: {model}")
        print(f"   Language: {language}")
        print(f"   Task: {task}")
        print(f"   Files to transcribe: {len(media_files)}")

        # Start workflow if orchestration is available
        workflow_result = {"status": "not_started"}
        if self.orchestration:
            workflow_result = self.orchestration.start_workflow(
                workflow_name="media_transcription",
                components=["media_processor"],
                parameters={
                    "engine": engine,
                    "model": model,
                    "language": language,
                    "task": task,
                    "file_count": len(media_files),
                },
            )

        transcripts = []
        failed_transcriptions = []

        try:
            for i, file_info in enumerate(media_files):
                file_path = Path(file_info["file_path"])

                print(f"\n📝 Transcribing {i + 1}/{len(media_files)}: {file_path.name}")
                print(f"   Type: {file_info['file_type']}")
                print(
                    f"   Duration: {file_info.get('duration_seconds', 'unknown'):.1f}s"
                )

                transcript_result = self._transcribe_single_file(
                    file_path=file_path,
                    file_info=file_info,
                    engine=engine,
                    model=model,
                    language=language,
                    task=task,
                    timestamp_resolution=timestamp_resolution,
                )

                if "error" in transcript_result:
                    print(f"❌ Transcription failed: {transcript_result['error']}")
                    failed_transcriptions.append(
                        {
                            "file_path": str(file_path),
                            "error": transcript_result["error"],
                        }
                    )
                else:
                    print(f"✅ Transcription successful")
                    print(f"   Segments: {len(transcript_result.get('segments', []))}")
                    print(
                        f"   Text length: {len(transcript_result.get('text', ''))} chars"
                    )

                    transcripts.append(transcript_result)

            execution_time = time.time() - start_time

            # Update statistics
            self.statistics["transcription_seconds"] += execution_time
            self.statistics["execution_time_seconds"] += execution_time
            self.statistics["boundary_checks"] += 1

            # Log evidence
            self.evidence_store.log_evidence(
                evidence_type="media_transcription_completed",
                content={
                    "files_transcribed": len(transcripts),
                    "files_failed": len(failed_transcriptions),
                    "total_execution_time": execution_time,
                    "average_time_per_file": execution_time / max(len(transcripts), 1),
                },
                source="media_processor.transcribe_media",
                metadata={
                    "engine": engine,
                    "model": model,
                    "language": language,
                    "task": task,
                },
            )

            print(f"\n✅ Media transcription completed:")
            print(f"   Successful transcriptions: {len(transcripts)}")
            print(f"   Failed transcriptions: {len(failed_transcriptions)}")
            print(f"   Total execution time: {execution_time:.2f}s")

            result = {
                "transcripts": transcripts,
                "failed_transcriptions": failed_transcriptions,
                "successful_count": len(transcripts),
                "failed_count": len(failed_transcriptions),
                "execution_time": execution_time,
                "engine_used": engine,
                "model_used": model,
            }

            # Complete workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="media_transcription",
                    status="completed",
                    summary={
                        "transcripts_generated": len(transcripts),
                        "execution_time": execution_time,
                        "transcription_results": result,
                    },
                )

            return result

        except Exception as e:
            print(f"❌ Media transcription failed: {e}")

            # Fail workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="media_transcription",
                    status="failed",
                    summary={"error": str(e)},
                )

            return {"error": f"Media transcription failed: {e}"}

    @glass_box_boundary()
    def _transcribe_single_file(
        self,
        file_path: Path,
        file_info: Dict[str, Any],
        engine: str = "whisper",
        model: str = "base",
        language: str = "en",
        task: str = "transcribe",
        timestamp_resolution: str = "word",
    ) -> Dict[str, Any]:
        """
        Transcribe a single media file.

        Args:
            file_path: Path to the media file
            file_info: File information dictionary
            engine: Transcription engine to use
            model: Model to use for transcription
            language: Language for transcription
            task: "transcribe" or "translate"
            timestamp_resolution: "word" or "segment"

        Returns:
            Transcription result
        """
        start_time = time.time()

        try:
            if engine == "whisper" and WHISPER_AVAILABLE:
                # Load Whisper model
                whisper_model = whisper.load_model(model)

                # Transcribe audio
                result = whisper_model.transcribe(
                    str(file_path),
                    language=language,
                    task=task,
                    word_timestamps=(timestamp_resolution == "word"),
                )

                transcription_result = {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_type": file_info["file_type"],
                    "duration_seconds": file_info.get("duration_seconds"),
                    "text": result["text"],
                    "segments": result.get("segments", []),
                    "language": result.get("language", language),
                    "engine": engine,
                    "model": model,
                    "transcription_time": time.time() - start_time,
                    "success": True,
                }

            else:
                # Simulated transcription for demonstration
                duration = file_info.get("duration_seconds", 300)  # Default 5 minutes
                word_count = int(duration * 2)  # ~2 words per second

                # Generate simulated transcription text
                simulated_text = f"Simulated transcription of {file_path.name}. "
                simulated_text += "This is a placeholder for actual transcription. "
                simulated_text += f"File duration: {duration:.1f} seconds. "
                simulated_text += "Actual transcription requires Whisper installation. "

                # Add more simulated content (handle zero duration case)
                if word_count > 0:
                    for i in range(min(word_count // 10, 50)):
                        simulated_text += (
                            f"Simulated sentence {i + 1} for demonstration. "
                        )
                else:
                    simulated_text += "File has no content or zero duration. "

                # Create simulated segments
                segments = []
                segment_duration = min(
                    30, duration / 10
                )  # 30-second segments or 10 segments
                for i in range(int(duration / segment_duration)):
                    segments.append(
                        {
                            "id": i,
                            "start": i * segment_duration,
                            "end": (i + 1) * segment_duration,
                            "text": f"Simulated segment {i + 1} of {file_path.name}",
                        }
                    )

                transcription_result = {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_type": file_info["file_type"],
                    "duration_seconds": file_info.get("duration_seconds"),
                    "text": simulated_text,
                    "segments": segments,
                    "language": language,
                    "engine": "simulated",
                    "model": "simulated",
                    "transcription_time": time.time() - start_time,
                    "success": True,
                    "simulated": True,
                }

            # Log evidence
            self.evidence_store.log_evidence(
                evidence_type="file_transcription_completed",
                content={
                    "file_path": str(file_path),
                    "transcription_time": transcription_result["transcription_time"],
                    "text_length": len(transcription_result["text"]),
                    "segment_count": len(transcription_result.get("segments", [])),
                },
                source="media_processor._transcribe_single_file",
                metadata={
                    "engine": engine,
                    "model": model,
                    "language": language,
                },
            )

            return transcription_result

        except Exception as e:
            print(f"❌ Transcription failed for {file_path}: {e}")

            # Log error evidence
            self.evidence_store.log_evidence(
                evidence_type="file_transcription_failed",
                content={
                    "file_path": str(file_path),
                    "error": str(e),
                    "transcription_time": time.time() - start_time,
                },
                source="media_processor._transcribe_single_file",
                metadata={
                    "engine": engine,
                    "model": model,
                },
            )

            return {
                "file_path": str(file_path),
                "error": str(e),
                "success": False,
            }

    @glass_box_boundary()
    def chunk_transcripts(
        self,
        transcripts: List[Dict[str, Any]],
        strategy: str = "timestamp_based",
        seconds_per_chunk: int = 300,
        speaker_aware: bool = True,
        preserve_speaker_labels: bool = True,
        overlap_seconds: int = 30,
    ) -> Dict[str, Any]:
        """
        Chunk transcriptions into manageable pieces.

        Args:
            transcripts: List of transcription results
            strategy: Chunking strategy ("timestamp_based", "segment_based", "fixed_size")
            seconds_per_chunk: Target chunk size in seconds
            speaker_aware: Whether to preserve speaker boundaries
            preserve_speaker_labels: Whether to keep speaker labels in chunks
            overlap_seconds: Overlap between chunks in seconds

        Returns:
            Chunked transcripts
        """
        start_time = time.time()

        print("=" * 70)
        print("TRANSCRIPT CHUNKING: Organizing Transcription Data")
        print("=" * 70)
        print(f"   Strategy: {strategy}")
        print(f"   Seconds per chunk: {seconds_per_chunk}")
        print(f"   Speaker aware: {speaker_aware}")
        print(f"   Overlap: {overlap_seconds}s")
        print(f"   Transcripts to chunk: {len(transcripts)}")

        # Start workflow if orchestration is available
        workflow_result = {"status": "not_started"}
        if self.orchestration:
            workflow_result = self.orchestration.start_workflow(
                workflow_name="transcript_chunking",
                components=["media_processor"],
                parameters={
                    "strategy": strategy,
                    "seconds_per_chunk": seconds_per_chunk,
                    "speaker_aware": speaker_aware,
                    "transcript_count": len(transcripts),
                },
            )

        all_chunks = []
        chunk_metadata = []

        try:
            for transcript in transcripts:
                file_chunks = self._chunk_single_transcript(
                    transcript=transcript,
                    strategy=strategy,
                    seconds_per_chunk=seconds_per_chunk,
                    speaker_aware=speaker_aware,
                    preserve_speaker_labels=preserve_speaker_labels,
                    overlap_seconds=overlap_seconds,
                )

                all_chunks.extend(file_chunks)

                # Create chunk metadata
                for i, chunk in enumerate(file_chunks):
                    chunk_metadata.append(
                        {
                            "chunk_id": f"T{len(chunk_metadata):04d}",
                            "source_file": transcript["file_path"],
                            "source_file_name": transcript["file_name"],
                            "chunk_index": i,
                            "total_chunks": len(file_chunks),
                            "timestamp_start": chunk.get("timestamp_start", 0),
                            "timestamp_end": chunk.get("timestamp_end", 0),
                            "duration": chunk.get("duration", 0),
                            "word_count": len(chunk.get("text", "").split()),
                            "char_count": len(chunk.get("text", "")),
                            "speaker": chunk.get("speaker", "unknown"),
                        }
                    )

            execution_time = time.time() - start_time

            # Update statistics
            self.statistics["chunks_generated"] = len(all_chunks)
            self.statistics["execution_time_seconds"] += execution_time
            self.statistics["boundary_checks"] += 1

            # Log evidence
            self.evidence_store.log_evidence(
                evidence_type="transcript_chunking_completed",
                content={
                    "total_chunks": len(all_chunks),
                    "transcripts_processed": len(transcripts),
                    "average_chunks_per_transcript": len(all_chunks)
                    / max(len(transcripts), 1),
                    "execution_time": execution_time,
                },
                source="media_processor.chunk_transcripts",
                metadata={
                    "strategy": strategy,
                    "seconds_per_chunk": seconds_per_chunk,
                    "speaker_aware": speaker_aware,
                },
            )

            print(f"\n✅ Transcript chunking completed:")
            print(f"   Total chunks generated: {len(all_chunks)}")
            print(
                f"   Average chunks per transcript: {len(all_chunks) / max(len(transcripts), 1):.1f}"
            )
            print(f"   Execution time: {execution_time:.2f}s")

            result = {
                "chunks": all_chunks,
                "chunk_metadata": chunk_metadata,
                "total_chunks": len(all_chunks),
                "transcripts_processed": len(transcripts),
                "execution_time": execution_time,
                "chunking_strategy": strategy,
            }

            # Complete workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="transcript_chunking",
                    status="completed",
                    summary={
                        "chunks_generated": len(all_chunks),
                        "execution_time": execution_time,
                        "chunking_results": result,
                    },
                )

            return result

        except Exception as e:
            print(f"❌ Transcript chunking failed: {e}")

            # Fail workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="transcript_chunking",
                    status="failed",
                    summary={"error": str(e)},
                )

            return {"error": f"Transcript chunking failed: {e}"}

    @glass_box_boundary()
    def _chunk_single_transcript(
        self,
        transcript: Dict[str, Any],
        strategy: str = "timestamp_based",
        seconds_per_chunk: int = 300,
        speaker_aware: bool = True,
        preserve_speaker_labels: bool = True,
        overlap_seconds: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Chunk a single transcript.

        Args:
            transcript: Transcription result
            strategy: Chunking strategy
            seconds_per_chunk: Target chunk size in seconds
            speaker_aware: Whether to preserve speaker boundaries
            preserve_speaker_labels: Whether to keep speaker labels
            overlap_seconds: Overlap between chunks

        Returns:
            List of chunks
        """
        chunks = []
        text = transcript.get("text", "")
        segments = transcript.get("segments", [])
        duration = transcript.get("duration_seconds", 0)

        if strategy == "timestamp_based" and segments:
            # Chunk based on timestamps and segments
            current_chunk = {
                "text": "",
                "timestamp_start": segments[0]["start"] if segments else 0,
                "timestamp_end": 0,
                "segments": [],
                "speaker": "unknown",
            }

            for segment in segments:
                segment_duration = segment["end"] - segment["start"]

                # Check if we need to start a new chunk
                if (
                    current_chunk["timestamp_end"]
                    - current_chunk["timestamp_start"]
                    + segment_duration
                    > seconds_per_chunk
                ):
                    # Finalize current chunk
                    if current_chunk["text"]:
                        current_chunk["duration"] = (
                            current_chunk["timestamp_end"]
                            - current_chunk["timestamp_start"]
                        )
                        chunks.append(current_chunk)

                    # Start new chunk with overlap
                    overlap_start = max(
                        current_chunk["timestamp_start"],
                        current_chunk["timestamp_end"] - overlap_seconds,
                    )
                    current_chunk = {
                        "text": "",
                        "timestamp_start": overlap_start,
                        "timestamp_end": 0,
                        "segments": [],
                        "speaker": segment.get("speaker", "unknown")
                        if speaker_aware
                        else "unknown",
                    }

                # Add segment to current chunk
                current_chunk["text"] += segment["text"] + " "
                current_chunk["segments"].append(segment)
                current_chunk["timestamp_end"] = segment["end"]

            # Add the last chunk
            if current_chunk["text"]:
                current_chunk["duration"] = (
                    current_chunk["timestamp_end"] - current_chunk["timestamp_start"]
                )
                chunks.append(current_chunk)

        elif strategy == "segment_based" and segments:
            # Chunk based on segment count
            segments_per_chunk = max(
                1, seconds_per_chunk // 30
            )  # Assume 30-second segments
            for i in range(0, len(segments), segments_per_chunk):
                chunk_segments = segments[i : i + segments_per_chunk]
                if chunk_segments:
                    chunk_text = " ".join(seg["text"] for seg in chunk_segments)
                    chunk = {
                        "text": chunk_text,
                        "timestamp_start": chunk_segments[0]["start"],
                        "timestamp_end": chunk_segments[-1]["end"],
                        "duration": chunk_segments[-1]["end"]
                        - chunk_segments[0]["start"],
                        "segments": chunk_segments,
                        "speaker": "mixed"
                        if len(
                            set(seg.get("speaker", "unknown") for seg in chunk_segments)
                        )
                        > 1
                        else chunk_segments[0].get("speaker", "unknown"),
                    }
                    chunks.append(chunk)

        else:
            # Fixed-size text chunking (fallback)
            words = text.split()
            words_per_chunk = seconds_per_chunk * 2  # Assume 2 words per second

            for i in range(0, len(words), words_per_chunk):
                chunk_words = words[i : i + words_per_chunk]
                chunk_text = " ".join(chunk_words)

                # Calculate approximate timestamps
                chunk_duration = len(chunk_words) / 2  # 2 words per second
                timestamp_start = (i / len(words)) * duration if duration > 0 else 0
                timestamp_end = timestamp_start + chunk_duration

                chunk = {
                    "text": chunk_text,
                    "timestamp_start": timestamp_start,
                    "timestamp_end": timestamp_end,
                    "duration": chunk_duration,
                    "segments": [],
                    "speaker": "unknown",
                }
                chunks.append(chunk)

        return chunks

    @glass_box_boundary()
    def process_media_pipeline(
        self,
        include_patterns: Optional[List[str]] = None,
        transcription_config: Optional[Dict[str, Any]] = None,
        chunking_config: Optional[Dict[str, Any]] = None,
        output_dir: Union[str, Path] = "./media_processing_output",
    ) -> Dict[str, Any]:
        """
        Execute complete media processing pipeline.

        Args:
            include_patterns: Media file patterns to include
            transcription_config: Transcription configuration
            chunking_config: Chunking configuration
            output_dir: Directory to save outputs

        Returns:
            Complete pipeline results
        """
        start_time = time.time()

        print("=" * 70)
        print("MEDIA PROCESSING PIPELINE: Complete Audio/Video Processing")
        print("=" * 70)

        # Use default configurations if not provided
        if transcription_config is None:
            transcription_config = self.transcription_config

        if chunking_config is None:
            chunking_config = self.chunking_config

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Start complete workflow
        workflow_result = {"status": "not_started"}
        if self.orchestration:
            workflow_result = self.orchestration.start_workflow(
                workflow_name="complete_media_pipeline",
                components=["media_processor"],
                parameters={
                    "include_patterns": include_patterns,
                    "output_dir": str(output_dir),
                },
            )

        try:
            # Step 1: Scan for media files
            print("\n📁 Step 1: Scanning for media files...")
            scan_result = self.scan_media_files(
                include_patterns=include_patterns,
                extract_metadata=True,
            )

            if "error" in scan_result:
                return {"error": f"Media scan failed: {scan_result['error']}"}

            media_files = scan_result.get("media_files", [])
            if not media_files:
                print("⚠️ No media files found. Pipeline complete.")

                # Complete workflow
                if self.orchestration and workflow_result.get("status") == "started":
                    self.orchestration.complete_workflow(
                        workflow_name="complete_media_pipeline",
                        status="completed",
                        summary={
                            "media_files_found": 0,
                            "execution_time": time.time() - start_time,
                            "message": "No media files to process",
                        },
                    )

                return {
                    "media_files_found": 0,
                    "transcripts_generated": 0,
                    "chunks_generated": 0,
                    "execution_time": time.time() - start_time,
                    "message": "No media files to process",
                }

            # Step 2: Transcribe media files
            print(f"\n📝 Step 2: Transcribing {len(media_files)} media files...")
            transcription_result = self.transcribe_media(
                media_files=media_files,
                engine=transcription_config.get("engine", "whisper"),
                model=transcription_config.get("model", "base"),
                language=transcription_config.get("language", "en"),
                task=transcription_config.get("task", "transcribe"),
                timestamp_resolution=transcription_config.get(
                    "timestamp_resolution", "word"
                ),
            )

            if "error" in transcription_result:
                return {
                    "error": f"Transcription failed: {transcription_result['error']}"
                }

            transcripts = transcription_result.get("transcripts", [])

            # Step 3: Chunk transcripts
            print(f"\n✂️ Step 3: Chunking {len(transcripts)} transcripts...")
            chunking_result = self.chunk_transcripts(
                transcripts=transcripts,
                strategy=chunking_config.get("strategy", "timestamp_based"),
                seconds_per_chunk=chunking_config.get("seconds_per_chunk", 300),
                speaker_aware=chunking_config.get("speaker_aware", True),
                preserve_speaker_labels=chunking_config.get(
                    "preserve_speaker_labels", True
                ),
                overlap_seconds=chunking_config.get("overlap_seconds", 30),
            )

            if "error" in chunking_result:
                return {"error": f"Chunking failed: {chunking_result['error']}"}

            # Step 4: Save outputs
            print(f"\n💾 Step 4: Saving outputs to {output_dir}...")
            save_result = self._save_pipeline_outputs(
                scan_result=scan_result,
                transcription_result=transcription_result,
                chunking_result=chunking_result,
                output_dir=output_path,
            )

            execution_time = time.time() - start_time

            # Update statistics
            self.statistics["execution_time_seconds"] += execution_time
            self.statistics["boundary_checks"] += 1

            # Log evidence
            self.evidence_store.log_evidence(
                evidence_type="media_pipeline_completed",
                content={
                    "media_files_processed": len(media_files),
                    "transcripts_generated": len(transcripts),
                    "chunks_generated": chunking_result.get("total_chunks", 0),
                    "total_execution_time": execution_time,
                    "output_directory": str(output_dir),
                },
                source="media_processor.process_media_pipeline",
                metadata={
                    "transcription_config": transcription_config,
                    "chunking_config": chunking_config,
                },
            )

            print(f"\n✅ Media processing pipeline completed:")
            print(f"   Media files processed: {len(media_files)}")
            print(f"   Transcripts generated: {len(transcripts)}")
            print(f"   Chunks generated: {chunking_result.get('total_chunks', 0)}")
            print(f"   Total execution time: {execution_time:.2f}s")
            print(f"   Output directory: {output_dir}")

            result = {
                "scan_result": scan_result,
                "transcription_result": transcription_result,
                "chunking_result": chunking_result,
                "save_result": save_result,
                "total_media_files": len(media_files),
                "total_transcripts": len(transcripts),
                "total_chunks": chunking_result.get("total_chunks", 0),
                "execution_time": execution_time,
                "output_directory": str(output_dir),
                "statistics": self.statistics,
            }

            # Complete workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="complete_media_pipeline",
                    status="completed",
                    summary={
                        "media_files_processed": len(media_files),
                        "transcripts_generated": len(transcripts),
                        "chunks_generated": chunking_result.get("total_chunks", 0),
                        "execution_time": execution_time,
                        "pipeline_results": result,
                    },
                )

            return result

        except Exception as e:
            print(f"❌ Media processing pipeline failed: {e}")

            # Fail workflow if started
            if self.orchestration and workflow_result.get("status") == "started":
                self.orchestration.complete_workflow(
                    workflow_name="complete_media_pipeline",
                    status="failed",
                    summary={"error": str(e)},
                )

            return {"error": f"Media processing pipeline failed: {e}"}

    @glass_box_boundary()
    def _save_pipeline_outputs(
        self,
        scan_result: Dict[str, Any],
        transcription_result: Dict[str, Any],
        chunking_result: Dict[str, Any],
        output_dir: Path,
    ) -> Dict[str, Any]:
        """
        Save media processing pipeline outputs to files.

        Args:
            scan_result: Media scan results
            transcription_result: Transcription results
            chunking_result: Chunking results
            output_dir: Directory to save outputs

        Returns:
            Save operation results
        """
        try:
            # Create subdirectories
            scan_dir = output_dir / "scan_results"
            transcription_dir = output_dir / "transcriptions"
            chunking_dir = output_dir / "chunks"
            metadata_dir = output_dir / "metadata"

            for directory in [scan_dir, transcription_dir, chunking_dir, metadata_dir]:
                directory.mkdir(parents=True, exist_ok=True)

            # Save scan results
            scan_file = scan_dir / "media_scan.json"
            with open(scan_file, "w", encoding="utf-8") as f:
                json.dump(scan_result, f, indent=2, default=str)

            # Save transcription results
            transcription_file = transcription_dir / "transcriptions.json"
            with open(transcription_file, "w", encoding="utf-8") as f:
                json.dump(transcription_result, f, indent=2, default=str)

            # Save chunking results
            chunking_file = chunking_dir / "chunks.json"
            with open(chunking_file, "w", encoding="utf-8") as f:
                json.dump(chunking_result, f, indent=2, default=str)

            # Save individual transcript files
            transcripts = transcription_result.get("transcripts", [])
            for i, transcript in enumerate(transcripts):
                transcript_file = transcription_dir / f"transcript_{i:04d}.json"
                with open(transcript_file, "w", encoding="utf-8") as f:
                    json.dump(transcript, f, indent=2, default=str)

                # Also save as text file
                text_file = transcription_dir / f"transcript_{i:04d}.txt"
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(transcript.get("text", ""))

            # Save individual chunk files
            chunks = chunking_result.get("chunks", [])
            chunk_metadata = chunking_result.get("chunk_metadata", [])
            for i, (chunk, metadata) in enumerate(zip(chunks, chunk_metadata)):
                chunk_file = (
                    chunking_dir
                    / f"chunk_{metadata.get('chunk_id', f'chunk_{i:04d}')}.json"
                )
                with open(chunk_file, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "metadata": metadata,
                            "content": chunk,
                        },
                        f,
                        indent=2,
                        default=str,
                    )

                # Also save as text file
                text_file = (
                    chunking_dir
                    / f"chunk_{metadata.get('chunk_id', f'chunk_{i:04d}')}.txt"
                )
                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(chunk.get("text", ""))

            # Save metadata summary
            metadata_summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "pipeline_version": "1.0.0",
                "schema_id": "GB-MEDIA-PROCESSOR-1.0",
                "statistics": self.statistics,
                "file_counts": {
                    "media_files_scanned": len(scan_result.get("media_files", [])),
                    "transcripts_generated": len(transcripts),
                    "chunks_generated": len(chunks),
                },
                "output_structure": {
                    "scan_results": str(scan_dir.relative_to(output_dir)),
                    "transcriptions": str(transcription_dir.relative_to(output_dir)),
                    "chunks": str(chunking_dir.relative_to(output_dir)),
                    "metadata": str(metadata_dir.relative_to(output_dir)),
                },
            }

            metadata_file = metadata_dir / "pipeline_metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata_summary, f, indent=2, default=str)

            # Save statistics
            stats_file = metadata_dir / "statistics.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.statistics, f, indent=2, default=str)

            # Log evidence
            self.evidence_store.log_evidence(
                evidence_type="media_outputs_saved",
                content={
                    "scan_results_saved": scan_file.exists(),
                    "transcriptions_saved": transcription_file.exists(),
                    "chunks_saved": chunking_file.exists(),
                    "individual_transcripts": len(transcripts),
                    "individual_chunks": len(chunks),
                    "output_directory": str(output_dir),
                },
                source="media_processor._save_pipeline_outputs",
                metadata={"output_dir": str(output_dir)},
            )

            print(f"✅ Pipeline outputs saved to {output_dir}")
            print(f"   Scan results: {scan_file}")
            print(
                f"   Transcriptions: {transcription_file} ({len(transcripts)} individual files)"
            )
            print(f"   Chunks: {chunking_file} ({len(chunks)} individual files)")
            print(f"   Metadata: {metadata_file}")

            return {
                "saved": True,
                "output_directory": str(output_dir),
                "files_saved": {
                    "scan_results": str(scan_file),
                    "transcriptions": str(transcription_file),
                    "chunks": str(chunking_file),
                    "metadata": str(metadata_file),
                    "individual_transcripts": len(transcripts),
                    "individual_chunks": len(chunks),
                },
                "statistics": self.statistics,
            }

        except Exception as e:
            print(f"❌ Failed to save pipeline outputs: {e}")

            # Log error evidence
            self.evidence_store.log_evidence(
                evidence_type="media_outputs_save_failed",
                content={
                    "error": str(e),
                    "output_directory": str(output_dir),
                },
                source="media_processor._save_pipeline_outputs",
                metadata={"output_dir": str(output_dir)},
            )

            return {
                "saved": False,
                "error": str(e),
                "output_directory": str(output_dir),
            }

    @glass_box_boundary()
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the Media Processor.

        Returns:
            Status information
        """
        return {
            "statistics": self.statistics,
            "workspace_root": str(self.workspace_root),
            "supported_formats": self.supported_formats,
            "transcription_available": WHISPER_AVAILABLE,
            "video_processing_available": MOVIEPY_AVAILABLE,
            "audio_processing_available": PYDUB_AVAILABLE,
            "orchestration_initialized": self.orchestration is not None,
            "session_id": self.orchestration.session_id if self.orchestration else None,
        }


def main():
    """Main entry point for the Media Processor CLI."""
    parser = argparse.ArgumentParser(
        description="Media Processor CLI - Audio/Video Transcription and Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan --workspace ./media_files
  %(prog)s transcribe --input ./media_scan.json
  %(prog)s chunk --input ./transcriptions.json
  %(prog)s pipeline --workspace . --output ./media_output
  %(prog)s status
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for media files")
    scan_parser.add_argument(
        "--workspace", default=".", help="Workspace directory to scan"
    )
    scan_parser.add_argument(
        "--include-patterns",
        nargs="+",
        default=["*.mp3", "*.wav", "*.mp4", "*.mov"],
        help="File patterns to include",
    )
    scan_parser.add_argument(
        "--max-duration-hours",
        type=float,
        default=10.0,
        help="Maximum media duration to process (hours)",
    )
    scan_parser.add_argument(
        "--extract-metadata",
        action="store_true",
        default=True,
        help="Extract metadata from media files",
    )

    # Transcribe command
    transcribe_parser = subparsers.add_parser(
        "transcribe", help="Transcribe media files"
    )
    transcribe_parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file from scan command",
    )
    transcribe_parser.add_argument(
        "--engine",
        default="whisper",
        choices=["whisper", "simulated"],
        help="Transcription engine to use",
    )
    transcribe_parser.add_argument(
        "--model",
        default="base",
        help="Model to use for transcription",
    )
    transcribe_parser.add_argument(
        "--language",
        default="en",
        help="Language for transcription",
    )
    transcribe_parser.add_argument(
        "--task",
        default="transcribe",
        choices=["transcribe", "translate"],
        help="Transcription task",
    )
    transcribe_parser.add_argument(
        "--output",
        default="./transcriptions.json",
        help="Output file for transcription results",
    )

    # Chunk command
    chunk_parser = subparsers.add_parser("chunk", help="Chunk transcriptions")
    chunk_parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file from transcribe command",
    )
    chunk_parser.add_argument(
        "--strategy",
        default="timestamp_based",
        choices=["timestamp_based", "segment_based", "fixed_size"],
        help="Chunking strategy",
    )
    chunk_parser.add_argument(
        "--seconds-per-chunk",
        type=int,
        default=300,
        help="Target chunk size in seconds",
    )
    chunk_parser.add_argument(
        "--speaker-aware",
        action="store_true",
        default=True,
        help="Preserve speaker boundaries",
    )
    chunk_parser.add_argument(
        "--output",
        default="./chunks.json",
        help="Output file for chunking results",
    )

    # Pipeline command
    pipeline_parser = subparsers.add_parser(
        "pipeline", help="Execute complete media processing pipeline"
    )
    pipeline_parser.add_argument(
        "--workspace", default=".", help="Workspace directory to process"
    )
    pipeline_parser.add_argument(
        "--include-patterns",
        nargs="+",
        default=["*.mp3", "*.wav", "*.mp4", "*.mov"],
        help="File patterns to include",
    )
    pipeline_parser.add_argument(
        "--output-dir",
        default="./media_processing_output",
        help="Directory to save pipeline outputs",
    )
    pipeline_parser.add_argument(
        "--transcription-engine",
        default="whisper",
        help="Transcription engine to use",
    )
    pipeline_parser.add_argument(
        "--transcription-model",
        default="base",
        help="Model to use for transcription",
    )
    pipeline_parser.add_argument(
        "--chunking-strategy",
        default="timestamp_based",
        help="Chunking strategy to use",
    )

    # Status command
    subparsers.add_parser("status", help="Show Media Processor status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        # Initialize Media Processor
        if args.command in ["scan", "pipeline"]:
            workspace = args.workspace if hasattr(args, "workspace") else "."
            processor = MediaProcessor(workspace_root=workspace)
        else:
            processor = MediaProcessor()

        # Initialize orchestration
        processor.initialize_orchestration()

        if args.command == "scan":
            result = processor.scan_media_files(
                include_patterns=args.include_patterns,
                max_duration_hours=args.max_duration_hours,
                extract_metadata=args.extract_metadata,
            )

            if "error" in result:
                print(f"❌ Scan failed: {result['error']}")
                return 1

            # Save scan results
            output_file = (
                Path(args.workspace if hasattr(args, "workspace") else ".")
                / "media_scan.json"
            )
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)

            print(f"✅ Scan results saved to {output_file}")
            print(f"   Media files found: {result.get('total_files', 0)}")
            print(f"   Audio files: {len(result.get('audio_files', []))}")
            print(f"   Video files: {len(result.get('video_files', []))}")

        elif args.command == "transcribe":
            # Load scan results
            with open(args.input, "r", encoding="utf-8") as f:
                scan_data = json.load(f)

            media_files = scan_data.get("media_files", [])
            if not media_files:
                print("❌ No media files found in input")
                return 1

            result = processor.transcribe_media(
                media_files=media_files,
                engine=args.engine,
                model=args.model,
                language=args.language,
                task=args.task,
            )

            if "error" in result:
                print(f"❌ Transcription failed: {result['error']}")
                return 1

            # Save transcription results
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)

            print(f"✅ Transcription results saved to {args.output}")
            print(f"   Transcripts generated: {result.get('successful_count', 0)}")
            print(f"   Failed transcriptions: {result.get('failed_count', 0)}")

        elif args.command == "chunk":
            # Load transcription results
            with open(args.input, "r", encoding="utf-8") as f:
                transcription_data = json.load(f)

            transcripts = transcription_data.get("transcripts", [])
            if not transcripts:
                print("❌ No transcripts found in input")
                return 1

            result = processor.chunk_transcripts(
                transcripts=transcripts,
                strategy=args.strategy,
                seconds_per_chunk=args.seconds_per_chunk,
                speaker_aware=args.speaker_aware,
                preserve_speaker_labels=True,
                overlap_seconds=30,
            )

            if "error" in result:
                print(f"❌ Chunking failed: {result['error']}")
                return 1

            # Save chunking results
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, default=str)

            print(f"✅ Chunking results saved to {args.output}")
            print(f"   Chunks generated: {result.get('total_chunks', 0)}")
            print(f"   Transcripts processed: {result.get('transcripts_processed', 0)}")

        elif args.command == "pipeline":
            result = processor.process_media_pipeline(
                include_patterns=args.include_patterns,
                transcription_config={
                    "engine": args.transcription_engine,
                    "model": args.transcription_model,
                },
                chunking_config={
                    "strategy": args.chunking_strategy,
                },
                output_dir=args.output_dir,
            )

            if "error" in result:
                print(f"❌ Pipeline failed: {result['error']}")
                return 1

            print(f"✅ Media processing pipeline completed successfully")
            print(f"   Output directory: {args.output_dir}")
            print(f"   Total execution time: {result.get('execution_time', 0):.2f}s")

        elif args.command == "status":
            status = processor.get_status()
            print("\n📊 Media Processor Status:")
            print(f"   Workspace: {status['workspace_root']}")
            print(
                f"   Media files processed: {status['statistics']['media_files_processed']}"
            )
            print(
                f"   Transcripts generated: {status['statistics'].get('transcription_seconds', 0)}s of processing"
            )
            print(f"   Chunks generated: {status['statistics']['chunks_generated']}")
            print(f"   Whisper available: {status['transcription_available']}")
            print(f"   MoviePy available: {status['video_processing_available']}")
            print(f"   Pydub available: {status['audio_processing_available']}")
            print(
                f"   Orchestration: {'Initialized' if status['orchestration_initialized'] else 'Not initialized'}"
            )
            if status["orchestration_initialized"]:
                print(f"   Session ID: {status['session_id']}")

        else:
            print(f"❌ Unknown command: {args.command}")
            return 1

        # Save final state
        if processor.orchestration:
            processor.orchestration.save_state()

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
