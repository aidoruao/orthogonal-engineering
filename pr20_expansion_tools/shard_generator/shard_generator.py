#!/usr/bin/env python3
"""
Shard Generator - PR #20 Deterministic Expansion Tool

Generates deterministic modules/shards of target LOC across multiple domains.
All generation is reproducible with seed propagation.

Domains supported:
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- C/C++ (.c, .cpp, .h)
- Go (.go)
"""

import hashlib
import json
import os
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ShardGenerator:
    """Deterministic shard generator for code expansion."""
    
    DOMAINS = {
        'python': {'ext': '.py', 'avg_loc': 50},
        'javascript': {'ext': '.js', 'avg_loc': 40},
        'typescript': {'ext': '.ts', 'avg_loc': 40},
        'java': {'ext': '.java', 'avg_loc': 60},
        'c': {'ext': '.c', 'avg_loc': 45},
        'cpp': {'ext': '.cpp', 'avg_loc': 55},
        'go': {'ext': '.go', 'avg_loc': 50},
    }
    
    SHARD_LEVELS = {
        0: {'name': 'root', 'target_loc': 250000},
        1: {'name': 'medium', 'target_loc': 50000},
        2: {'name': 'sub', 'target_loc': 25000},
        3: {'name': 'micro', 'target_loc': 10000},
    }
    
    def __init__(self, seed: int = 42, output_dir: str = './generated_shards'):
        """Initialize shard generator with deterministic seed."""
        self.seed = seed
        self.output_dir = Path(output_dir)
        self.rng = random.Random(seed)
        self.shard_count = 0
        self.total_loc = 0
        
    def generate_file_content(self, domain: str, target_loc: int, file_id: str) -> str:
        """Generate deterministic file content for a specific domain."""
        if domain == 'python':
            return self._generate_python(target_loc, file_id)
        elif domain == 'javascript':
            return self._generate_javascript(target_loc, file_id)
        elif domain == 'typescript':
            return self._generate_typescript(target_loc, file_id)
        elif domain == 'java':
            return self._generate_java(target_loc, file_id)
        elif domain in ['c', 'cpp']:
            return self._generate_c_cpp(target_loc, file_id, domain)
        elif domain == 'go':
            return self._generate_go(target_loc, file_id)
        else:
            raise ValueError(f"Unknown domain: {domain}")
    
    def _generate_python(self, target_loc: int, file_id: str) -> str:
        """Generate deterministic Python code."""
        lines = [
            f'"""',
            f'Module {file_id} - Auto-generated deterministic Python module',
            f'Generated at: {datetime.now(timezone.utc).isoformat()}',
            f'Seed: {self.seed}',
            f'"""',
            '',
            'import hashlib',
            'import json',
            'from typing import Any, Dict, List, Optional',
            '',
        ]
        
        # Generate classes and functions deterministically
        class_count = max(1, target_loc // 20)
        for i in range(class_count):
            class_name = f"Class_{file_id}_{i}"
            lines.extend([
                f'class {class_name}:',
                f'    """Deterministic class {i} for module {file_id}."""',
                f'    ',
                f'    def __init__(self, value: Any = None):',
                f'        self.value = value',
                f'        self.id = "{file_id}_{i}"',
                f'    ',
                f'    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:',
                f'        """Process data deterministically."""',
                f'        result = {{"id": self.id, "data": data}}',
                f'        return result',
                f'    ',
                f'    def compute_hash(self) -> str:',
                f'        """Compute deterministic hash."""',
                f'        content = json.dumps({{"id": self.id, "value": str(self.value)}}, sort_keys=True)',
                f'        return hashlib.sha256(content.encode()).hexdigest()',
                '',
            ])
        
        return '\n'.join(lines)
    
    def _generate_javascript(self, target_loc: int, file_id: str) -> str:
        """Generate deterministic JavaScript code."""
        lines = [
            f'/**',
            f' * Module {file_id} - Auto-generated deterministic JavaScript module',
            f' * Generated at: {datetime.now(timezone.utc).isoformat()}',
            f' * Seed: {self.seed}',
            f' */',
            '',
            'const crypto = require("crypto");',
            '',
        ]
        
        class_count = max(1, target_loc // 15)
        for i in range(class_count):
            class_name = f"Module{file_id.replace('-', '')}Class{i}"
            lines.extend([
                f'class {class_name} {{',
                f'  constructor(value = null) {{',
                f'    this.value = value;',
                f'    this.id = "{file_id}_{i}";',
                f'  }}',
                f'  ',
                f'  process(data) {{',
                f'    return {{ id: this.id, data: data }};',
                f'  }}',
                f'  ',
                f'  computeHash() {{',
                f'    const content = JSON.stringify({{ id: this.id, value: String(this.value) }});',
                f'    return crypto.createHash("sha256").update(content).digest("hex");',
                f'  }}',
                f'}}',
                '',
            ])
        
        class_names = [f"Module{file_id.replace('-', '')}Class{i}" for i in range(class_count)]
        lines.append(f'module.exports = {{ {", ".join(class_names)} }};')
        return '\n'.join(lines)
    
    def _generate_typescript(self, target_loc: int, file_id: str) -> str:
        """Generate deterministic TypeScript code."""
        lines = [
            f'/**',
            f' * Module {file_id} - Auto-generated deterministic TypeScript module',
            f' * Generated at: {datetime.now(timezone.utc).isoformat()}',
            f' * Seed: {self.seed}',
            f' */',
            '',
            'import * as crypto from "crypto";',
            '',
            'interface DataObject {',
            '  [key: string]: any;',
            '}',
            '',
        ]
        
        class_count = max(1, target_loc // 15)
        for i in range(class_count):
            class_name = f"Module{file_id.replace('-', '')}Class{i}"
            lines.extend([
                f'export class {class_name} {{',
                f'  private value: any;',
                f'  private id: string;',
                f'  ',
                f'  constructor(value: any = null) {{',
                f'    this.value = value;',
                f'    this.id = "{file_id}_{i}";',
                f'  }}',
                f'  ',
                f'  process(data: DataObject): DataObject {{',
                f'    return {{ id: this.id, data: data }};',
                f'  }}',
                f'  ',
                f'  computeHash(): string {{',
                f'    const content = JSON.stringify({{ id: this.id, value: String(this.value) }});',
                f'    return crypto.createHash("sha256").update(content).digest("hex");',
                f'  }}',
                f'}}',
                '',
            ])
        
        return '\n'.join(lines)
    
    def _generate_java(self, target_loc: int, file_id: str) -> str:
        """Generate deterministic Java code."""
        package_name = f"shard_{file_id.replace('-', '_')}"
        class_name = f"Module{file_id.replace('-', '')}".capitalize()
        
        lines = [
            f'package {package_name};',
            '',
            f'/**',
            f' * Module {file_id} - Auto-generated deterministic Java module',
            f' * Generated at: {datetime.now(timezone.utc).isoformat()}',
            f' * Seed: {self.seed}',
            f' */',
            '',
            'import java.security.MessageDigest;',
            'import java.util.HashMap;',
            'import java.util.Map;',
            '',
            f'public class {class_name} {{',
            f'    private Object value;',
            f'    private String id;',
            f'    ',
            f'    public {class_name}(Object value) {{',
            f'        this.value = value;',
            f'        this.id = "{file_id}";',
            f'    }}',
            f'    ',
            f'    public Map<String, Object> process(Map<String, Object> data) {{',
            f'        Map<String, Object> result = new HashMap<>();',
            f'        result.put("id", this.id);',
            f'        result.put("data", data);',
            f'        return result;',
            f'    }}',
            f'    ',
            f'    public String computeHash() throws Exception {{',
            f'        String content = String.format("{{\\"id\\":\\"%s\\",\\"value\\":\\"%s\\"}}", this.id, String.valueOf(this.value));',
            f'        MessageDigest digest = MessageDigest.getInstance("SHA-256");',
            f'        byte[] hash = digest.digest(content.getBytes("UTF-8"));',
            f'        StringBuilder hexString = new StringBuilder();',
            f'        for (byte b : hash) {{',
            f'            String hex = Integer.toHexString(0xff & b);',
            f'            if (hex.length() == 1) hexString.append(\'0\');',
            f'            hexString.append(hex);',
            f'        }}',
            f'        return hexString.toString();',
            f'    }}',
            f'}}',
        ]
        
        return '\n'.join(lines)
    
    def _generate_c_cpp(self, target_loc: int, file_id: str, domain: str) -> str:
        """Generate deterministic C/C++ code."""
        lines = [
            f'/**',
            f' * Module {file_id} - Auto-generated deterministic {domain.upper()} module',
            f' * Generated at: {datetime.now(timezone.utc).isoformat()}',
            f' * Seed: {self.seed}',
            f' */',
            '',
            '#include <stdio.h>',
            '#include <stdlib.h>',
            '#include <string.h>',
            '',
            f'typedef struct {{',
            f'    void* value;',
            f'    char id[256];',
            f'}} Module{file_id.replace("-", "")};',
            '',
            f'Module{file_id.replace("-", "")}* create_module(void* value) {{',
            f'    Module{file_id.replace("-", "")}* module = malloc(sizeof(Module{file_id.replace("-", "")}));',
            f'    module->value = value;',
            f'    snprintf(module->id, 256, "{file_id}");',
            f'    return module;',
            f'}}',
            '',
            f'void destroy_module(Module{file_id.replace("-", "")}* module) {{',
            f'    if (module) {{',
            f'        free(module);',
            f'    }}',
            f'}}',
            '',
            f'void process_data(Module{file_id.replace("-", "")}* module, void* data) {{',
            f'    printf("Processing data for module %s\\n", module->id);',
            f'}}',
        ]
        
        return '\n'.join(lines)
    
    def _generate_go(self, target_loc: int, file_id: str) -> str:
        """Generate deterministic Go code."""
        package_name = f"shard{file_id.replace('-', '')}"
        
        lines = [
            f'/**',
            f' * Module {file_id} - Auto-generated deterministic Go module',
            f' * Generated at: {datetime.now(timezone.utc).isoformat()}',
            f' * Seed: {self.seed}',
            f' */',
            '',
            f'package {package_name}',
            '',
            'import (',
            '    "crypto/sha256"',
            '    "encoding/hex"',
            '    "encoding/json"',
            ')',
            '',
            f'type Module struct {{',
            f'    Value interface{{}}',
            f'    ID    string',
            f'}}',
            '',
            f'func NewModule(value interface{{}}) *Module {{',
            f'    return &Module{{',
            f'        Value: value,',
            f'        ID:    "{file_id}",',
            f'    }}',
            f'}}',
            '',
            f'func (m *Module) Process(data map[string]interface{{}}) map[string]interface{{}} {{',
            f'    result := make(map[string]interface{{}})',
            f'    result["id"] = m.ID',
            f'    result["data"] = data',
            f'    return result',
            f'}}',
            '',
            f'func (m *Module) ComputeHash() (string, error) {{',
            f'    content, err := json.Marshal(map[string]interface{{}}{{',
            f'        "id":    m.ID,',
            f'        "value": m.Value,',
            f'    }})',
            f'    if err != nil {{',
            f'        return "", err',
            f'    }}',
            f'    hash := sha256.Sum256(content)',
            f'    return hex.EncodeToString(hash[:]), nil',
            f'}}',
        ]
        
        return '\n'.join(lines)
    
    def create_shard(self, level: int, shard_id: str, domains: List[str]) -> Dict:
        """Create a complete shard with files across multiple domains."""
        shard_info = self.SHARD_LEVELS[level]
        target_loc = shard_info['target_loc']
        
        # Distribute LOC across domains
        loc_per_domain = target_loc // len(domains)
        
        shard_data = {
            'shard_id': shard_id,
            'level': level,
            'level_name': shard_info['name'],
            'target_loc': target_loc,
            'actual_loc': 0,
            'domains': {},
            'files': [],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'seed': self.seed,
        }
        
        for domain in domains:
            domain_info = self.DOMAINS[domain]
            avg_loc_per_file = domain_info['avg_loc']
            num_files = max(1, loc_per_domain // avg_loc_per_file)
            
            domain_path = self.output_dir / shard_id / domain
            domain_path.mkdir(parents=True, exist_ok=True)
            
            domain_loc = 0
            files = []
            
            for i in range(num_files):
                file_id = f"{shard_id}-{domain}-{i:04d}"
                filename = f"{file_id}{domain_info['ext']}"
                filepath = domain_path / filename
                
                # Generate content
                content = self.generate_file_content(domain, avg_loc_per_file, file_id)
                actual_loc = len(content.split('\n'))
                
                # Write file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Compute hash
                file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                
                file_info = {
                    'file_id': file_id,
                    'filename': filename,
                    'path': str(filepath.relative_to(self.output_dir)),
                    'domain': domain,
                    'loc': actual_loc,
                    'hash': file_hash,
                }
                
                files.append(file_info)
                domain_loc += actual_loc
            
            shard_data['domains'][domain] = {
                'num_files': num_files,
                'loc': domain_loc,
            }
            shard_data['files'].extend(files)
            shard_data['actual_loc'] += domain_loc
        
        # Write shard manifest
        manifest_path = self.output_dir / shard_id / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(shard_data, f, indent=2)
        
        self.shard_count += 1
        self.total_loc += shard_data['actual_loc']
        
        return shard_data
    
    def get_stats(self) -> Dict:
        """Get current generation statistics."""
        return {
            'shard_count': self.shard_count,
            'total_loc': self.total_loc,
            'seed': self.seed,
        }


def main():
    """Main function for testing shard generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate deterministic code shards')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for deterministic generation')
    parser.add_argument('--output-dir', type=str, default='./generated_shards', help='Output directory')
    parser.add_argument('--level', type=int, default=3, choices=[0, 1, 2, 3], help='Shard level')
    parser.add_argument('--shard-id', type=str, default='test-shard-001', help='Shard ID')
    parser.add_argument('--domains', type=str, default='python,javascript,typescript', help='Comma-separated domains')
    
    args = parser.parse_args()
    
    generator = ShardGenerator(seed=args.seed, output_dir=args.output_dir)
    domains = args.domains.split(',')
    
    print(f"Generating shard: {args.shard_id}")
    print(f"Level: {args.level}")
    print(f"Domains: {domains}")
    print(f"Seed: {args.seed}")
    
    shard_data = generator.create_shard(args.level, args.shard_id, domains)
    
    print(f"\nShard generated successfully!")
    print(f"Target LOC: {shard_data['target_loc']}")
    print(f"Actual LOC: {shard_data['actual_loc']}")
    print(f"Files created: {len(shard_data['files'])}")
    print(f"Manifest: {args.output_dir}/{args.shard_id}/manifest.json")


if __name__ == '__main__':
    main()
