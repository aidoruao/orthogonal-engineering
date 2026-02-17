"""
Unit tests for logger module.

Tests JSONL logging with monotonic step_id and ISO8601 timestamps.
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scaffold.logger import ScaffoldLogger


class TestLogger(unittest.TestCase):
    """Test cases for logger module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.logger = ScaffoldLogger(log_dir=self.test_path)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test logger initialization."""
        self.assertTrue(self.test_path.exists())
        self.assertEqual(self.logger.get_handling_steps(), 0)
        self.assertEqual(self.logger.get_verification_steps(), 0)
    
    def test_log_handling_step(self):
        """Test logging handling pipeline steps."""
        step_id = self.logger.log_handling_step(
            action="test_action",
            details={"key": "value"}
        )
        
        self.assertEqual(step_id, 1)
        self.assertEqual(self.logger.get_handling_steps(), 1)
        
        # Check log file was created
        self.assertTrue(self.logger.handling_pipeline_log.exists())
        
        # Read and verify log entry
        entries = self.logger.read_handling_log()
        self.assertEqual(len(entries), 1)
        
        entry = entries[0]
        self.assertEqual(entry['step_id'], 1)
        self.assertEqual(entry['pipeline'], 'handling')
        self.assertEqual(entry['action'], 'test_action')
        self.assertEqual(entry['status'], 'success')
        self.assertEqual(entry['details']['key'], 'value')
        
        # Check timestamp format (ISO8601)
        timestamp = entry['timestamp']
        # Should be parseable as ISO8601
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_log_verification_step(self):
        """Test logging verification pipeline steps."""
        step_id = self.logger.log_verification_step(
            action="verify_test",
            details={"verified": True}
        )
        
        self.assertEqual(step_id, 1)
        self.assertEqual(self.logger.get_verification_steps(), 1)
        
        # Check log file
        entries = self.logger.read_verification_log()
        self.assertEqual(len(entries), 1)
        
        entry = entries[0]
        self.assertEqual(entry['pipeline'], 'verification')
        self.assertEqual(entry['action'], 'verify_test')
    
    def test_monotonic_step_ids(self):
        """Test that step IDs are monotonically increasing."""
        for i in range(5):
            step_id = self.logger.log_handling_step(
                action=f"step_{i}",
                details={"index": i}
            )
            self.assertEqual(step_id, i + 1)
        
        # Verify all steps
        entries = self.logger.read_handling_log()
        self.assertEqual(len(entries), 5)
        
        # Check monotonic IDs
        for i, entry in enumerate(entries):
            self.assertEqual(entry['step_id'], i + 1)
    
    def test_separate_pipelines(self):
        """Test that handling and verification pipelines are separate."""
        self.logger.log_handling_step("handling_1", {})
        self.logger.log_verification_step("verification_1", {})
        self.logger.log_handling_step("handling_2", {})
        
        self.assertEqual(self.logger.get_handling_steps(), 2)
        self.assertEqual(self.logger.get_verification_steps(), 1)
    
    def test_log_error(self):
        """Test error logging."""
        self.logger.log_error(
            pipeline="handling",
            error="Test error message",
            details={"context": "test"}
        )
        
        entries = self.logger.read_handling_log()
        self.assertEqual(len(entries), 1)
        
        entry = entries[0]
        self.assertEqual(entry['status'], 'error')
        self.assertEqual(entry['details']['error'], 'Test error message')
        self.assertEqual(entry['details']['context'], 'test')
    
    def test_reset_counters(self):
        """Test resetting step counters."""
        self.logger.log_handling_step("test", {})
        self.logger.log_verification_step("test", {})
        
        self.assertEqual(self.logger.get_handling_steps(), 1)
        self.assertEqual(self.logger.get_verification_steps(), 1)
        
        self.logger.reset_counters()
        
        self.assertEqual(self.logger.get_handling_steps(), 0)
        self.assertEqual(self.logger.get_verification_steps(), 0)
    
    def test_jsonl_format(self):
        """Test that logs are in valid JSONL format."""
        # Log multiple entries
        for i in range(3):
            self.logger.log_handling_step(f"action_{i}", {"index": i})
        
        # Read file directly
        with open(self.logger.handling_pipeline_log, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 3)
        
        # Each line should be valid JSON
        for line in lines:
            data = json.loads(line)
            self.assertIn('step_id', data)
            self.assertIn('timestamp', data)
            self.assertIn('action', data)


if __name__ == '__main__':
    unittest.main()
