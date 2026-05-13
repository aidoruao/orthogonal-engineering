import json
import sys
import os

log_path = "/mnt/c/Users/Aidor/Downloads/register_standards_output.txt"

with open(log_path, 'w') as log:
    log.write("=== STANDARDS REGISTRY UPDATE ===\n\n")
    
    with open('/home/idor/oe-local/STANDARDS_REGISTRY.json', 'r') as f:
        registry = json.load(f)
    
    log.write(f"Keys in registry: {list(registry.keys())}\n")
    log.write(f"Type of standards: {type(registry.get('standards'))}\n")
    
    if isinstance(registry['standards'], list):
        log.write("ERROR: 'standards' is a list, not a dict. Converting.\n")
        old_list = registry['standards']
        registry['standards'] = {}
        for item in old_list:
            if isinstance(item, dict) and 'id' in item:
                registry['standards'][item['id']] = item
    
    log.write(f"Current standards count: {len(registry['standards'])}\n\n")
    
    turtle_standards = {
        "YS-TURTLE-STORAGE-INVENTORY": {
            "domain": "d_dag_theory",
            "category": "turtle_storage",
            "phase": 1,
            "description": "Turtle inventory awareness across all 16 slots with fuel monitoring.",
            "falsifies_if": "scanSlot returns nil for a non-empty slot.",
            "status": "IMPLEMENTED",
            "file": "automation/computer_craft/storage/inventory.lua",
            "functions": ["scanSlot","scanAll","classify","needsRestock","checkFuel","formatReport"]
        },
        "YS-TURTLE-STORAGE-CRAFTING": {
            "domain": "d_dag_theory",
            "category": "turtle_storage",
            "phase": 2,
            "description": "Recipe DAG topological sort and reachability via transitive closure.",
            "falsifies_if": "topologicalSort violates a dependency edge.",
            "status": "IMPLEMENTED",
            "file": "automation/computer_craft/storage/crafting.lua",
            "functions": ["buildDependencyGraph","topologicalSort","computeTransitiveClosure","craftItem"]
        },
        "YS-TURTLE-STORAGE-PATHFINDING": {
            "domain": "d_dag_theory",
            "category": "turtle_storage",
            "phase": 3,
            "description": "Graph Laplacian 3D pathfinding with OVER strategy obstacle avoidance.",
            "falsifies_if": "findPath returns a path intersecting a known obstacle.",
            "status": "IMPLEMENTED",
            "file": "automation/computer_craft/storage/pathfinding.lua",
            "functions": ["findPath","executePath","faceDirection","manhattanDistance"]
        },
        "YS-TURTLE-STORAGE-VERIFY": {
            "domain": "d_dag_theory",
            "category": "turtle_storage",
            "phase": 5,
            "description": "Merkle-anchored state verification via Yeshua HTTP bridge.",
            "falsifies_if": "verifyState returns true for mismatched hashes.",
            "status": "IMPLEMENTED",
            "file": "automation/computer_craft/storage/verify.lua",
            "functions": ["postToYeshua","generateProofObject","logTransfer","verifyState","runAudit"]
        },
        "YS-TURTLE-STORAGE-DAG-THEORY": {
            "domain": "d_dag_theory",
            "category": "turtle_storage",
            "phase": "meta",
            "description": "Meta-standard: d_dag_theory verified by 10-AI industry consensus.",
            "falsifies_if": "Any gate derivation is keyword-only without mathematical reasoning.",
            "status": "VERIFIED",
            "verification": "10-AI consensus (2026-05-12)",
            "puzzle": "docs/turtle_governance_puzzle.html"
        }
    }
    
    for k, v in turtle_standards.items():
        registry['standards'][k] = v
        log.write(f"Added: {k}\n")
    
    registry['_meta']['total_standards'] = len(registry['standards'])
    registry['_meta']['last_updated'] = '2026-05-12'
    
    with open('/home/idor/oe-local/STANDARDS_REGISTRY.json', 'w') as f:
        json.dump(registry, f, indent=2)
    
    log.write(f"\nDone. {len(registry['standards'])} standards total.\n")
    log.write(f"Output also at: /home/idor/oe-local/STANDARDS_REGISTRY.json\n")

print("Script complete. Log at /mnt/c/Users/Aidor/Downloads/register_standards_output.txt")
