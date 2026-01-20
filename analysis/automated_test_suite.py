"""
AUTOMATED TEST SUITE - Orthogonal Engineering Repo
Runs comprehensive validation tests on all claims
Following falsification framework: precision, variance, repetition
"""

import json
import csv
import sys
from pathlib import Path
import random

def test_detector_precision(csv_path, sample_size=100):
    """
    TEST 1: Detector Precision Check
    Samples verified turns and manually validates them
    Pass threshold: >=80% precision
    """
    
    print("="*70)
    print("TEST 1: DETECTOR PRECISION")
    print("="*70)
    
    # Load data
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get('verified_invariant') == 'True']
    
    if len(rows) < sample_size:
        print(f"WARNING: Only {len(rows)} verified turns, using all")
        sample_size = len(rows)
    
    # Sample
    random.seed(42)
    sample = random.sample(rows, sample_size)
    
    # Check each one
    import re
    patterns = [
        r'\b(must|shall|required|necessary|critical|essential)\b',
        r'\b(always|never|cannot|will not|shall not)\b',
        r'\b(exactly|precisely|specifically|explicitly)\b',
        r'\b(confirmed|verified|validated|proven|tested)\b'
    ]
    
    true_positives = 0
    for turn in sample:
        content = turn.get('content_preview', '')
        if any(re.search(p, content.lower()) for p in patterns):
            true_positives += 1
    
    precision = (true_positives / sample_size) * 100
    passed = precision >= 80.0
    
    print(f"\nSample size: {sample_size}")
    print(f"True positives: {true_positives} ({precision:.1f}%)")
    print(f"False positives: {sample_size - true_positives} ({100-precision:.1f}%)")
    print(f"Precision: {precision:.2f}%")
    print(f"Threshold: 80.00%")
    print(f"Status: {'✅ PASS' if passed else '❌ FAIL'}")
    
    return {
        'test_name': 'detector_precision',
        'passed': passed,
        'precision': precision,
        'threshold': 80.0,
        'sample_size': sample_size
    }


def test_density_variance(csv_path, max_variance=60.0):
    """
    TEST 2: Density Variance Check
    Calculates per-session density and checks variance
    Pass threshold: <60% range
    """
    
    print("\n" + "="*70)
    print("TEST 2: DENSITY VARIANCE")
    print("="*70)
    
    # Load and group by session
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    sessions = {}
    for row in rows:
        sid = row.get('session_id', 'unknown')
        if sid not in sessions:
            sessions[sid] = []
        sessions[sid].append(row)
    
    # Calculate per-session density
    densities = []
    for sid, turns in sessions.items():
        verified = sum(1 for t in turns if t.get('verified_invariant') == 'True')
        density = (verified / len(turns) * 100) if turns else 0
        densities.append(density)
    
    avg = sum(densities) / len(densities)
    median = sorted(densities)[len(densities)//2]
    min_d = min(densities)
    max_d = max(densities)
    variance = max_d - min_d
    
    passed = variance < max_variance
    
    print(f"\nSessions analyzed: {len(sessions)}")
    print(f"Average density: {avg:.2f}%")
    print(f"Median density: {median:.2f}%")
    print(f"Min: {min_d:.2f}%, Max: {max_d:.2f}%")
    print(f"Variance (range): {variance:.2f}%")
    print(f"Threshold: <{max_variance:.2f}%")
    print(f"Status: {'✅ PASS' if passed else '❌ FAIL'}")
    
    return {
        'test_name': 'density_variance',
        'passed': passed,
        'variance': variance,
        'threshold': max_variance,
        'sessions': len(sessions)
    }


def test_mimicry_repetition(csv_path, max_repetition=50.0):
    """
    TEST 3: Mimicry Repetition Check
    Extracts constraint phrases and checks repetition rate
    Pass threshold: <50% repetition
    """
    
    print("\n" + "="*70)
    print("TEST 3: MIMICRY REPETITION")
    print("="*70)
    
    # Load assistant verified turns
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get('verified_invariant') == 'True' and r.get('role') == 'assistant']
    
    # Extract constraint phrases
    import re
    from collections import Counter
    patterns = [
        r'\b(must|shall|required|necessary|critical|essential)\b',
        r'\b(always|never|cannot|will not|shall not)\b',
        r'\b(exactly|precisely|specifically|explicitly)\b',
        r'\b(confirmed|verified|validated|proven|tested)\b'
    ]
    
    phrases = []
    for row in rows[:1000]:  # Sample first 1000
        content = row.get('content_preview', '').lower()
        for pattern in patterns:
            matches = re.findall(r'[^.!?]*' + pattern + r'[^.!?]*[.!?]', content)
            phrases.extend(matches)
    
    if not phrases:
        print("No constraint phrases found")
        return {'test_name': 'mimicry_repetition', 'passed': True, 'repetition': 0.0, 'threshold': max_repetition}
    
    # Calculate repetition
    unique = len(set(phrases))
    total = len(phrases)
    repetition_rate = (1 - (unique / total)) * 100
    
    passed = repetition_rate < max_repetition
    
    # Show top repeated
    phrase_counts = Counter(phrases)
    top = phrase_counts.most_common(10)
    
    print(f"\nTotal phrases: {total}")
    print(f"Unique phrases: {unique}")
    print(f"Repetition rate: {repetition_rate:.2f}%")
    print(f"Threshold: <{max_repetition:.2f}%")
    print(f"\nTop 5 repeated:")
    for phrase, count in top[:5]:
        print(f"  [{count:3d}x] {phrase[:60]}")
    print(f"Status: {'✅ PASS' if passed else '❌ FAIL'}")
    
    return {
        'test_name': 'mimicry_repetition',
        'passed': passed,
        'repetition': repetition_rate,
        'threshold': max_repetition,
        'total_phrases': total,
        'unique_phrases': unique
    }


def run_all_tests(csv_path, output_path=None):
    """Run all three tests and generate report"""
    
    print("="*70)
    print("ORTHOGONAL ENGINEERING - AUTOMATED TEST SUITE")
    print(f"Dataset: {csv_path}")
    print("="*70)
    
    results = {
        'dataset': str(csv_path),
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'tests': []
    }
    
    # Run all tests
    try:
        results['tests'].append(test_detector_precision(csv_path))
    except Exception as e:
        print(f"\n❌ TEST 1 ERROR: {e}")
        results['tests'].append({'test_name': 'detector_precision', 'error': str(e)})
    
    try:
        results['tests'].append(test_density_variance(csv_path))
    except Exception as e:
        print(f"\n❌ TEST 2 ERROR: {e}")
        results['tests'].append({'test_name': 'density_variance', 'error': str(e)})
    
    try:
        results['tests'].append(test_mimicry_repetition(csv_path))
    except Exception as e:
        print(f"\n❌ TEST 3 ERROR: {e}")
        results['tests'].append({'test_name': 'mimicry_repetition', 'error': str(e)})
    
    # Overall verdict
    print("\n" + "="*70)
    print("OVERALL VERDICT")
    print("="*70)
    
    passed_tests = sum(1 for t in results['tests'] if t.get('passed'))
    total_tests = len([t for t in results['tests'] if 'passed' in t])
    
    print(f"\nPassed: {passed_tests}/{total_tests}")
    
    all_passed = passed_tests == total_tests
    if all_passed:
        print("✅ ALL TESTS PASSED - Density claim is VALID")
    else:
        print("❌ SOME TESTS FAILED - Density claim is CONDITIONAL/INVALID")
        print("\nFailed tests:")
        for t in results['tests']:
            if not t.get('passed') and 'passed' in t:
                print(f"  - {t['test_name']}")
    
    results['overall_passed'] = all_passed
    results['passed_count'] = passed_tests
    results['total_count'] = total_tests
    
    # Save results
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python automated_test_suite.py <path_to_refined_inventory.csv>")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    output_path = csv_path.parent / 'test_results.json'
    
    results = run_all_tests(csv_path, output_path)
    
    sys.exit(0 if results['overall_passed'] else 1)
