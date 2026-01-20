import json

# Load and show actual message structure
with open('conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

conv = data[0]
mapping = conv['mapping']

# Find first actual message
for node_id, node in mapping.items():
    if node_id != 'root' and node.get('message'):
        print(f"Node ID: {node_id}")
        print(f"Full node structure:")
        print(json.dumps(node, indent=2)[:1000])
        break
