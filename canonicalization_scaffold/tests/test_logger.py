"""
Unit tests for logger module
"""

import json
import tempfile
import unittest
from pathlib import Path

from canonicalization_scaffold.logger import (
    JSONLLogger,
    create_hello_world_logger,
    create_verification_logger,
)


class TestJSONLLogger(unittest.TestCase):
    """Test cases for JSONLLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_logger(self):
        """Test creating a logger."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        self.assertEqual(logger.output_dir, self.temp_path)
        self.assertEqual(logger.log_name, "test_log")
        self.assertIsNotNone(logger.session_id)
    
    def test_log_creates_file(self):
        """Test that logging creates output file."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        logger.log("test_event", {"key": "value"})
        
        log_file = self.temp_path / "test_log.jsonl"
        self.assertTrue(log_file.exists())
    
    def test_log_format(self):
        """Test log record format."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        logger.log("test_event", {"key": "value"}, step_id="step123")
        
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            line = f.readline()
        
        record = json.loads(line)
        
        # Check required fields
        self.assertIn("timestamp", record)
        self.assertIn("session_id", record)
        self.assertIn("step_id", record)
        self.assertIn("event_type", record)
        
        # Check values
        self.assertEqual(record["event_type"], "test_event")
        self.assertEqual(record["step_id"], "step123")
        self.assertEqual(record["key"], "value")
    
    def test_log_timestamp_format(self):
        """Test that timestamp is ISO8601 format."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        logger.log("test_event", {})
        
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            record = json.loads(f.readline())
        
        timestamp = record["timestamp"]
        
        # Should be ISO8601 format
        from datetime import datetime
        # This will raise ValueError if not valid ISO format
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    def test_log_auto_step_id(self):
        """Test automatic step ID generation."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        logger.log("test_event", {})
        
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            record = json.loads(f.readline())
        
        # Should have auto-generated step_id
        self.assertIn("step_id", record)
        self.assertIsNotNone(record["step_id"])
    
    def test_start_operation(self):
        """Test start_operation method."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        step_id = logger.start_operation("my_operation", param1="value1")
        
        # Should return a step_id
        self.assertIsNotNone(step_id)
        
        # Check log record
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record["event_type"], "start")
        self.assertEqual(record["operation"], "my_operation")
        self.assertEqual(record["param1"], "value1")
        self.assertEqual(record["step_id"], step_id)
    
    def test_complete_operation(self):
        """Test complete_operation method."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        step_id = logger.start_operation("my_operation")
        logger.complete_operation(step_id, "my_operation", result="success")
        
        # Check log records
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Should have 2 records
        self.assertEqual(len(lines), 2)
        
        # Check complete record
        complete_record = json.loads(lines[1])
        self.assertEqual(complete_record["event_type"], "complete")
        self.assertEqual(complete_record["operation"], "my_operation")
        self.assertEqual(complete_record["result"], "success")
        self.assertEqual(complete_record["step_id"], step_id)
    
    def test_error_operation(self):
        """Test error_operation method."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        step_id = logger.start_operation("my_operation")
        logger.error_operation(step_id, "my_operation", "Something went wrong")
        
        # Check log records
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Check error record
        error_record = json.loads(lines[1])
        self.assertEqual(error_record["event_type"], "error")
        self.assertEqual(error_record["operation"], "my_operation")
        self.assertEqual(error_record["error"], "Something went wrong")
    
    def test_multiple_logs(self):
        """Test logging multiple events."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        logger.log("event1", {"data": 1})
        logger.log("event2", {"data": 2})
        logger.log("event3", {"data": 3})
        
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Should have 3 records
        self.assertEqual(len(lines), 3)
        
        # Each should be valid JSON
        for line in lines:
            record = json.loads(line)
            self.assertIn("event_type", record)
    
    def test_unicode_logging(self):
        """Test logging with Unicode characters."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        logger.log("test_event", {"message": "Hello 世界 🌍"})
        
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r', encoding='utf-8') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record["message"], "Hello 世界 🌍")
    
    def test_session_id_consistency(self):
        """Test that session_id is consistent across logs."""
        logger = JSONLLogger(self.temp_path, "test_log")
        
        logger.log("event1", {})
        logger.log("event2", {})
        
        log_file = self.temp_path / "test_log.jsonl"
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        record1 = json.loads(lines[0])
        record2 = json.loads(lines[1])
        
        # Should have same session_id
        self.assertEqual(record1["session_id"], record2["session_id"])


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions for logger creation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_create_hello_world_logger(self):
        """Test creating hello world logger."""
        logger = create_hello_world_logger(self.temp_path)
        
        self.assertIsInstance(logger, JSONLLogger)
        self.assertEqual(logger.log_name, "hello_world_handling_pipeline")
        
        # Should have init log
        log_file = self.temp_path / "hello_world_handling_pipeline.jsonl"
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r') as f:
            record = json.loads(f.readline())
        
        self.assertEqual(record["event_type"], "init")
        self.assertIn("message", record)
    
    def test_create_verification_logger(self):
        """Test creating verification logger."""
        logger = create_verification_logger(self.temp_path)
        
        self.assertIsInstance(logger, JSONLLogger)
        self.assertEqual(logger.log_name, "handling_verification_pipeline")
        
        # Should have init log
        log_file = self.temp_path / "handling_verification_pipeline.jsonl"
        self.assertTrue(log_file.exists())


if __name__ == '__main__':
    unittest.main()
