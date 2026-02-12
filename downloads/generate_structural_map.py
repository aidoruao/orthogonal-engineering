#!/usr/bin/env python3
"""
Atomic Structural Map Generator
Creates JSON/YAML repository map for AI orchestration.
"""

import json
import os
from pathlib import Path

import yaml

REPO_ROOT = Path(".").resolve()
DOWNLOADS = Path("downloads")

DOWNLOADS.mkdir(parents=True, exist_ok=True)


def walk_repo(root):
    data = {}
    for dirpath, dirs, files in os.walk(root):
        try:
            rel_path = str(Path(dirpath).relative_to(root))
            # Handle root directory specially
            if rel_path == ".":
                rel_path = ""
            data[rel_path] = {"files": files, "dirs": dirs}
        except ValueError:
            # If we can't get relative path, use absolute path
            data[str(dirpath)] = {"files": files, "dirs": dirs}
    return data


struct_map = walk_repo(REPO_ROOT)

# Ensure downloads directory exists
DOWNLOADS.mkdir(parents=True, exist_ok=True)

json_file = DOWNLOADS / "repository_structural_map_full.json"
yaml_file = DOWNLOADS / "repository_structural_map_full.yaml"

with open(json_file, "w") as f:
    json.dump(struct_map, f, indent=2)

with open(yaml_file, "w") as f:
    yaml.dump(struct_map, f)

print(f"Structural map generated:")
print(f"  JSON: {json_file}")
print(f"  YAML: {yaml_file}")
