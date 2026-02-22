"""
Onboarding Check Module - IDE-AI Integration for Orthogonal Engineering

Implements the atomic instruction blueprint: "Check-Onboarding Status"
Provides idempotent, read-only verification of onboarding artifacts.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
Schema: GB-ORIGIN-1.11
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Import Glass-Box Boundary components
from toolkit.oe.boundary_enforcer import (
    glass_box_boundary,
    validate_input_schema,
    validate_output_schema,
)

# UD-Bounded(k) enforcement for onboarding/audit loops
from oe_ifm.halt_condition import BoundedCounter, HaltConditionError

# Maximum artifacts processed per pipeline run (UD-Bounded guard)
_MAX_AUDIT_ARTIFACTS: int = 10_000


class OnboardingStatus(Enum):
    """Status of onboarding verification."""

    FULL = "full"  # All expected files, hashes, and tokens acknowledged
    PARTIAL = "partial"  # Some files or sections missing, incomplete, or corrupted
    ABSENT = "absent"  # No onboarding artifact present


class ArtifactType(Enum):
    """Types of onboarding artifacts."""

    ONBOARDING_FILE = "onboarding_file"
    LOCK_FILE = "lock_file"
    ACK_FILE = "ack_file"
    HASH_MANIFEST = "hash_manifest"
    COMMIT_HASH = "commit_hash"
    DIRECTORY_SCAN = "directory_scan"
    PERMISSION_RECORD = "permission_record"
    TOKEN_BUDGET = "token_budget"


@dataclass
class CandidateArtifact:
    """Represents a candidate onboarding artifact found during scanning."""

    path: str
    artifact_type: ArtifactType
    size_bytes: int
    commit_hash: Optional[str] = None
    last_modified: Optional[datetime] = None
    content_preview: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of artifact structure validation."""

    artifact_path: str
    is_valid: bool
    status: str  # "valid", "partial", "invalid"
    missing_fields: List[str]
    validation_errors: List[str]
    structure_summary: Dict[str, Any]


@dataclass
class CrossCheckResult:
    """Result of cross-checking artifact with repository."""

    artifact_commit_hash: Optional[str]
    current_repo_head: Optional[str]
    commit_match: bool
    directories_exist: List[str]
    directories_missing: List[str]
    files_exist: List[str]
    files_missing: List[str]
    mismatches: List[str]


@dataclass
class OnboardingReport:
    """Final onboarding status report."""

    status: OnboardingStatus
    artifact_path: Optional[str]
    missing_fields: List[str]
    mismatched_files: List[str]
    repo_commit: Optional[str]
    candidate_artifacts: List[CandidateArtifact]
    validation_results: List[ValidationResult]
    cross_check_results: Optional[CrossCheckResult]
    generated_at: datetime
    repository_root: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        data = asdict(self)
        # Convert enums to strings
        data["status"] = self.status.value
        data["generated_at"] = self.generated_at.isoformat()

        # Convert nested objects
        if self.candidate_artifacts:
            data["candidate_artifacts"] = [
                {
                    "path": ca.path,
                    "artifact_type": ca.artifact_type.value,
                    "size_bytes": ca.size_bytes,
                    "commit_hash": ca.commit_hash,
                    "last_modified": ca.last_modified.isoformat()
                    if ca.last_modified
                    else None,
                    "content_preview": ca.content_preview,
                }
                for ca in self.candidate_artifacts
            ]

        if self.validation_results:
            data["validation_results"] = [
                {
                    "artifact_path": vr.artifact_path,
                    "is_valid": vr.is_valid,
                    "status": vr.status,
                    "missing_fields": vr.missing_fields,
                    "validation_errors": vr.validation_errors,
                    "structure_summary": vr.structure_summary,
                }
                for vr in self.validation_results
            ]

        if self.cross_check_results:
            data["cross_check_results"] = asdict(self.cross_check_results)

        return data

    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class OnboardingChecker:
    """
    Main class for checking onboarding status.
    Implements the atomic instruction blueprint for IDE-AI integration.
    """

    def __init__(self, repository_root: Optional[str] = None):
        """
        Initialize the onboarding checker.

        Args:
            repository_root: Path to repository root. If None, uses current directory.
        """
        self.repository_root = Path(repository_root) if repository_root else Path.cwd()
        self.report: Optional[OnboardingReport] = None

        # Patterns for identifying candidate artifacts
        self.artifact_patterns = {
            ArtifactType.ONBOARDING_FILE: [
                r"onboarding.*\.(md|txt|json|yaml|yml)$",
                r"ONBOARDING.*\.(md|txt|json|yaml|yml)$",
                r"onboard.*\.(md|txt|json|yaml|yml)$",
                r".*onboard.*\.(md|txt|json|yaml|yml)$",
            ],
            ArtifactType.LOCK_FILE: [
                r".*\.lock$",
                r"lockfile.*",
                r".*lock.*",
            ],
            ArtifactType.ACK_FILE: [
                r".*ack.*\.(md|txt|json|yaml|yml)$",
                r"acknowledgment.*",
                r"acknowledgement.*",
            ],
            ArtifactType.HASH_MANIFEST: [
                r".*hash.*\.(md|txt|json|yaml|yml)$",
                r"manifest.*\.(md|txt|json|yaml|yml)$",
                r"sha256.*",
            ],
        }

        # Expected fields in onboarding artifacts
        self.expected_fields = [
            "commit_hash",
            "directories_scanned",
            "file_count",
            "read_write_permissions",
            "token_budget",  # Optional
            "generated_at",
            "repository_root",
            "artifact_type",
        ]

    @glass_box_boundary(
        input_schema={"type": "object", "properties": {}, "required": []},
        output_schema={
            "type": "object",
            "properties": {
                "candidate_artifacts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "artifact_type": {"type": "string"},
                            "size_bytes": {"type": "integer"},
                            "commit_hash": {"type": ["string", "null"]},
                            "last_modified": {"type": ["string", "null"]},
                            "content_preview": {"type": ["string", "null"]},
                        },
                    },
                }
            },
        },
    )
    def identify_candidate_artifacts(self) -> List[CandidateArtifact]:
        """
        Step 1 — Identify Candidate Artifacts

        Scan the repository for files matching onboarding patterns.

        Returns:
            List of candidate artifacts found.
        """
        candidate_artifacts = []

        for artifact_type, patterns in self.artifact_patterns.items():
            for pattern in patterns:
                # Convert pattern to regex
                regex = re.compile(pattern, re.IGNORECASE)

                # Walk through repository
                for root, dirs, files in os.walk(self.repository_root):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith(".")]

                    for file in files:
                        file_path = Path(root) / file
                        relative_path = file_path.relative_to(self.repository_root)

                        if regex.match(str(relative_path)) or regex.match(file):
                            # Get file info
                            try:
                                stat = file_path.stat()
                                size_bytes = stat.st_size
                                last_modified = datetime.fromtimestamp(stat.st_mtime)

                                # Read first 500 chars for preview
                                content_preview = None
                                if (
                                    size_bytes > 0 and size_bytes < 100000
                                ):  # Skip very large files
                                    try:
                                        with open(
                                            file_path,
                                            "r",
                                            encoding="utf-8",
                                            errors="ignore",
                                        ) as f:
                                            content_preview = f.read(500)
                                    except:
                                        pass

                                # Try to extract commit hash from content
                                commit_hash = None
                                if content_preview:
                                    # Look for commit hash patterns
                                    hash_patterns = [
                                        r"commit[:\s]+([a-f0-9]{40})",
                                        r"hash[:\s]+([a-f0-9]{64})",
                                        r"[a-f0-9]{40}",  # SHA-1
                                        r"[a-f0-9]{64}",  # SHA-256
                                    ]
                                    for hash_pattern in hash_patterns:
                                        match = re.search(
                                            hash_pattern, content_preview, re.IGNORECASE
                                        )
                                        if match:
                                            commit_hash = match.group(1)
                                            break

                                artifact = CandidateArtifact(
                                    path=str(relative_path),
                                    artifact_type=artifact_type,
                                    size_bytes=size_bytes,
                                    commit_hash=commit_hash,
                                    last_modified=last_modified,
                                    content_preview=content_preview,
                                )
                                candidate_artifacts.append(artifact)

                            except (OSError, PermissionError) as e:
                                # Skip files we can't access
                                continue

        # Also check for specific known onboarding files
        known_files = [
            "ONBOARD_FIRST.md",
            "onboarding/LEVEL1.md",
            "onboarding/LEVEL2.md",
            "onboarding/LEVEL3.md",
            "onboarding/README.md",
            "onboarding/verify_onboarding.py",
        ]

        for known_file in known_files:
            file_path = self.repository_root / known_file
            if file_path.exists():
                # Check if already in candidates
                if not any(ca.path == known_file for ca in candidate_artifacts):
                    try:
                        stat = file_path.stat()
                        artifact = CandidateArtifact(
                            path=known_file,
                            artifact_type=ArtifactType.ONBOARDING_FILE,
                            size_bytes=stat.st_size,
                            last_modified=datetime.fromtimestamp(stat.st_mtime),
                        )
                        candidate_artifacts.append(artifact)
                    except (OSError, PermissionError):
                        pass

        return candidate_artifacts

    @glass_box_boundary(
        input_schema={
            "type": "object",
            "properties": {
                "artifact": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "artifact_type": {"type": "string"},
                        "content_preview": {"type": ["string", "null"]},
                    },
                }
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "is_valid": {"type": "boolean"},
                "status": {"type": "string"},
                "missing_fields": {"type": "array", "items": {"type": "string"}},
                "validation_errors": {"type": "array", "items": {"type": "string"}},
                "structure_summary": {"type": "object"},
            },
        },
    )
    def validate_artifact_structure(
        self, artifact: CandidateArtifact
    ) -> ValidationResult:
        """
        Step 2 — Validate Structure

        For each candidate artifact, check if it contains required fields.

        Args:
            artifact: Candidate artifact to validate.

        Returns:
            Validation result with status and missing fields.
        """
        missing_fields = []
        validation_errors = []
        structure_summary = {}

        try:
            artifact_path = self.repository_root / artifact.path

            # Read artifact content
            content = ""
            if artifact_path.exists() and artifact_path.is_file():
                try:
                    with open(
                        artifact_path, "r", encoding="utf-8", errors="ignore"
                    ) as f:
                        content = f.read()
                except (OSError, PermissionError, UnicodeDecodeError) as e:
                    validation_errors.append(f"Cannot read file: {e}")

            # Check for expected fields in content
            found_fields = []

            # Check for commit hash
            if re.search(r"commit[:\s]+[a-f0-9]{40}", content, re.IGNORECASE):
                found_fields.append("commit_hash")
                structure_summary["has_commit_hash"] = True
            else:
                missing_fields.append("commit_hash")
                structure_summary["has_commit_hash"] = False

            # Check for directories scanned
            dir_patterns = [
                r"directories?[:\s]+\[.*\]",
                r"directories?[:\s]+\d+",
                r"scanned[:\s]+\d+\s+directories?",
                r"directories?\s+scanned[:\s]+\d+",
            ]
            if any(
                re.search(pattern, content, re.IGNORECASE) for pattern in dir_patterns
            ):
                found_fields.append("directories_scanned")
                structure_summary["has_directories"] = True
            else:
                missing_fields.append("directories_scanned")
                structure_summary["has_directories"] = False

            # Check for file count
            file_count_patterns = [
                r"file[_\s]?count[:\s]+\d+",
                r"\d+\s+files?",
                r"total[_\s]?files?[:\s]+\d+",
            ]
            if any(
                re.search(pattern, content, re.IGNORECASE)
                for pattern in file_count_patterns
            ):
                found_fields.append("file_count")
                structure_summary["has_file_count"] = True
            else:
                missing_fields.append("file_count")
                structure_summary["has_file_count"] = False

            # Check for permissions
            perm_patterns = [
                r"permissions?[:\s]+",
                r"read[_\s]?write",
                r"access[_\s]?rights",
            ]
            if any(
                re.search(pattern, content, re.IGNORECASE) for pattern in perm_patterns
            ):
                found_fields.append("read_write_permissions")
                structure_summary["has_permissions"] = True
            else:
                missing_fields.append("read_write_permissions")
                structure_summary["has_permissions"] = False

            # Check for token budget (optional)
            token_patterns = [
                r"token[_\s]?budget",
                r"tokens?[:\s]+\d+",
                r"budget[:\s]+\d+\s+tokens?",
            ]
            if any(
                re.search(pattern, content, re.IGNORECASE) for pattern in token_patterns
            ):
                found_fields.append("token_budget")
                structure_summary["has_token_budget"] = True
            else:
                structure_summary["has_token_budget"] = False  # Optional field

            # Check for timestamp
            time_patterns = [
                r"generated[_\s]?at[:\s]+",
                r"timestamp[:\s]+",
                r"date[:\s]+\d{4}[-/]\d{2}[-/]\d{2}",
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",  # ISO format
            ]
            if any(
                re.search(pattern, content, re.IGNORECASE) for pattern in time_patterns
            ):
                found_fields.append("generated_at")
                structure_summary["has_timestamp"] = True
            else:
                missing_fields.append("generated_at")
                structure_summary["has_timestamp"] = False

            # Check for repository root
            root_patterns = [
                r"repository[_\s]?root[:\s]+",
                r"repo[_\s]?root[:\s]+",
                r"root[:\s]+\S+",
            ]
            if any(
                re.search(pattern, content, re.IGNORECASE) for pattern in root_patterns
            ):
                found_fields.append("repository_root")
                structure_summary["has_repo_root"] = True
            else:
                missing_fields.append("repository_root")
                structure_summary["has_repo_root"] = False

            # Check for artifact type
            type_patterns = [
                r"artifact[_\s]?type[:\s]+",
                r"type[:\s]+\S+",
            ]
            if any(
                re.search(pattern, content, re.IGNORECASE) for pattern in type_patterns
            ):
                found_fields.append("artifact_type")
                structure_summary["has_artifact_type"] = True
            else:
                missing_fields.append("artifact_type")
                structure_summary["has_artifact_type"] = False

            # Determine status
            if len(missing_fields) == 0:
                status = "valid"
                is_valid = True
            elif len(missing_fields) <= 4:  # Allow some missing fields
                status = "partial"
                is_valid = False
            else:
                status = "invalid"
                is_valid = False

            # Add content stats to summary
            structure_summary.update(
                {
                    "content_length": len(content),
                    "lines": content.count("\n") + 1,
                    "fields_found": len(found_fields),
                    "fields_missing": len(missing_fields),
                    "found_fields": found_fields,
                }
            )

        except Exception as e:
            validation_errors.append(f"Validation error: {e}")
            status = "invalid"
            is_valid = False
            structure_summary = {"error": str(e)}

        return ValidationResult(
            artifact_path=artifact.path,
            is_valid=is_valid,
            status=status,
            missing_fields=missing_fields,
            validation_errors=validation_errors,
            structure_summary=structure_summary,
        )

    @glass_box_boundary(
        input_schema={
            "type": "object",
            "properties": {"artifact_commit_hash": {"type": ["string", "null"]}},
        },
        output_schema={
            "type": "object",
            "properties": {
                "artifact_commit_hash": {"type": ["string", "null"]},
                "current_repo_head": {"type": ["string", "null"]},
                "commit_match": {"type": "boolean"},
                "directories_exist": {"type": "array", "items": {"type": "string"}},
                "directories_missing": {"type": "array", "items": {"type": "string"}},
                "files_exist": {"type": "array", "items": {"type": "string"}},
                "files_missing": {"type": "array", "items": {"type": "string"}},
                "mismatches": {"type": "array", "items": {"type": "string"}},
            },
        },
    )
    def cross_check_with_repository(
        self, artifact_commit_hash: Optional[str] = None
    ) -> CrossCheckResult:
        """
        Step 3 — Cross-Check with Repository

        1. Take commit hash from artifact
        2. Compare against current repo head
        3. Ensure all directories/files listed in artifact exist in the repo
        4. Any mismatch = "partial" or "needs update"

        Args:
            artifact_commit_hash: Commit hash from artifact (if any).

        Returns:
            Cross-check result with comparison details.
        """
        # Get current repository head
        current_repo_head = None
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repository_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                current_repo_head = result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            # Git not available or not a git repository
            pass

        # Check commit match
        commit_match = False
        if artifact_commit_hash and current_repo_head:
            commit_match = artifact_commit_hash == current_repo_head

        # For now, we'll return basic cross-check results
        # In a full implementation, we would parse artifact content to get
        # specific directories and files to check

        directories_exist = []
        directories_missing = []
        files_exist = []
        files_missing = []
        mismatches = []

        # Check for common directories
        common_dirs = ["onboarding", "automation", "toolkit", "documentation", "logs"]

        for dir_name in common_dirs:
            dir_path = self.repository_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                directories_exist.append(dir_name)
            else:
                directories_missing.append(dir_name)
                mismatches.append(f"Directory missing: {dir_name}")

        # Check for critical files
        critical_files = [
            "ONBOARD_FIRST.md",
            "onboarding/LEVEL1.md",
            "onboarding/LEVEL2.md",
            "AGENT.md",
            "AI_INSTRUCTIONS.md",
            "_START_HERE.md",
        ]

        for file_path in critical_files:
            full_path = self.repository_root / file_path
            if full_path.exists() and full_path.is_file():
                files_exist.append(file_path)
            else:
                files_missing.append(file_path)
                mismatches.append(f"Critical file missing: {file_path}")

        return CrossCheckResult(
            artifact_commit_hash=artifact_commit_hash,
            current_repo_head=current_repo_head,
            commit_match=commit_match,
            directories_exist=directories_exist,
            directories_missing=directories_missing,
            files_exist=files_exist,
            files_missing=files_missing,
            mismatches=mismatches,
        )

    @glass_box_boundary(
        input_schema={
            "type": "object",
            "properties": {
                "candidate_artifacts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "artifact_type": {"type": "string"},
                            "commit_hash": {"type": ["string", "null"]},
                        },
                    },
                },
                "validation_results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "artifact_path": {"type": "string"},
                            "is_valid": {"type": "boolean"},
                            "status": {"type": "string"},
                            "missing_fields": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "artifact_path": {"type": ["string", "null"]},
                "missing_fields": {"type": "array", "items": {"type": "string"}},
                "mismatched_files": {"type": "array", "items": {"type": "string"}},
                "repo_commit": {"type": ["string", "null"]},
                "candidate_artifacts_count": {"type": "integer"},
                "validation_results_count": {"type": "integer"},
            },
        },
    )
    def generate_report(
        self,
        candidate_artifacts: List[CandidateArtifact],
        validation_results: List[ValidationResult],
        cross_check_results: Optional[CrossCheckResult] = None,
    ) -> OnboardingReport:
        """
        Step 4 — Produce Report

        Generate atomic report object with onboarding status.

        Args:
            candidate_artifacts: List of candidate artifacts found.
            validation_results: List of validation results.
            cross_check_results: Optional cross-check results.

        Returns:
            Onboarding status report.
        """
        # Determine overall status
        status = OnboardingStatus.ABSENT
        artifact_path = None
        missing_fields = []
        mismatched_files = []
        repo_commit = None

        if not candidate_artifacts:
            status = OnboardingStatus.ABSENT
        else:
            # Find the best artifact (most complete validation)
            best_artifact = None
            best_validation = None

            for artifact in candidate_artifacts:
                for validation in validation_results:
                    if validation.artifact_path == artifact.path:
                        if best_validation is None:
                            best_artifact = artifact
                            best_validation = validation
                        elif (
                            validation.status == "valid"
                            and best_validation.status != "valid"
                        ):
                            best_artifact = artifact
                            best_validation = validation
                        elif (
                            validation.status == "partial"
                            and best_validation.status == "invalid"
                        ):
                            best_artifact = artifact
                            best_validation = validation

            if best_artifact and best_validation:
                artifact_path = best_artifact.path
                missing_fields = best_validation.missing_fields

                if best_validation.status == "valid":
                    status = OnboardingStatus.FULL
                elif best_validation.status == "partial":
                    status = OnboardingStatus.PARTIAL
                else:
                    status = OnboardingStatus.ABSENT

                # Get repo commit from cross-check or artifact
                if cross_check_results and cross_check_results.current_repo_head:
                    repo_commit = cross_check_results.current_repo_head
                elif best_artifact.commit_hash:
                    repo_commit = best_artifact.commit_hash

                # Get mismatched files from cross-check
                if cross_check_results:
                    mismatched_files = cross_check_results.mismatches

        # Create report
        report = OnboardingReport(
            status=status,
            artifact_path=artifact_path,
            missing_fields=missing_fields,
            mismatched_files=mismatched_files,
            repo_commit=repo_commit,
            candidate_artifacts=candidate_artifacts,
            validation_results=validation_results,
            cross_check_results=cross_check_results,
            generated_at=datetime.now(),
            repository_root=str(self.repository_root),
        )

        self.report = report
        return report

    @glass_box_boundary(
        input_schema={"type": "object", "properties": {}, "required": []},
        output_schema={
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "artifact_path": {"type": ["string", "null"]},
                "missing_fields": {"type": "array", "items": {"type": "string"}},
                "mismatched_files": {"type": "array", "items": {"type": "string"}},
                "repo_commit": {"type": ["string", "null"]},
                "generated_at": {"type": "string"},
            },
        },
    )
    def run_full_check(self) -> OnboardingReport:
        """
        Run the complete onboarding check pipeline.

        Returns:
            Complete onboarding status report.
        """
        print("=" * 60)
        print("ONBOARDING STATUS CHECK - IDE-AI Integration")
        print("=" * 60)
        print(f"Repository: {self.repository_root}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Step 1: Identify candidate artifacts
        print("Step 1 — Identifying candidate artifacts...")
        candidate_artifacts = self.identify_candidate_artifacts()
        print(f"  Found {len(candidate_artifacts)} candidate artifacts")

        # Step 2: Validate structure
        print("\nStep 2 — Validating artifact structure...")
        validation_results = []
        for artifact in candidate_artifacts:
            result = self.validate_artifact_structure(artifact)
            validation_results.append(result)
            status_symbol = (
                "✅"
                if result.status == "valid"
                else "⚠️ "
                if result.status == "partial"
                else "❌"
            )
            print(f"  {status_symbol} {artifact.path}: {result.status}")

        # Step 3: Cross-check with repository
        print("\nStep 3 — Cross-checking with repository...")
        cross_check_results = None
        if candidate_artifacts:
            # Use first artifact with commit hash for cross-check
            artifact_with_hash = next(
                (a for a in candidate_artifacts if a.commit_hash),
                candidate_artifacts[0] if candidate_artifacts else None,
            )
            if artifact_with_hash:
                cross_check_results = self.cross_check_with_repository(
                    artifact_with_hash.commit_hash
                )
                print(f"  Commit match: {cross_check_results.commit_match}")
                print(f"  Missing files: {len(cross_check_results.files_missing)}")

        # Step 4: Generate report
        print("\nStep 4 — Generating report...")
        report = self.generate_report(
            candidate_artifacts, validation_results, cross_check_results
        )

        # Print summary
        print("\n" + "=" * 60)
        print("ONBOARDING STATUS SUMMARY")
        print("=" * 60)
        print(f"Status: {report.status.value.upper()}")

        if report.artifact_path:
            print(f"Primary artifact: {report.artifact_path}")

        if report.missing_fields:
            print(f"Missing fields: {', '.join(report.missing_fields)}")

        if report.mismatched_files:
            print(f"Mismatched files: {len(report.mismatched_files)}")
            for mismatch in report.mismatched_files[:3]:  # Show first 3
                print(f"  - {mismatch}")
            if len(report.mismatched_files) > 3:
                print(f"  ... and {len(report.mismatched_files) - 3} more")

        if report.repo_commit:
            print(f"Repository commit: {report.repo_commit[:8]}...")

        print(f"\nGenerated at: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        return report

    def save_report(self, output_path: Optional[str] = None) -> str:
        """
        Save the report to a file.

        Args:
            output_path: Path to save report. If None, uses default location.

        Returns:
            Path where report was saved.
        """
        if not self.report:
            raise ValueError("No report available. Run check first.")

        if output_path is None:
            # Create logs directory if it doesn't exist
            logs_dir = self.repository_root / "logs" / "onboarding_checks"
            logs_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = logs_dir / f"onboarding_check_{timestamp}.json"

        output_path = Path(output_path)

        # Save report as JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.report.to_dict(), f, indent=2, ensure_ascii=False)

        return str(output_path)


# Pipeline form implementation
class CheckOnboardingPipeline:
    """
    Pipeline form of the onboarding check.
    Each stage can be executed independently and produces atomic output.
    """

    def __init__(self, repository_root: Optional[str] = None):
        self.checker = OnboardingChecker(repository_root)
        self.stage_outputs = {}

    def stage_1_identify_candidate_artifacts(self) -> List[CandidateArtifact]:
        """Stage 1: Identify candidate artifacts."""
        artifacts = self.checker.identify_candidate_artifacts()
        self.stage_outputs["stage_1"] = artifacts
        return artifacts

    def stage_2_validate_structure(
        self, artifacts: List[CandidateArtifact]
    ) -> List[ValidationResult]:
        """Stage 2: Validate artifact structure (UD-Bounded)."""
        results = []
        counter = BoundedCounter(max_steps=_MAX_AUDIT_ARTIFACTS)
        for artifact in artifacts:
            counter.step()
            result = self.checker.validate_artifact_structure(artifact)
            results.append(result)
        self.stage_outputs["stage_2"] = results
        return results

    def stage_3_cross_check_repo(
        self, artifact_commit_hash: Optional[str] = None
    ) -> CrossCheckResult:
        """Stage 3: Cross-check with repository."""
        result = self.checker.cross_check_with_repository(artifact_commit_hash)
        self.stage_outputs["stage_3"] = result
        return result

    def stage_4_generate_report(
        self,
        artifacts: List[CandidateArtifact],
        validation_results: List[ValidationResult],
        cross_check_results: Optional[CrossCheckResult] = None,
    ) -> OnboardingReport:
        """Stage 4: Generate report."""
        report = self.checker.generate_report(
            artifacts, validation_results, cross_check_results
        )
        self.stage_outputs["stage_4"] = report
        return report

    def run_pipeline(self) -> OnboardingReport:
        """Run the complete pipeline."""
        print("Running CheckOnboarding pipeline...")

        # Stage 1
        print("  Stage 1: Identifying candidate artifacts")
        artifacts = self.stage_1_identify_candidate_artifacts()

        # Stage 2
        print("  Stage 2: Validating artifact structure")
        validation_results = self.stage_2_validate_structure(artifacts)

        # Stage 3
        print("  Stage 3: Cross-checking with repository")
        cross_check_results = None
        if artifacts:
            artifact_with_hash = next((a for a in artifacts if a.commit_hash), None)
            cross_check_results = self.stage_3_cross_check_repo(
                artifact_with_hash.commit_hash if artifact_with_hash else None
            )

        # Stage 4
        print("  Stage 4: Generating report")
        report = self.stage_4_generate_report(
            artifacts, validation_results, cross_check_results
        )

        print(f"\nPipeline complete. Status: {report.status.value.upper()}")
        return report

    def save_stage_outputs(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Save all stage outputs to files for debugging or chaining.

        Args:
            output_dir: Directory to save outputs. If None, uses default.

        Returns:
            Dictionary mapping stage names to output file paths.
        """
        if output_dir is None:
            output_dir = self.checker.repository_root / "logs" / "pipeline_stages"

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        for stage_name, output in self.stage_outputs.items():
            output_path = (
                output_dir
                / f"{stage_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            if isinstance(output, list):
                # Convert list of objects to list of dicts
                if output and hasattr(output[0], "to_dict"):
                    data = [item.to_dict() for item in output]
                else:
                    data = [asdict(item) if is_dataclass(item) else item for item in output]
            elif hasattr(output, "to_dict"):
                data = output.to_dict()
            elif hasattr(output, "__dict__"):
                data = asdict(output) if is_dataclass(output) else vars(output)
            else:
                data = output

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False,
                          default=lambda o: o.value if isinstance(o, Enum) else str(o))

            saved_files[stage_name] = str(output_path)

        return saved_files


# Command-line interface
def main():
    """Command-line entry point for onboarding check."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check onboarding status for IDE-AI integration"
    )
    parser.add_argument(
        "--repository",
        "-r",
        type=str,
        help="Repository root path (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path for report (default: auto-generated)",
    )
    parser.add_argument(
        "--pipeline",
        "-p",
        action="store_true",
        help="Use pipeline form with stage outputs",
    )
    parser.add_argument(
        "--save-stages",
        action="store_true",
        help="Save stage outputs when using pipeline form",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        if args.pipeline:
            # Use pipeline form
            pipeline = CheckOnboardingPipeline(args.repository)
            report = pipeline.run_pipeline()

            if args.save_stages:
                saved_files = pipeline.save_stage_outputs()
                if args.verbose:
                    print("\nSaved stage outputs:")
                    for stage, path in saved_files.items():
                        print(f"  {stage}: {path}")
        else:
            # Use direct form
            checker = OnboardingChecker(args.repository)
            report = checker.run_full_check()

        # Save report
        if args.output or not args.pipeline:
            output_path = args.output
            if not output_path and hasattr(checker, "save_report"):
                output_path = checker.save_report()
            elif not output_path and hasattr(pipeline, "checker"):
                output_path = pipeline.checker.save_report()

            if output_path:
                print(f"\nReport saved to: {output_path}")

        # Exit with appropriate code
        if report.status == OnboardingStatus.FULL:
            print("\n✅ Onboarding status: FULL - All artifacts verified")
            sys.exit(0)
        elif report.status == OnboardingStatus.PARTIAL:
            print(
                "\n⚠️  Onboarding status: PARTIAL - Some artifacts missing or incomplete"
            )
            sys.exit(1)
        else:
            print(
                "\n❌ Onboarding status: ABSENT - No valid onboarding artifacts found"
            )
            sys.exit(2)

    except Exception as e:
        print(f"\n❌ Error during onboarding check: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
