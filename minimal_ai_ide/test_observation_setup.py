"""
TEST OBSERVATION SETUP
Quick test to verify observation system is properly configured
"""

import json
import os
import sys
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"🎯 {title}")
    print("=" * 70)


def test_directory_structure():
    """Test that directory structure exists"""
    print_header("TEST 1: DIRECTORY STRUCTURE")

    required_dirs = [
        "observations",
        "observation_reports",
        "stability_metrics",
        "weekly_reviews",
    ]

    all_exist = True
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ (missing)")
            all_exist = False

    return all_exist


def test_required_files():
    """Test that required files exist"""
    print_header("TEST 2: REQUIRED FILES")

    required_files = [
        "CLOSED_LOOP_OBSERVATION_PROTOCOL.md",
        "observation_runner.py",
        "analyze_observation_data.py",
        "check_stability.py",
        "initialize_observation.py",
        "run_daily_observations.py",
        "OBSERVATION_README.md",
        "observation_config.json",
    ]

    all_exist = True
    for filename in required_files:
        if Path(filename).exists():
            print(f"✅ {filename}")
        else:
            print(f"❌ {filename} (missing)")
            all_exist = False

    return all_exist


def test_config_file():
    """Test that config file is valid"""
    print_header("TEST 3: CONFIGURATION FILE")

    config_path = Path("observation_config.json")
    if not config_path.exists():
        print("❌ Config file not found")
        return False

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        required_keys = ["protocol", "phase", "goal", "feature_freeze"]
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing key in config: {key}")
                return False

        print(f"✅ Config file valid")
        print(f"   Protocol: {config.get('protocol')}")
        print(f"   Phase: {config.get('phase')}")
        print(f"   Goal: {config.get('goal')}")
        print(f"   Feature Freeze: {config.get('feature_freeze')}")

        return True

    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False


def test_imports():
    """Test that scripts can be imported"""
    print_header("TEST 4: SCRIPT IMPORTS")

    scripts_to_test = [
        "observation_runner.py",
        "analyze_observation_data.py",
        "check_stability.py",
    ]

    all_imported = True

    for script in scripts_to_test:
        if not Path(script).exists():
            print(f"❌ {script} not found")
            all_imported = False
            continue

        try:
            # Try to import the module
            import importlib.util

            spec = importlib.util.spec_from_file_location("test_module", script)
            module = importlib.util.module_from_spec(spec)

            # Don't actually execute, just check syntax
            with open(script, "r", encoding="utf-8") as f:
                content = f.read()
                compile(content, script, "exec")

            print(f"✅ {script} (syntax OK)")

        except SyntaxError as e:
            print(f"❌ {script} syntax error: {e}")
            all_imported = False
        except Exception as e:
            print(f"⚠️  {script} import warning: {e}")
            # Not fatal, just a warning

    return all_imported


def test_protocol_documentation():
    """Test that protocol documentation exists"""
    print_header("TEST 5: PROTOCOL DOCUMENTATION")

    protocol_path = Path("CLOSED_LOOP_OBSERVATION_PROTOCOL.md")
    if not protocol_path.exists():
        print("❌ Protocol document not found")
        return False

    try:
        with open(protocol_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for key sections
        key_sections = [
            "CLOSED-LOOP OBSERVATION PROTOCOL",
            "WHAT WE DO NOT DO",
            "WHAT WE DO",
            "OBSERVATION PROTOCOL",
        ]

        missing_sections = []
        for section in key_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            print(f"❌ Missing sections: {', '.join(missing_sections)}")
            return False

        print(f"✅ Protocol document complete")
        print(f"   Size: {len(content)} characters")
        print(
            f"   Key sections present: {len(key_sections) - len(missing_sections)}/{len(key_sections)}"
        )

        return True

    except Exception as e:
        print(f"❌ Error reading protocol: {e}")
        return False


def generate_setup_summary():
    """Generate setup summary"""
    print_header("🎯 OBSERVATION SYSTEM SETUP SUMMARY")

    # Count observations if any exist
    obs_dir = Path("observations")
    observation_count = 0
    if obs_dir.exists():
        observation_count = len(list(obs_dir.glob("*.json")))

    # Count reports
    reports_dir = Path("observation_reports")
    report_count = 0
    if reports_dir.exists():
        report_count = len(list(reports_dir.glob("*.json")))

    print(f"\n📊 SYSTEM STATUS:")
    print(f"  Observations collected: {observation_count}")
    print(f"  Analysis reports: {report_count}")
    print(f"  Days of data: {'None' if observation_count == 0 else 'Some'}")

    print(f"\n🚀 READY FOR OBSERVATION:")
    print(f"  {'✅ YES' if observation_count == 0 else '⚠️  ALREADY STARTED'}")

    print(f"\n📋 NEXT STEPS:")
    if observation_count == 0:
        print("  1. Start API server: python stage4_deployment.py --mode server")
        print(
            "  2. Run first observation: python observation_runner.py --platforms chat.openai.com --count 2"
        )
        print("  3. Set up daily: python run_daily_observations.py")
    else:
        print("  1. Continue daily observations")
        print("  2. Run weekly analysis: python analyze_observation_data.py --days 7")
        print("  3. Check stability: python check_stability.py")

    print(f"\n🚨 CRITICAL REMINDERS:")
    print("  • This is OBSERVATION, NOT optimization")
    print("  • Goal: Stability under repeated contact")
    print("  • DO NOT adjust system based on observations")
    print("  • Microscope, not megaphone")
    print("  • Diagnostic instrument, not belief engine")

    return True


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("🔬 TESTING OBSERVATION SYSTEM SETUP")
    print("=" * 70)
    print("Verifying closed-loop observation protocol configuration")
    print("=" * 70)

    # Run all tests
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Required Files", test_required_files),
        ("Configuration File", test_config_file),
        ("Script Imports", test_imports),
        ("Protocol Documentation", test_protocol_documentation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Generate summary
    print_header("📊 TEST RESULTS SUMMARY")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\nTests passed: {passed_count}/{total_count}")

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")

    # Generate setup summary
    generate_setup_summary()

    print("\n" + "=" * 70)
    print("🔬 TEST COMPLETE")
    print("=" * 70)

    if passed_count == total_count:
        print("✅ All tests passed! Observation system is ready.")
        return 0
    else:
        print(f"⚠️  {total_count - passed_count} test(s) failed. Review and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
