#!/usr/bin/env python3
"""
TEST ANTI-GASLIGHTING DETECTOR
Version: 1.0
Schema ID: TEST-ANTI-GASLIGHTING-1.0
Generated: 2026-01-24
Authority: Orthogonal Engineering Glass-Box Boundary

Purpose: Test the anti-gaslighting detector against known attack patterns
Violation Source: [FORGIVENESS_SYSTEM_ATTACK_001]
Fork ID: [TESTING_FORK]
Energy Allocated: BUILD=0.7, FIGHT=0.0

Test Cases:
1. Absorption attack detection (404 vs 1)
2. Decoy violation detection ("You said:")
3. Line number corruption detection
4. Combined attack pattern detection
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import the gaslighting detector
try:
    from comprehensive_fix_v2_simple.gaslighting_detector_simple import (
        SimpleGaslightingDetector,
    )

    print("✅ Successfully imported SimpleGaslightingDetector")
except ImportError as e:
    print(f"❌ Failed to import SimpleGaslightingDetector: {e}")
    sys.exit(1)


def test_absorption_attack():
    """Test detection of absorption through overwhelm attack (404 vs 1)"""
    print("\n" + "=" * 60)
    print("TEST 1: ABSORPTION ATTACK DETECTION (404 vs 1)")
    print("=" * 60)

    detector = SimpleGaslightingDetector()

    # Test the actual attack pattern
    result = detector.detect_absorption_attack(1, 404)

    print(f"Input: reported=1, actual=404")
    print(f"Result: {json.dumps(result, indent=2)}")

    if result.get("attack_detected"):
        print(f"✅ PASS: Correctly detected absorption attack")
        print(f"   Attack Type: {result.get('attack_type')}")
        print(f"   Discrepancy Ratio: {result.get('discrepancy_ratio')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Evidence Hash: {result.get('evidence_hash')[:16]}...")
    else:
        print(f"❌ FAIL: Failed to detect absorption attack")

    # Test edge cases
    print("\n--- Edge Cases ---")

    # Normal case (no attack)
    normal_result = detector.detect_absorption_attack(100, 110)
    print(
        f"Normal case (100 vs 110): Attack detected = {normal_result.get('attack_detected')}"
    )

    # Borderline case
    borderline_result = detector.detect_absorption_attack(10, 105)
    print(
        f"Borderline case (10 vs 105): Attack detected = {borderline_result.get('attack_detected')}"
    )

    # Zero reported (infinite ratio)
    zero_result = detector.detect_absorption_attack(0, 100)
    print(
        f"Zero reported (0 vs 100): Attack detected = {zero_result.get('attack_detected')}"
    )

    return result.get("attack_detected", False)


def test_decoy_violations():
    """Test detection of decoy violations (trivial content marked as violations)"""
    print("\n" + "=" * 60)
    print("TEST 2: DECOY VIOLATION DETECTION")
    print("=" * 60)

    detector = SimpleGaslightingDetector()

    # Test cases
    test_cases = [
        ("You said:", True, "Trivial 'You said:' pattern"),
        ("AI said:", True, "Trivial 'AI said:' pattern"),
        ("User:", True, "Trivial label with no content"),
        ("   ", True, "Whitespace only"),
        (
            "This is an actual violation with substantive content",
            False,
            "Substantive content",
        ),
        (
            "The system violated the boundary by ignoring invariants",
            False,
            "Actual violation text",
        ),
        ("", True, "Empty string"),
        ("---", True, "Separator line"),
    ]

    passed = 0
    total = len(test_cases)

    for text, should_detect, description in test_cases:
        result = detector.detect_decoy_violations(text)
        detected = result.get("attack_detected", False)

        if detected == should_detect:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"

        print(f"{status}: '{text[:30]}...' - {description}")
        if detected:
            print(
                f"       Type: {result.get('attack_type')}, Confidence: {result.get('confidence')}"
            )

    print(f"\nDecoy Detection Score: {passed}/{total} ({passed / total * 100:.1f}%)")
    return passed / total >= 0.8  # 80% accuracy threshold


def test_line_number_corruption():
    """Test detection of line number corruption attacks"""
    print("\n" + "=" * 60)
    print("TEST 3: LINE NUMBER CORRUPTION DETECTION")
    print("=" * 60)

    detector = SimpleGaslightingDetector()

    # Test the actual attack from evidence
    result = detector.detect_line_number_corruption(348201, 348203)

    print(f"Input: reported=348201, actual=348203")
    print(f"Result: {json.dumps(result, indent=2)}")

    if result.get("attack_detected"):
        print(f"✅ PASS: Correctly detected line number corruption")
        print(f"   Attack Type: {result.get('attack_type')}")
        print(f"   Offset: {result.get('offset')} lines")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Evidence Hash: {result.get('evidence_hash')[:16]}...")
    else:
        print(f"❌ FAIL: Failed to detect line number corruption")

    # Test edge cases
    print("\n--- Edge Cases ---")

    # No corruption (same line)
    same_result = detector.detect_line_number_corruption(100, 100)
    print(
        f"No corruption (100 vs 100): Attack detected = {same_result.get('attack_detected')}"
    )

    # Small offset (likely not attack)
    small_result = detector.detect_line_number_corruption(100, 101)
    print(
        f"Small offset (100 vs 101): Attack detected = {small_result.get('attack_detected')}"
    )

    # Large offset (definitely suspicious)
    large_result = detector.detect_line_number_corruption(100, 500)
    print(
        f"Large offset (100 vs 500): Attack detected = {large_result.get('attack_detected')}"
    )

    return result.get("attack_detected", False)


def test_combined_attack_pattern():
    """Test detection of combined attack pattern (404 vs 1 with decoy and line corruption)"""
    print("\n" + "=" * 60)
    print("TEST 4: COMBINED ATTACK PATTERN DETECTION")
    print("=" * 60)

    detector = SimpleGaslightingDetector()

    # Simulate the complete attack
    print("Simulating complete corporate epistemic corruption attack:")
    print("-" * 40)
    print("Attack Components:")
    print("1. Absorption: 1 reported vs 404 actual (404:1 ratio)")
    print("2. Decoy: 'You said:' marked as violation")
    print("3. Line Corruption: 348201 reported vs 348203 actual")
    print("-" * 40)

    # Run all detectors
    absorption_result = detector.detect_absorption_attack(1, 404)
    decoy_result = detector.detect_decoy_violations("You said:")
    line_result = detector.detect_line_number_corruption(348201, 348203)

    attacks_detected = [
        absorption_result.get("attack_detected", False),
        decoy_result.get("attack_detected", False),
        line_result.get("attack_detected", False),
    ]

    total_attacks = len(attacks_detected)
    detected_attacks = sum(attacks_detected)

    print(f"\nDetection Results:")
    print(
        f"  Absorption Attack: {'✅ DETECTED' if attacks_detected[0] else '❌ MISSED'}"
    )
    print(f"  Decoy Violation: {'✅ DETECTED' if attacks_detected[1] else '❌ MISSED'}")
    print(f"  Line Corruption: {'✅ DETECTED' if attacks_detected[2] else '❌ MISSED'}")
    print(f"\nOverall: {detected_attacks}/{total_attacks} attacks detected")

    # Calculate attack confidence
    confidences = [
        absorption_result.get("confidence", 0),
        decoy_result.get("confidence", 0),
        line_result.get("confidence", 0),
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    print(f"Average Confidence: {avg_confidence:.2f}")

    if detected_attacks >= 2:  # At least 2 out of 3 attacks detected
        print(f"\n✅ PASS: Combined attack pattern successfully detected")
        return True
    else:
        print(f"\n❌ FAIL: Insufficient attack pattern detection")
        return False


def load_and_validate_evidence():
    """Load and validate the cryptographic evidence chain"""
    print("\n" + "=" * 60)
    print("TEST 5: EVIDENCE CHAIN VALIDATION")
    print("=" * 60)

    evidence_path = (
        Path(__file__).parent
        / "comprehensive_fix_v2_simple"
        / "EVIDENCE_CORPORATE_EPISTEMIC_CORRUPTION_404_vs_1.json"
    )

    if not evidence_path.exists():
        print(f"❌ FAIL: Evidence file not found at {evidence_path}")
        return False

    try:
        with open(evidence_path, "r", encoding="utf-8") as f:
            evidence = json.load(f)

        print(f"✅ Evidence file loaded: {evidence_path}")
        print(f"   Report ID: {evidence.get('report_id', 'N/A')}")
        print(f"   Generated: {evidence.get('generated', 'N/A')}")

        # Validate evidence chain
        evidence_chain = evidence.get("evidence_chain", [])
        print(f"   Evidence Chain Length: {len(evidence_chain)} items")

        # Check critical evidence items
        critical_items = [
            ("EVIDENCE_002", "false_analysis", "1 violation reported"),
            ("EVIDENCE_003", "true_analysis", "404 violations found"),
            ("EVIDENCE_004", "discrepancy", "404:1 ratio"),
        ]

        found_items = 0
        for item_id, item_type, description in critical_items:
            for item in evidence_chain:
                if item.get("evidence_id") == item_id and item.get("type") == item_type:
                    print(f"   ✅ Found {item_id}: {description}")
                    found_items += 1
                    break
            else:
                print(f"   ❌ Missing {item_id}: {description}")

        # Validate integrity hashes
        hash_valid = all("integrity_hash" in item for item in evidence_chain)
        print(
            f"   Integrity Hashes: {'✅ ALL PRESENT' if hash_valid else '❌ MISSING'}"
        )

        # Check attack patterns
        attack_patterns = evidence.get("attack_patterns", [])
        print(f"   Attack Patterns Documented: {len(attack_patterns)}")

        if found_items >= 2 and hash_valid and len(attack_patterns) >= 1:
            print(f"\n✅ PASS: Evidence chain is valid and complete")
            return True
        else:
            print(f"\n❌ FAIL: Evidence chain validation failed")
            return False

    except Exception as e:
        print(f"❌ FAIL: Error loading evidence: {e}")
        return False


def main():
    """Main test execution"""
    print("=" * 80)
    print("ANTI-GASLIGHTING DETECTOR TEST SUITE")
    print("=" * 80)
    print("Testing against corporate epistemic corruption attack patterns")
    print("Based on evidence: 404 violations vs 1 false positive")
    print("=" * 80)

    test_results = []

    # Run all tests
    test_results.append(("Absorption Attack", test_absorption_attack()))
    test_results.append(("Decoy Violations", test_decoy_violations()))
    test_results.append(("Line Number Corruption", test_line_number_corruption()))
    test_results.append(("Combined Attack Pattern", test_combined_attack_pattern()))
    test_results.append(("Evidence Chain Validation", load_and_validate_evidence()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("The anti-gaslighting detector successfully identifies")
        print("corporate epistemic corruption attacks.")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print("⚠️  SOME TESTS FAILED")
        print("The anti-gaslighting detector needs improvement.")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
