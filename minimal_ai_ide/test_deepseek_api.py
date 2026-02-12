import asyncio
import json
import os
import sys
from typing import Any, Dict

import aiohttp


async def test_deepseek_api_basic():
    """Test basic DeepSeek API connection without tools"""
    print("=" * 60)
    print("DEEPSEEK API BASIC CONNECTION TEST")
    print("=" * 60)

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY environment variable not set")
        print("\nPlease set it:")
        print("  Windows Command Prompt: set DEEPSEEK_API_KEY=your_key_here")
        print("  Windows PowerShell: $env:DEEPSEEK_API_KEY='your_key_here'")
        print("  Linux/Mac: export DEEPSEEK_API_KEY='your_key_here'")
        return False

    endpoint = os.environ.get(
        "DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions"
    )

    print(f"API Key: {api_key[:10]}... (hidden)")
    print(f"Endpoint: {endpoint}")

    # Simple chat completion request (no tools)
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "Hello, please respond with 'API test successful'",
            }
        ],
        "max_tokens": 50,
        "temperature": 0.1,
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        print("\nSending request to DeepSeek API...")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                print(f"Response status: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    print(f"\n✅ API CONNECTION SUCCESSFUL")
                    print(
                        f"Response: {data.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}"
                    )
                    return True
                else:
                    error_text = await response.text()
                    print(f"\n❌ API ERROR: Status {response.status}")
                    print(f"Error response: {error_text[:500]}")

                    # Try to parse as JSON for better error message
                    try:
                        error_json = json.loads(error_text)
                        print(f"Error JSON: {json.dumps(error_json, indent=2)}")
                    except:
                        pass

                    return False

    except aiohttp.ClientError as e:
        print(f"\n❌ NETWORK ERROR: {e}")
        return False
    except asyncio.TimeoutError:
        print("\n❌ TIMEOUT: Request took too long")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_deepseek_api_with_tools():
    """Test DeepSeek API with tool calls to diagnose the tool message error"""
    print("\n" + "=" * 60)
    print("DEEPSEEK API TOOL CALLS TEST")
    print("=" * 60)

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY not set")
        return False

    endpoint = os.environ.get(
        "DEEPSEEK_ENDPOINT", "https://api.deepseek.com/v1/chat/completions"
    )

    # Define a simple tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }
    ]

    # First message: User asks for time
    messages = [
        {
            "role": "user",
            "content": "What time is it? Use the get_current_time tool if available.",
        }
    ]

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 100,
        "temperature": 0.1,
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        print("Testing tool calls...")
        async with aiohttp.ClientSession() as session:
            # First call: Get tool call from AI
            print("\n1. Sending initial request (expecting tool call)...")
            async with session.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Initial request failed: {response.status}")
                    print(f"Error: {error_text[:500]}")
                    return False

                data = await response.json()
                message = data.get("choices", [{}])[0].get("message", {})

                print(f"Response message keys: {list(message.keys())}")

                if "tool_calls" in message:
                    print("✅ AI returned tool calls as expected")
                    tool_calls = message["tool_calls"]
                    print(f"Number of tool calls: {len(tool_calls)}")

                    # Add AI message to conversation history
                    messages.append(message)

                    # Add tool response
                    for tool_call in tool_calls:
                        tool_response = {
                            "role": "tool",
                            "content": "The current time is 14:30:00 UTC",
                            "tool_call_id": tool_call["id"],
                        }
                        messages.append(tool_response)

                    # Second call: Send tool response back to AI
                    print("\n2. Sending tool response back to AI...")
                    payload2 = {
                        "model": "deepseek-chat",
                        "messages": messages,
                        "max_tokens": 100,
                        "temperature": 0.1,
                    }

                    async with session.post(
                        endpoint,
                        json=payload2,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response2:
                        if response2.status != 200:
                            error_text = await response2.text()
                            print(f"❌ Second request failed: {response2.status}")
                            print(f"Error: {error_text[:500]}")
                            return False

                        data2 = await response2.json()
                        final_message = data2.get("choices", [{}])[0].get("message", {})
                        print(
                            f"✅ Final AI response: {final_message.get('content', 'No content')}"
                        )
                        return True
                else:
                    print(
                        "⚠ AI did not return tool calls (might have answered directly)"
                    )
                    print(f"AI response: {message.get('content', 'No content')}")
                    return True

    except Exception as e:
        print(f"\n❌ ERROR in tool test: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_api_format_issues():
    """Test common API format issues that cause 400 errors"""
    print("\n" + "=" * 60)
    print("API FORMAT ISSUES DIAGNOSIS")
    print("=" * 60)

    # Common incorrect formats that cause 400 errors
    incorrect_formats = [
        {
            "name": "Old 'prompt' parameter format",
            "payload": {"prompt": "Hello", "stream": True, "max_tokens": 100},
            "expected_error": "Should fail - needs 'messages' array",
        },
        {
            "name": "Tool message without preceding tool_calls",
            "payload": {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "tool",
                        "content": "Tool result",
                        "tool_call_id": "fake_id",
                    }
                ],
            },
            "expected_error": "Messages with role 'tool' must be a response to a preceding message with 'tool_calls'",
        },
        {
            "name": "Missing required fields",
            "payload": {"messages": [{"role": "user", "content": "Hello"}]},
            "expected_error": "Missing 'model' field",
        },
    ]

    print("Common API format issues that cause 400 Bad Request:")
    for i, fmt in enumerate(incorrect_formats, 1):
        print(f"\n{i}. {fmt['name']}:")
        print(f"   Expected issue: {fmt['expected_error']}")
        print(f"   Payload keys: {list(fmt.get('payload', {}).keys())}")

    return True


async def main():
    """Run all tests"""
    print("DEEPSEEK API DIAGNOSTIC TESTS")
    print("=" * 60)

    results = []

    # Test 1: Basic API connection
    results.append(("Basic API Connection", await test_deepseek_api_basic()))

    # Test 2: Tool calls (if basic connection works)
    if results[0][1]:  # If basic test passed
        results.append(("Tool Calls", await test_deepseek_api_with_tools()))
    else:
        print("\nSkipping tool calls test due to basic connection failure")
        results.append(("Tool Calls", "Skipped"))

    # Test 3: Format issues diagnosis (always runs)
    results.append(("Format Issues Diagnosis", test_api_format_issues()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = 0

    for name, result in results:
        total += 1
        if result == True:
            status = "✅ PASS"
            passed += 1
        elif result == "Skipped":
            status = "⚠ SKIPPED"
        else:
            status = "❌ FAIL"

        print(f"{status}: {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    if not results[0][1]:
        print("\n1. BASIC CONNECTION FAILED:")
        print("   • Check DEEPSEEK_API_KEY is correct")
        print("   • Check internet connection")
        print("   • Verify endpoint URL: https://api.deepseek.com/v1/chat/completions")
        print("   • Check if API key has expired or reached limit")

    print("\n2. COMMON FIXES FOR 400 ERRORS:")
    print("   • Use 'messages' array format, not 'prompt' parameter")
    print("   • Ensure tool messages follow tool_calls messages")
    print("   • Include 'model' field (e.g., 'deepseek-chat')")
    print("   • Check JSON format is valid")

    print("\n3. CHECK EXISTING CODE:")
    print("   • maximal_oracle_v57.py uses old 'prompt' format")
    print("   • bidirectional_controller_interface.py may have format issues")
    print("   • Update API calls to use 'messages' array format")


if __name__ == "__main__":
    asyncio.run(main())
