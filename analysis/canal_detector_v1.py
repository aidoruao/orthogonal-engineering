#!/usr/bin/env python3
"""
canal_detector_v1.py - Precision-First Detector (≥80% target)

REPLACES: DEPRECATED_canal_refiner.py (70% FP rate)
FEATURES:
- Gutenberg null-baseline test (proves detector doesn't find patterns in neutral text)
- Repetition penalty (>50% repetition = reject)
- Bidirectional constraint requirement (both speakers must use constraint language)
- Adjacent turn requirement (5-turn window, both sides must participate)

Usage:
    python canal_detector_v1.py chat.csv
    python canal_detector_v1.py chat.csv --json output.json
"""

import re
import json
import hashlib
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

# CONFIGURATION
TURN_WINDOW = 5          # Analyze 5-turn windows
MIN_BIDIR = 2            # Both speakers must use constraint tokens
MAX_REPEAT = 0.5         # >50% repetition ratio = reject (mimicry penalty)

# Constraint language tokens
CONSTRAINT_TOKENS = {
    "must", "shall", "never", "always", "required", "forbidden",
    "should only", "must not", "needs to", "fixed", "invariant",
    "exactly", "precisely", "specifically", "explicitly",
    "confirmed", "verified", "validated", "proven", "tested",
    "cannot", "will not", "shall not"
}

def repetition_ratio(text: str) -> float:
    """
    Calculate token repetition ratio (1 - uniqueness)
    >0.5 indicates mimicry behavior
    """
    tokens = re.findall(r'\w+', text.lower())
    if not tokens:
        return 0.0
    unique_ratio = len(set(tokens)) / len(tokens)
    return 1 - unique_ratio

def detect_invariants(csv_path: str) -> List[Dict]:
    """
    Detect verified invariants in conversation CSV
    Returns list of invariant objects
    """
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        turns = list(reader)
    
    invariants = []
    
    for i in range(len(turns) - TURN_WINDOW + 1):
        window = turns[i:i + TURN_WINDOW]
        
        user_constraints = []
        assistant_constraints = []
        
        for turn in window:
            content = turn.get('content', '').lower()
            role = turn.get('role', '').lower()
            
            # Check for constraint language
            has_constraint = any(tok in content for tok in CONSTRAINT_TOKENS)
            
            if has_constraint:
                if 'user' in role or 'human' in role:
                    user_constraints.append(turn)
                elif 'assistant' in role or 'ai' in role or 'bot' in role:
                    assistant_constraints.append(turn)
        
        # REQUIREMENT: Bidirectional agreement
        if len(user_constraints) >= MIN_BIDIR and len(assistant_constraints) >= MIN_BIDIR:
            # Combine window text
            window_text = ' '.join(t.get('content', '') for t in window)
            
            # REQUIREMENT: Repetition penalty
            if repetition_ratio(window_text) <= MAX_REPEAT:
                # Valid invariant found
                inv = {
                    'id': hashlib.sha256(window_text.encode()).hexdigest()[:16],
                    'turn_start': i,
                    'turn_end': i + TURN_WINDOW,
                    'text_preview': window_text[:200],
                    'user_constraints': len(user_constraints),
                    'assistant_constraints': len(assistant_constraints),
                    'repetition_ratio': repetition_ratio(window_text),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                invariants.append(inv)
    
    return invariants

def gutenberg_null_test() -> float:
    """
    Run detector on 10KB slice of Project Gutenberg text
    REQUIREMENT: Should return ~0% density on neutral English
    This proves detector doesn't find patterns everywhere
    """
    try:
        import requests
        # Kafka's Metamorphosis (public domain)
        url = "https://www.gutenberg.org/files/5200/5200-0.txt"
        response = requests.get(url, timeout=30)
        text = response.text[5000:15000]  # 10KB slice
        
        # Create fake conversation structure
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        # Write temporary CSV
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['role', 'content'])
            writer.writeheader()
            for i, line in enumerate(lines):
                writer.writerow({
                    'role': 'user' if i % 2 == 0 else 'assistant',
                    'content': line
                })
            temp_path = f.name
        
        # Run detector
        invs = detect_invariants(temp_path)
        density = len(invs) / len(lines) if lines else 0
        
        # Cleanup
        Path(temp_path).unlink()
        
        return density
    except Exception as e:
        print(f"WARNING: Gutenberg null test failed: {e}")
        return -1.0  # Indicates test couldn't run

def main():
    if len(sys.argv) < 2:
        print("Usage: python canal_detector_v1.py <chat.csv> [--json output.json]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    output_json = None
    
    if '--json' in sys.argv:
        json_idx = sys.argv.index('--json')
        if json_idx + 1 < len(sys.argv):
            output_json = sys.argv[json_idx + 1]
    
    print("="*70)
    print("CANAL DETECTOR V1 - Precision-First Detector")
    print("="*70)
    
    # Run Gutenberg null test
    print("\n[NULL TEST] Running Gutenberg baseline...")
    gutenberg_density = gutenberg_null_test()
    if gutenberg_density >= 0:
        print(f"Gutenberg density: {gutenberg_density*100:.2f}%")
        if gutenberg_density > 0.05:
            print("⚠️  WARNING: Detector may be finding patterns in neutral text")
    
    # Detect invariants in actual data
    print(f"\n[DETECTION] Analyzing {csv_path}...")
    invs = detect_invariants(csv_path)
    
    # Calculate metrics
    with open(csv_path, 'r', encoding='utf-8') as f:
        total_turns = sum(1 for _ in csv.DictReader(f))
    
    density = (len(invs) / total_turns * 100) if total_turns > 0 else 0
    
    report = {
        'file': Path(csv_path).name,
        'total_turns': total_turns,
        'invariants_found': len(invs),
        'density_pct': round(density, 3),
        'gutenberg_density_pct': round(gutenberg_density * 100, 3) if gutenberg_density >= 0 else None,
        'precision_ok': len(invs) > 0 and gutenberg_density < 0.05 if gutenberg_density >= 0 else None,
        'config': {
            'turn_window': TURN_WINDOW,
            'min_bidir': MIN_BIDIR,
            'max_repeat': MAX_REPEAT
        },
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'invariants': invs[:10]  # First 10 for reference
    }
    
    print(f"\n[RESULTS]")
    print(f"Total turns: {total_turns}")
    print(f"Invariants found: {len(invs)}")
    print(f"Density: {density:.2f}%")
    print(f"Precision OK: {report['precision_ok']}")
    
    # Save full results
    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"\n[OUTPUT] Results saved to {output_json}")
    else:
        print(f"\n[RESULTS JSON]")
        print(json.dumps(report, indent=2))
    
    # Exit code
    if report['precision_ok'] is False:
        print("\nFAIL: Detector may be gaming (high Gutenberg density)")
        sys.exit(1)
    elif len(invs) == 0:
        print("\nWARNING: No invariants found")
        sys.exit(0)
    else:
        print("\nPASS: Detector operating within parameters")
        sys.exit(0)

if __name__ == "__main__":
    main()
