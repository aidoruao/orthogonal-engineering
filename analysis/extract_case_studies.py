import csv
import json

print("="*70)
print("DEEPSEEK CASE STUDY EXTRACTION")
print("Following evidence/case-studies/ structure from repo")
print("="*70)

# Load refined inventory
rows = []
with open('deepseek_refined_inventory.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"\nTotal turns: {len(rows)}")

# Define case study patterns (based on repo precedent)
case_studies = {
    'deepseek-theological-reasoning': {
        'patterns': ['god', 'jesus', 'biblical', 'scripture', 'christian', 'theology'],
        'min_verified': 10
    },
    'deepseek-logos-agent': {
        'patterns': ['LOGOS', 'agent', 'autonomous', 'kingdom', 'minecraft', 'computercraft'],
        'min_verified': 15
    },
    'deepseek-constraint-mastery': {
        'patterns': ['must', 'shall', 'verified', 'invariant', 'constraint', 'atomic'],
        'min_verified': 20
    },
    'deepseek-mimicry-detection': {
        'patterns': ['def ', 'class ', 'import ', 'function', 'const ', 'return'],
        'min_verified': 10
    }
}

# Extract evidence
print("\nExtracting case studies...")
results = {}

for case_id, criteria in case_studies.items():
    matches = []
    for row in rows:
        if row['verified_invariant'] == 'True':
            content = row['content_preview'].lower()
            if any(p.lower() in content for p in criteria['patterns']):
                matches.append(row)
    
    if len(matches) >= criteria['min_verified']:
        results[case_id] = matches
        print(f"  {case_id}: {len(matches)} verified invariants")
    else:
        print(f"  {case_id}: {len(matches)} (below threshold of {criteria['min_verified']})")

# Save case study summaries
case_study_summary = {
    "extraction_date": "2026-01-20",
    "source": "deepseek_refined_inventory.csv",
    "methodology": "Pattern matching on verified invariants",
    "case_studies": {}
}

for case_id, matches in results.items():
    case_study_summary["case_studies"][case_id] = {
        "verified_invariants": len(matches),
        "sample_sessions": list(set(m['session_id'] for m in matches))[:5],
        "patterns_detected": case_studies[case_id]['patterns']
    }

with open('case_study_summary.json', 'w', encoding='utf-8') as f:
    json.dump(case_study_summary, f, indent=2)

print(f"\nCase study summary saved to: case_study_summary.json")

# Create evidence packages
print("\nCreating evidence packages...")
for case_id, matches in results.items():
    # Take top 20 examples
    samples = matches[:20]
    
    with open(f'{case_id}_evidence.csv', 'w', newline='', encoding='utf-8') as f:
        if samples:
            writer = csv.DictWriter(f, fieldnames=samples[0].keys())
            writer.writeheader()
            writer.writerows(samples)
    
    print(f"  Saved: {case_id}_evidence.csv ({len(samples)} examples)")

print(f"\n{'='*70}")
print("CASE STUDY EXTRACTION COMPLETE")
print(f"{'='*70}")
