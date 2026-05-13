import json, sys, hashlib

def parse_oe(path):
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Required fields for .oe files
    required = ['domain', 'status']
    for field in required:
        if field not in data:
            raise ValueError(f".oe file missing required field: {field}")
    
    # Hash anchoring
    content_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    data['_hash'] = content_hash
    
    return data

if __name__ == '__main__':
    result = parse_oe(sys.argv[1])
    print(json.dumps(result, indent=2))
