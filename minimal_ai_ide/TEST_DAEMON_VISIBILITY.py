#!/usr/bin/env python3
"""
DAEMON VISIBILITY TESTER
Generates traffic to show daemon activity in real-time
"""

import requests
import time
import sys
from pathlib import Path

DAEMON_URL = "http://127.0.0.1:5001"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_endpoint(endpoint, description):
    """Test an endpoint and show result"""
    url = f"{DAEMON_URL}{endpoint}"
    print(f"\n→ Testing: {description}")
    print(f"  URL: {url}")
    
    try:
        response = requests.get(url, timeout=3)
        print(f"  ✓ Status: {response.status_code}")
        
        if response.headers.get('content-type') == 'application/json':
            data = response.json()
            print(f"  📄 Response: {data}")
        
        return True
    except requests.exceptions.ConnectionError:
        print(f"  ✗ ERROR: Cannot connect - is daemon running?")
        return False
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def create_file_changes(watch_dir):
    """Create file changes to trigger monitoring"""
    watch_path = Path(watch_dir)
    test_file = watch_path / "DAEMON_TEST_TRIGGER.txt"
    
    print(f"\n→ Creating file change in watched directory")
    print(f"  Path: {test_file}")
    
    try:
        with open(test_file, 'w') as f:
            f.write(f"Test change at {time.strftime('%H:%M:%S')}\n")
        print(f"  ✓ File created - check daemon terminal for detection")
        time.sleep(1)
        
        # Modify it
        with open(test_file, 'a') as f:
            f.write(f"Modified at {time.strftime('%H:%M:%S')}\n")
        print(f"  ✓ File modified - check daemon terminal")
        time.sleep(1)
        
        # Delete it
        test_file.unlink()
        print(f"  ✓ File deleted - check daemon terminal")
        
        return True
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False

def continuous_heartbeat_test(duration=30):
    """Send requests continuously to show daemon activity"""
    print(f"\n→ Sending requests for {duration} seconds...")
    print(f"  Watch the daemon terminal for activity!")
    
    start = time.time()
    request_count = 0
    
    try:
        while time.time() - start < duration:
            try:
                response = requests.get(f"{DAEMON_URL}/health", timeout=1)
                request_count += 1
                elapsed = int(time.time() - start)
                print(f"  [{elapsed}s] Request #{request_count} → {response.status_code}", end='\r')
                time.sleep(2)
            except:
                print(f"  ✗ Connection lost                    ", end='\r')
                break
        
        print(f"\n  ✓ Sent {request_count} requests in {int(time.time() - start)} seconds")
        return True
    except KeyboardInterrupt:
        print(f"\n  ⚠ Interrupted by user")
        return False

def main():
    print_header("DAEMON VISIBILITY TESTER")
    print("\nThis script will:")
    print("  1. Test all daemon endpoints")
    print("  2. Trigger file change detection")
    print("  3. Send continuous requests")
    print("\n👁️  WATCH THE DAEMON TERMINAL for real-time activity!")
    input("\nPress Enter to start testing...")
    
    # Test endpoints
    print_header("ENDPOINT TESTS")
    
    endpoints = [
        ('/', 'Root endpoint'),
        ('/health', 'Health check'),
        ('/constraints', 'Σ_LORA constraints'),
        ('/stats', 'Statistics'),
    ]
    
    daemon_alive = False
    for endpoint, description in endpoints:
        if test_endpoint(endpoint, description):
            daemon_alive = True
        time.sleep(1)
    
    if not daemon_alive:
        print("\n❌ DAEMON NOT RESPONDING")
        print("\nMake sure to:")
        print("  1. Run RUN_VISIBLE_DAEMON.bat")
        print("  2. Wait for 'DAEMON IS NOW VISIBLE' message")
        print("  3. Then run this test script")
        sys.exit(1)
    
    # File change test
    print_header("FILE CHANGE DETECTION TEST")
    print("\n⚠️  This requires the daemon to be watching a directory")
    
    if input("\nTrigger file changes? (y/n): ").lower() == 'y':
        watch_dir = input("Enter watch directory path (or press Enter for current): ").strip()
        if not watch_dir:
            watch_dir = "."
        create_file_changes(watch_dir)
    
    # Continuous test
    print_header("CONTINUOUS ACTIVITY TEST")
    
    if input("\nSend continuous requests? (y/n): ").lower() == 'y':
        continuous_heartbeat_test(30)
    
    # Final stats
    print_header("FINAL STATISTICS")
    if test_endpoint('/stats', 'Get final daemon stats'):
        print("\n✓ Visibility test complete!")
        print("\n👁️  Check the daemon terminal to see all logged activity")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
