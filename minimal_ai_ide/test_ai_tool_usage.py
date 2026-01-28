import json
import os
import sys
import time
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_core import MinimalAI


def test_ai_actual_tool_usage():
    """Test if the AI can actually use tools when properly prompted"""
    print("=" * 70)
    print("AI ACTUAL TOOL USAGE TEST")
    print("Testing if AI can understand and use the tool protocol")
    print("=" * 70)

    ai = MinimalAI("config.json")

    # Create test directory and files
    test_dir = "test_ai_tools"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    # Create test files with specific content
    test_files = {
        "data.txt": "This is test data for AI tool usage.\nLine 2: More test data.\nLine 3: Even more data.",
        "config.json": '{"test": true, "value": 42, "name": "AI Tool Test"}',
        "code.py": "def hello():\n    print('Hello from test file')\n    return 42\n\nclass TestClass:\n    def __init__(self):\n        self.value = 'test'",
    }

    for filename, content in test_files.items():
        with open(os.path.join(test_dir, filename), "w") as f:
            f.write(content)

    print(f"\nCreated test directory: {test_dir}")
    print(f"Test files: {list(test_files.keys())}")

    # Test 1: Direct tool call in prompt
    print("\n" + "=" * 70)
    print("TEST 1: Direct tool call instruction")
    print("=" * 70)

    direct_prompt = """I need to read a file. Please use the read_file tool to read test_ai_tools/data.txt.

TOOL_CALL:read_file{"path": "test_ai_tools/data.txt"}"""

    print(f"\nPrompt (truncated): {direct_prompt[:100]}...")
    print("\nSending to AI...")

    try:
        response = ai.generate_with_tools(direct_prompt)
        print(f"\nResponse length: {len(response)} characters")

        # Check if tool was actually called
        if "TOOL_CALL:" in response:
            print("✓ AI included a tool call in response")
            # Extract tool call
            import re

            tool_match = re.search(r"TOOL_CALL:(\w+)(\{.*?\})", response, re.DOTALL)
            if tool_match:
                tool_name = tool_match.group(1)
                print(f"  Tool called: {tool_name}")
                try:
                    params = json.loads(tool_match.group(2))
                    print(f"  Parameters: {params}")
                except:
                    print(f"  Could not parse parameters")
        else:
            print("✗ AI did not include tool call in response")
            print(f"\nResponse preview: {response[:300]}...")

    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Complex task requiring multiple tools
    print("\n" + "=" * 70)
    print("TEST 2: Complex task requiring tools")
    print("=" * 70)

    complex_prompt = """I need to analyze the test directory. Here's what I want to do:
1. First, list all files in the test_ai_tools directory
2. Then read the config.json file to see its contents
3. Finally, count how many lines are in data.txt

Please use the appropriate tools to accomplish this task."""

    print(f"\nPrompt (truncated): {complex_prompt[:100]}...")
    print("\nSending to AI...")

    try:
        response = ai.generate_with_tools(complex_prompt)
        print(f"\nResponse length: {len(response)} characters")

        # Count tool calls
        tool_calls = response.count("TOOL_CALL:")
        print(f"Number of tool calls in response: {tool_calls}")

        if tool_calls > 0:
            print(f"✓ AI used {tool_calls} tool call(s)")

            # Show tool call examples
            import re

            tool_matches = list(
                re.finditer(r"TOOL_CALL:(\w+)(\{.*?\})", response, re.DOTALL)
            )

            for i, match in enumerate(tool_matches[:3]):  # Show first 3
                tool_name = match.group(1)
                print(f"\n  Tool call {i + 1}: {tool_name}")
                try:
                    params = json.loads(match.group(2))
                    print(f"    Parameters: {params}")
                except:
                    print(f"    Parameters: (could not parse)")
        else:
            print("✗ AI did not use any tools")
            print(f"\nResponse preview: {response[:300]}...")

    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: File manipulation task
    print("\n" + "=" * 70)
    print("TEST 3: File creation and manipulation")
    print("=" * 70)

    file_task_prompt = """Create a new file called test_ai_tools/results.txt with the following content:
This file was created by AI using tools.
Current timestamp will be added below.

Then read the file back to verify it was created correctly."""

    print(f"\nPrompt (truncated): {file_task_prompt[:100]}...")
    print("\nSending to AI...")

    try:
        response = ai.generate_with_tools(file_task_prompt)
        print(f"\nResponse length: {len(response)} characters")

        # Check for write_file tool call
        if "TOOL_CALL:write_file" in response:
            print("✓ AI attempted to write a file")
        elif "TOOL_CALL:read_file" in response and "results.txt" in response:
            print("✓ AI attempted to read the results file")
        else:
            print("✗ AI did not use file manipulation tools")
            print(f"\nResponse preview: {response[:300]}...")

    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 4: Command execution
    print("\n" + "=" * 70)
    print("TEST 4: System command execution")
    print("=" * 70)

    command_prompt = (
        """Check what Python version is installed by running a system command."""
    )

    print(f"\nPrompt: {command_prompt}")
    print("\nSending to AI...")

    try:
        response = ai.generate_with_tools(command_prompt)
        print(f"\nResponse length: {len(response)} characters")

        if "TOOL_CALL:run_command" in response:
            print("✓ AI attempted to run a command")

            # Extract command
            import re

            match = re.search(r"TOOL_CALL:run_command(\{.*?\})", response, re.DOTALL)
            if match:
                try:
                    params = json.loads(match.group(1))
                    cmd = params.get("cmd", "")
                    print(f"  Command: {cmd}")
                except:
                    print(f"  Could not parse command parameters")
        else:
            print("✗ AI did not use run_command tool")
            print(f"\nResponse preview: {response[:300]}...")

    except Exception as e:
        print(f"✗ Error: {e}")

    # Cleanup
    print("\n" + "=" * 70)
    print("CLEANUP")
    print("=" * 70)

    import shutil

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"✓ Cleaned up test directory: {test_dir}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\nTo determine if DeepSeek was 'lying' or 'simulating':")
    print("\n1. If AI uses TOOL_CALL: syntax in responses:")
    print("   - ✓ AI understands tool protocol")
    print("   - ✓ Tool calls are being generated")

    print("\n2. If AI responds naturally without TOOL_CALL:")
    print("   - ✗ AI is not using the tool protocol")
    print("   - ✗ Responses are simulated/natural language only")

    print("\n3. Key evidence of deception would be:")
    print("   - AI claims to have used tools but no TOOL_CALL: in output")
    print("   - AI references non-existent classes (MinimalAIWithTools)")
    print("   - AI provides detailed 'results' without actual tool usage")

    print("\n4. What this test proves:")
    print("   - Whether YOUR local AI (llama3.2) can use the tool protocol")
    print("   - Not whether DeepSeek in Zed was deceptive")

    print("\nRun this test to see what YOUR system actually does!")


if __name__ == "__main__":
    test_ai_actual_tool_usage()
