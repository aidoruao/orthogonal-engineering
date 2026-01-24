# COMPLETE PYTHON TEST FILE: test_glass_box_boundary.py

## File: automation/test_glass_box_boundary.py
## Purpose: Glass Box Boundary enforcer test suite
## Lines: 384 total
## Status: Operational test suite with intentional failures

```python
#!/usr/bin/env python3
"""
GLASS BOX BOUNDARY ENFORCER TEST SUITE

Tests the Glass Box Boundary enforcement system as defined in:
documentation/GLASS_BOX_BOUNDARY_v1.11.html

Exit codes:
- 0: All tests passed
- 2: Boundary violations detected (intentional fail-fast)
"""

import sys
import os
import json
import subprocess
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the boundary decorator from the enforcer
try:
    from automation.run_full_audit_with_trace import (
        glass_box_boundary,
        BoundaryViolation,
        generate_trace,
        validate_trace
    )
    BOUNDARY_IMPORT_SUCCESS = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import boundary enforcer: {e}")
    BOUNDARY_IMPORT_SUCCESS = False


class TestResult:
    """Container for test results."""
    
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
    
    def __str__(self) -> str:
        status = "✓" if self.passed else "✗"
        return f"  {status} {self.name} {'passed' if self.passed else 'failed'}{': ' + self.message if self.message else ''}"


class TestSuite:
    """Main test suite class."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
    
    def add_result(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)
        self.test_count += 1
        if result.passed:
            self.pass_count += 1
        else:
            self.fail_count += 1
    
    def run_test(self, name: str, test_func, *args, **kwargs) -> bool:
        """Run a test and record the result."""
        try:
            passed, message = test_func(*args, **kwargs)
            self.add_result(TestResult(name, passed, message))
            return passed
        except Exception as e:
            self.add_result(TestResult(name, False, f"Exception: {str(e)}"))
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY:")
        print(f"  Total tests: {self.test_count}")
        print(f"  Passed: {self.pass_count}")
        print(f"  Failed: {self.fail_count}")
        print("=" * 60)
        
        # Print individual results
        for result in self.results:
            print(result)
        
        print("=" * 60)
        
        if self.fail_count == 0:
            print("[OK] ALL TESTS PASSED")
            return 0
        else:
            print("[X] TEST SUITE FAILED")
            return 2
    
    def run_all_tests(self) -> int:
        """Run all tests and return exit code."""
        print("=" * 60)
        print("GLASS BOX BOUNDARY ENFORCER TEST SUITE")
        print("=" * 60)
        print(f"Python: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print()
        
        # Run test categories
        print("Test: Boundary Decorator")
        self.run_boundary_decorator_tests()
        
        print("\nTest: Required Artifacts")
        self.run_required_artifacts_tests()
        
        print("\nTest: Enforcer Execution")
        self.run_enforcer_execution_tests()
        
        print("\nTest: Trace Generation")
        self.run_trace_generation_tests()
        
        print("\nTest: Validation Mode")
        self.run_validation_mode_tests()
        
        print("\nTest: Exit Codes")
        self.run_exit_code_tests()
        
        # Return exit code based on results
        return self.print_summary()
    
    def run_boundary_decorator_tests(self):
        """Test boundary decorator functionality."""
        
        def test_decorator_application():
            """Test that decorator can be applied to functions."""
            if not BOUNDARY_IMPORT_SUCCESS:
                return False, "Boundary enforcer not imported"
            
            # Test function with decorator
            @glass_box_boundary()
            def test_function(x: int) -> int:
                return x * 2
            
            # Call the function
            result = test_function(5)
            return result == 10, f"Function returned {result}, expected 10"
        
        def test_decorator_parameters():
            """Test decorator with different parameters."""
            if not BOUNDARY_IMPORT_SUCCESS:
                return False, "Boundary enforcer not imported"
            
            # Define validation schemas
            input_schema = {
                "type": "object",
                "properties": {
                    "value": {"type": "integer", "minimum": 0}
                },
                "required": ["value"]
            }
            
            output_schema = {
                "type": "object",
                "properties": {
                    "result": {"type": "integer"}
                },
                "required": ["result"]
            }
            
            @glass_box_boundary(
                input_validator=input_schema,
                output_validator=output_schema,
                side_effect_check=True,
                orthogonal_separation=False
            )
            def validated_function(data: dict) -> dict:
                return {"result": data["value"] * 3}
            
            # Test valid input
            result = validated_function({"value": 4})
            return result["result"] == 12, f"Result: {result['result']}, expected 12"
        
        self.run_test("Decorator application test", test_decorator_application)
        self.run_test("Decorator parameter test", test_decorator_parameters)
        
        # Check if tests passed
        passed_tests = sum(1 for r in self.results[-2:] if r.passed)
        if passed_tests == 2:
            print("  [OK] Boundary Decorator PASSED")
        else:
            print("  [X] Boundary Decorator FAILED")
    
    def run_required_artifacts_tests(self):
        """Test that required artifacts exist."""
        
        def test_required_files():
            """Check that all required files exist."""
            required_files = [
                "documentation/GLASS_BOX_BOUNDARY_v1.11.html",
                "automation/run_full_audit_with_trace.py",
                "AGENT.md",
                "AI_INSTRUCTIONS.md",
                "_START_HERE.md",
                "onboarding/LEVEL1.md",
                "onboarding/LEVEL2.md",
                ".rules/ORTHOGONAL_GB_ORIGIN.rules",
                "toolkit/oe/local_metering_device.py",
                "toolkit/oe/suppressed_signal_detector.py",
                "toolkit/oe/evidence_store.py"
            ]
            
            missing_files = []
            for file_path in required_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                return False, f"Missing files: {', '.join(missing_files[:3])}{'...' if len(missing_files) > 3 else ''}"
            return True, f"All {len(required_files)} required artifacts found"
        
        passed = self.run_test("All 11 required artifacts found", test_required_files)
        
        if passed:
            print("  [OK] Required Artifacts PASSED")
        else:
            print("  [X] Required Artifacts FAILED")
    
    def run_enforcer_execution_tests(self):
        """Test enforcer execution."""
        
        def test_python_syntax():
            """Test that enforcer Python syntax is valid."""
            enforcer_path = "automation/run_full_audit_with_trace.py"
            try:
                # Try to compile the file
                with open(enforcer_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                compile(source, enforcer_path, 'exec')
                return True, "Python syntax validation passed"
            except SyntaxError as e:
                return False, f"Syntax error: {e}"
        
        def test_module_import():
            """Test that the enforcer module can be imported."""
            try:
                # Try to import the module
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "run_full_audit_with_trace",
                    "automation/run_full_audit_with_trace.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True, "Module import successful"
            except Exception as e:
                return False, f"Import error: {e}"
        
        def test_help_command():
            """Test that enforcer help command works."""
            try:
                result = subprocess.run(
                    [sys.executable, "automation/run_full_audit_with_trace.py", "--help"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode in [0, 2]:  # 0=success, 2=boundary violation (acceptable)
                    return True, "Help command execution passed"
                else:
                    return False, f"Help command failed with exit code {result.returncode}"
            except subprocess.TimeoutExpired:
                return False, "Help command timed out"
            except Exception as e:
                return False, f"Help command error: {e}"
        
        self.run_test("Python syntax validation passed", test_python_syntax)
        self.run_test("Module import successful", test_module_import)
        self.run_test("Help command execution passed", test_help_command)
        
        # Check if tests passed
        passed_tests = sum(1 for r in self.results[-3:] if r.passed)
        if passed_tests == 3:
            print("  [OK] Enforcer Execution PASSED")
        else:
            print("  [X] Enforcer Execution FAILED")
    
    def run_trace_generation_tests(self):
        """Test trace generation functionality."""
        
        def test_trace_generation():
            """Test that trace can be generated."""
            try:
                # Create a temporary file for trace output
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                    tmp_path = tmp.name
                
                # Run trace generation
                result = subprocess.run(
                    [sys.executable, "automation/run_full_audit_with_trace.py", 
                     "--output", tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Check if trace file was created and has content
                if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                    with open(tmp_path, 'r') as f:
                        trace_data = json.load(f)
                    
                    # Check required fields
                    required_fields = [
                        "trace_id", "timestamp", "repository_meta",
                        "environment_snapshot", "artifact_scan"
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in trace_data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        return False, f"Missing trace fields: {missing_fields}"
                    
                    # Clean up
                    os.unlink(tmp_path)
                    
                    return True, "Trace generation command executed successfully"
                else:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    return False, f"Trace generation failed with exit code {result.returncode}"
                    
            except subprocess.TimeoutExpired:
                return False, "Trace generation timed out"
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in trace: {e}"
            except Exception as e:
                return False, f"Trace generation error: {e}"
        
        passed = self.run_test("Trace generation command executed successfully", test_trace_generation)
        
        if passed:
            print("  [OK] Trace Generation PASSED")
        else:
            print("  [X] Trace Generation FAILED")
    
    def run_validation_mode_tests(self):
        """Test validation mode functionality."""
        
        def test_valid_trace_validation():
            """Test that a valid trace passes validation."""
            # Create a minimal valid trace
            valid_trace = {
                "trace_id": "GB-TRACE-TEST-1234-5678-9012-3456-789012345678",
                "timestamp": "2026-01-24T10:00:00Z",
                "repository_meta": {
                    "name": "test-repo",
                    "version": "v1.0.0",
                    "commit_hash": "a" * 40,
                    "branch": "main"
                },
                "environment_snapshot": {
                    "python_version": "3.14.0",
                    "dependencies": ["test==1.0.0"],
                    "system_info": {
                        "platform": "test",
                        "architecture": "AMD64",
                        "cwd": "/test"
                    }
                },
                "artifact_scan": {
                    "required_artifacts": 7,
                    "found_artifacts": 7,
                    "missing_artifacts": 0
                },
                "boundary_violations": [],
                "suppressed_signals": [],
                "timeline_sequence": {
                    "events": [
                        {
                            "timestamp": "2026-01-24T09:59:00Z",
                            "event_type": "onboarding_start",
                            "description": "Onboarding started"
                        }
                    ],
                    "valid": True
                },
                "hash_manifest": {
                    "algorithm": "SHA256",
                    "files_hashed": 9,
                    "root_hash": "a" * 64
                },
                "signature": {
                    "algorithm": "HMAC-SHA256",
                    "value": "test_signature",
                    "timestamp": "2026-01-24T10:00:00Z"
                },
                "python_enforcer_active": True,
                "ide_integration": {
                    "autofix": True,
                    "structural_consistency": True,
                    "boundary_awareness": True,
                    "documentation_sync": True
                }
            }
            
            # Write trace to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                json.dump(valid_trace, tmp)
                tmp_path = tmp.name
            
            try:
                # Try to validate
                result = subprocess.run(
                    [sys.executable, "automation/run_full_audit_with_trace.py",
                     "--validate-only", "--trace-file", tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Clean up
                os.unlink(tmp_path)
                
                # Check result
                if result.returncode == 0:
                    return True, "Valid trace validation passed"
                else:
                    return False, f"Valid trace rejected with exit code {result.returncode}"
                    
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return False, f"Validation error: {e}"
        
        def test_invalid_trace_rejection():
            """Test that an invalid trace is rejected with exit code 2."""
            # Create an invalid trace (missing required fields)
            invalid_trace = {
                "trace_id": "invalid",
                "timestamp": "invalid"
                # Missing all other required fields
            }
            
            # Write trace to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                json.dump(invalid_trace, tmp)
                tmp_path = tmp.name
            
            try:
                # Try to validate
                result = subprocess.run(
                    [sys.executable, "automation/run_full_audit_with_trace.py",
                     "--validate-only", "--trace-file", tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Clean up
                os.unlink(tmp_path)
                
                # Check result - should be exit code 2 for boundary violation
                if result.returncode == 2:
                    return True, "Invalid trace correctly rejected with exit code 2"
                else:
                    return False, f"Invalid trace accepted with exit code {result.returncode}"
                    
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return False, f"Validation error: {e}"
        
        # These tests require trace generation to work first
        # Check if we have a working trace generation
        trace_test_passed = any(
            r.passed and "Trace generation" in r.name 
            for r in self.results
        )
        
        if trace_test_passed:
            self.run_test("Valid trace validation passed", test_valid_trace_validation)
            self.run_test("Invalid trace correctly rejected with exit code 2", test_invalid_trace_rejection)
            
            # Check if tests passed
            passed_tests = sum(1 for r in self.results[-2:] if r.passed)
            if passed_tests == 2:
                print("  [OK] Validation Mode PASSED")
            else:
                print("  [X] Validation Mode FAILED")
        else:
            print("  [SKIP] Validation Mode (trace generation not working)")
            self.add_result(TestResult(
                "Cannot generate trace for validation test", 
                False, 
                "Trace generation prerequisite failed"
            ))
    
    def run_exit_code_tests(self):
        """Test exit code behavior."""
        
        def test_exit_code_0():
            """Test that successful validation returns exit code 0."""
            # This test is partially covered by other tests
            # We'll check if any test returned exit code 0 when expected
            
            # Look for successful trace generation or validation
            success_found = any(
                r.passed and ("trace" in r.name.lower() or