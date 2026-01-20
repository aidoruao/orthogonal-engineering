import json
import csv
from datetime import datetime

# Load DeepSeek conversations
print("Loading DeepSeek conversations...")
with open('conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total conversations: {len(data)}")

# Analyze structure (following repo precedent)
if len(data) > 0:
    print(f"\nFirst conversation structure:")
    print(f"Keys: {list(data[0].keys())}")
    
    if 'messages' in data[0]:
        print(f"Messages in first convo: {len(data[0]['messages'])}")
        if len(data[0]['messages']) > 0:
            print(f"Message keys: {list(data[0]['messages'][0].keys())}")

# Convert to turn-based format (like claude.md/gpt.md processing)
print("\nConverting to turn-based inventory...")
turns = []
for conv_idx, conv in enumerate(data):
    conv_id = conv.get('id', f'conv_{conv_idx}')
    messages = conv.get('messages', [])
    
    for msg_idx, msg in enumerate(messages):
        turns.append({
            'conversation_id': conv_id,
            'turn_index': msg_idx,
            'role': msg.get('role', 'unknown'),
            'content': msg.get('content', '')[:500],  # Preview only
            'timestamp': msg.get('timestamp', '')
        })

print(f"Total turns extracted: {len(turns)}")

# Save inventory
print("\nSaving inventory...")
with open('deepseek_inventory.csv', 'w', newline='', encoding='utf-8') as f:
    if turns:
        writer = csv.DictWriter(f, fieldnames=turns[0].keys())
        writer.writeheader()
        writer.writerows(turns)

print(f"Saved to deepseek_inventory.csv")
print(f"\nREADY FOR CANAL DETECTION")
