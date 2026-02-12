"""
TEST_DAEMON_ACCESS.py
=====================

Simple test script to verify daemon accessibility
Tests if the Self-Automative Master System daemon is accessible
"""

import json
import socket
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_port_access(port: int, service_name: str) -> bool:
    """Test if a port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()

        if result == 0:
            print(f"✅ {service_name} (port {port}): ACCESSIBLE")
            return True
        else:
            print(f"❌ {service_name} (port {port}): NOT ACCESSIBLE")
            return False
    except Exception as e:
        print(f"❌ {service_name} (port {port}): ERROR - {e}")
        return False


def test_simple_daemon():
    """Test the simple working daemon"""
    print("=" * 70)
    print("SELF-AUTOMATIVE MASTER SYSTEM - DAEMON ACCESS TEST")
    print("=" * 70)
    print(f"Test time: {datetime.now().isoformat()}")
    print(f"Project root: {project_root}")
    print("=" * 70)

    # Test standard ports
    ports_to_test = [
        (8080, "Daemon"),
        (8082, "Status Dashboard"),
        (8083, "Formal Integration"),
        (8000, "Alternative Daemon Port"),
        (5000, "Test Port"),
    ]

    print("\n📊 Testing port accessibility:")
    accessible_ports = []

    for port, service in ports_to_test:
        if test_port_access(port, service):
            accessible_ports.append((port, service))

    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)

    if accessible_ports:
        print("✅ Accessible ports found:")
        for port, service in accessible_ports:
            print(f"   • {service}: port {port}")

        print("\n🎉 Daemon accessibility verified!")
        print("\nThe Self-Automative Master System has accessible endpoints.")
        print("You can now:")
        print("1. Test repository activation")
        print("2. Verify formal specifications")
        print("3. Test constraint preservation")
    else:
        print("❌ No accessible ports found")
        print("\n⚠️  Daemon accessibility issues detected.")
        print("\nPossible solutions:")
        print("1. Check if daemon is running: python SIMPLE_WORKING_DAEMON.py")
        print("2. Check Windows Firewall settings")
        print("3. Try different port numbers")
        print("4. Run as administrator")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("1. Start daemon: python SIMPLE_WORKING_DAEMON.py")
    print("2. Test with: python TEST_DAEMON_ACCESS.py")
    print("3. Verify system: python VERIFY_SYSTEM_OPERATION.py")
    print("=" * 70)

    return len(accessible_ports) > 0


def main():
    """Main entry point"""
    success = test_simple_daemon()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
