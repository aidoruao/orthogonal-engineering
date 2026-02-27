"""
Crusader Combat Refrigerator - I/O Utilities
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

I/O utility functions for file operations, logging, and system interactions.
"""

import asyncio
import csv
import gzip
import hashlib
import json
import os
import pickle
import shutil
import tempfile
import time
import zipfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, BinaryIO, Dict, Generator, List, Optional, TextIO, Tuple, Union

import yaml


class FileMode(Enum):
    """File access modes."""

    READ = auto()
    WRITE = auto()
    APPEND = auto()
    READ_WRITE = auto()
    BINARY_READ = auto()
    BINARY_WRITE = auto()
    BINARY_APPEND = auto()


class FileFormat(Enum):
    """Supported file formats."""

    JSON = auto()
    YAML = auto()
    CSV = auto()
    TEXT = auto()
    BINARY = auto()
    PICKLE = auto()


class CompressionType(Enum):
    """Compression types."""

    NONE = auto()
    GZIP = auto()
    ZIP = auto()


@dataclass
class FileInfo:
    """File information structure."""

    path: str
    size_bytes: int
    created_time: datetime
    modified_time: datetime
    accessed_time: datetime
    is_file: bool
    is_dir: bool
    is_symlink: bool
    permissions: int
    owner: Optional[str] = None
    group: Optional[str] = None
    hash_md5: Optional[str] = None
    hash_sha256: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_time"] = self.created_time.isoformat()
        data["modified_time"] = self.modified_time.isoformat()
        data["accessed_time"] = self.accessed_time.isoformat()
        return data


@dataclass
class DirectoryInfo:
    """Directory information structure."""

    path: str
    total_files: int
    total_dirs: int
    total_size_bytes: int
    created_time: datetime
    modified_time: datetime
    file_types: Dict[str, int]  # extension -> count
    largest_file: Optional[FileInfo] = None
    oldest_file: Optional[FileInfo] = None
    newest_file: Optional[FileInfo] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_time"] = self.created_time.isoformat()
        data["modified_time"] = self.modified_time.isoformat()

        if self.largest_file:
            data["largest_file"] = self.largest_file.to_dict()
        if self.oldest_file:
            data["oldest_file"] = self.oldest_file.to_dict()
        if self.newest_file:
            data["newest_file"] = self.newest_file.to_dict()

        return data


class FileLogger:
    """Structured file logging system."""

    def __init__(
        self,
        log_dir: str = "./logs",
        max_file_size_mb: int = 10,
        max_backup_files: int = 10,
        compression: bool = True,
    ):
        """Initialize file logger."""
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.max_backup_files = max_backup_files
        self.compression = compression

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current log file
        self.current_log_file = None
        self.current_file_size = 0

        # Statistics
        self.statistics = {
            "total_logs": 0,
            "total_bytes": 0,
            "log_files_created": 0,
            "log_files_rotated": 0,
            "compressed_files": 0,
        }

    def initialize(self):
        """Initialize the file logger."""
        print(f"🔧 Initializing File Logger in {self.log_dir}...")
        self._rotate_log_file()
        print("✅ File Logger initialized")

    def _rotate_log_file(self):
        """Rotate to a new log file."""
        if self.current_log_file and os.path.exists(self.current_log_file):
            # Archive current file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"log_{timestamp}.log"
            archive_path = self.log_dir / archive_name

            try:
                shutil.move(self.current_log_file, archive_path)

                # Compress if enabled
                if self.compression:
                    self._compress_file(archive_path)

                # Clean up old files
                self._cleanup_old_files()

                self.statistics["log_files_rotated"] += 1

            except Exception as e:
                print(f"❌ Failed to rotate log file: {e}")

        # Create new log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_log_file = self.log_dir / f"current_{timestamp}.log"
        self.current_file_size = 0

        # Write header
        self._write_log_header()

        self.statistics["log_files_created"] += 1

    def _write_log_header(self):
        """Write header to new log file."""
        header = f"# Crusader Log File - Started at {datetime.now().isoformat()}\n"
        header += f"# System: Crusader Combat Refrigerator\n"
        header += f"# Version: 1.0.0\n"
        header += "#" * 80 + "\n\n"

        try:
            with open(self.current_log_file, "w", encoding="utf-8") as f:
                f.write(header)
            self.current_file_size = len(header.encode("utf-8"))
        except Exception as e:
            print(f"❌ Failed to write log header: {e}")

    def _compress_file(self, file_path: Path):
        """Compress a file using gzip."""
        try:
            compressed_path = file_path.with_suffix(".log.gz")
            with open(file_path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove original
            os.remove(file_path)
            self.statistics["compressed_files"] += 1

        except Exception as e:
            print(f"❌ Failed to compress file {file_path}: {e}")

    def _cleanup_old_files(self):
        """Clean up old log files."""
        log_files = sorted(
            self.log_dir.glob("log_*.log*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        # Remove old files
        for file in log_files[self.max_backup_files :]:
            try:
                file.unlink()
            except Exception as e:
                print(f"❌ Failed to delete old log file {file}: {e}")

    def log(
        self,
        level: str,
        source: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        """Write a log entry."""
        if not self.current_log_file:
            self._rotate_log_file()

        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "source": source,
            "message": message,
            "data": data or {},
        }

        # Format log entry
        log_line = json.dumps(log_entry) + "\n"
        log_bytes = log_line.encode("utf-8")

        try:
            # Check if we need to rotate
            if self.current_file_size + len(log_bytes) > self.max_file_size:
                self._rotate_log_file()

            # Write to file
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(log_line)

            # Update statistics
            self.current_file_size += len(log_bytes)
            self.statistics["total_logs"] += 1
            self.statistics["total_bytes"] += len(log_bytes)

        except Exception as e:
            print(f"❌ Failed to write log entry: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get logger statistics."""
        stats = self.statistics.copy()
        stats["current_log_file"] = (
            str(self.current_log_file) if self.current_log_file else None
        )
        stats["current_file_size_bytes"] = self.current_file_size
        stats["log_directory"] = str(self.log_dir)
        return stats


class IOEngine:
    """System I/O operations and utilities."""

    def __init__(self):
        """Initialize system I/O."""
        self.temp_dir = Path(tempfile.gettempdir()) / "crusader"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # File locks for concurrent access
        self.file_locks: Dict[str, asyncio.Lock] = {}
        self.lock_lock = asyncio.Lock()

        # Statistics
        self.statistics = {
            "files_read": 0,
            "files_written": 0,
            "bytes_read": 0,
            "bytes_written": 0,
            "temp_files_created": 0,
            "temp_files_deleted": 0,
        }

    def initialize(self):
        """Initialize system I/O."""
        print("🔧 Initializing System I/O...")
        # Clean up old temp files
        self._cleanup_temp_files()
        print(f"✅ System I/O initialized. Temp directory: {self.temp_dir}")

    def _cleanup_temp_files(self):
        """Clean up old temporary files."""
        try:
            for file in self.temp_dir.glob("*"):
                try:
                    # Delete files older than 24 hours
                    if file.stat().st_mtime < time.time() - 86400:
                        file.unlink()
                        self.statistics["temp_files_deleted"] += 1
                except:
                    pass
        except Exception as e:
            print(f"⚠️ Failed to clean up temp files: {e}")

    async def _get_file_lock(self, file_path: str) -> asyncio.Lock:
        """Get or create a lock for a file."""
        async with self.lock_lock:
            if file_path not in self.file_locks:
                self.file_locks[file_path] = asyncio.Lock()
            return self.file_locks[file_path]

    async def read_file(
        self,
        file_path: str,
        format: FileFormat = FileFormat.TEXT,
        encoding: str = "utf-8",
        lock: bool = True,
    ) -> Any:
        """
        Read a file with optional locking.

        Returns:
            File contents in specified format
        """
        file_lock = await self._get_file_lock(file_path) if lock else None

        if lock and file_lock:
            async with file_lock:
                return await self._read_file_internal(file_path, format, encoding)
        else:
            return await self._read_file_internal(file_path, format, encoding)

    async def _read_file_internal(
        self, file_path: str, format: FileFormat, encoding: str
    ) -> Any:
        """Internal file reading implementation."""
        try:
            if format == FileFormat.TEXT:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()

            elif format == FileFormat.JSON:
                with open(file_path, "r", encoding=encoding) as f:
                    content = json.load(f)

            elif format == FileFormat.YAML:
                with open(file_path, "r", encoding=encoding) as f:
                    content = yaml.safe_load(f)

            elif format == FileFormat.CSV:
                with open(file_path, "r", encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    content = list(reader)

            elif format == FileFormat.BINARY:
                with open(file_path, "rb") as f:
                    content = f.read()

            elif format == FileFormat.PICKLE:
                with open(file_path, "rb") as f:
                    content = pickle.load(f)

            else:
                raise ValueError(f"Unsupported format: {format}")

            # Update statistics
            file_size = os.path.getsize(file_path)
            self.statistics["files_read"] += 1
            self.statistics["bytes_read"] += file_size

            return content

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

    async def write_file(
        self,
        file_path: str,
        data: Any,
        format: FileFormat = FileFormat.TEXT,
        encoding: str = "utf-8",
        lock: bool = True,
        create_backup: bool = True,
    ) -> bool:
        """
        Write data to a file with optional locking and backup.

        Returns:
            True if successful
        """
        file_lock = await self._get_file_lock(file_path) if lock else None

        if lock and file_lock:
            async with file_lock:
                return await self._write_file_internal(
                    file_path, data, format, encoding, create_backup
                )
        else:
            return await self._write_file_internal(
                file_path, data, format, encoding, create_backup
            )

    async def _write_file_internal(
        self,
        file_path: str,
        data: Any,
        format: FileFormat,
        encoding: str,
        create_backup: bool,
    ) -> bool:
        """Internal file writing implementation."""
        try:
            # Create backup if file exists
            if create_backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup_{int(time.time())}"
                shutil.copy2(file_path, backup_path)

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write file based on format
            if format == FileFormat.TEXT:
                with open(file_path, "w", encoding=encoding) as f:
                    f.write(str(data))

            elif format == FileFormat.JSON:
                with open(file_path, "w", encoding=encoding) as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            elif format == FileFormat.YAML:
                with open(file_path, "w", encoding=encoding) as f:
                    yaml.dump(data, f, default_flow_style=False)

            elif format == FileFormat.CSV:
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    with open(file_path, "w", encoding=encoding, newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                else:
                    raise ValueError("CSV data must be a list of dictionaries")

            elif format == FileFormat.BINARY:
                with open(file_path, "wb") as f:
                    if isinstance(data, bytes):
                        f.write(data)
                    else:
                        f.write(str(data).encode(encoding))

            elif format == FileFormat.PICKLE:
                with open(file_path, "wb") as f:
                    pickle.dump(data, f)

            else:
                raise ValueError(f"Unsupported format: {format}")

            # Update statistics
            file_size = os.path.getsize(file_path)
            self.statistics["files_written"] += 1
            self.statistics["bytes_written"] += file_size

            return True

        except Exception as e:
            print(f"❌ Failed to write file {file_path}: {e}")
            return False

    async def append_file(
        self,
        file_path: str,
        data: Any,
        format: FileFormat = FileFormat.TEXT,
        encoding: str = "utf-8",
        lock: bool = True,
    ) -> bool:
        """Append data to a file."""
        file_lock = await self._get_file_lock(file_path) if lock else None

        if lock and file_lock:
            async with file_lock:
                return await self._append_file_internal(
                    file_path, data, format, encoding
                )
        else:
            return await self._append_file_internal(file_path, data, format, encoding)

    async def _append_file_internal(
        self, file_path: str, data: Any, format: FileFormat, encoding: str
    ) -> bool:
        """Internal file appending implementation."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if format == FileFormat.TEXT:
                with open(file_path, "a", encoding=encoding) as f:
                    f.write(str(data))

            elif format == FileFormat.JSON:
                # For JSON, we need to read, update, and write
                existing_data = []
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            existing_data = json.load(f)
                            if not isinstance(existing_data, list):
                                existing_data = [existing_data]
                    except:
                        existing_data = []

                if isinstance(data, list):
                    existing_data.extend(data)
                else:
                    existing_data.append(data)

                with open(file_path, "w", encoding=encoding) as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)

            else:
                # For other formats, treat as text append
                with open(file_path, "a", encoding=encoding) as f:
                    f.write(str(data))

            return True

        except Exception as e:
            print(f"❌ Failed to append to file {file_path}: {e}")
            return False

    def create_temp_file(
        self,
        prefix: str = "crusader_",
        suffix: str = ".tmp",
        content: Optional[Any] = None,
        format: FileFormat = FileFormat.TEXT,
    ) -> str:
        """Create a temporary file."""
        try:
            # Create unique temporary file
            with tempfile.NamedTemporaryFile(
                mode="w" if format == FileFormat.TEXT else "wb",
                prefix=prefix,
                suffix=suffix,
                delete=False,
            ) as temp_file:
                temp_path = temp_file.name

                # Write content if provided
                if content is not None:
                    if format == FileFormat.JSON:
                        json.dump(content, temp_file, indent=2)
                    elif format == FileFormat.YAML:
                        yaml.dump(content, temp_file, default_flow_style=False)
                    elif format == FileFormat.CSV:
                        if isinstance(content, list) and len(content) > 0:
                            writer = csv.writer(temp_file)
                            if isinstance(content[0], dict):
                                # Write header from dict keys
                                writer.writerow(content[0].keys())
                                for row in content:
                                    writer.writerow(row.values())
                            else:
                                writer.writerows(content)
                        else:
                            temp_file.write(str(content))
                    elif format == FileFormat.PICKLE:
                        pickle.dump(content, temp_file)
                    elif format == FileFormat.BINARY:
                        if isinstance(content, bytes):
                            temp_file.write(content)
                        else:
                            temp_file.write(str(content).encode())
                    else:  # TEXT format
                        temp_file.write(str(content))

                return temp_path

        except Exception as e:
            print(f"❌ Failed to create temporary file: {e}")
            raise

    def cleanup_temp_files(self, pattern: str = "crusader_*.tmp") -> int:
        """Clean up temporary files matching pattern."""
        try:
            temp_dir = tempfile.gettempdir()
            count = 0

            for file_path in Path(temp_dir).glob(pattern):
                try:
                    file_path.unlink()
                    count += 1
                except Exception as e:
                    print(f"❌ Failed to delete {file_path}: {e}")

            return count

        except Exception as e:
            print(f"❌ Failed to cleanup temp files: {e}")
            return 0

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.cleanup_temp_files()
        except:
            pass  # Ignore errors during cleanup


# Additional I/O utility classes and functions


@dataclass
class IOResult:
    """Result of an I/O operation."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    bytes_processed: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data if self.data is not None else None,
            "error": self.error,
            "bytes_processed": self.bytes_processed,
            "duration_ms": self.duration_ms,
        }


@dataclass
class IOOperation:
    """I/O operation metadata."""

    operation_type: str  # "read", "write", "append", "delete", "copy", "move"
    file_path: str
    timestamp: datetime
    success: bool
    bytes_processed: int = 0
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    process_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_type": self.operation_type,
            "file_path": self.file_path,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "bytes_processed": self.bytes_processed,
            "error_message": self.error_message,
            "user_id": self.user_id,
            "process_id": self.process_id,
        }


class SystemIO:
    """System-level I/O operations with monitoring and auditing."""

    def __init__(self, audit_logger: Optional[FileLogger] = None):
        """Initialize system I/O."""
        self.engine = IOEngine()
        self.audit_logger = audit_logger or FileLogger()
        self.operations: List[IOOperation] = []

    def initialize(self) -> bool:
        """Initialize system I/O."""
        print("🔧 Initializing System I/O...")
        # Initialize the IOEngine
        self.engine.initialize()
        print("✅ System I/O initialized")
        return True

    async def read_file(
        self,
        file_path: str,
        format: FileFormat = FileFormat.TEXT,
        encoding: str = "utf-8",
        lock: bool = True,
        audit: bool = True,
    ) -> IOResult:
        """Read a file with auditing."""
        start_time = time.time()
        operation = IOOperation(
            operation_type="read",
            file_path=file_path,
            timestamp=datetime.now(),
            success=False,
            user_id=os.getenv("USER", "unknown"),
            process_id=os.getpid(),
        )

        try:
            data = await self.engine.read_file(file_path, format, encoding, lock)
            duration_ms = (time.time() - start_time) * 1000

            # Get file size for bytes processed
            bytes_processed = 0
            if os.path.exists(file_path):
                bytes_processed = os.path.getsize(file_path)

            operation.success = True
            operation.bytes_processed = bytes_processed

            result = IOResult(
                success=True,
                data=data,
                bytes_processed=bytes_processed,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            operation.success = False
            operation.error_message = str(e)

            result = IOResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )

        # Audit logging
        if audit:
            self.operations.append(operation)
            self.audit_logger.log(
                level="INFO" if operation.success else "ERROR",
                source="SystemIO.read_file",
                message=f"File read: {file_path}",
                data=operation.to_dict(),
            )

        return result

    async def write_file(
        self,
        file_path: str,
        data: Any,
        format: FileFormat = FileFormat.TEXT,
        encoding: str = "utf-8",
        lock: bool = True,
        create_backup: bool = True,
        audit: bool = True,
    ) -> IOResult:
        """Write a file with auditing."""
        start_time = time.time()
        operation = IOOperation(
            operation_type="write",
            file_path=file_path,
            timestamp=datetime.now(),
            success=False,
            user_id=os.getenv("USER", "unknown"),
            process_id=os.getpid(),
        )

        try:
            success = await self.engine.write_file(
                file_path, data, format, encoding, lock, create_backup
            )
            duration_ms = (time.time() - start_time) * 1000

            # Calculate bytes processed
            bytes_processed = 0
            if success and os.path.exists(file_path):
                bytes_processed = os.path.getsize(file_path)

            operation.success = success
            operation.bytes_processed = bytes_processed

            result = IOResult(
                success=success,
                bytes_processed=bytes_processed,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            operation.success = False
            operation.error_message = str(e)

            result = IOResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )

        # Audit logging
        if audit:
            self.operations.append(operation)
            self.audit_logger.log(
                level="INFO" if operation.success else "ERROR",
                source="SystemIO.write_file",
                message=f"File write: {file_path}",
                data=operation.to_dict(),
            )

        return result

    async def append_file(
        self,
        file_path: str,
        data: Any,
        format: FileFormat = FileFormat.TEXT,
        encoding: str = "utf-8",
        lock: bool = True,
        audit: bool = True,
    ) -> IOResult:
        """Append to a file with auditing."""
        start_time = time.time()
        operation = IOOperation(
            operation_type="append",
            file_path=file_path,
            timestamp=datetime.now(),
            success=False,
            user_id=os.getenv("USER", "unknown"),
            process_id=os.getpid(),
        )

        try:
            success = await self.engine.append_file(
                file_path, data, format, encoding, lock
            )
            duration_ms = (time.time() - start_time) * 1000

            # Calculate bytes added
            bytes_processed = len(str(data).encode(encoding)) if success else 0
            operation.success = success
            operation.bytes_processed = bytes_processed

            result = IOResult(
                success=success,
                bytes_processed=bytes_processed,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            operation.success = False
            operation.error_message = str(e)

            result = IOResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )

        # Audit logging
        if audit:
            self.operations.append(operation)
            self.audit_logger.log(
                level="INFO" if operation.success else "ERROR",
                source="SystemIO.append_file",
                message=f"File append: {file_path}",
                data=operation.to_dict(),
            )

        return result

    def create_temp_file(
        self,
        prefix: str = "crusader_",
        suffix: str = ".tmp",
        content: Optional[Any] = None,
        format: FileFormat = FileFormat.TEXT,
    ) -> str:
        """Create a temporary file."""
        return self.engine.create_temp_file(prefix, suffix, content, format)

    def cleanup_temp_files(self, pattern: str = "crusader_*.tmp") -> int:
        """Clean up temporary files."""
        return self.engine.cleanup_temp_files(pattern)

    def get_statistics(self) -> Dict[str, Any]:
        """Get I/O statistics."""
        engine_stats = self.engine.get_statistics()
        return {
            "engine": engine_stats,
            "total_operations": len(self.operations),
            "successful_operations": sum(1 for op in self.operations if op.success),
            "failed_operations": sum(1 for op in self.operations if not op.success),
            "total_bytes_processed": sum(op.bytes_processed for op in self.operations),
            "operations": [
                op.to_dict() for op in self.operations[-100:]
            ],  # Last 100 ops
        }

    def clear_operations(self):
        """Clear operation history."""
        self.operations.clear()

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.engine.cleanup_temp_files()
        except:
            pass  # Ignore errors during cleanup
