"""
TEST_DAEMON_CONNECTIVITY.py
===========================

Simple connectivity test for the Local AI Daemon.
Tests if the daemon is accessible on various ports and provides
diagnostic information about Windows networking issues.
"""

import os
import socket
import subprocess
import sys
import time
from datetime import datetime

import requests


def test_port(host="127.0.0.1", port=5000, timeout=2):
    """Test if a port is open and accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"  ❌ Socket error on port {port}: {e}")
        return False


def test_http_endpoint(host="127.0.0.1", port=5000, endpoint="/", timeout=3):
    """Test if HTTP endpoint responds"""
    url = f"http://{host}:{port}{endpoint}"
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "success": True,
            "status_code": response.status_code,
            "response": response.text[:200] if response.text else "",
            "url": url,
        }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection refused", "url": url}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout", "url": url}
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}


def check_windows_firewall():
    """Check Windows firewall status"""
    print("\n🔍 Checking Windows Firewall...")
    try:
        # Check if firewall is enabled
        result = subprocess.run(
            ["netsh", "advfirewall", "show", "allprofiles", "state"],
            capture_output=True,
            text=True,
            shell=True,
        )

        firewall_status = result.stdout
        if "ON" in firewall_status:
            print("  ⚠️  Windows Firewall is ON (may block connections)")

            # Check for Python exceptions
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
                capture_output=True,
                text=True,
                shell=True,
            )

            python_rules = [
                line for line in result.stdout.split("\n") if "python" in line.lower()
            ]
            if python_rules:
                print(f"  ✅ Found {len(python_rules)} Python firewall rules")
            else:
                print(
                    "  ❌ No Python firewall rules found (connections may be blocked)"
                )
        else:
            print("  ✅ Windows Firewall is OFF")

    except Exception as e:
        print(f"  ⚠️  Could not check firewall: {e}")


def check_listening_ports():
    """Check which ports are currently listening"""
    print("\n🔍 Checking listening ports...")
    try:
        # Use netstat to find listening ports
        result = subprocess.run(
            ["netstat", "-an", "-p", "TCP"], capture_output=True, text=True, shell=True
        )

        listening_ports = []
        for line in result.stdout.split("\n"):
            if "LISTENING" in line and "127.0.0.1" in line:
                parts = line.split()
                if len(parts) > 1:
                    addr = parts[1]
                    if ":" in addr:
                        port = int(addr.split(":")[-1])
                        listening_ports.append(port)

        print(f"  Found {len(listening_ports)} ports listening on localhost:")
        for port in sorted(listening_ports):
            print(f"    • Port {port}")

        return listening_ports

    except Exception as e:
        print(f"  ⚠️  Could not check listening ports: {e}")
        return []


def test_daemon_ports():
    """Test common daemon ports"""
    print("\n🔌 Testing daemon ports...")

    ports_to_test = [5000, 8080, 8000, 3000, 5001, 8081]

    for port in ports_to_test:
        print(f"\n  Testing port {port}:")
        if test_port("127.0.0.1", port):
            print(f"    ✅ Port {port} is OPEN")

            # Test HTTP endpoint
            http_result = test_http_endpoint(port=port)
            if http_result["success"]:
                print(
                    f"    ✅ HTTP endpoint responds (Status: {http_result['status_code']})"
                )
                print(f"    📄 Response preview: {http_result['response'][:100]}...")
            else:
                print(f"    ⚠️  Port open but HTTP failed: {http_result['error']}")
        else:
            print(f"    ❌ Port {port} is CLOSED or not listening")


def test_external_connectivity():
    """Test if external connections work"""
    print("\n🌐 Testing external connectivity...")

    # Test localhost
    print("  Testing localhost connectivity:")
    if test_port("127.0.0.1", 80, timeout=1):
        print("    ✅ Can connect to localhost:80")
    else:
        print("    ⚠️  Cannot connect to localhost:80")

    # Test if we can bind to a port
    print("\n  Testing port binding capability:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))  # Bind to any available port
        port = sock.getsockname()[1]
        sock.close()
        print(f"    ✅ Can bind to port {port}")
    except Exception as e:
        print(f"    ❌ Cannot bind to ports: {e}")


def run_comprehensive_test():
    """Run comprehensive connectivity test"""
    print("=" * 60)
    print("DAEMON CONNECTIVITY TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.version}")
    print("=" * 60)

    # Check Windows firewall
    check_windows_firewall()

    # Check listening ports
    listening_ports = check_listening_ports()

    # Test daemon ports
    test_daemon_ports()

    # Test external connectivity
    test_external_connectivity()

    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    if 5000 in listening_ports or 8080 in listening_ports:
        print("✅ Daemon appears to be running!")
        print("\nTo test the daemon manually:")
        print("1. Open browser to http://127.0.0.1:5000/")
        print("2. Or run: curl http://127.0.0.1:5000/health")
        print("\nIf connection fails, try:")
        print("• Run as Administrator")
        print("• Check Windows Defender Firewall")
    else:
        print("❌ Daemon not detected on common ports")
        print("\nTROUBLESHOOTING STEPS:")
        print("1. Start the daemon: python SIMPLE_WORKING_DAEMON.py --windows-mode")
        print("2. Run as Administrator to bypass firewall")
        print("3. Check if another process is using port 5000:")
        print("   netstat -ano | findstr :5000")
        print("4. Try alternative port: python SIMPLE_WORKING_DAEMON.py --port 5001")

    print("\n" + "=" * 60)
    print("QUICK FIXES")
    print("=" * 60)
    print("To add firewall rule for Python:")
    print(
        '''netsh advfirewall firewall add rule name="Python Daemon" dir=in action=allow protocol=TCP localport=5000 program="%PYTHONPATH%\\python.exe"'''
    )
    print("\nTo check current firewall rules:")
    print('netsh advfirewall firewall show rule name="Python Daemon"')

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        run_comprehensive_test()

        # Ask user if they want to try starting the daemon
        print("\nWould you like to try starting the daemon now? (y/n): ", end="")
        response = input().strip().lower()

        if response == "y":
            print("\n🚀 Starting daemon in test mode...")
            print("Press Ctrl+C to stop the daemon")
            print("-" * 40)

            # Start daemon in subprocess
            daemon_script = "SIMPLE_WORKING_DAEMON.py"
            if os.path.exists(daemon_script):
                try:
                    import subprocess

                    process = subprocess.Popen(
                        ["python", daemon_script, "--windows-mode"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                    )

                    # Read output for a few seconds
                    print("Daemon output (first 10 seconds):")
                    print("-" * 40)
                    for _ in range(10):
                        line = process.stdout.readline()
                        if line:
                            print(line.strip())
                        time.sleep(1)

                    print("\n" + "-" * 40)
                    print("Stopping test daemon...")
                    process.terminate()

                except Exception as e:
                    print(f"Failed to start daemon: {e}")
            else:
                print(f"Daemon script not found: {daemon_script}")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

    print("\nPress Enter to exit...")
    input()
