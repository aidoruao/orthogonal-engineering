import json

# Load and inspect structure
with open('conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total conversations: {len(data)}")
print(f"\nFirst conversation:")
conv = data[0]
print(f"  ID: {conv.get('id')}")
print(f"  Title: {conv.get('title')}")
print(f"  Keys: {list(conv.keys())}")

# Check mapping structure
if 'mapping' in conv:
    mapping = conv['mapping']
    print(f"\n  Mapping type: {type(mapping)}")
    
    if isinstance(mapping, dict):
        print(f"  Mapping keys (first 5): {list(mapping.keys())[:5]}")
        first_key = list(mapping.keys())[0]
        print(f"\n  First mapping entry structure:")
        print(f"    {json.dumps(mapping[first_key], indent=2)[:500]}")
