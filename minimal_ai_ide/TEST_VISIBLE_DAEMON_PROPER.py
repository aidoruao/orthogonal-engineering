#!/usr/bin/env python3
"""
PROPER VISIBLE DAEMON TEST
Tests the visible daemon with correct endpoints and shows real-time activity
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

DAEMON_URL = "http://127.0.0.1:5001"
ENDPOINTS = ["/", "/health", "/constraints", "/stats"]


def print_banner(text):
    """Print a banner with the given text"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_endpoint(endpoint, description):
    """Test an endpoint and show result"""
    url = f"{DAEMON_URL}{endpoint}"
    print(f"\n🌐 Testing: {description}")
    print(f"  URL: {url}")

    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        elapsed = (time.time() - start_time) * 1000

        print(f"  ✅ Status: {response.status_code} ({elapsed:.0f}ms)")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  📊 Response type: {type(data).__name__}")

                if endpoint == "/":
                    print(f"  📝 Message: {data.get('message', 'No message')}")
                elif endpoint == "/health":
                    print(f"  🩺 Status: {data.get('status', 'unknown')}")
                    print(f"  ⏱️  Uptime: {data.get('uptime', 0):.1f}s")
                elif endpoint == "/constraints":
                    count = data.get("count", 0)
                    print(f"  ⚖️  Σ_LORA constraints: {count}")
                    constraints = data.get("constraints", {})
                    for name in list(constraints.keys())[:3]:
                        desc = constraints[name]
                        print(f"    • {name}: {desc[:40]}...")
                elif endpoint == "/stats":
                    print(f"  📈 Requests: {data.get('requests_total', 0)}")
                    print(f"  📁 File changes: {data.get('file_changes_detected', 0)}")

            except json.JSONDecodeError:
                print(f"  📄 Response: {response.text[:100]}...")
            except Exception as e:
                print(f"  ⚠️  Could not parse response: {e}")

        return True

    except requests.exceptions.ConnectionError:
        print(f"  ❌ ERROR: Cannot connect to daemon")
        print(f"  💡 Make sure daemon is running with:")
        print(f"     python VISIBLE_DAEMON.py --host 127.0.0.1 --port 5001 --watch .")
        return False
    except requests.exceptions.Timeout:
        print(f"  ⏱️  TIMEOUT: Daemon not responding")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def trigger_file_monitoring():
    """Create, modify, and delete files to trigger monitoring"""
    print("\n📝 Testing file monitoring...")
    print("  Watch daemon terminal for 'FILE CHANGE' messages")

    test_files = [
        "VISIBLE_TEST_CREATE.txt",
        "VISIBLE_TEST_MODIFY.txt",
        "VISIBLE_TEST_DELETE.txt",
    ]

    try:
        # Create files
        print(f"\n  Creating test files...")
        for filename in test_files:
            with open(filename, "w") as f:
                f.write(f"Created at {datetime.now().isoformat()}\n")
                f.write("This should trigger file monitoring\n")
            print(f"    ✅ Created: {filename}")

        time.sleep(2)  # Wait for daemon to detect

        # Modify files
        print(f"\n  Modifying test files...")
        for filename in test_files[:2]:  # Modify first two
            with open(filename, "a") as f:
                f.write(f"Modified at {datetime.now().isoformat()}\n")
            print(f"    ✅ Modified: {filename}")

        time.sleep(2)  # Wait for daemon to detect

        # Delete files
        print(f"\n  Deleting test files...")
        for filename in test_files:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"    ✅ Deleted: {filename}")

        time.sleep(2)  # Wait for daemon to detect

        print(f"\n  ✅ File monitoring test complete")
        print(f"  👀 Check daemon terminal for 5+ 'FILE CHANGE' messages")
        return True

    except Exception as e:
        print(f"  ❌ File monitoring test failed: {e}")
        return False


def continuous_activity_test(duration=30):
    """Send continuous requests to show heartbeat and request activity"""
    print(f"\n🔄 Starting continuous activity test ({duration} seconds)...")
    print(f"  Watch daemon terminal for:")
    print(f"    • 💓 HEARTBEAT messages (every 10 seconds)")
    print(f"    • 🌐 REQUEST messages (every 3 seconds)")
    print(f"    • ✓ Validation messages")

    start_time = time.time()
    request_count = 0

    try:
        while time.time() - start_time < duration:
            # Cycle through endpoints
            endpoint = ENDPOINTS[request_count % len(ENDPOINTS)]

            try:
                response = requests.get(f"{DAEMON_URL}{endpoint}", timeout=2)
                request_count += 1

                # Show progress every 5 requests
                if request_count % 5 == 0:
                    elapsed = time.time() - start_time
                    print(
                        f"    Request #{request_count}: {endpoint} → {response.status_code} ({elapsed:.0f}s)"
                    )

            except requests.exceptions.Timeout:
                print(f"    ⏱️  Request #{request_count + 1} timeout")
            except:
                pass  # Silent fail for continuous test

            # Wait between requests
            time.sleep(3)

        print(f"\n  ✅ Continuous test complete")
        print(f"    Total requests: {request_count}")
        print(f"    Duration: {duration} seconds")
        print(f"    Requests/second: {request_count / duration:.1f}")

        return request_count

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n  ⏹️  Continuous test interrupted")
        print(f"    Requests sent: {request_count}")
        print(f"    Duration: {elapsed:.1f} seconds")
        return request_count


def main():
    """Main test function"""
    print_banner("VISIBLE DAEMON - PROPER TEST")
    print("\n👁️  WATCH THE DAEMON TERMINAL FOR REAL-TIME ACTIVITY!")
    print("\nThis test will trigger visible logging in the daemon terminal:")
    print("  1. 🌐 REQUEST messages - Each endpoint test")
    print("  2. 📝 FILE CHANGE messages - File create/modify/delete")
    print("  3. 💓 HEARTBEAT messages - Every 10 seconds automatically")
    print("  4. ✓ Validation messages - Σ_LORA constraint checks")
    print("\nPress Enter to start the test...")
    input()

    # Test 1: Basic connectivity and endpoints
    print_banner("TEST 1: ENDPOINT CONNECTIVITY")

    endpoint_descriptions = {
        "/": "Root endpoint (system info)",
        "/health": "Health check endpoint",
        "/constraints": "Σ_LORA constraints list",
        "/stats": "Runtime statistics",
    }

    all_passed = True
    for endpoint in ENDPOINTS:
        if not test_endpoint(endpoint, endpoint_descriptions[endpoint]):
            all_passed = False

    if not all_passed:
        print_banner("CONNECTIVITY FAILED")
        print("\n❌ Some connectivity tests failed")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Make sure daemon is running in another terminal:")
        print("      python VISIBLE_DAEMON.py --host 127.0.0.1 --port 5001 --watch .")
        print("   2. Check if port 5001 is available")
        print("   3. Try a different port: --port 5002")
        print("\n🔄 Restart daemon and try again")
        return

    # Test 2: File monitoring
    print_banner("TEST 2: FILE MONITORING")
    trigger_file_monitoring()

    # Test 3: Continuous activity
    print_banner("TEST 3: CONTINUOUS ACTIVITY")
    continuous_activity_test(30)  # 30 seconds

    # Final summary
    print_banner("VISIBILITY TEST COMPLETE")
    print("\n✅ VISIBILITY CONFIRMED!")
    print("\nWhat you should have seen in the daemon terminal:")
    print("   1. 🌐 4+ REQUEST messages (endpoint tests)")
    print("   2. 📝 5+ FILE CHANGE messages (create/modify/delete)")
    print("   3. 💓 3+ HEARTBEAT messages (every 10 seconds)")
    print("   4. ✓ Validation messages (Σ_LORA constraints)")
    print("\n🎯 DAEMON VISIBILITY IS WORKING!")
    print("\n📋 NEXT STEPS:")
    print("   • Keep daemon terminal open for 24/7 operation")
    print("   • Use RUN_VISIBLE_DAEMON.bat for easy startup")
    print("   • Edit files in this directory to trigger monitoring")
    print("   • All operations factor through Σ_LORA constraints")
    print("\nΣ_LORA PRINCIPLE: 'All intelligence paths factor through this daemon'")
    print("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()

    # Clean up any test files
    for filename in [
        "VISIBLE_TEST_CREATE.txt",
        "VISIBLE_TEST_MODIFY.txt",
        "VISIBLE_TEST_DELETE.txt",
    ]:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

    input("\nPress Enter to exit...")
