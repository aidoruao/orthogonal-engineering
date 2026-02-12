#!/usr/bin/env python3
"""
TEST ORTHOGONAL MCP SERVER - FIXED VERSION
Subtractive Clarity and Glass-Box Boundary Compliance Test

Version: 1.1.0 - Protocol Correct
Date: 2026-01-25
Purpose: Test the orthogonal MCP server with explicit communication protocol
FIXED: MCP protocol violations (binary mode, byte-safe framing, Windows compatibility)
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


class OrthogonalMCPTest:
    """Test orthogonal MCP server with subtractive clarity principles."""

    def __init__(self):
        self.server_process = None
        self.test_results = []
        self.audit_logs = []

    def start_server(self):
        """Start the orthogonal MCP server in BINARY MODE."""
        print("Starting Orthogonal MCP Server...")

        server_path = Path(__file__).parent / "orthogonal_mcp_server.py"

        # FIX 1: Binary mode, no text=True, bufsize=0 for unbuffered
        self.server_process = subprocess.Popen(
            [sys.executable, str(server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,  # IMPORTANT: unbuffered
        )

        # Wait for server to start
        time.sleep(1)

        # Check if server is running
        if self.server_process.poll() is not None:
            stderr_output = self.server_process.stderr.read()
            raise RuntimeError(f"Server failed to start: {stderr_output}")

        print("✅ Server started successfully")
        return True

    def send_mcp_message(self, message: dict) -> dict:
        """Send MCP message with proper BYTE framing."""
        # FIX 2: Send as bytes, not text
        body = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")

        # Send header + body as bytes
        self.server_process.stdin.write(header + body)
        self.server_process.stdin.flush()

        # Read response
        response = self.read_mcp_response()
        return response

    def read_mcp_response(self) -> dict:
        """Read MCP response with BYTE-SAFE framing."""
        headers = {}

        # FIX 3: Read header lines as bytes
        while True:
            # Read bytes until newline
            line_bytes = b""
            while True:
                char = self.server_process.stdout.read(1)
                if not char:
                    raise RuntimeError("MCP server closed stdout")
                if char == b"\n":
                    break
                line_bytes += char

            # Remove trailing \r if present
            if line_bytes.endswith(b"\r"):
                line_bytes = line_bytes[:-1]

            # Empty line means end of headers
            if line_bytes == b"":
                break

            # Parse header
            if b":" not in line_bytes:
                raise ValueError(f"Invalid header line: {line_bytes}")

            key, value = line_bytes.split(b":", 1)
            headers[key.decode().strip().lower()] = value.decode().strip()

        if "content-length" not in headers:
            raise ValueError("Missing Content-Length header")

        length = int(headers["content-length"])

        # Read exact number of bytes
        body_bytes = b""
        while len(body_bytes) < length:
            chunk = self.server_process.stdout.read(length - len(body_bytes))
            if not chunk:
                raise RuntimeError(f"Expected {length} bytes, got {len(body_bytes)}")
            body_bytes += chunk

        return json.loads(body_bytes.decode("utf-8"))

    def capture_audit_logs(self):
        """Capture audit logs from stderr - Windows compatible."""
        # FIX 4: Ultra-simple approach - just try to read without fancy non-blocking
        # This is a test, not production, so we can keep it simple

        try:
            # Just try to read a line from stderr
            # If it blocks, we'll just skip it for this test
            stderr = self.server_process.stderr

            # Check if there's data available (platform-specific)
            import sys

            if sys.platform == "win32":
                # Windows: use a simple timeout-based approach
                # We'll just try to read and see what happens
                try:
                    # Try to read without blocking
                    # On Windows, we can't easily do non-blocking reads on pipes
                    # So we'll just attempt and catch any blocking
                    import msvcrt

                    # Try to peek to see if data is available
                    # This is a hack, but works for our test case
                    import time

                    start_time = time.time()

                    # Read whatever is available
                    log_line = b""
                    while time.time() - start_time < 0.01:  # 10ms timeout
                        try:
                            char = stderr.read(1)
                            if char:
                                log_line += char
                                if char == b"\n":
                                    break
                            else:
                                # No more data
                                break
                        except (IOError, OSError):
                            # Read would block
                            break

                    if log_line and b"[GLASS-BOX AUDIT]" in log_line:
                        self.audit_logs.append(log_line.decode().strip())
                        print(f"📝 Audit: {log_line.decode().strip()}")

                except Exception:
                    # If anything fails, just skip
                    pass
            else:
                # Unix/Linux: use select for non-blocking check
                import select

                # Check if stderr has data ready
                ready, _, _ = select.select([stderr], [], [], 0.01)  # 10ms timeout
                if ready:
                    # Data is available, read it
                    log_line = stderr.readline()
                    if log_line and b"[GLASS-BOX AUDIT]" in log_line:
                        self.audit_logs.append(log_line.decode().strip())
                        print(f"📝 Audit: {log_line.decode().strip()}")

        except Exception:
            # If anything goes wrong, just skip audit capture
            # This is a test, not production code
            pass

    def test_list_tools(self):
        """Test 1: List available tools."""
        print("\n=== Test 1: List Tools ===")

        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

        try:
            response = self.send_mcp_message(request)

            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"✅ Success! Found {len(tools)} tools:")
                for tool in tools:
                    print(
                        f"   • {tool['name']} ({tool['category']}): {tool['description']}"
                    )

                self.test_results.append(
                    {"test": "list_tools", "passed": True, "tool_count": len(tools)}
                )
                return True
            else:
                print(f"❌ Failed: Invalid response: {response}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_echo_tool(self):
        """Test 2: Echo tool."""
        print("\n=== Test 2: Echo Tool ===")

        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"message": "Hello from orthogonal MCP test!"},
            },
        }

        try:
            response = self.send_mcp_message(request)
            self.capture_audit_logs()

            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if result.get("success") and "echoed_message" in result.get("data", {}):
                    print(f"✅ Echo successful: {result['data']['echoed_message']}")

                    self.test_results.append(
                        {"test": "echo", "passed": True, "response": result}
                    )
                    return True
                else:
                    print(f"❌ Echo failed: {result}")
                    return False
            else:
                print(f"❌ Invalid response: {response}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_hash_evidence(self):
        """Test 3: Hash evidence tool."""
        print("\n=== Test 3: Hash Evidence Tool ===")

        test_data = "Orthogonal Engineering Test Data 12345"

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "hash_evidence",
                "arguments": {"data": test_data, "algorithm": "sha256"},
            },
        }

        try:
            response = self.send_mcp_message(request)
            self.capture_audit_logs()

            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if result.get("success") and "hash" in result.get("data", {}):
                    hash_value = result["data"]["hash"]
                    print(f"✅ Hash successful: {hash_value}")
                    print(f"   Algorithm: {result['data']['algorithm']}")
                    print(f"   Input length: {result['data']['input_length']}")

                    self.test_results.append(
                        {"test": "hash_evidence", "passed": True, "hash": hash_value}
                    )
                    return True
                else:
                    print(f"❌ Hash failed: {result}")
                    return False
            else:
                print(f"❌ Invalid response: {response}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_timestamp(self):
        """Test 4: Timestamp tool."""
        print("\n=== Test 4: Timestamp Tool ===")

        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "timestamp",
                "arguments": {"purpose": "test_validation"},
            },
        }

        try:
            response = self.send_mcp_message(request)
            self.capture_audit_logs()

            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if result.get("success") and "iso_timestamp" in result.get("data", {}):
                    timestamp = result["data"]["iso_timestamp"]
                    print(f"✅ Timestamp generated: {timestamp}")
                    print(f"   Purpose: {result['data']['purpose']}")
                    print(f"   Hash: {result['data']['hash']}")

                    self.test_results.append(
                        {"test": "timestamp", "passed": True, "timestamp": timestamp}
                    )
                    return True
                else:
                    print(f"❌ Timestamp failed: {result}")
                    return False
            else:
                print(f"❌ Invalid response: {response}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def test_get_audit_trail(self):
        """Test 5: Get audit trail."""
        print("\n=== Test 5: Get Audit Trail ===")

        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "get_audit_trail", "arguments": {"format": "summary"}},
        }

        try:
            response = self.send_mcp_message(request)
            self.capture_audit_logs()

            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if result.get("success") and "summary" in result.get("data", {}):
                    summary = result["data"]["summary"]
                    print(f"✅ Audit trail retrieved:")
                    print(f"   Time range: {summary['time_range']}")
                    print(f"   Total operations: {summary['total_operations']}")
                    print(f"   Boundary violations: {summary['boundary_violations']}")

                    self.test_results.append(
                        {
                            "test": "get_audit_trail",
                            "passed": True,
                            "operations": summary["total_operations"],
                        }
                    )
                    return True
                else:
                    print(f"❌ Audit trail failed: {result}")
                    return False
            else:
                print(f"❌ Invalid response: {response}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def run_all_tests(self):
        """Run all tests."""
        print("=" * 60)
        print("ORTHOGONAL MCP SERVER TEST SUITE - FIXED")
        print("Subtractive Clarity & Glass-Box Boundary Compliance")
        print("Protocol Correct: Binary Mode, Byte-Safe Framing")
        print("=" * 60)

        try:
            # Start server
            if not self.start_server():
                print("❌ Failed to start server")
                return False

            # Run tests
            tests = [
                self.test_list_tools,
                self.test_echo_tool,
                self.test_hash_evidence,
                self.test_timestamp,
                self.test_get_audit_trail,
            ]

            passed_count = 0
            for i, test_func in enumerate(tests):
                try:
                    if test_func():
                        passed_count += 1
                    print(f"Test {i + 1}: {'PASS' if passed_count > i else 'FAIL'}")
                except Exception as e:
                    print(f"Test {i + 1} error: {e}")

            # Print summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print(f"Total tests: {len(tests)}")
            print(f"Passed: {passed_count}")
            print(f"Failed: {len(tests) - passed_count}")
            print(f"Success rate: {(passed_count / len(tests)) * 100:.1f}%")

            # Print audit logs
            print(f"\nAudit logs captured: {len(self.audit_logs)}")
            for i, log in enumerate(self.audit_logs[:5]):  # Show first 5
                print(f"  {i + 1}. {log}")
            if len(self.audit_logs) > 5:
                print(f"  ... and {len(self.audit_logs) - 5} more")

            # Falsifiability claim
            print("\n" + "=" * 60)
            print("FALSIFIABILITY CLAIM")
            print("=" * 60)
            print("Claim: Orthogonal MCP server implements subtractive clarity")
            print("WITH protocol-correct MCP framing (binary, byte-safe)")
            print("Falsification test: Run this test script independently")
            print(f"Expected: {len(tests)} tests pass with audit logging")
            print(f"Actual: {passed_count}/{len(tests)} tests passed")

            return passed_count == len(tests)

        finally:
            # Cleanup
            if self.server_process:
                print("\nStopping server...")
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()

    def generate_test_report(self):
        """Generate test report in orthogonal engineering format."""
        report = {
            "test_report": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "server": "orthogonal_mcp_server",
                "version": "1.1.0",
                "schema_id": "MCP-ORTHOGONAL-1.1",
                "protocol_fixes": [
                    "binary_mode",
                    "byte_safe_framing",
                    "windows_compatible",
                    "no_text_mode",
                    "correct_content_length",
                ],
                "test_results": self.test_results,
                "audit_logs_count": len(self.audit_logs),
                "summary": {
                    "total_tests": len(self.test_results),
                    "passed_tests": sum(1 for r in self.test_results if r["passed"]),
                    "failed_tests": sum(
                        1 for r in self.test_results if not r["passed"]
                    ),
                    "success_rate": (
                        sum(1 for r in self.test_results if r["passed"])
                        / len(self.test_results)
                    )
                    * 100
                    if self.test_results
                    else 0,
                },
            }
        }

        return report


def main():
    """Main test execution."""
    tester = OrthogonalMCPTest()

    success = tester.run_all_tests()

    # Generate report
    report = tester.generate_test_report()

    # Save report
    report_path = Path(__file__).parent / "test_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nTest report saved to: {report_path}")

    # Exit with appropriate code
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Orthogonal MCP server is ready for Zed integration.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Review test output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
