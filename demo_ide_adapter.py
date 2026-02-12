"""
Demonstration Script for IDE Adapter System

This script demonstrates the complete IDE Adapter system as implemented
according to PHASE 1-4 ATOMIC EXECUTION requirements.

The system includes:
1. Registry initialization and loading
2. Query routing with priority logic
3. Trace generation and logging
4. Session management
5. Scoped context enforcement
"""

import json
import os
import sys
from datetime import datetime

# Add current directory to path to import ide_adapter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ide_adapter import IDEAdapter, route_ide_query


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def demonstrate_registry_loading():
    """Demonstrate registry loading and inspection."""
    print_header("1. REGISTRY LOADING & INSPECTION")

    # Initialize adapter
    workspace = os.path.dirname(os.path.abspath(__file__))
    adapter = IDEAdapter(workspace)

    # Get session info
    session_info = adapter.get_session_info()

    print(f"📁 Workspace: {session_info['workspace_root']}")
    print(f"💻 IDE: {session_info['ide_name']}")
    print(f"🔑 Session ID: {session_info['session_id']}")
    print(f"👥 Total Wardens: {session_info['total_wardens']}")

    # List available wardens
    print("\n📋 Available Wardens:")
    print("-" * 40)

    wardens = adapter.registry.get("wardens", {})
    for warden_id, warden_data in wardens.items():
        folder_path = warden_data.get("folder_path", "N/A")
        status = warden_data.get("status", "unknown")
        print(f"  • {warden_id}")
        print(f"    └─ Folder: {folder_path}")
        print(f"    └─ Status: {status}")

    print("\n✅ Registry loaded successfully in READ-ONLY mode")
    print("   (Non-negotiable: DO NOT overwrite .ai_registry.json)")


def demonstrate_routing_logic():
    """Demonstrate query routing logic."""
    print_header("2. QUERY ROUTING LOGIC")

    workspace = os.path.dirname(os.path.abspath(__file__))
    adapter = IDEAdapter(workspace)

    print("Routing Priority:")
    print("1. 📁 Explicit folder path → matching warden")
    print("2. 📄 File path → owning folder's warden")
    print("3. 🔤 Keyword match → single warden only")
    print("4. ❓ No match → dynamic warden")
    print("5. 🚫 Still ambiguous → REJECT")
    print("\nKeyword conflict rule: If keywords match >1 warden → REJECT")

    # Test cases
    test_cases = [
        {
            "description": "📁 Folder path match (Priority 1)",
            "query": "What's in the automation folder?",
            "metadata": {"folder_path": "automation"}
        },
        {
            "description": "📄 File path match (Priority 2)",
            "query": "Fix this file",
            "metadata": {"file_path": "toolkit/oe/autofix_engine.py"}
        },
        {
            "description": "🔤 Keyword match (Priority 3)",
            "query": "How do I use the automation tools?",
            "metadata": {}
        },
        {
            "description": "🚫 Ambiguous keyword (REJECT)",
            "query": "automation documentation logs",
            "metadata": {}
        },
        {
            "description": "❓ General query → dynamic warden (Priority 4)",
            "query": "How does this system work?",
            "metadata": {}
        },
        {
            "description": "🚫 No match found (Priority 5)",
            "query": "Random unrelated query",
            "metadata": {}
        }
    ]

    for test in test_cases:
        print(f"\n{test['description']}")
        print(f"  Query: \"{test['query']}\"")

        result = adapter.route_query(test["query"], test.get("metadata"))

        status_emoji = "✅" if result["status"] == "success" else "❌"
        print(f"  Result: {status_emoji} {result['status'].upper()}")
        print(f"  Warden: {result['warden_id'] or 'None'}")
        print(f"  Reason: {result['reason']}")

        # Show trace file location
        trace_file = os.path.join(workspace, "logs", "traces", f"ide_query_{result['trace_id']}.json")
        if os.path.exists(trace_file):
            print(f"  Trace: {trace_file}")


def demonstrate_trace_generation():
    """Demonstrate trace generation and logging."""
    print_header("3. TRACE GENERATION & LOGGING")

    workspace = os.path.dirname(os.path.abspath(__file__))
    adapter = IDEAdapter(workspace)

    # Make a query to generate a trace
    query = "Demonstrate trace generation"
    metadata = {
        "demo": True,
        "purpose": "Trace generation demonstration"
    }

    print("Making query to generate trace...")
    result = adapter.route_query(query, metadata)

    trace_id = result["trace_id"]
    trace_file = os.path.join(workspace, "logs", "traces", f"ide_query_{trace_id}.json")

    print(f"\n📊 Query Result:")
    print(f"  Trace ID: {trace_id}")
    print(f"  Status: {result['status']}")
    print(f"  Warden: {result['warden_id']}")

    print(f"\n📁 Trace File: {trace_file}")

    if os.path.exists(trace_file):
        # Load and display trace content
        with open(trace_file, "r") as f:
            trace_data = json.load(f)

        print("\n📄 Trace Content:")
        print("-" * 40)

        # Show trace structure
        print("Required fields in trace:")
        for field in ["trace_id", "query", "metadata", "result", "timestamp"]:
            if field in trace_data:
                value = trace_data[field]
                if field == "metadata":
                    print(f"  • {field}: {list(value.keys())}")
                elif field == "result":
                    print(f"  • {field}: keys: {list(value.keys())}")
                else:
                    print(f"  • {field}: {value}")

        # Show metadata details
        print("\n📋 Metadata includes:")
        meta = trace_data.get("metadata", {})
        for key, value in meta.items():
            print(f"  • {key}: {value}")

        print("\n✅ Every query generates a trace with:")
        print("   - Unique trace_id (UUID v4)")
        print("   - IDE name and timestamp")
        print("   - Session ID persistence")
        print("   - Complete routing result")


def demonstrate_session_management():
    """Demonstrate session ID generation and persistence."""
    print_header("4. SESSION MANAGEMENT")

    workspace = os.path.dirname(os.path.abspath(__file__))

    print("Session ID Format: <IDE>_<timestamp>_<random>")
    print("  • IDE: IDE name (uppercase)")
    print("  • timestamp: ISO format without colons")
    print("  • random: 8-character hex string")

    # Create multiple adapters to show session persistence
    print("\n🔄 Creating multiple adapter instances:")

    adapters = []
    for i in range(3):
        adapter = IDEAdapter(workspace)
        adapters.append(adapter)
        session_info = adapter.get_session_info()
        print(f"\n  Adapter {i+1}:")
        print(f"    Session ID: {session_info['session_id']}")
        print(f"    IDE: {session_info['ide_name']}")
        print(f"    Workspace: {session_info['workspace_root']}")

    print("\n📝 Key Session Rules:")
    print("  • Generated by IDE at conversation start")
    print("  • Persists for entire IDE session")
    print("  • Each adapter instance gets unique session ID")
    print("  • Same IDE and workspace across instances")

    # Demonstrate session persistence in queries
    print("\n🔗 Session persistence in queries:")
    adapter = adapters[0]

    queries = ["First query", "Second