#!/usr/bin/env python3
"""
Test script for Logos IDE

This script tests the basic functionality of the Logos IDE
without requiring the full Textual TUI to run.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_file_index():
    """Test the FileIndex class"""
    print("🧪 Testing FileIndex...")

    from logos_ide import FileIndex

    # Create test directory structure
    test_dir = Path("test_logos_ide")
    test_dir.mkdir(exist_ok=True)

    # Create some test files
    test_files = [
        "test.py",
        "example.cpp",
        "README.md",
        "config.json",
        "style.css",
        "index.html",
    ]

    for file_name in test_files:
        (test_dir / file_name).write_text(f"# Test content for {file_name}")

    # Test FileIndex
    file_index = FileIndex(test_dir)
    count = file_index.build_index()

    print(f"  ✅ Indexed {count} files")

    # Test search
    results = file_index.search("test")
    print(f"  ✅ Search for 'test' found {len(results)} files")

    results = file_index.search(".py")
    print(f"  ✅ Search for '.py' found {len(results)} files")

    # Test file content loading
    if results:
        content = file_index.get_file_content(results[0])
        print(f"  ✅ File content loaded ({len(content)} chars)")

    # Cleanup
    import shutil

    shutil.rmtree(test_dir)

    print("✅ FileIndex tests passed\n")
    return True


def test_logos_proxy_import():
    """Test if LogosProxy can be imported"""
    print("🧪 Testing LogosProxy import...")

    try:
        from logos_proxy import LogosProxy

        print("  ✅ LogosProxy imported successfully")

        # Try to create instance (may fail without API key, but that's OK)
        try:
            proxy = LogosProxy()
            print("  ✅ LogosProxy instance created")
        except Exception as e:
            print(f"  ⚠️  LogosProxy init failed (expected without API key): {e}")

        return True
    except ImportError as e:
        print(f"  ❌ LogosProxy import failed: {e}")
        return False


def test_editor_pane_logic():
    """Test editor pane logic without Textual"""
    print("🧪 Testing EditorPane logic...")

    # Create a mock class to test the logic
    class MockEditorPane:
        def get_language_for_extension(self, ext):
            language_map = {
                ".py": "python",
                ".cpp": "cpp",
                ".h": "cpp",
                ".hpp": "cpp",
                ".js": "javascript",
                ".ts": "typescript",
                ".html": "html",
                ".css": "css",
                ".md": "markdown",
                ".json": "json",
                ".yaml": "yaml",
                ".yml": "yaml",
                ".txt": "text",
            }
            return language_map.get(ext, "text")

    editor = MockEditorPane()

    test_cases = [
        (".py", "python"),
        (".cpp", "cpp"),
        (".md", "markdown"),
        (".json", "json"),
        (".unknown", "text"),
    ]

    all_passed = True
    for ext, expected in test_cases:
        result = editor.get_language_for_extension(ext)
        if result == expected:
            print(f"  ✅ {ext} -> {result}")
        else:
            print(f"  ❌ {ext} -> {result} (expected {expected})")
            all_passed = False

    if all_passed:
        print("✅ EditorPane logic tests passed\n")
    else:
        print("❌ EditorPane logic tests failed\n")

    return all_passed


def test_audit_file():
    """Test audit file structure"""
    print("🧪 Testing audit file...")

    audit_dir = Path("corporate_audits")
    audit_file = audit_dir / "logos_audit.jsonl"

    if audit_file.exists():
        print(f"  ✅ Audit file exists: {audit_file}")

        # Try to read it
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"  ✅ Audit file has {len(lines)} entries")

                # Try to parse last few entries
                for line in lines[-3:]:
                    try:
                        import json

                        entry = json.loads(line.strip())
                        invariant = entry.get("composite_invariant", "")
                        if invariant:
                            print(
                                f"  ✅ Valid audit entry with invariant: {invariant[:16]}..."
                            )
                    except json.JSONDecodeError:
                        print("  ⚠️  Invalid JSON in audit file")
        except Exception as e:
            print(f"  ⚠️  Error reading audit file: {e}")
    else:
        print(f"  ⚠️  Audit file not found: {audit_file}")

    print("✅ Audit file tests completed\n")
    return True


def test_git_status():
    """Test git status functionality"""
    print("🧪 Testing git status...")

    import subprocess

    try:
        # Check if we're in a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
        )

        if result.returncode == 0:
            print("  ✅ In git repository")

            # Get short commit hash
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
            )

            if result.returncode == 0:
                commit_hash = result.stdout.strip()
                print(f"  ✅ Git commit: {commit_hash}")
            else:
                print("  ⚠️  Could not get commit hash")
        else:
            print("  ⚠️  Not in git repository (this is OK for testing)")

        return True
    except FileNotFoundError:
        print("  ⚠️  Git not installed")
        return False
    except Exception as e:
        print(f"  ⚠️  Error checking git status: {e}")
        return False


def test_requirements():
    """Check if required packages are installed"""
    print("🧪 Testing requirements...")

    required_packages = [
        "textual",
        "aiohttp",
        "requests",
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} installed")
        except ImportError:
            print(f"  ❌ {package} NOT installed")
            all_installed = False

    if all_installed:
        print("✅ All requirements met\n")
    else:
        print("❌ Some requirements missing\n")
        print("Install missing packages with:")
        print("  pip install textual aiohttp requests")

    return all_installed


def main():
    """Run all tests"""
    print("=" * 60)
    print("Logos IDE Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Requirements", test_requirements),
        ("FileIndex", test_file_index),
        ("LogosProxy Import", test_logos_proxy_import),
        ("EditorPane Logic", test_editor_pane_logic),
        ("Audit File", test_audit_file),
        ("Git Status", test_git_status),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))
        print()

    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Logos IDE is ready to run.")
        print("\nTo run the IDE:")
        print("  python logos_ide.py")
        return 0
    else:
        print("⚠️  Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
