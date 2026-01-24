#!/usr/bin/env python3
"""
FALSIFICATION TESTS FOR INCREMENTAL PROCESSING SYSTEM
Version: 1.11
Schema ID: GB-ORIGIN-1.11
Generated: 2026-01-23
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Test boundary conditions and failure modes of incremental processing system
Principle: "If it can break, we should know how and why"

Glass Box Boundary Compliance:
- Tests boundary violation detection
- Tests state corruption recovery
- Tests token limit enforcement
- Tests forgiveness system integration

Forgiveness System Integration:
- Tests built from violation energy redirection
- Each test failure creates a building opportunity
- No recursive engagement with test failures
"""

import json
import os
import shutil
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.incremental_file_processor import (
    CHARS_PER_TOKEN,
    CHECKPOINT_DIR,
    MAX_CHUNK_BYTES,
    MAX_CHUNK_TOKENS,
    STATE_DIR,
    TOKEN_RATIO,
    IncrementalProcessor,
    ProcessingState,
    TokenAwareChunker,
)
from automation.zed_incremental_hook import ZedIncrementalHook


class IncrementalFalsificationTests:
    """Falsification tests for incremental processing system"""

    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="incremental_falsify_"))
        self.results = {
            "test_suite": "incremental_processing_falsification",
            "timestamp": datetime.now().isoformat(),
            "schema_id": "GB-ORIGIN-1.11",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "boundary_violations_detected": 0,
            "detailed_results": [],
        }

    def setup(self):
        """Setup test environment"""
        print(f"Setting up test environment in: {self.test_dir}")

        # Create test files
        self._create_test_files()

        # Backup original state directory
        if STATE_DIR.exists():
            backup_dir = self.test_dir / "state_backup"
            shutil.copytree(STATE_DIR, backup_dir)
            self.state_backup = backup_dir

        # Clear state for clean tests
        if STATE_DIR.exists():
            shutil.rmtree(STATE_DIR)

        return True

    def teardown(self):
        """Cleanup test environment"""
        print(f"Cleaning up test environment")

        # Restore original state
        if hasattr(self, "state_backup") and self.state_backup.exists():
            if STATE_DIR.exists():
                shutil.rmtree(STATE_DIR)
            shutil.copytree(self.state_backup, STATE_DIR)

        # Remove test directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

        return True

    def _create_test_files(self):
        """Create test files for falsification"""

        # 1. Very large JSON file (exceeds token limits)
        large_json = self.test_dir / "very_large.json"
        data = {"items": []}
        # Create ~2MB JSON file (~400K tokens)
        for i in range(10000):
            data["items"].append(
                {
                    "id": i,
                    "name": f"Item {i}",
                    "description": "A" * 100,  # 100 chars each
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "updated": datetime.now().isoformat(),
                        "tags": ["test", "falsification", f"item_{i}"],
                    },
                }
            )

        with open(large_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # 2. Corrupted JSON file
        corrupted_json = self.test_dir / "corrupted.json"
        with open(corrupted_json, "w", encoding="utf-8") as f:
            f.write('{"valid": true, "broken": [1, 2, 3, ')  # Missing closing

        # 3. Binary file (should fail gracefully)
        binary_file = self.test_dir / "binary.bin"
        with open(binary_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03" * 1000)

        # 4. Empty file
        empty_file = self.test_dir / "empty.txt"
        empty_file.touch()

        # 5. File with special characters
        special_file = self.test_dir / "special_chars.txt"
        with open(special_file, "w", encoding="utf-8") as f:
            f.write("Special: \u2261 \u2200 \u2203 \u2227 \u2228\n" * 1000)

        # 6. Nested JSON structure (tests structured chunking)
        nested_json = self.test_dir / "nested_structure.json"
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "items": [{"id": i, "data": "X" * 50} for i in range(1000)]
                    }
                }
            }
        }
        with open(nested_json, "w", encoding="utf-8") as f:
            json.dump(nested_data, f, indent=2)

        self.test_files = {
            "very_large": large_json,
            "corrupted": corrupted_json,
            "binary": binary_file,
            "empty": empty_file,
            "special_chars": special_file,
            "nested": nested_json,
        }

    def run_all_tests(self):
        """Run all falsification tests"""
        print("\n" + "=" * 80)
        print("RUNNING INCREMENTAL PROCESSING FALSIFICATION TESTS")
        print("=" * 80)

        tests = [
            self.test_token_limit_enforcement,
            self.test_state_corruption_recovery,
            self.test_nonexistent_file_handling,
            self.test_concurrent_processing,
            self.test_resume_after_crash,
            self.test_boundary_violation_detection,
            self.test_file_type_strategies,
            self.test_zed_integration_boundaries,
            self.test_forgiveness_integration,
            self.test_performance_under_load,
        ]

        for test_func in tests:
            test_name = test_func.__name__
            print(f"\n{'=' * 60}")
            print(f"TEST: {test_name}")
            print(f"{'=' * 60}")

            self.results["tests_run"] += 1

            try:
                success = test_func()
                if success:
                    print(f"✅ PASS: {test_name}")
                    self.results["tests_passed"] += 1
                    self.results["detailed_results"].append(
                        {
                            "test": test_name,
                            "status": "passed",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                else:
                    print(f"❌ FAIL: {test_name}")
                    self.results["tests_failed"] += 1
                    self.results["detailed_results"].append(
                        {
                            "test": test_name,
                            "status": "failed",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
            except Exception as e:
                print(f"💥 ERROR in {test_name}: {str(e)}")
                self.results["tests_failed"] += 1
                self.results["detailed_results"].append(
                    {
                        "test": test_name,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return self.results

    def test_token_limit_enforcement(self) -> bool:
        """Test that token limits are properly enforced"""
        print("Testing token limit enforcement...")

        processor = IncrementalProcessor()
        chunker = TokenAwareChunker()

        # Test with very large file
        large_file = self.test_files["very_large"]
        analysis = processor.analyze_file_for_processing(large_file)

        # Should exceed single chunk
        if not analysis["exceeds_single_chunk"]:
            print(f"  ❌ File should exceed single chunk: {analysis}")
            return False

        # Should require multiple chunks
        chunks_needed = analysis["chunks_needed"]
        if chunks_needed <= 1:
            print(f"  ❌ Should require >1 chunk, got: {chunks_needed}")
            return False

        # Verify chunk boundaries don't exceed limits
        for chunk_index in range(chunks_needed):
            start_byte, end_byte = chunker.get_chunk_boundaries(
                large_file, chunk_index, chunks_needed
            )
            chunk_size = end_byte - start_byte

            # Check byte limit
            if chunk_size > MAX_CHUNK_BYTES * 1.1:  # 10% tolerance
                print(
                    f"  ❌ Chunk {chunk_index} exceeds byte limit: {chunk_size} > {MAX_CHUNK_BYTES}"
                )
                return False

            # Estimate tokens
            estimated_tokens = int((chunk_size * TOKEN_RATIO) / CHARS_PER_TOKEN)
            if estimated_tokens > MAX_CHUNK_TOKENS * 1.1:  # 10% tolerance
                print(
                    f"  ❌ Chunk {chunk_index} exceeds token limit: {estimated_tokens} > {MAX_CHUNK_TOKENS}"
                )
                return False

        print(f"  ✅ Token limits enforced: {chunks_needed} chunks needed")
        return True

    def test_state_corruption_recovery(self) -> bool:
        """Test recovery from corrupted state files"""
        print("Testing state corruption recovery...")

        # Create a processor and start processing
        processor = IncrementalProcessor()
        test_file = self.test_files["nested"]

        # Start processing
        process_id = processor.process_file_incrementally(test_file)

        # Corrupt the state file
        state_file = STATE_DIR / "processing_state.json"
        if state_file.exists():
            with open(state_file, "w", encoding="utf-8") as f:
                f.write("{corrupted json")

        # Try to resume - should handle corruption gracefully
        try:
            processor.resume_processing(process_id)
            print("  ✅ Handled corrupted state gracefully")
            return True
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  ✅ Correctly detected corrupted state: {e}")
            return True
        except Exception as e:
            print(f"  ❌ Unexpected error with corrupted state: {e}")
            return False

    def test_nonexistent_file_handling(self) -> bool:
        """Test handling of non-existent files"""
        print("Testing non-existent file handling...")

        processor = IncrementalProcessor()
        nonexistent = self.test_dir / "does_not_exist.json"

        # Should raise FileNotFoundError
        try:
            processor.process_file_incrementally(nonexistent)
            print("  ❌ Should have raised FileNotFoundError")
            return False
        except FileNotFoundError:
            print("  ✅ Correctly raised FileNotFoundError")
            return True
        except Exception as e:
            print(f"  ❌ Wrong exception type: {type(e).__name__}: {e}")
            return False

    def test_concurrent_processing(self) -> bool:
        """Test concurrent processing of multiple files"""
        print("Testing concurrent processing...")

        import threading

        processor = IncrementalProcessor()
        results = []
        errors = []

        def process_file(file_path, result_list, error_list):
            try:
                process_id = processor.process_file_incrementally(file_path)
                result_list.append((file_path, process_id, "success"))
            except Exception as e:
                error_list.append((file_path, str(e)))

        # Process multiple files concurrently
        threads = []
        files_to_process = [
            self.test_files["empty"],
            self.test_files["special_chars"],
            self.test_files["nested"],
        ]

        for file_path in files_to_process:
            thread = threading.Thread(
                target=process_file, args=(file_path, results, errors)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check results
        if errors:
            print(f"  ❌ Errors in concurrent processing: {errors}")
            return False

        if len(results) != len(files_to_process):
            print(
                f"  ❌ Not all files processed: {len(results)}/{len(files_to_process)}"
            )
            return False

        print(f"  ✅ Concurrent processing successful: {len(results)} files")
        return True

    def test_resume_after_crash(self) -> bool:
        """Test resuming processing after simulated crash"""
        print("Testing resume after crash...")

        processor = IncrementalProcessor()
        test_file = self.test_files["very_large"]

        # Start processing but simulate crash after first chunk
        process_id = None

        # We'll manually control chunking to simulate crash
        chunker = TokenAwareChunker()
        chunks_needed = chunker.calculate_chunks_needed(test_file)

        # Process first chunk
        strategy = chunker.get_chunking_strategy(test_file)
        start_byte, end_byte = chunker.get_chunk_boundaries(test_file, 0, chunks_needed)
        chunk = chunker.read_chunk(test_file, start_byte, end_byte, strategy)

        # Create processing state manually
        state_manager = ProcessingState()
        process_id = state_manager.start_file_processing(test_file, chunks_needed)

        # Update progress for first chunk
        chunk_bytes = len(chunk.encode("utf-8"))
        chunk_tokens = int((chunk_bytes * TOKEN_RATIO) / CHARS_PER_TOKEN)
        state_manager.update_chunk_progress(process_id, 0, chunk_bytes, chunk_tokens)

        # Simulate crash - processor object is lost

        # Create new processor and resume
        new_processor = IncrementalProcessor()

        try:
            result = new_processor.resume_processing(process_id)
            if result["status"] == "completed":
                print("  ✅ Successfully resumed after crash")
                return True
            else:
                print(f"  ❌ Resume failed: {result}")
                return False
        except Exception as e:
            print(f"  ❌ Error during resume: {e}")
            return False

    def test_boundary_violation_detection(self) -> bool:
        """Test that boundary violations are properly detected"""
        print("Testing boundary violation detection...")

        # Test 1: File exceeding hard limits
        processor = IncrementalProcessor()

        # Create a file that would exceed system limits
        huge_file = self.test_dir / "huge_test.bin"
        with open(huge_file, "wb") as f:
            f.write(b"X" * (MAX_CHUNK_BYTES * 10))  # 10x limit

        try:
            processor.process_file_incrementally(huge_file)
            print("  ❌ Should have detected boundary violation")
            return False
        except RuntimeError as e:
            if "boundary violation" in str(e).lower():
                print("  ✅ Correctly detected boundary violation")
                self.results["boundary_violations_detected"] += 1
                return True
            else:
                print(f"  ❌ Wrong error message: {e}")
                return False
        except Exception as e:
            print(f"  ❌ Wrong exception type: {type(e).__name__}: {e}")
            return False

    def test_file_type_strategies(self) -> bool:
        """Test that different file types use appropriate strategies"""
        print("Testing file type strategies...")

        chunker = TokenAwareChunker()

        test_cases = [
            (self.test_files["nested"], "structured"),  # JSON
            (self.test_files["special_chars"], "line_based"),  # TXT
            (self.test_dir / "test.md", "section_based"),  # Create MD file
            (self.test_dir / "test.py", "function_based"),  # Create Python file
        ]

        # Create test files
        md_file = self.test_dir / "test.md"
        md_file.write_text("# Header\n\nSome content\n\n## Subheader\nMore content")

        py_file = self.test_dir / "test.py"
        py_file.write_text("def test():\n    pass\n\nclass TestClass:\n    pass")

        for file_path, expected_strategy in test_cases:
            if not file_path.exists():
                continue

            strategy = chunker.get_chunking_strategy(file_path)
            if strategy != expected_strategy:
                print(
                    f"  ❌ Wrong strategy for {file_path.suffix}: {strategy} != {expected_strategy}"
                )
                return False

        print("  ✅ File type strategies correct")
        return True

    def test_zed_integration_boundaries(self) -> bool:
        """Test Zed integration boundary conditions"""
        print("Testing Zed integration boundaries...")

        try:
            hook = ZedIncrementalHook()

            # Test 1: Non-existent file
            result = hook.handle_file_saved(self.test_dir / "ghost.txt")
            if result["status"] != "error":
                print(f"  ❌ Should error on non-existent file: {result}")
                return False

            # Test 2: Binary file (should skip)
            binary_result = hook.handle_file_saved(self.test_files["binary"])
            if binary_result["status"] != "skipped":
                print(f"  ❌ Should skip binary files: {binary_result}")
                return False

            # Test 3: Get status
            status = hook.get_processing_status()
            if not isinstance(status, dict):
                print(f"  ❌ Status should be dict: {type(status)}")
                return False

            print("  ✅ Zed integration boundaries correct")
            return True

        except Exception as e:
            print(f"  ❌ Zed integration test failed: {e}")
            return False

    def test_forgiveness_integration(self) -> bool:
        """Test forgiveness system integration"""
        print("Testing forgiveness system integration...")

        # Check that violation was properly logged
        violation_file = (
            Path(__file__).parent.parent
            / "forgiveness_system"
            / "violations"
            / "violation_ide_token_grenade.json"
        )

        if not violation_file.exists():
            print(f"  ❌ Violation file not found: {violation_file}")
            return False

        # Load and verify violation
        with open(violation_file, "r", encoding="utf-8") as f:
            violation = json.load(f)

        # Check required fields
        required_fields = [
            "violation_id",
            "description",
            "emotional_pointer",
            "redirected_to_building",
        ]
        for field in required_fields:
            if field not in violation:
                print(f"  ❌ Missing field in violation: {field}")
                return False

        # Verify this is the correct violation
        if violation.get("violation_id") != "VIOLATION-IDE-TOKEN-GRENADE-001":
            print(f"  ❌ Wrong violation ID: {violation.get('violation_id')}")
            return False

        # Check fork exists
        fork_file = violation_file.parent / "fork_ide_token_grenade.json"
        if not fork_file.exists():
            print(f"  ❌ Fork file not found: {fork_file}")
            return False

        with open(fork_file, "r", encoding="utf-8") as f:
            fork = json.load(f)

        # Verify energy redirection
        if not fork.get("energy_redirection", {}).get("redirection_complete", False):
            print("  ❌ Energy redirection not marked complete")
            return False

        print("  ✅ Forgiveness system integration verified")
        return True

    def test_performance_under_load(self) -> bool:
        """Test performance under heavy load"""
        print("Testing performance under load...")

        import concurrent.futures
        import time

        processor = IncrementalProcessor()

        # Create multiple medium-sized files
        test_files = []
        for i in range(10):
            file_path = self.test_dir / f"load_test_{i}.json"
            data = {"items": [{"id": j, "data": "X" * 100} for j in range(1000)]}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            test_files.append(file_path)

        start_time = time.time()
        results = []
        errors = []

        # Process files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(
                    processor.process_file_incrementally, file_path
                ): file_path
                for file_path in test_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    process_id = future.result(timeout=30)  # 30 second timeout
                    results.append((file_path, process_id))
                except concurrent.futures.TimeoutError:
                    errors.append((file_path, "timeout"))
                except Exception as e:
                    errors.append((file_path, str(e)))

        end_time = time.time()
        total_time = end_time - start_time

        # Check results
        if errors:
            print(f"  ❌ Errors under load: {len(errors)} errors")
            for file_path, error in errors[:3]:  # Show first 3 errors
                print(f"      - {file_path.name}: {error}")
            return False

        if len(results) != len(test_files):
            print(f"  ❌ Not all files processed: {len(results)}/{len(test_files)}")
            return False

        # Performance check: should process ~10 files in reasonable time
        avg_time_per_file = total_time / len(test_files)
        if avg_time_per_file > 10:  # More than 10 seconds per file is too slow
            print(f"  ❌ Performance too slow: {avg_time_per_file:.2f}s per file")
            return False

        print(
            f"  ✅ Performance under load: {len(results)} files in {total_time:.2f}s ({avg_time_per_file:.2f}s/file)"
        )
        return True


def main():
    """Main entry point for falsification tests"""
    print("=" * 80)
    print("INCREMENTAL PROCESSING FALSIFICATION TEST SUITE")
    print("=" * 80)
    print("Testing boundary conditions, failure modes, and system limits")
    print("Built from violation energy: VIOLATION-IDE-TOKEN-GRENADE-001")
    print()

    tester = IncrementalFalsificationTests()

    try:
        # Setup test environment
        if not tester.setup():
            print("❌ Failed to setup test environment")
            sys.exit(1)

        # Run all tests
        results = tester.run_all_tests()

        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Tests Run:    {results['tests_run']}")
        print(f"Tests Passed: {results['tests_passed']}")
        print(f"Tests Failed: {results['tests_failed']}")
        print(
            f"Boundary Violations Detected: {results['boundary_violations_detected']}"
        )
        print()

        # Calculate success rate
        success_rate = (
            (results["tests_passed"] / results["tests_run"]) * 100
            if results["tests_run"] > 0
            else 0
        )
        print(f"Success Rate: {success_rate:.1f}%")

        # Glass-Box Boundary compliance check
        if results["boundary_violations_detected"] > 0:
            print("⚠️  Boundary violations detected (expected in falsification tests)")

        # Forgiveness system check
        if results["tests_failed"] > 0:
            print(
                "⚠️  Test failures create building opportunities for forgiveness system"
            )

        # Overall status
        if results["tests_failed"] == 0:
            print("✅ All falsification tests passed!")
            print("System is robust against boundary conditions and failure modes")
        else:
            print(f"⚠️  {results['tests_failed']} test(s) failed")
            print(
                "These represent known boundary conditions for the forgiveness system"
            )

        # Save results
        results_file = Path(__file__).parent / "falsification_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to: {results_file}")

        # Exit code based on results
        if results["tests_failed"] == 0:
            sys.exit(0)  # Success
        else:
            sys.exit(2)  # Boundary violation (expected in falsification)

    except Exception as e:
        print(f"💥 Fatal error in test suite: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        # Always cleanup
        tester.teardown()


if __name__ == "__main__":
    main()
