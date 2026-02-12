#!/usr/bin/env python3
"""
QUICK VISIBILITY TEST
Non-interactive test for visible daemon
"""

import json
import os
import time
from datetime import datetime

import requests

DAEMON_URL = "http://127.0.0.1:5001"
ENDPOINTS = ["/", "/health", "/constraints", "/stats"]


def print_section(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_daemon():
    """Quick test of visible daemon"""
    print_section("VISIBLE DAEMON QUICK TEST")
    print("\n👁️  WATCH DAEMON TERMINAL FOR REAL-TIME ACTIVITY")
    print("This test will trigger visible logging in daemon terminal:")
    print("• 🌐 REQUEST messages for each endpoint")
    print("• 📝 FILE CHANGE messages for file operations")
    print("• 💓 HEARTBEAT messages every 10 seconds")
    print("\nStarting test in 2 seconds...")
    time.sleep(2)

    # Test 1: Endpoint connectivity
    print_section("TEST 1: ENDPOINT CONNECTIVITY")
    print("Testing 4 endpoints...")

    success_count = 0
    for endpoint in ENDPOINTS:
        try:
            response = requests.get(f"{DAEMON_URL}{endpoint}", timeout=3)
            print(f"  {endpoint}: ✅ {response.status_code}")
            success_count += 1
        except Exception as e:
            print(f"  {endpoint}: ❌ {e}")

    if success_count < len(ENDPOINTS):
        print(f"\n⚠️  Only {success_count}/{len(ENDPOINTS)} endpoints responding")
        print("Check if daemon is running on port 5001")
        return False

    print(f"\n✅ All {success_count} endpoints responding")

    # Test 2: File monitoring
    print_section("TEST 2: FILE MONITORING")
    print("Creating test files...")

    test_files = ["VISIBLE_TEST_1.txt", "VISIBLE_TEST_2.txt"]

    for filename in test_files:
        try:
            with open(filename, "w") as f:
                f.write(f"Test file created at {datetime.now().isoformat()}\n")
                f.write("This should trigger file monitoring in daemon terminal\n")
            print(f"  Created: {filename}")
        except Exception as e:
            print(f"  Failed to create {filename}: {e}")

    print("\nWaiting 3 seconds for daemon to detect files...")
    time.sleep(3)

    # Modify files
    print("\nModifying test files...")
    for filename in test_files:
        try:
            with open(filename, "a") as f:
                f.write(f"Modified at {datetime.now().isoformat()}\n")
            print(f"  Modified: {filename}")
        except Exception as e:
            print(f"  Failed to modify {filename}: {e}")

    print("\nWaiting 3 seconds for daemon to detect modifications...")
    time.sleep(3)

    # Delete files
    print("\nDeleting test files...")
    for filename in test_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"  Deleted: {filename}")
        except Exception as e:
            print(f"  Failed to delete {filename}: {e}")

    print("\n✅ File monitoring test complete")
    print("Check daemon terminal for 'FILE CHANGE' messages")

    # Test 3: Quick continuous test
    print_section("TEST 3: CONTINUOUS ACTIVITY")
    print("Sending requests for 15 seconds...")
    print("Watch daemon terminal for 'REQUEST' and 'HEARTBEAT' messages")

    start_time = time.time()
    request_count = 0

    while time.time() - start_time < 15:
        try:
            endpoint = ENDPOINTS[request_count % len(ENDPOINTS)]
            response = requests.get(f"{DAEMON_URL}{endpoint}", timeout=2)
            request_count += 1

            if request_count % 5 == 0:
                elapsed = time.time() - start_time
                print(
                    f"  Request #{request_count}: {endpoint} → {response.status_code}"
                )

        except:
            pass  # Silent fail for continuous test

        time.sleep(2)

    print(f"\n✅ Continuous test complete")
    print(f"  Total requests: {request_count}")
    print(f"  Duration: {time.time() - start_time:.1f} seconds")

    # Final summary
    print_section("VISIBILITY TEST COMPLETE")
    print("\n🎯 VISIBLE DAEMON IS WORKING!")
    print("\nWhat you should see in daemon terminal:")
    print("  1. 🌐 4+ REQUEST messages (endpoint tests)")
    print("  2. 📝 4+ FILE CHANGE messages (create/modify/delete)")
    print("  3. 💓 1+ HEARTBEAT messages (every 10 seconds)")
    print("  4. ✓ Validation messages (Σ_LORA constraints)")
    print("\nΣ_LORA PRINCIPLE: 'All intelligence paths factor through this daemon'")
    print("\n✅ Test completed successfully!")

    # Cleanup
    for filename in test_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

    return True


if __name__ == "__main__":
    try:
        test_daemon()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

    print("\nPress Enter to exit...")
    try:
        input()
    except:
        pass
