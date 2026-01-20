import csv
import re
from datetime import datetime

print("="*70)
print("DEEPSEEK MUTUAL AGREEMENT REFINEMENT")
print("Following canal_refiner.py methodology from repo")
print("="*70)

# Load canal-detected data
rows = []
with open('deepseek_with_canals.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"\nTotal turns: {len(rows)}")

# Session grouping (30-minute gaps like repo)
print("\nGrouping sessions...")
sessions = {}
for row in rows:
    session_id = row['session_id']
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append(row)

print(f"Total sessions: {len(sessions)}")

# MUTUAL AGREEMENT DETECTION (following repo's canal_refiner.py)
# Both user AND assistant must use constraint language within 5-turn window

invariant_patterns = [
    r'\b(must|should|required|necessary|critical|essential)\b',
    r'\b(always|never|cannot|will not|shall not)\b',
    r'\b(exactly|precisely|specifically|explicitly)\b',
    r'\b(confirmed|verified|validated|proven|tested)\b'
]

def has_invariant_language(text):
    """Check if text contains invariant markers"""
    return any(re.search(p, text.lower()) for p in invariant_patterns)

def check_mutual_agreement(session_turns, window_size=5):
    """Check if user AND assistant both use invariant language in window"""
    verified = []
    
    for i, turn in enumerate(session_turns):
        # Look at window around this turn
        start = max(0, i - window_size)
        end = min(len(session_turns), i + window_size + 1)
        window = session_turns[start:end]
        
        # Check if both user and assistant use invariant language
        user_has_invariant = False
        assistant_has_invariant = False
        
        for t in window:
            content = t['content_preview']
            if has_invariant_language(content):
                if t['role'] == 'user':
                    user_has_invariant = True
                elif t['role'] == 'assistant':
                    assistant_has_invariant = True
        
        # MUTUAL AGREEMENT = both parties use invariant language
        if user_has_invariant and assistant_has_invariant:
            turn['verified_invariant'] = 'True'
            verified.append(turn)
        else:
            turn['verified_invariant'] = 'False'
    
    return verified

# Process all sessions
print("\nApplying mutual agreement detection...")
all_verified = []
for session_id, turns in sessions.items():
    verified = check_mutual_agreement(turns)
    all_verified.extend(verified)

verified_count = len(all_verified)
density = (verified_count / len(rows) * 100) if rows else 0

print(f"\n{'='*70}")
print("REFINEMENT RESULTS:")
print(f"  Total turns: {len(rows)}")
print(f"  Canal candidates: {sum(1 for r in rows if r['canal_detected']=='True')}")
print(f"  Verified invariants: {verified_count}")
print(f"  Invariant density: {density:.2f}%")
print(f"{'='*70}")

# Compare to repo baseline
print("\nCOMPARISON TO REPO BASELINE:")
print(f"  Chat canon density: 7.57%")
print(f"  DeepSeek density: {density:.2f}%")
if density > 7.57:
    print(f"  Result: {density - 7.57:.2f}% HIGHER")
elif density < 7.57:
    print(f"  Result: {7.57 - density:.2f}% LOWER")
else:
    print(f"  Result: EXACT MATCH")

# Save refined inventory
print("\nSaving deepseek_refined_inventory.csv...")
with open('deepseek_refined_inventory.csv', 'w', newline='', encoding='utf-8') as f:
    if rows:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

print(f"Saved {len(rows)} turns with verified_invariant flags")

# Generate statistics JSON (following repo's chat_canon_summary.json)
stats = {
    "dataset": "DeepSeek Conversations",
    "extraction_date": datetime.now().isoformat(),
    "source_file": "deepseek_data-2026-01-20.zip",
    "total_turns": len(rows),
    "total_sessions": len(sessions),
    "canal_candidates": sum(1 for r in rows if r['canal_detected']=='True'),
    "canal_rate_pct": (sum(1 for r in rows if r['canal_detected']=='True') / len(rows) * 100) if rows else 0,
    "verified_invariants": verified_count,
    "invariant_density_pct": density,
    "methodology": "canal_detector.py + mutual_agreement refinement",
    "comparison_to_baseline": {
        "baseline_density": 7.57,
        "deepseek_density": round(density, 2),
        "difference": round(density - 7.57, 2)
    },
    "mimicry_patterns": {
        "christian_signals": sum(1 for r in rows if r.get('christian_signal')=='True'),
        "logos_signals": sum(1 for r in rows if r.get('logos_signal')=='True'),
        "coder_signals": sum(1 for r in rows if r.get('coder_signal')=='True')
    }
}

import json
with open('deepseek_statistics.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2)

print(f"\nStatistics saved to: deepseek_statistics.json")
print(f"\n{'='*70}")
print("READY FOR COMPARISON ANALYSIS")
print(f"{'='*70}")
