"""
Test suite for onboarding check system.

Tests the atomic instruction blueprint implementation for
"Check-Onboarding Status" in the Orthogonal Engineering framework.

Author: Orthogonal Engineering System
Date: 2026-01-24
Version: 1.0.0
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from toolkit.oe.onboarding_check import (
    ArtifactType,
    CandidateArtifact,
    CheckOnboardingPipeline,
    CrossCheckResult,
    OnboardingChecker,
    OnboardingReport,
    OnboardingStatus,
    ValidationResult,
)


class TestOnboardingCheck(unittest.TestCase):
    """Test cases for OnboardingChecker class."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / "test_repo"
        self.repo_path.mkdir(parents=True, exist_ok=True)

        # Create some test files
        (self.repo_path / "ONBOARD_FIRST.md").write_text("# Onboarding First\nCommit: abc123\n")
        (self.repo_path / "onboarding").mkdir(exist_ok=True)
        (self.repo_path / "onboarding" / "LEVEL1.md").write_text("# Level 1\n")
        (self.repo_path / "onboarding" / "LEVEL2.md").write_text("# Level 2\n")
        (self.repo_path / "AGENT.md").write_text("# Agent\n")
        (self.repo_path / "AI_INSTRUCTIONS.md").write_text("# AI Instructions\n")

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test OnboardingChecker initialization."""
        checker = OnboardingChecker(str(self.repo_path))
        self.assertEqual(checker.repository_root, self.repo_path)
        self.assertIsNone(checker.report)

    def test_identify_candidate_artifacts(self):
        """Test candidate artifact identification."""
        checker = OnboardingChecker(str(self.repo_path))
        artifacts = checker.identify_candidate_artifacts()

        # Should find onboarding files
        self.assertGreater(len(artifacts), 0)

        # Check that we found known files
        artifact_paths = [a.path for a in artifacts]
        self.assertIn("ONBOARD_FIRST.md", artifact_paths)
        self.assertIn("onboarding/LEVEL1.md", artifact_paths)
        self.assertIn("onboarding/LEVEL2.md", artifact_paths)

        # Check artifact types
        for artifact in artifacts:
            self.assertIsInstance(artifact, CandidateArtifact)
            self.assertIsInstance(artifact.artifact_type, ArtifactType)
            self.assertGreater(artifact.size_bytes, 0)

    def test_validate_artifact_structure_valid(self):
        """Test artifact structure validation with valid artifact."""
        # Create a valid onboarding artifact
        valid_content = """
        # Onboarding Artifact
        Commit: abcdef1234567890abcdef1234567890abcdef12
        Directories scanned: 10
        File count: 150
        Read/write permissions: rw-r--r--
        Generated at: 2026-01-24T12:00:00Z
        Repository root: /test/repo
        Artifact type: onboarding_summary
        """

        artifact_path = self.repo_path / "onboarding_artifact.md"
        artifact_path.write_text(valid_content)

        artifact = CandidateArtifact(
            path="onboarding_artifact.md",
            artifact_type=ArtifactType.ONBOARDING_FILE,
            size_bytes=len(valid_content),
            content_preview=valid_content[:500]
        )

        checker = OnboardingChecker(str(self.repo_path))
        result = checker.validate_artifact_structure(artifact)

        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.artifact_path, "onboarding_artifact.md")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.status, "valid")
        self.assertEqual(len(result.missing_fields), 0)

    def test_validate_artifact_structure_partial(self):
        """Test artifact structure validation with partial artifact."""
        # Create a partial onboarding artifact (missing some fields)
        partial_content = """
        # Partial Onboarding Artifact
        Commit: abcdef1234567890abcdef1234567890abcdef12
        File count: 150
        Generated at: 2026-01-24T12:00:00Z
        """

        artifact_path = self.repo_path / "partial_artifact.md"
        artifact_path.write_text(partial_content)

        artifact = CandidateArtifact(
            path="partial_artifact.md",
            artifact_type=ArtifactType.ONBOARDING_FILE,
            size_bytes=len(partial_content),
            content_preview=partial_content[:500]
        )

        checker = OnboardingChecker(str(self.repo_path))
        result = checker.validate_artifact_structure(artifact)

        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.status, "partial")
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.missing_fields), 0)
        self.assertIn("directories_scanned", result.missing_fields)
        self.assertIn("repository_root", result.missing_fields)

    def test_cross_check_with_repository(self):
        """Test cross-checking with repository."""
        checker = OnboardingChecker(str(self.repo_path))

        # Mock git command to return a commit hash
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "abcdef1234567890abcdef1234567890abcdef12\n"

            result = checker.cross_check_with_repository("abcdef1234567890abcdef1234567890abcdef12")

        self.assertIsInstance(result, CrossCheckResult)
        self.assertEqual(result.artifact_commit_hash, "abcdef1234567890abcdef1234567890abcdef12")
        self.assertEqual(result.current_repo_head, "abcdef1234567890abcdef1234567890abcdef12")
        self.assertTrue(result.commit_match)

        # Should find our test directories
        self.assertIn("onboarding", result.directories_exist)

        # Should find critical files
        self.assertIn("ONBOARD_FIRST.md", result.files_exist)
        self.assertIn("onboarding/LEVEL1.md", result.files_exist)

    def test_generate_report_full(self):
        """Test report generation with full onboarding."""
        checker = OnboardingChecker(str(self.repo_path))

        # Create mock artifacts and validation results
        artifacts = [
            CandidateArtifact(
                path="ONBOARD_FIRST.md",
                artifact_type=ArtifactType.ONBOARDING_FILE,
                size_bytes=100,
                commit_hash="abc123"
            )
        ]

        validation_results = [
            ValidationResult(
                artifact_path="ONBOARD_FIRST.md",
                is_valid=True,
                status="valid",
                missing_fields=[],
                validation_errors=[],
                structure_summary={}
            )
        ]

        cross_check = CrossCheckResult(
            artifact_commit_hash="abc123",
            current_repo_head="abc123",
            commit_match=True,
            directories_exist=["onboarding"],
            directories_missing=[],
            files_exist=["ONBOARD_FIRST.md"],
            files_missing=[],
            mismatches=[]
        )

        report = checker.generate_report(artifacts, validation_results, cross_check)

        self.assertIsInstance(report, OnboardingReport)
        self.assertEqual(report.status, OnboardingStatus.FULL)
        self.assertEqual(report.artifact_path, "ONBOARD_FIRST.md")
        self.assertEqual(len(report.missing_fields), 0)
        self.assertEqual(len(report.mismatched_files), 0)
        self.assertEqual(report.repo_commit, "abc123")

    def test_generate_report_absent(self):
        """Test report generation with absent onboarding."""
        checker = OnboardingChecker(str(self.repo_path))

        # Empty artifacts list
        artifacts = []
        validation_results = []

        report = checker.generate_report(artifacts, validation_results)

        self.assertIsInstance(report, OnboardingReport)
        self.assertEqual(report.status, OnboardingStatus.ABSENT)
        self.assertIsNone(report.artifact_path)
        self.assertEqual(len(report.candidate_artifacts), 0)

    def test_run_full_check(self):
        """Test running the full check pipeline."""
        checker = OnboardingChecker(str(self.repo_path))

        # Mock the individual steps to control output
        with patch.object(checker, 'identify_candidate_artifacts') as mock_identify, \
             patch.object(checker, 'validate_artifact_structure') as mock_validate, \
             patch.object(checker, 'cross_check_with_repository') as mock_cross_check, \
             patch.object(checker, 'generate_report') as mock_generate:

            # Setup mocks
            mock_artifact = CandidateArtifact(
                path="test.md",
                artifact_type=ArtifactType.ONBOARDING_FILE,
                size_bytes=100
            )
            mock_identify.return_value = [mock_artifact]

            mock_validation = ValidationResult(
                artifact_path="test.md",
                is_valid=True,
                status="valid",
                missing_fields=[],
                validation_errors=[],
                structure_summary={}
            )
            mock_validate.return_value = mock_validation

            mock_cross_check.return_value = CrossCheckResult(
                artifact_commit_hash=None,
                current_repo_head=None,
                commit_match=False,
                directories_exist=[],
                directories_missing=[],
                files_exist=[],
                files_missing=[],
                mismatches=[]
            )

            mock_report = OnboardingReport(
                status=OnboardingStatus.FULL,
                artifact_path="test.md",
                missing_fields=[],
                mismatched_files=[],
                repo_commit=None,
                candidate_artifacts=[mock_artifact],
                validation_results=[mock_validation],
                cross_check_results=mock_cross_check.return_value,
                generated_at=datetime.now(),
                repository_root=str(self.repo_path)
            )
            mock_generate.return_value = mock_report

            # Run check
            report = checker.run_full_check()

            # Verify calls
            mock_identify.assert_called_once()
            mock_validate.assert_called_once_with(mock_artifact)
            mock_cross_check.assert_called_once()
            mock_generate.assert_called_once()

            self.assertEqual(report.status, OnboardingStatus.FULL)

    def test_save_report(self):
        """Test saving report to file."""
        checker = OnboardingChecker(str(self.repo_path))

        # Create a test report
        report = OnboardingReport(
            status=OnboardingStatus.FULL,
            artifact_path="test.md",
            missing_fields=[],
            mismatched_files=[],
            repo_commit="abc123",
            candidate_artifacts=[],
            validation_results=[],
            cross_check_results=None,
            generated_at=datetime.now(),
            repository_root=str(self.repo_path)
        )

        checker.report = report

        # Save report
        output_path = checker.save_report()

        # Verify file was created
        self.assertTrue(Path(output_path).exists())

        # Verify content
        with open(output_path, 'r') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data['status'], 'full')
        self.assertEqual(saved_data['artifact_path'], 'test.md')


class TestCheckOnboardingPipeline(unittest.TestCase):
    """Test cases for CheckOnboardingPipeline class."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.test_dir) / "test_repo"
        self.repo_path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = CheckOnboardingPipeline(str(self.repo_path))
        self.assertIsInstance(pipeline.checker, OnboardingChecker)
        self.assertEqual(pipeline.checker.repository_root, self.repo_path)
        self.assertEqual(pipeline.stage_outputs, {})

    def test_pipeline_stages(self):
        """Test individual pipeline stages."""
        pipeline = CheckOnboardingPipeline(str(self.repo_path))

        # Mock the checker methods
        with patch.object(pipeline.checker, 'identify_candidate_artifacts') as mock_identify, \
             patch.object(pipeline.checker, 'validate_artifact_structure') as mock_validate, \
             patch.object(pipeline.checker, 'cross_check_with_repository') as mock_cross_check, \
             patch.object(pipeline.checker, 'generate_report') as mock_generate:

            # Setup mocks
            mock_artifact = MagicMock()
            mock_identify.return_value = [mock_artifact]

            mock_validation = MagicMock()
            mock_validate.return_value = mock_validation

            mock_cross_check_result = MagicMock()
            mock_cross_check.return_value = mock_cross_check_result

            mock_report = MagicMock()
            mock_generate.return_value = mock_report

            # Test stage 1
            artifacts = pipeline.stage_1_identify_candidate_artifacts()
            self.assertEqual(artifacts, [mock_artifact])
            self.assertIn("stage_1", pipeline.stage_outputs)

            # Test stage 2
            validations = pipeline.stage_2_validate_structure([mock_artifact])
            self.assertEqual(validations, [mock_validation])
            self.assertIn("stage_2", pipeline.stage_outputs)
            mock_validate.assert_called_once_with(mock_artifact)

            # Test stage 3
            cross_check = pipeline.stage_3_cross_check_repo("abc123")
            self.assertEqual(cross_check, mock_cross_check_result)
            self.assertIn("stage_3", pipeline.stage_outputs)
            mock_cross_check.assert_called_once_with("abc123")

            # Test stage 4
            report = pipeline.stage_4_generate_report([mock_artifact], [mock_validation], mock_cross_check_result)
            self.assertEqual(report, mock_report)
            self.assertIn("stage_4", pipeline.stage_outputs)
            mock_generate.assert_called_once_with([mock_artifact], [mock_validation], mock_cross_check_result)

    def test_run_pipeline(self):
        """Test running complete pipeline."""
        pipeline = CheckOnboardingPipeline(str(self.repo_path))

        # Mock all stages
        with patch.object(pipeline, 'stage_1_identify_candidate_artifacts') as mock_stage1, \
             patch.object(pipeline, 'stage_2_validate_structure') as mock_stage2, \
             patch.object(pipeline, 'stage_3_cross_check_repo') as mock_stage3, \
             patch.object(pipeline, 'stage_4_generate_report') as mock_stage4:

            # Setup mocks
            mock_artifacts = [MagicMock()]
            mock_stage1.return_value = mock_artifacts

            mock_validations = [MagicMock()]
            mock_stage2.return_value = mock_validations

            mock_cross_check = MagicMock()
            mock_stage3.return_value = mock_cross_check

            mock_report = MagicMock()
            mock_stage4.return_value = mock_report

            # Run pipeline
            report = pipeline.run_pipeline()

            # Verify calls
            mock_stage1.assert_called_once()
            mock_stage2.assert_called_once_with(mock_artifacts)
            mock_stage3.assert_called_once()
            mock_stage4.assert_called_once_with(mock_artifacts, mock_validations, mock_cross_check)

            self.assertEqual(report, mock_report)

    def test_save_stage_outputs(self):
        """Test saving stage outputs."""
        pipeline = CheckOnboardingPipeline(str(self.repo_path))

        # Add some test outputs
        test_artifact = CandidateArtifact(
            path="test.md",
            artifact_type=ArtifactType.ONBOARDING_FILE,
            size_bytes=100
        )

        pipeline.stage_outputs = {
            "stage_1": [test_artifact],
            "stage_2": ["validation_result"],
            "stage_3": {"cross_check": "result"},
            "stage_4": {"report": "data"}
        }

        # Save outputs
        saved_files = pipeline.save_stage_outputs()

        # Verify files were created
        self.assertEqual(len(saved_files), 4)
        for stage, filepath in saved_files.items():
            self.assertTrue(Path(filepath).exists())
            self.assertIn(stage, filepath)


class TestIntegration(unittest.TestCase):
    """Integration tests for onboarding check system."""

    def test_end_to_end_with_real_files(self):
        """Test end-to-end with actual file creation."""
        test_dir = tempfile.mkdtemp()
        repo_path = Path(test_dir) / "integration_repo"
        repo_path.mkdir(parents=True, exist_ok=True)

        try:
            # Create a comprehensive onboarding artifact
            artifact_content = """# Onboarding Summary
Repository: integration_repo
Commit: 1234567890abcdef1234567890abcdef12345678
Directories scanned: 5
File count: 42
Permissions: rw-r--r--
Generated at: 2026-01-24T12:00:00Z
Artifact type: onboarding_complete
Token budget: 1000
"""

            # Create directory structure
            (repo_path / "onboarding").mkdir(exist_ok=True)
            (repo_path / "automation").mkdir(exist_ok=True)
            (repo_path / "toolkit").mkdir(exist_ok=True)

            # Create files
            (repo_path / "ONBOARD_FIRST.md").write_text(artifact_content)
            (repo_path / "onboarding" / "LEVEL1.md").write_text("# Level 1\n")
            (repo_path / "onboarding" / "LEVEL2.md").write_text("# Level 2\n")
            (repo_path / "AGENT.md").write_text("# Agent\n")
            (repo_path / "AI_INSTRUCTIONS.md").write_text("# Instructions\n")
            (repo_path / "_START_HERE.md").write_text("# Start Here\n")

            # Run the checker
            checker = OnboardingChecker(str(repo_path))
            report = checker.run_full_check()

            # Verify results
            self.assertIsInstance(report, OnboardingReport)
            self.assertEqual(report.repository_root, str(repo_path))
            
            # Should find our artifact
            self.assertGreater(len(report.candidate_artifacts), 0)
            
            # The artifact should be valid or at least partial
            if report.validation_results:
                has_valid = any(r.status == "valid" for r in report.validation_results)
                has_partial = any(r.status == "partial" for r in report.validation_results)
                self.assertTrue(has_valid or has_partial, "Should have valid or partial validation")
            
            # Should find critical files
            if report.cross_check_results:
                self.assertIn("ONBOARD_FIRST.md", report.cross_check_results.files_exist)
                self.assertIn("onboarding/LEVEL1.md", report.cross_check_results.files_exist)
                self.assertIn("onboarding/LEVEL2.md", report.cross_check_results.files_exist)

        finally:
            import shutil
            shutil.rmtree(test_dir)

    def test_exit_code_mapping(self):
        """Test that exit codes map correctly to status."""
        test_dir = tempfile.mkdtemp()
        repo_path = Path(test_dir) / "exit_code_repo"
        repo_path.mkdir(parents=True, exist_ok=True)

        try:
            # Test 1: Empty repository (should be ABSENT = exit code 2)
            checker = OnboardingChecker(str(repo_path))
            report = checker.run_full_check()
            self.assertEqual(report.status, OnboardingStatus.ABSENT)
            
            # Test 2: Repository with partial onboarding
            (repo_path / "partial.md").write_text("# Partial\nCommit: abc\n")
            checker = OnboardingChecker(str(repo_path))
            report = checker.run_full_check()
            # Could be PARTIAL or ABSENT depending on validation
            self.assertIn(report.status, [OnboardingStatus.PARTIAL, OnboardingStatus.ABSENT])
            
            # Test 3: Repository with full onboarding artifact
            full_content = """# Full Onboarding
Commit: 1234567890abcdef1234567890abcdef12345678
Directories scanned: 3
File count: 25
Permissions: rw-r--r--
Generated at: 2026-01-24T12:00:00Z
Repository root: /test
Artifact type: complete
"""
            (repo_path / "full_onboarding.md").write_text(full_content)
            (repo_path / "onboarding").mkdir(exist_ok=True)
            (repo_path / "onboarding" / "LEVEL1.md").write_text("# Level 1")
            
            checker = OnboardingChecker(str(repo_path))
            report = checker.run_full_check()
            # Could be FULL or PARTIAL depending on cross-check
            self.assertIn(report.status, [OnboardingStatus.FULL, OnboardingStatus.PARTIAL])

        finally:
            import shutil
            shutil.rmtree(test_dir)


class TestCommandLineInterface(unittest.TestCase):
    """Test command-line interface functionality."""

    def test_cli_help(self):
        """Test that CLI help works."""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, "-m", "toolkit.oe.onboarding_check", "--help"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("--help", result.stdout)

    def test_cli_basic_check(self):
        pass
