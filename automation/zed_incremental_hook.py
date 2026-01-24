#!/usr/bin/env python3
"""
ZED IDE INCREMENTAL PROCESSING HOOK
Version: 1.11
Schema ID: GB-ORIGIN-1.11
Generated: 2026-01-23
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Integrate incremental file processing with Zed IDE
Principle: "Process everything, just not all at once - with IDE awareness"

Glass Box Boundary Compliance:
- @glass_box_boundary decorator on all functions
- Exit code 2 on boundary violations
- Trace generation for IDE interactions
- State persistence across IDE sessions
- Token-aware chunking with IDE context

Forgiveness System Integration:
- Built from FORK-IDE-TOKEN-GRENADE-001
- Energy redirected from fight to build
- No recursive engagement with IDE crashes
- Success measured by IDE stability, not arguments won

Zed IDE Integration:
- File save hooks for large files
- Background incremental processing
- Progress reporting in IDE
- Resume capability across sessions
- Glass-Box Boundary compliance monitoring
"""

import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Import the incremental processor
sys.path.insert(0, str(Path(__file__).parent))
try:
    from incremental_file_processor import IncrementalProcessor, glass_box_boundary
except ImportError:
    # Fallback - define minimal decorator if import fails
    def glass_box_boundary(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    class IncrementalProcessor:
        def __init__(self):
            pass

# ============================================================================
# CONSTANTS
# ============================================================================

# Zed IDE integration paths
ZED_STATE_DIR = Path.home() / ".zed" / "state" / "orthogonal_engineering"
ZED_HOOKS_DIR = ZED_STATE_DIR / "hooks"
ZED_PROGRESS_DIR = ZED_STATE_DIR / "progress"
ZED_LOGS_DIR = ZED_STATE_DIR / "logs"

# File size thresholds for incremental processing
INCREMENTAL_THRESHOLD_BYTES = 100000  # 100KB
INCREMENTAL_THRESHOLD_TOKENS = 25000  # 25K tokens

# Processing modes
PROCESSING_MODES = {
    "immediate": "Process immediately in foreground",
    "background": "Process in background thread",
    "deferred": "Schedule for later processing",
    "manual": "Require manual initiation",
}

# Zed event types
ZED_EVENT_TYPES = {
    "file_saved": "File saved in editor",
    "file_opened": "File opened in editor",
    "project_loaded": "Project loaded in Zed",
    "ide_started": "Zed IDE started",
    "ide_shutdown": "Zed IDE shutting down",
    "processing_complete": "Incremental processing completed",
    "processing_failed": "Incremental processing failed",
    "boundary_violation": "Glass-Box Boundary violation detected",
}

# ============================================================================
# ZED INTEGRATION CLASSES
# ============================================================================


class ZedStateManager:
    """Manage Zed IDE state for incremental processing"""

    def __init__(self):
        self.state_dir = ZED_STATE_DIR
        self.hooks_dir = ZED_HOOKS_DIR
        self.progress_dir = ZED_PROGRESS_DIR
        self.logs_dir = ZED_LOGS_DIR

        # Ensure directories exist
        for directory in [
            self.state_dir,
            self.hooks_dir,
            self.progress_dir,
            self.logs_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Load Zed state
        self.state = self._load_state()

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def _load_state(self) -> Dict[str, Any]:
        """Load Zed IDE state from disk"""
        state_file = self.state_dir / "zed_state.json"

        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self._log_event("state_load_error", f"Could not load state file: {e}")

        # Default state
        return {
            "version": "1.11",
            "schema_id": "GB-ORIGIN-1.11",
            "zed_integration_active": True,
            "incremental_processing_enabled": True,
            "last_zed_session": None,
            "current_zed_session": str(uuid.uuid4()),
            "session_started": datetime.now().isoformat(),
            "files_processed_in_session": 0,
            "boundary_violations_in_session": 0,
            "processing_mode": "background",
            "file_size_threshold_bytes": INCREMENTAL_THRESHOLD_BYTES,
            "token_threshold": INCREMENTAL_THRESHOLD_TOKENS,
            "active_background_jobs": [],
            "completed_background_jobs": [],
            "user_preferences": {
                "notify_on_completion": True,
                "notify_on_failure": True,
                "auto_process_large_files": True,
                "resume_across_sessions": True,
                "generate_progress_reports": True,
            },
        }

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def save_state(self) -> None:
        """Save Zed IDE state to disk"""
        state_file = self.state_dir / "zed_state.json"

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self._log_event("state_save_error", f"Failed to save state: {e}")

    @glass_box_boundary(
        input_validator=lambda event_type, message: None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def _log_event(self, event_type: str, message: str) -> None:
        """Log an event to Zed logs"""
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y%m%d')}.log"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "session_id": self.state.get("current_zed_session", "unknown"),
        }

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except IOError:
            # Non-critical if we can't log
            pass

    @glass_box_boundary(
        input_validator=lambda file_path, job_id, status, message=None: None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def update_progress(
        self, file_path: Path, job_id: str, status: str, message: Optional[str] = None
    ) -> None:
        """Update progress for a processing job"""
        progress_file = self.progress_dir / f"{job_id}.json"

        progress_data = {
            "job_id": job_id,
            "file_path": str(file_path),
            "status": status,
            "message": message,
            "last_updated": datetime.now().isoformat(),
            "session_id": self.state.get("current_zed_session", "unknown"),
        }

        try:
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self._log_event("progress_update_error", f"Failed to update progress: {e}")

    @glass_box_boundary(
        input_validator=lambda file_path: None,
        output_validator=lambda result: isinstance(result, bool),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def should_process_incrementally(self, file_path: Path) -> bool:
        """Determine if a file should be processed incrementally"""
        if not self.state["incremental_processing_enabled"]:
            return False

        if not self.state["user_preferences"]["auto_process_large_files"]:
            return False

        try:
            file_size = file_path.stat().st_size

            # Check file size threshold
            if file_size > self.state["file_size_threshold_bytes"]:
                return True

            # For text files, also estimate tokens
            if file_path.suffix.lower() in [".txt", ".md", ".py", ".json", ".html"]:
                # Rough token estimate: 1 token ≈ 4 characters
                estimated_tokens = file_size // 4
                if estimated_tokens > self.state["token_threshold"]:
                    return True

            return False

        except OSError:
            # If we can't stat the file, don't process it
            return False

    @glass_box_boundary(
        input_validator=lambda file_path, job_id: None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def register_background_job(self, file_path: Path, job_id: str) -> None:
        """Register a background processing job"""
        job_info = {
            "job_id": job_id,
            "file_path": str(file_path),
            "started": datetime.now().isoformat(),
            "status": "running",
        }

        self.state["active_background_jobs"].append(job_info)
        self.save_state()
        self._log_event(
            "background_job_started", f"Started background job {job_id} for {file_path}"
        )

    @glass_box_boundary(
        input_validator=lambda job_id, status, result=None: None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def complete_background_job(
        self, job_id: str, status: str, result: Optional[Dict] = None
    ) -> None:
        """Complete a background processing job"""
        # Find and remove from active jobs
        for i, job in enumerate(self.state["active_background_jobs"]):
            if job["job_id"] == job_id:
                completed_job = self.state["active_background_jobs"].pop(i)
                completed_job["completed"] = datetime.now().isoformat()
                completed_job["status"] = status
                if result:
                    completed_job["result"] = result

                self.state["completed_background_jobs"].append(completed_job)
                self.state["files_processed_in_session"] += 1
                break

        self.save_state()
        self._log_event(
            "background_job_completed",
            f"Completed background job {job_id} with status {status}",
        )


class ZedIncrementalHook:
    """Main Zed IDE integration for incremental processing"""

    def __init__(self):
        self.zed_state = ZedStateManager()
        self.processor = IncrementalProcessor()
        self.background_threads = {}

    @glass_box_boundary(
        input_validator=lambda file_path: None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def handle_file_saved(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Handle file save event from Zed IDE"""
        file_path = Path(file_path)

        if not file_path.exists():
            return {
                "status": "error",
                "message": f"File not found: {file_path}",
                "action": "none",
            }

        # Check if incremental processing is needed
        if not self.zed_state.should_process_incrementally(file_path):
            return {
                "status": "skipped",
                "message": "File does not require incremental processing",
                "action": "none",
            }

        # Analyze the file
        analysis = self.processor.analyze_file_for_processing(file_path)

        # Determine processing mode
        processing_mode = self.zed_state.state["processing_mode"]

        if processing_mode == "immediate":
            # Process immediately in foreground
            return self._process_immediately(file_path, analysis)

        elif processing_mode == "background":
            # Process in background thread
            return self._process_in_background(file_path, analysis)

        elif processing_mode == "deferred":
            # Schedule for later
            return self._schedule_for_later(file_path, analysis)

        else:  # manual
            # Just notify user
            return {
                "status": "manual_required",
                "message": f"Large file detected ({analysis['file_size_bytes']:,} bytes, ~{analysis['estimated_tokens']:,} tokens). Requires {analysis['chunks_needed']} chunks.",
                "action": "notify_user",
                "analysis": analysis,
            }

    @glass_box_boundary(
        input_validator=lambda file_path, analysis: None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def _process_immediately(
        self, file_path: Path, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process file immediately in foreground"""
        try:
            self.zed_state._log_event(
                "processing_started", f"Starting immediate processing of {file_path}"
            )

            # Update progress
            job_id = str(uuid.uuid4())
            self.zed_state.update_progress(
                file_path, job_id, "starting", "Beginning immediate processing"
            )

            # Process the file
            process_id = self.processor.process_file_incrementally(file_path)

            # Update progress
            self.zed_state.update_progress(
                file_path,
                job_id,
                "completed",
                f"Processing completed with ID: {process_id}",
            )

            return {
                "status": "completed",
                "message": f"File processed incrementally in {analysis['chunks_needed']} chunks",
                "action": "processed",
                "process_id": process_id,
                "chunks": analysis["chunks_needed"],
                "analysis": analysis,
            }

        except Exception as e:
            error_msg = f"Failed to process {file_path}: {str(e)}"
            self.zed_state._log_event("processing_failed", error_msg)
            self.zed_state.state["boundary_violations_in_session"] += 1
            self.zed_state.save_state()

            return {
                "status": "error",
                "message": error_msg,
                "action": "failed",
                "analysis": analysis,
            }

    @glass_box_boundary(
        input_validator=lambda file_path, analysis: None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def _process_in_background(
        self, file_path: Path, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process file in background thread"""
        job_id = str(uuid.uuid4())

        # Register the background job
        self.zed_state.register_background_job(file_path, job_id)

        # Start background thread
        thread = threading.Thread(
            target=self._background_processing_task,
            args=(file_path, job_id, analysis),
            daemon=True,
        )
        thread.start()

        # Store thread reference
        self.background_threads[job_id] = thread

        return {
            "status": "background_started",
            "message": f"Background processing started for {file_path}",
            "action": "background_processing",
            "job_id": job_id,
            "chunks": analysis["chunks_needed"],
            "analysis": analysis,
        }

    def _background_processing_task(
        self, file_path: Path, job_id: str, analysis: Dict[str, Any]
    ) -> None:
        """Background task for processing files"""
        try:
            self.zed_state.update_progress(
                file_path,
                job_id,
                "running",
                f"Processing chunk 1/{analysis['chunks_needed']}",
            )

            # Process the file
            process_id = self.processor.process_file_incrementally(file_path)

            # Update progress and complete job
            self.zed_state.update_progress(
                file_path,
                job_id,
                "completed",
                f"Processing completed with ID: {process_id}",
            )
            self.zed_state.complete_background_job(
                job_id,
                "success",
                {"process_id": process_id, "chunks": analysis["chunks_needed"]},
            )

            # Remove thread reference
            if job_id in self.background_threads:
                del self.background_threads[job_id]

        except Exception as e:
            error_msg = f"Background processing failed: {str(e)}"
            self.zed_state.update_progress(file_path, job_id, "failed", error_msg)
            self.zed_state.complete_background_job(
                job_id, "failed", {"error": error_msg}
            )

            # Remove thread reference
            if job_id in self.background_threads:
                del self.background_threads[job_id]

    @glass_box_boundary(
        input_validator=lambda file_path, analysis: None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def _schedule_for_later(
        self, file_path: Path, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule file for later processing"""
        # Create a hook file that will be processed later
        hook_id = str(uuid.uuid4())
        hook_file = self.zed_state.hooks_dir / f"scheduled_{hook_id}.json"

        hook_data = {
            "hook_id": hook_id,
            "file_path": str(file_path),
            "scheduled": datetime.now().isoformat(),
            "analysis": analysis,
            "status": "scheduled",
        }

        try:
            with open(hook_file, "w", encoding="utf-8") as f:
                json.dump(hook_data, f, indent=2, ensure_ascii=False)

            return {
                "status": "scheduled",
                "message": f"File scheduled for deferred processing",
                "action": "scheduled",
                "hook_id": hook_id,
                "hook_file": str(hook_file),
                "analysis": analysis,
            }

        except IOError as e:
            return {
                "status": "error",
                "message": f"Failed to schedule processing: {str(e)}",
                "action": "failed",
                "analysis": analysis,
            }

    @glass_box_boundary(
        input_validator=None,
        output_validator=lambda result: isinstance(result, dict),
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status for Zed IDE"""
        stats = self.processor.get_processing_stats()
        zed_state = self.zed_state.state

        return {
            "zed_integration": {
                "active": zed_state["zed_integration_active"],
                "incremental_processing_enabled": zed_state[
                    "incremental_processing_enabled"
                ],
                "current_session": zed_state["current_zed_session"],
                "files_processed_in_session": zed_state["files_processed_in_session"],
                "boundary_violations_in_session": zed_state[
                    "boundary_violations_in_session"
                ],
                "processing_mode": zed_state["processing_mode"],
                "active_background_jobs": len(zed_state["active_background_jobs"]),
                "completed_background_jobs": len(
                    zed_state["completed_background_jobs"]
                ),
            },
            "incremental_processing": stats,
            "background_threads": len(self.background_threads),
            "timestamp": datetime.now().isoformat(),
        }

    @glass_box_boundary(
        input_validator=None,
        output_validator=None,
        side_effect_check=True,
        orthogonal_separation=True,
    )
    def shutdown(self) -> None:
        """Clean shutdown of Zed integration"""
        self.zed_state._log_event("shutdown", "Zed incremental hook shutting down")

        # Update session end time
        self.zed_state.state["last_zed_session"] = {
            "session_id": self.zed_state.state["current_zed_session"],
            "started": self.zed_state.state["session_started"],
            "ended": datetime.now().isoformat(),
            "files_processed": self.zed_state.state["files_processed_in_session"],
            "boundary_violations": self.zed_state.state[
                "boundary_violations_in_session"
            ],
        }

        self.zed_state.save_state()

        # Wait for background threads (with timeout)
        for job_id, thread in list(self.background_threads.items()):
            thread.join(timeout=5.0)
            if thread.is_alive():
                self.zed_state._log_event(
                    "shutdown_warning",
                    f"Background thread {job_id} did not complete before shutdown",
                )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main():
    """Main entry point for Zed incremental hook"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Zed IDE Incremental Processing Hook - Prevent token limit grenade pin behavior",
        epilog="Exit codes: 0=Success, 1=System error, 2=Boundary violation, 3=Processing failed",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # File saved command (called by Zed on file save)
    file_saved_parser = subparsers.add_parser(
        "file-saved", help="Handle file saved event from Zed"
    )
    file_saved_parser.add_argument("file", help="File that was saved")
    file_saved_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Get processing status")
    status_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze file for Zed processing"
    )
    analyze_parser.add_argument("file", help="File to analyze")
    analyze_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Configure command
    config_parser = subparsers.add_parser("config", help="Configure Zed integration")
    config_parser.add_argument(
        "--enable", action="store_true", help="Enable incremental processing"
    )
    config_parser.add_argument(
        "--disable", action="store_true", help="Disable incremental processing"
    )
    config_parser.add_argument(
        "--mode",
        choices=["immediate", "background", "deferred", "manual"],
        help="Set processing mode",
    )
    config_parser.add_argument(
        "--threshold-bytes",
        type=int,
        help=f"Set file size threshold in bytes (default: {INCREMENTAL_THRESHOLD_BYTES})",
    )
    config_parser.add_argument(
        "--threshold-tokens",
        type=int,
        help=f"Set token threshold (default: {INCREMENTAL_THRESHOLD_TOKENS})",
    )
    config_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Process scheduled command
    process_scheduled_parser = subparsers.add_parser(
        "process-scheduled", help="Process scheduled files"
    )
    process_scheduled_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    # Shutdown command
    shutdown_parser = subparsers.add_parser(
        "shutdown", help="Clean shutdown of Zed integration"
    )
    shutdown_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    try:
        hook = ZedIncrementalHook()

        if args.command == "file-saved":
            if args.verbose:
                print(f"Handling file saved event for: {args.file}")

            result = hook.handle_file_saved(args.file)

            if args.verbose:
                print(f"Result: {result['status']}")
                print(f"Message: {result['message']}")
                if "analysis" in result:
                    print(f"Chunks needed: {result['analysis']['chunks_needed']}")

            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "status":
            status = hook.get_processing_status()

            if args.verbose:
                print("Zed Incremental Processing Status")
                print("=" * 80)
                print(f"Session: {status['zed_integration']['current_session']}")
                print(
                    f"Processing enabled: {status['zed_integration']['incremental_processing_enabled']}"
                )
                print(f"Mode: {status['zed_integration']['processing_mode']}")
                print(
                    f"Files processed this session: {status['zed_integration']['files_processed_in_session']}"
                )
                print(
                    f"Active background jobs: {status['zed_integration']['active_background_jobs']}"
                )
                print(f"Background threads: {status['background_threads']}")
                print(
                    f"Total chunks processed: {status['incremental_processing']['total_chunks_processed']:,}"
                )
                print(
                    f"Total bytes processed: {status['incremental_processing']['total_bytes_processed']:,}"
                )
                print(
                    f"Total tokens estimated: {status['incremental_processing']['total_tokens_estimated']:,}"
                )

            print(json.dumps(status, indent=2, ensure_ascii=False))

        elif args.command == "analyze":
            analysis = hook.processor.analyze_file_for_processing(args.file)

            if args.verbose:
                print(f"Analysis for: {args.file}")
                print(f"  Size: {analysis['file_size_bytes']:,} bytes")
                print(f"  Estimated tokens: {analysis['estimated_tokens']:,}")
                print(f"  Chunks needed: {analysis['chunks_needed']}")
                print(f"  Strategy: {analysis['chunking_strategy']}")
                print(f"  Exceeds single chunk: {analysis['exceeds_single_chunk']}")

                # Check if Zed would process it
                if hook.zed_state.should_process_incrementally(Path(args.file)):
                    print("  ✅ Zed would process this file incrementally")
                else:
                    print("  ⚠️  Zed would NOT process this file incrementally")

            print(json.dumps(analysis, indent=2, ensure_ascii=False))

        elif args.command == "config":
            if args.enable:
                hook.zed_state.state["incremental_processing_enabled"] = True
                print("✅ Incremental processing enabled")
            if args.disable:
                hook.zed_state.state["incremental_processing_enabled"] = False
                print("✅ Incremental processing disabled")
            if args.mode:
                hook.zed_state.state["processing_mode"] = args.mode
                print(f"✅ Processing mode set to: {args.mode}")
            if args.threshold_bytes:
                hook.zed_state.state["file_size_threshold_bytes"] = args.threshold_bytes
                print(f"✅ File size threshold set to: {args.threshold_bytes:,} bytes")
            if args.threshold_tokens:
                hook.zed_state.state["token_threshold"] = args.threshold_tokens
                print(f"✅ Token threshold set to: {args.threshold_tokens:,} tokens")

            hook.zed_state.save_state()

            if args.verbose:
                print("\nCurrent configuration:")
                print(json.dumps(hook.zed_state.state, indent=2, ensure_ascii=False))

        elif args.command == "process-scheduled":
            # Process any scheduled hooks
            scheduled_files = list(hook.zed_state.hooks_dir.glob("scheduled_*.json"))

            if not scheduled_files:
                print("No scheduled files to process")
                sys.exit(0)

            print(f"Processing {len(scheduled_files)} scheduled files")

            for hook_file in scheduled_files:
                try:
                    with open(hook_file, "r", encoding="utf-8") as f:
                        hook_data = json.load(f)

                    file_path = Path(hook_data["file_path"])

                    if args.verbose:
                        print(f"Processing scheduled file: {file_path}")

                    result = hook.handle_file_saved(file_path)

                    if result["status"] in [
                        "completed",
                        "background_started",
                        "scheduled",
                    ]:
                        # Mark as processed
                        hook_data["status"] = "processed"
                        hook_data["processed"] = datetime.now().isoformat()
                        hook_data["result"] = result

                        with open(hook_file, "w", encoding="utf-8") as f:
                            json.dump(hook_data, f, indent=2, ensure_ascii=False)

                        print(f"✅ Processed: {file_path}")
                    else:
                        print(f"❌ Failed: {file_path} - {result['message']}")

                except Exception as e:
                    print(f"❌ Error processing {hook_file}: {str(e)}")

        elif args.command == "shutdown":
            if args.verbose:
                print("Shutting down Zed incremental hook...")

            hook.shutdown()

            if args.verbose:
                print("✅ Shutdown complete")

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
