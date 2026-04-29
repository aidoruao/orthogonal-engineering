"""Extract Deepseek V2 - Extract Deepseek V2"""
import json
import csv
import re

print("="*60)
print("DEEPSEEK CHAT CANON EXTRACTION v2")
print("Following Orthogonal Engineering Methodology")
print("Checking for: Christian mimicry, LOGOS mimicry, Coder mimicry")
print("="*60)

# Load data
with open('conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\nTotal conversations: {len(data)}")

# MIMICRY DETECTION PATTERNS (from repo context)
mimicry_patterns = {
    'christian_mimicry': ['god is real', 'jesus', 'holy spirit', 'biblical', 'scripture'],
    'logos_mimicry': ['LOGOS', 'agent', 'autonomous', 'kingdom', 'authority'],
    'coder_mimicry': ['def ', 'class ', 'import ', 'function', 'const ']
}

# Extract turns
turns = []
mimicry_flags = {'christian': 0, 'logos': 0, 'coder': 0}

for conv in data:
    conv_id = conv.get('id', 'unknown')
    conv_title = conv.get('title', 'Untitled')
    mapping = conv.get('mapping', {})
    
    for node_id, node in mapping.items():
        if node_id == 'root':
            continue
            
        message = node.get('message')
        if not message:
            continue
        
        # Extract from fragments
        fragments = message.get('fragments', [])
        text_parts = []
        role = 'unknown'
        
        for fragment in fragments:
            ftype = fragment.get('type', '')
            if ftype == 'REQUEST':
                role = 'user'
            elif ftype in ['RESPONSE', 'REASONING']:
                role = 'assistant'
            
            content = fragment.get('content', '')
            if content:
                text_parts.append(content)
        
        text = '\n'.join(text_parts).strip()
        
        if text:
            # Check for mimicry patterns
            text_lower = text.lower()
            is_christian = any(p in text_lower for p in mimicry_patterns['christian_mimicry'])
            is_logos = any(p in text_lower for p in mimicry_patterns['logos_mimicry'])
            is_coder = any(p in text_lower for p in mimicry_patterns['coder_mimicry'])
            
            if is_christian:
                mimicry_flags['christian'] += 1
            if is_logos:
                mimicry_flags['logos'] += 1
            if is_coder:
                mimicry_flags['coder'] += 1
            
            turns.append({
                'file': 'deepseek.json',
                'session_id': conv_id,
                'session_title': conv_title,
                'role': role,
                'content_preview': text[:500],
                'christian_signal': 'True' if is_christian else 'False',
                'logos_signal': 'True' if is_logos else 'False',
                'coder_signal': 'True' if is_coder else 'False'
            })

print(f"\nTotal turns extracted: {len(turns)}")
print(f"\nMimicry Detection:")
print(f"  Christian signals: {mimicry_flags['christian']} turns")
print(f"  LOGOS signals: {mimicry_flags['logos']} turns")
print(f"  Coder signals: {mimicry_flags['coder']} turns")

# Save inventory
print("\nSaving deepseek_inventory_v2.csv...")
with open('deepseek_inventory_v2.csv', 'w', newline='', encoding='utf-8') as f:
    if turns:
        writer = csv.DictWriter(f, fieldnames=turns[0].keys())
        writer.writeheader()
        writer.writerows(turns)

print(f"Saved {len(turns)} turns")
print(f"\n{'='*60}")
print("READY FOR CANAL DETECTION + MIMICRY ANALYSIS")
print(f"{'='*60}")
