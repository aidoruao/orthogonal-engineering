"""
Crusader Combat Refrigerator - Integrity Check Module
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Integrity verification system for the Crusader Combat Refrigerator.
Provides cryptographic integrity checks, hash verification, and system validation.
"""

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class IntegrityStatus(Enum):
    """Integrity check status codes."""

    VALID = auto()  # Integrity check passed
    INVALID = auto()  # Integrity check failed
    UNKNOWN = auto()  # Integrity status unknown
    ERROR = auto()  # Error during integrity check


class IntegrityCheckType(Enum):
    """Types of integrity checks."""

    FILE_HASH = auto()  # File hash verification
    CONFIG_VALIDATION = auto()  # Configuration validation
    DEPENDENCY_CHECK = auto()  # Dependency verification
    SYSTEM_INTEGRITY = auto()  # Overall system integrity
    RUNTIME_VALIDATION = auto()  # Runtime state validation


@dataclass
class IntegrityResult:
    """Result of an integrity check."""

    check_type: IntegrityCheckType
    status: IntegrityStatus
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    check_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "check_type": self.check_type.name,
            "status": self.status.name,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "check_id": self.check_id,
        }

    def is_valid(self) -> bool:
        """Check if integrity check passed."""
        return self.status == IntegrityStatus.VALID


class IntegrityCheck:
    """Base class for integrity checks."""

    def __init__(self, check_type: IntegrityCheckType, check_id: str):
        self.check_type = check_type
        self.check_id = check_id
        self.timestamp = datetime.now()

    def execute(self) -> IntegrityResult:
        """Execute the integrity check."""
        raise NotImplementedError("Subclasses must implement execute()")

    def _create_result(
        self, status: IntegrityStatus, message: str, details: Dict[str, Any]
    ) -> IntegrityResult:
        """Create an integrity result."""
        return IntegrityResult(
            check_type=self.check_type,
            status=status,
            message=message,
            details=details,
            timestamp=datetime.now(),
            check_id=self.check_id,
        )


class FileHashCheck(IntegrityCheck):
    """Check file integrity using cryptographic hashes."""

    def __init__(self, file_path: str, expected_hash: Optional[str] = None):
        super().__init__(
            IntegrityCheckType.FILE_HASH, f"file_hash_{Path(file_path).name}"
        )
        self.file_path = Path(file_path)
        self.expected_hash = expected_hash

    def execute(self) -> IntegrityResult:
        """Calculate file hash and compare with expected value."""
        try:
            if not self.file_path.exists():
                return self._create_result(
                    status=IntegrityStatus.ERROR,
                    message=f"File not found: {self.file_path}",
                    details={
                        "file_path": str(self.file_path),
                        "error": "File not found",
                    },
                )

            # Calculate SHA-256 hash
            sha256_hash = hashlib.sha256()
            with open(self.file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)

            actual_hash = sha256_hash.hexdigest()

            if self.expected_hash:
                if actual_hash == self.expected_hash:
                    return self._create_result(
                        status=IntegrityStatus.VALID,
                        message=f"File hash matches expected value: {self.file_path.name}",
                        details={
                            "file_path": str(self.file_path),
                            "actual_hash": actual_hash,
                            "expected_hash": self.expected_hash,
                            "file_size": self.file_path.stat().st_size,
                        },
                    )
                else:
                    return self._create_result(
                        status=IntegrityStatus.INVALID,
                        message=f"File hash mismatch: {self.file_path.name}",
                        details={
                            "file_path": str(self.file_path),
                            "actual_hash": actual_hash,
                            "expected_hash": self.expected_hash,
                            "file_size": self.file_path.stat().st_size,
                        },
                    )
            else:
                # No expected hash provided, just report the hash
                return self._create_result(
                    status=IntegrityStatus.VALID,
                    message=f"File hash calculated: {self.file_path.name}",
                    details={
                        "file_path": str(self.file_path),
                        "actual_hash": actual_hash,
                        "file_size": self.file_path.stat().st_size,
                    },
                )

        except Exception as e:
            return self._create_result(
                status=IntegrityStatus.ERROR,
                message=f"Error calculating file hash: {str(e)}",
                details={
                    "file_path": str(self.file_path),
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )


class ConfigValidationCheck(IntegrityCheck):
    """Validate configuration files."""

    def __init__(self, config_path: str, schema: Optional[Dict] = None):
        super().__init__(
            IntegrityCheckType.CONFIG_VALIDATION,
            f"config_validation_{Path(config_path).name}",
        )
        self.config_path = Path(config_path)
        self.schema = schema

    def execute(self) -> IntegrityResult:
        """Validate configuration file."""
        try:
            if not self.config_path.exists():
                return self._create_result(
                    status=IntegrityStatus.ERROR,
                    message=f"Configuration file not found: {self.config_path}",
                    details={
                        "config_path": str(self.config_path),
                        "error": "File not found",
                    },
                )

            # Load configuration
            import yaml

            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)

            if not config:
                return self._create_result(
                    status=IntegrityStatus.INVALID,
                    message=f"Empty configuration file: {self.config_path.name}",
                    details={"config_path": str(self.config_path), "config": config},
                )

            # Basic validation
            required_sections = ["system", "warfare", "monitoring", "hardware"]
            missing_sections = []

            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)

            if missing_sections:
                return self._create_result(
                    status=IntegrityStatus.INVALID,
                    message=f"Missing required sections in configuration: {', '.join(missing_sections)}",
                    details={
                        "config_path": str(self.config_path),
                        "missing_sections": missing_sections,
                        "present_sections": list(config.keys()),
                    },
                )

            # If schema provided, validate against it
            if self.schema:
                # Simple schema validation
                errors = []
                for key, expected_type in self.schema.items():
                    if key in config:
                        if not isinstance(config[key], expected_type):
                            errors.append(
                                f"{key}: expected {expected_type.__name__}, got {type(config[key]).__name__}"
                            )

                if errors:
                    return self._create_result(
                        status=IntegrityStatus.INVALID,
                        message=f"Schema validation failed: {self.config_path.name}",
                        details={
                            "config_path": str(self.config_path),
                            "errors": errors,
                            "config": config,
                        },
                    )

            return self._create_result(
                status=IntegrityStatus.VALID,
                message=f"Configuration validated successfully: {self.config_path.name}",
                details={
                    "config_path": str(self.config_path),
                    "sections": list(config.keys()),
                    "config_size": len(str(config)),
                },
            )

        except yaml.YAMLError as e:
            return self._create_result(
                status=IntegrityStatus.INVALID,
                message=f"Invalid YAML in configuration: {str(e)}",
                details={
                    "config_path": str(self.config_path),
                    "error": str(e),
                    "error_type": "YAMLError",
                },
            )
        except Exception as e:
            return self._create_result(
                status=IntegrityStatus.ERROR,
                message=f"Error validating configuration: {str(e)}",
                details={
                    "config_path": str(self.config_path),
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )


class DependencyCheck(IntegrityCheck):
    """Check system dependencies."""

    def __init__(self):
        super().__init__(IntegrityCheckType.DEPENDENCY_CHECK, "dependency_check")

    def execute(self) -> IntegrityResult:
        """Check if required dependencies are available."""
        try:
            dependencies = [
                ("psutil", "psutil"),
                ("yaml", "yaml"),
                ("cryptography", "cryptography"),
                ("numpy", "numpy"),
                ("pandas", "pandas"),
                ("PIL", "PIL.Image"),
            ]

            missing_deps = []
            available_deps = []

            for dep_name, import_name in dependencies:
                try:
                    __import__(import_name.split(".")[0])
                    available_deps.append(dep_name)
                except ImportError:
                    missing_deps.append(dep_name)

            if missing_deps:
                return self._create_result(
                    status=IntegrityStatus.INVALID,
                    message=f"Missing dependencies: {', '.join(missing_deps)}",
                    details={
                        "missing_dependencies": missing_deps,
                        "available_dependencies": available_deps,
                        "total_checked": len(dependencies),
                    },
                )
            else:
                return self._create_result(
                    status=IntegrityStatus.VALID,
                    message="All dependencies available",
                    details={
                        "available_dependencies": available_deps,
                        "total_checked": len(dependencies),
                    },
                )

        except Exception as e:
            return self._create_result(
                status=IntegrityStatus.ERROR,
                message=f"Error checking dependencies: {str(e)}",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )


class SystemIntegrityCheck(IntegrityCheck):
    """Check overall system integrity."""

    def __init__(self):
        super().__init__(IntegrityCheckType.SYSTEM_INTEGRITY, "system_integrity")

    def execute(self) -> IntegrityResult:
        """Perform comprehensive system integrity check."""
        try:
            checks = []

            # Check critical directories exist
            critical_dirs = [
                "core",
                "warfare",
                "monitoring",
                "hardware",
                "interface",
            ]

            missing_dirs = []
            for dir_name in critical_dirs:
                dir_path = Path(dir_name)
                if dir_path.exists() and dir_path.is_dir():
                    checks.append(f"Directory exists: {dir_name}")
                else:
                    missing_dirs.append(dir_name)
                    checks.append(f"Directory missing: {dir_name}")

            # Check critical files
            critical_files = [
                "core/main.py",
                "core/config.yaml",
                "core/constants.py",
            ]

            missing_files = []
            for file_path in critical_files:
                file_obj = Path(file_path)
                if file_obj.exists() and file_obj.is_file():
                    checks.append(f"File exists: {file_path}")
                else:
                    missing_files.append(file_path)
                    checks.append(f"File missing: {file_path}")

            if missing_dirs or missing_files:
                return self._create_result(
                    status=IntegrityStatus.INVALID,
                    message="System integrity check failed",
                    details={
                        "missing_directories": missing_dirs,
                        "missing_files": missing_files,
                        "checks_performed": checks,
                    },
                )
            else:
                return self._create_result(
                    status=IntegrityStatus.VALID,
                    message="System integrity check passed",
                    details={
                        "checks_performed": checks,
                        "critical_directories": critical_dirs,
                        "critical_files": critical_files,
                    },
                )

        except Exception as e:
            return self._create_result(
                status=IntegrityStatus.ERROR,
                message=f"Error during system integrity check: {str(e)}",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
            )


class IntegrityVerifier:
    """
    Main integrity verification system.
    Coordinates multiple integrity checks and provides comprehensive validation.
    """

    def __init__(self):
        self.checks: List[IntegrityCheck] = []
        self.results: List[IntegrityResult] = []

    def add_check(self, check: IntegrityCheck) -> None:
        """Add an integrity check to the verifier."""
        self.checks.append(check)

    def run_all_checks(self) -> List[IntegrityResult]:
        """Run all registered integrity checks."""
        self.results = []
        for check in self.checks:
            result = check.execute()
            self.results.append(result)

        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all integrity check results."""
        if not self.results:
            return {
                "status": "NO_CHECKS_RUN",
                "message": "No integrity checks have been run",
            }

        total = len(self.results)
        valid = sum(1 for r in self.results if r.status == IntegrityStatus.VALID)
        invalid = sum(1 for r in self.results if r.status == IntegrityStatus.INVALID)
        error = sum(1 for r in self.results if r.status == IntegrityStatus.ERROR)
        unknown = sum(1 for r in self.results if r.status == IntegrityStatus.UNKNOWN)

        overall_status = (
            IntegrityStatus.VALID
            if invalid == 0 and error == 0
            else IntegrityStatus.INVALID
        )

        return {
            "overall_status": overall_status.name,
            "total_checks": total,
            "valid_checks": valid,
            "invalid_checks": invalid,
            "error_checks": error,
            "unknown_checks": unknown,
            "results": [r.to_dict() for r in self.results],
        }

    def is_system_valid(self) -> bool:
        """Check if all integrity checks passed."""
        if not self.results:
            return False

        return all(r.status == IntegrityStatus.VALID for r in self.results)

    def create_default_verifier(self) -> "IntegrityVerifier":
        """Create a verifier with default checks."""
        verifier = IntegrityVerifier()

        # Add system integrity check
        verifier.add_check(SystemIntegrityCheck())

        # Add dependency check
        verifier.add_check(DependencyCheck())

        # Add configuration validation if config file exists
        config_path = Path("core/config.yaml")
        if config_path.exists():
            verifier.add_check(ConfigValidationCheck(str(config_path)))

        return verifier


# Convenience function for quick integrity verification
def verify_integrity() -> Dict[str, Any]:
    """Quick integrity verification of the system."""
    verifier = IntegrityVerifier().create_default_verifier()
    verifier.run_all_checks()
    return verifier.get_summary()
