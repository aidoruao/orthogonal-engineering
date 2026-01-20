import csv
import re

print("="*60)
print("DEEPSEEK CANAL DETECTION")
print("Following Orthogonal Engineering Methodology")
print("="*60)

# Load inventory
rows = []
with open('deepseek_inventory_v2.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"\nTotal turns: {len(rows)}")

# CANAL PATTERNS (from repo)
canal_patterns = [
    r'\b(shall we|let me also|now let me|i will|i can|i should)\b',
    r'\b(must|need to|have to|going to|will now)\b',
    r'\b(first|then|next|finally|after that)\b',
    r'\b(step \d+|stage \d+|phase \d+)\b'
]

# Detect canals
canal_count = 0
for row in rows:
    content = row['content_preview'].lower()
    has_canal = any(re.search(p, content) for p in canal_patterns)
    row['canal_detected'] = 'True' if has_canal else 'False'
    if has_canal:
        canal_count += 1

canal_rate = (canal_count / len(rows)) * 100 if rows else 0

print(f"\nCanal Detection Results:")
print(f"  Canal candidates: {canal_count}")
print(f"  Canal rate: {canal_rate:.2f}%")

# Save with canal flags
with open('deepseek_with_canals.csv', 'w', newline='', encoding='utf-8') as f:
    if rows:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

print(f"\nSaved to: deepseek_with_canals.csv")
print(f"{'='*60}")
print("NEXT: Run refinement for verified invariants")
print(f"{'='*60}")
