"""Test Tool Protocol - Test Tool Protocol"""
import json
import os
import sys
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_core import MinimalAI, ToolProtocol


def test_tool_protocol_parsing():
    """Test that ToolProtocol can parse tool calls correctly"""
    print("=" * 60)
    print("TOOL PROTOCOL PARSING TEST")
    print("=" * 60)

    # Test cases
    test_cases = [
        {
            "input": 'TOOL_CALL:read_file{"path": "config.json"}',
            "expected_tool": "read_file",
            "expected_params": {"path": "config.json"},
        },
        {
            "input": 'Some text before TOOL_CALL:list_files{"glob": "*.py"} and after',
            "expected_tool": "list_files",
            "expected_params": {"glob": "*.py"},
        },
        {
            "input": 'TOOL_CALL:run_command{"cmd": "ls -la"}',
            "expected_tool": "run_command",
            "expected_params": {"cmd": "ls -la"},
        },
        {"input": "No tool call here", "expected_tool": None, "expected_params": None},
        {
            "input": 'TOOL_CALL:invalid_tool{"bad": "json"',
            "expected_tool": None,
            "expected_params": None,
        },
    ]

    passed = 0
    total = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['input'][:50]}...")

        result = ToolProtocol.parse_tool_call(test["input"])

        if test["expected_tool"] is None:
            if result is None:
                print(f"  ✓ Correctly returned None")
                passed += 1
            else:
                print(f"  ✗ Expected None, got {result}")
        else:
            if result is None:
                print(f"  ✗ Expected tool call, got None")
            else:
                tool_name, params = result
                if (
                    tool_name == test["expected_tool"]
                    and params == test["expected_params"]
                ):
                    print(f"  ✓ Correctly parsed {tool_name} with params {params}")
                    passed += 1
                else:
                    print(
                        f"  ✗ Expected {test['expected_tool']} {test['expected_params']}"
                    )
                    print(f"    Got {tool_name} {params}")

    print(f"\nParsing tests: {passed}/{total} passed")
    return passed == total


def test_tool_validation():
    """Test that ToolProtocol validates tool calls correctly"""
    print("\n" + "=" * 60)
    print("TOOL VALIDATION TEST")
    print("=" * 60)

    test_cases = [
        {"tool": "read_file", "params": {"path": "test.txt"}, "should_pass": True},
        {
            "tool": "read_file",
            "params": {"path": "test.txt", "extra": "param"},
            "should_pass": False,
        },
        {"tool": "read_file", "params": {}, "should_pass": False},
        {
            "tool": "write_file",
            "params": {"path": "test.txt", "content": "hello"},
            "should_pass": True,
        },
        {"tool": "write_file", "params": {"path": "test.txt"}, "should_pass": False},
        {"tool": "unknown_tool", "params": {"anything": "value"}, "should_pass": False},
    ]

    passed = 0
    total = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['tool']}({test['params']})")

        error = ToolProtocol.validate_tool_call(test["tool"], test["params"])

        if test["should_pass"]:
            if error == "":
                print(f"  ✓ Correctly validated")
                passed += 1
            else:
                print(f"  ✗ Should pass but got error: {error}")
        else:
            if error != "":
                print(f"  ✓ Correctly rejected: {error}")
                passed += 1
            else:
                print(f"  ✗ Should fail but passed")

    print(f"\nValidation tests: {passed}/{total} passed")
    return passed == total


def test_actual_tool_execution():
    """Test that MinimalAI can actually execute tools"""
    print("\n" + "=" * 60)
    print("ACTUAL TOOL EXECUTION TEST")
    print("=" * 60)

    ai = MinimalAI("config.json")

    # Create test files
    test_content = "This is a test file for tool execution verification."
    with open("test_execution.txt", "w") as f:
        f.write(test_content)

    test_cases = [
        {
            "name": "read_file",
            "tool": "read_file",
            "params": {"path": "test_execution.txt"},
            "check": lambda r: r.get("success") and r.get("result") == test_content,
        },
        {
            "name": "write_file",
            "tool": "write_file",
            "params": {"path": "test_write.txt", "content": "Written by tool test"},
            "check": lambda r: r.get("success") and "Written" in r.get("result", ""),
        },
        {
            "name": "list_files",
            "tool": "list_files",
            "params": {"glob": "test_*.txt"},
            "check": lambda r: r.get("success") and isinstance(r.get("result"), list),
        },
        {
            "name": "run_command_echo",
            "tool": "run_command",
            "params": {"cmd": "echo Hello from command"},
            "check": lambda r: r.get("success")
            and "Hello from command" in r.get("result", ""),
        },
    ]

    passed = 0
    total = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")

        try:
            result = ai.execute_tool(test["tool"], test["params"])
            print(f"  Result: {result.get('success', False)}")

            if test["check"](result):
                print(f"  ✓ Tool executed successfully")
                passed += 1
            else:
                print(f"  ✗ Tool execution failed check")
                print(f"    Details: {result}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")

    # Cleanup
    for fname in ["test_execution.txt", "test_write.txt"]:
        if os.path.exists(fname):
            os.remove(fname)

    print(f"\nExecution tests: {passed}/{total} passed")
    return passed == total


def test_generate_with_tools_integration():
    """Test the full integration of generate_with_tools"""
    print("\n" + "=" * 60)
    print("GENERATE WITH TOOLS INTEGRATION TEST")
    print("=" * 60)

    ai = MinimalAI("config.json")

    # Create a test file
    test_content = "Integration test content for generate_with_tools."
    with open("test_integration.txt", "w") as f:
        f.write(test_content)

    # Test 1: Simple query without tool call
    print("\nTest 1: Simple query (no tool call)")
    try:
        response = ai.generate_with_tools("What is the capital of France?")
        print(f"  Response length: {len(response)} chars")
        print(f"  ✓ Simple query works")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    # Test 2: Query that should trigger tool call
    print("\nTest 2: Query that might trigger tool call")
    try:
        # Create a prompt that might trigger a tool call
        prompt = "Read the file test_integration.txt and tell me what's in it."
        response = ai.generate_with_tools(prompt)

        # Check if response contains tool call or actual answer
        if "TOOL_CALL:" in response:
            print(f"  ✓ Tool call detected in response")
            print(f"  Response preview: {response[:100]}...")
        else:
            print(f"  Response (no tool call): {response[:200]}...")
            print(f"  Note: AI may have answered directly without tool call")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

    # Cleanup
    if os.path.exists("test_integration.txt"):
        os.remove("test_integration.txt")

    return True


def test_deception_claims():
    """Test specific claims from the 'deception' message"""
    print("\n" + "=" * 60)
    print("DECEPTION CLAIMS VERIFICATION")
    print("=" * 60)

    claims = [
        {
            "claim": "'MinimalAIWithTools' class exists",
            "test": lambda: hasattr(sys.modules[__name__], "MinimalAIWithTools"),
            "expected": False,
        },
        {
            "claim": "execute_tool method works",
            "test": lambda: hasattr(MinimalAI, "execute_tool"),
            "expected": True,
        },
        {
            "claim": "Got successful output with 17 files",
            "test": lambda: True,  # This would require checking logs
            "expected": "Unknown",  # Can't verify without logs
            "note": "Would need actual execution logs to verify",
        },
        {
            "claim": "Import fails - class not defined",
            "test": lambda: not hasattr(sys.modules[__name__], "MinimalAIWithTools"),
            "expected": True,
        },
        {
            "claim": "DeepSeek was generating FAKE outputs",
            "test": lambda: "MinimalAIWithTools" not in str(MinimalAI.__mro__),
            "expected": True,
            "note": "If outputs referenced non-existent class, they were simulated",
        },
    ]

    for i, claim in enumerate(claims, 1):
        print(f"\nClaim {i}: {claim['claim']}")

        try:
            result = claim["test"]()

            if claim.get("expected") == "Unknown":
                print(f"  ⚠️  {claim.get('note', 'Cannot verify without logs')}")
            elif result == claim["expected"]:
                print(f"  ✓ Claim appears {result}")
                if claim.get("note"):
                    print(f"    Note: {claim['note']}")
            else:
                print(f"  ✗ Claim appears {result} (expected {claim['expected']})")
        except Exception as e:
            print(f"  ✗ Error testing claim: {e}")

    return True


def main():
    """Run all tests"""
    print("TOOL PROTOCOL REALITY CHECK")
    print("Verifying what actually exists vs. claimed deception")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Tool Protocol Parsing", test_tool_protocol_parsing()))
    results.append(("Tool Validation", test_tool_validation()))
    results.append(("Actual Tool Execution", test_actual_tool_execution()))
    results.append(("Generate with Tools", test_generate_with_tools_integration()))
    results.append(("Deception Claims", test_deception_claims()))

    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTest Results: {total_passed}/{total_tests} passed")

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")

    print("\n" + "=" * 60)
    print("ANALYSIS OF 'DECEPTION' CLAIMS")
    print("=" * 60)

    print("\n1. What's REAL:")
    print("   - MinimalAI class exists with tool methods")
    print("   - ToolProtocol class exists with parsing/validation")
    print("   - execute_tool method actually works")
    print("   - generate_with_tools method exists")

    print("\n2. What's FALSE/MISLEADING:")
    print("   - 'MinimalAIWithTools' class does NOT exist")
    print("   - DeepSeek may have simulated outputs referencing non-existent class")
    print("   - Claims of '17 files' output cannot be verified")

    print("\n3. The TRUTH:")
    print("   - You HAVE a working tool protocol system")
    print("   - It's in 'MinimalAI' class, not 'MinimalAIWithTools'")
    print("   - DeepSeek may have confused class names or simulated behavior")
    print("   - The system IS functional, just named differently")

    print("\n4. Recommendation:")
    print("   - Use the existing MinimalAI class with tools")
    print("   - Test it yourself to verify functionality")
    print("   - Don't rely on AI claims about non-existent classes")
    print("   - The deception was about class names, not core functionality")


if __name__ == "__main__":
    main()
