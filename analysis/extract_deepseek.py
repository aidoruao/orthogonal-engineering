import json
import csv
from datetime import datetime

print("="*60)
print("DEEPSEEK CHAT CANON EXTRACTION")
print("Following Orthogonal Engineering Methodology")
print("="*60)

# Load data
with open('conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\nTotal conversations: {len(data)}")

# Extract turns (following repo's canal_detector.py approach)
turns = []
total_messages = 0

for conv in data:
    conv_id = conv.get('id', 'unknown')
    conv_title = conv.get('title', 'Untitled')
    mapping = conv.get('mapping', {})
    
    # Traverse tree structure (like ChatGPT exports)
    for node_id, node in mapping.items():
        if node_id == 'root':
            continue
            
        message = node.get('message')
        if message:
            role = message.get('author', {}).get('role', 'unknown')
            content = message.get('content', {})
            
            # Extract text content
            if isinstance(content, dict):
                text = content.get('parts', [''])[0] if 'parts' in content else str(content)
            else:
                text = str(content)
            
            if text.strip():
                turns.append({
                    'file': 'deepseek.json',
                    'session_id': conv_id,
                    'session_title': conv_title,
                    'role': role,
                    'content_preview': text[:500]
                })
                total_messages += 1

print(f"Total turns extracted: {len(turns)}")
print(f"Total messages: {total_messages}")

# Save inventory (following refined_inventory.csv structure)
print("\nSaving deepseek_inventory.csv...")
with open('deepseek_inventory.csv', 'w', newline='', encoding='utf-8') as f:
    if turns:
        writer = csv.DictWriter(f, fieldnames=turns[0].keys())
        writer.writeheader()
        writer.writerows(turns)

print(f"✅ Saved {len(turns)} turns")
print(f"\n{'='*60}")
print("READY FOR CANAL DETECTION")
print("Next: Run canal_detector.py on deepseek_inventory.csv")
print(f"{'='*60}")
