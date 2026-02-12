#!/usr/bin/env python3
"""
SIMPLE VISIBILITY TESTER
Tests the visible daemon and shows real-time activity
"""

import os
import sys
import time
from datetime import datetime

import requests

DAEMON_URL = "http://127.0.0.1:5001"


def print_banner(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


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
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"  🔑 Keys: {keys[:5]}{'...' if len(keys) > 5 else ''}")
            except:
                print(f"  📄 Response: {response.text[:100]}...")

        return True
    except requests.exceptions.ConnectionError:
        print(f"  ❌ ERROR: Cannot connect to daemon")
        print(f"  💡 Make sure daemon is running on {DAEMON_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"  ⏱️  TIMEOUT: Daemon not responding")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def create_test_file():
    """Create a test file to trigger file monitoring"""
    test_file = "VISIBILITY_TEST_FILE.txt"

    print(f"\n📝 Creating test file to trigger monitoring...")
    print(f"  File: {test_file}")

    try:
        with open(test_file, "w") as f:
            f.write(f"Test file created at {datetime.now().isoformat()}\n")
            f.write("This should trigger file monitoring in the daemon terminal.\n")
            f.write("Watch the daemon terminal for 'FILE CHANGE' messages.\n")

        print(f"  ✅ File created successfully")

        # Wait a moment for daemon to detect
        print(f"  ⏳ Waiting 2 seconds for daemon detection...")
        time.sleep(2)

        # Modify the file
        print(f"\n📝 Modifying test file...")
        with open(test_file, "a") as f:
            f.write(f"File modified at {datetime.now().isoformat()}\n")

        print(f"  ✅ File modified")

        # Wait again
        print(f"  ⏳ Waiting 2 seconds...")
        time.sleep(2)

        # Delete the file
        print(f"\n📝 Deleting test file...")
        os.remove(test_file)
        print(f"  ✅ File deleted")

        return True
    except Exception as e:
        print(f"  ❌ File operation failed: {e}")
        return False


def continuous_test():
    """Send continuous requests to show heartbeat activity"""
    print(f"\n🔄 Starting continuous test (30 seconds)...")
    print(f"  Watch daemon terminal for 'HEARTBEAT' and 'REQUEST' messages")

    endpoints = ["/", "/health", "/stats", "/constraints"]
    start_time = time.time()
    request_count = 0

    try:
        while time.time() - start_time < 30:
            # Pick a random endpoint
            endpoint = endpoints[request_count % len(endpoints)]

            try:
                response = requests.get(f"{DAEMON_URL}{endpoint}", timeout=2)
                request_count += 1
                print(
                    f"  Request #{request_count}: {endpoint} → {response.status_code}"
                )
            except:
                pass  # Silent fail for continuous test

            # Wait between requests
            time.sleep(3)

        print(f"\n✅ Continuous test complete")
        print(f"  Total requests: {request_count}")
        print(f"  Duration: {time.time() - start_time:.1f} seconds")

    except KeyboardInterrupt:
        print(f"\n⏹️  Continuous test interrupted")
        print(f"  Requests sent: {request_count}")


def main():
    print_banner("VISIBLE DAEMON TESTER")
    print("\n👁️  WATCH THE DAEMON TERMINAL FOR REAL-TIME ACTIVITY!")
    print("   This test will make the daemon terminal light up with:")
    print("   • 🌐 REQUEST messages for each endpoint test")
    print("   • 📝 FILE CHANGE messages for file operations")
    print("   • 💓 HEARTBEAT messages every 10 seconds")
    print("\nPress Enter to start...")
    input()

    # Test 1: Basic connectivity
    print_banner("TEST 1: BASIC CONNECTIVITY")

    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/stats", "Runtime statistics"),
        ("/constraints", "Σ_LORA constraints"),
    ]

    all_passed = True
    for endpoint, description in endpoints:
        if not test_endpoint(endpoint, description):
            all_passed = False

    if not all_passed:
        print(f"\n❌ Some connectivity tests failed")
        print(
            f"💡 Make sure daemon is running with: python VISIBLE_DAEMON.py --host 127.0.0.1 --port 5001 --watch ."
        )
        return

    # Test 2: File monitoring
    print_banner("TEST 2: FILE MONITORING")
    print("Creating, modifying, and deleting a test file...")
    print("Watch daemon terminal for 'FILE CHANGE' messages")

    create_test_file()

    # Test 3: Continuous activity
    print_banner("TEST 3: CONTINUOUS ACTIVITY")
    print("Sending requests every 3 seconds for 30 seconds...")
    print("Watch daemon terminal for 'HEARTBEAT' and 'REQUEST' messages")

    continuous_test()

    # Final summary
    print_banner("TEST COMPLETE")
    print("\n✅ VISIBILITY CONFIRMED!")
    print("\nWhat you should have seen in the daemon terminal:")
    print("  1. 🌐 REQUEST messages for each endpoint test")
    print("  2. 📝 FILE CHANGE messages (created/modified/deleted)")
    print("  3. 💓 HEARTBEAT messages every 10 seconds")
    print("  4. ✓ Validation messages for Σ_LORA constraints")
    print("\n🎯 DAEMON VISIBILITY IS WORKING!")
    print("\nTo keep daemon running: Leave the daemon terminal open")
    print("To stop daemon: Press Ctrl+C in the daemon terminal")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

    print("\nPress Enter to exit...")
    input()
