"""
Unit tests for AlphaOmegaFinalizer.

Tests the alpha-omega verification process for content integrity.
"""

import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.alpha_omega_finalizer import AlphaOmegaFinalizer


class TestAlphaOmegaFinalizer(unittest.TestCase):
    """Test cases for AlphaOmegaFinalizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test files
        self.test_file1 = self.temp_path / "test1.txt"
        self.test_file1.write_text("Test content 1")
        
        self.test_file2 = self.temp_path / "test2.txt"
        self.test_file2.write_text("Test content 2")
        
        self.finalizer = AlphaOmegaFinalizer(name="test")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_alpha_phase_captures_state(self):
        """Test that alpha phase captures initial state."""
        files = [self.test_file1, self.test_file2]
        alpha_state = self.finalizer.alpha(files)
        
        self.assertIsNotNone(alpha_state)
        self.assertEqual(alpha_state["phase"], "alpha")
        self.assertEqual(len(alpha_state["files"]), 2)
        self.assertIsNotNone(alpha_state["merkle_root"])
        
        # Check file states
        for file_state in alpha_state["files"]:
            self.assertTrue(file_state["exists"])
            self.assertIn("hash", file_state)
            self.assertIn("size", file_state)
    
    def test_omega_phase_verifies_unchanged_content(self):
        """Test that omega phase verifies unchanged content."""
        files = [self.test_file1, self.test_file2]
        
        # Alpha phase
        self.finalizer.alpha(files)
        
        # Omega phase (no changes)
        omega_state = self.finalizer.omega(verify=True)
        
        self.assertIsNotNone(omega_state)
        self.assertEqual(omega_state["phase"], "omega")
        self.assertTrue(omega_state["verification"]["verified"])
        self.assertEqual(len(omega_state["verification"]["issues"]), 0)
    
    def test_omega_detects_content_changes(self):
        """Test that omega phase detects content changes."""
        files = [self.test_file1, self.test_file2]
        
        # Alpha phase
        self.finalizer.alpha(files)
        
        # Modify file
        self.test_file1.write_text("Modified content")
        
        # Omega phase
        omega_state = self.finalizer.omega(verify=True)
        
        self.assertFalse(omega_state["verification"]["verified"])
        self.assertGreater(len(omega_state["verification"]["issues"]), 0)
    
    def test_omega_detects_missing_files(self):
        """Test that omega phase detects missing files."""
        files = [self.test_file1, self.test_file2]
        
        # Alpha phase
        self.finalizer.alpha(files)
        
        # Delete file
        self.test_file1.unlink()
        
        # Omega phase
        omega_state = self.finalizer.omega(verify=True)
        
        self.assertFalse(omega_state["verification"]["verified"])
        self.assertTrue(
            any("Existence changed" in issue or "missing" in issue.lower() 
                for issue in omega_state["verification"]["issues"])
        )
    
    def test_alpha_handles_missing_files(self):
        """Test that alpha phase handles missing files gracefully."""
        nonexistent = self.temp_path / "nonexistent.txt"
        files = [self.test_file1, nonexistent]
        
        alpha_state = self.finalizer.alpha(files)
        
        self.assertEqual(len(alpha_state["files"]), 2)
        
        # Check that nonexistent file is marked as not existing
        file_states = {fs["path"]: fs for fs in alpha_state["files"]}
        self.assertFalse(file_states[str(nonexistent)]["exists"])
        self.assertTrue(file_states[str(self.test_file1)]["exists"])
    
    def test_merkle_root_consistency(self):
        """Test that merkle root is consistent for unchanged files."""
        files = [self.test_file1, self.test_file2]
        
        # First finalization
        finalizer1 = AlphaOmegaFinalizer(name="test1")
        alpha1 = finalizer1.alpha(files)
        
        # Second finalization
        finalizer2 = AlphaOmegaFinalizer(name="test2")
        alpha2 = finalizer2.alpha(files)
        
        # Merkle roots should match
        self.assertEqual(alpha1["merkle_root"], alpha2["merkle_root"])
    
    def test_report_generation(self):
        """Test that report generation works."""
        files = [self.test_file1, self.test_file2]
        
        self.finalizer.alpha(files)
        self.finalizer.omega(verify=True)
        
        report = self.finalizer.get_report()
        
        self.assertIn("alpha", report)
        self.assertIn("omega", report)
        self.assertIn("name", report)
    
    def test_report_saving(self):
        """Test that report can be saved to file."""
        files = [self.test_file1, self.test_file2]
        
        self.finalizer.alpha(files)
        self.finalizer.omega(verify=True)
        
        report_path = self.temp_path / "report.json"
        self.finalizer.save_report(report_path)
        
        self.assertTrue(report_path.exists())
        
        # Verify report content
        with open(report_path, 'r') as f:
            saved_report = json.load(f)
        
        self.assertIn("alpha", saved_report)
        self.assertIn("omega", saved_report)
    
    def test_omega_requires_alpha(self):
        """Test that omega phase requires alpha phase to run first."""
        with self.assertRaises(RuntimeError):
            self.finalizer.omega()
    
    def test_metadata_preservation(self):
        """Test that metadata is preserved in alpha state."""
        files = [self.test_file1]
        metadata = {"test_key": "test_value", "number": 42}
        
        alpha_state = self.finalizer.alpha(files, metadata=metadata)
        
        self.assertEqual(alpha_state["metadata"], metadata)


if __name__ == "__main__":
    unittest.main()
