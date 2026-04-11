#!/usr/bin/env python3
"""
tools/website/generate_data.py — Website Data Generator

Reads repository state and outputs JSON for the witness node website.
Generates:
- domain_status.json (157 domains, deepened/stub counts)
- case_study_index.json (all CS entries)
- kernel_modules.json (all kernel files + line counts)
- merkle_state.json (current Merkle root)
- youtuber_audit_stats.json (all channels + entry counts)

Usage:
    python tools/website/generate_data.py

Output goes to website/api/

Authority: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = REPO_ROOT / "website" / "api"


def count_lines(filepath: Path) -> int:
    """Count non-empty lines in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for line in f if line.strip())
    except:
        return 0


def get_git_commit() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()[:12]
    except:
        return "unknown"


def generate_domain_status() -> Dict[str, Any]:
    """Generate domain status from DOMAIN_INVARIANT_STATUS.md or source files."""
    domains_dir = REPO_ROOT / "src" / "domains"
    domains = []
    
    if domains_dir.exists():
        for d in sorted(domains_dir.iterdir()):
            if d.is_dir() and d.name.startswith("d_"):
                invariants_file = d / "invariants.py"
                line_count = count_lines(invariants_file) if invariants_file.exists() else 0
                
                # Determine status based on line count
                if line_count > 200:
                    status = "deepened"
                elif line_count > 100:
                    status = "moderate"
                elif line_count > 50:
                    status = "basic"
                else:
                    status = "stub"
                
                domains.append({
                    "id": d.name,
                    "name": d.name[2:].replace("_", " ").title(),
                    "lines": line_count,
                    "status": status,
                })
    
    total = len(domains)
    deepened = sum(1 for d in domains if d["status"] == "deepened")
    moderate = sum(1 for d in domains if d["status"] == "moderate")
    basic = sum(1 for d in domains if d["status"] == "basic")
    stub = sum(1 for d in domains if d["status"] == "stub")
    
    return {
        "total": total,
        "deepened": deepened,
        "moderate": moderate,
        "basic": basic,
        "stub": stub,
        "domains": domains,
    }


def generate_case_study_index() -> Dict[str, Any]:
    """Generate case study index from ontology/case_studies.json."""
    case_studies_file = REPO_ROOT / "ontology" / "case_studies.json"
    
    entries = []
    if case_studies_file.exists():
        try:
            with open(case_studies_file, 'r') as f:
                data = json.load(f)
                for cs_id, cs_data in data.items():
                    entries.append({
                        "id": cs_id,
                        "title": cs_data.get("title", "Unknown"),
                        "category": cs_data.get("category", "Uncategorized"),
                        "violation": cs_data.get("violation_type", "Unknown"),
                    })
        except:
            pass
    
    # Count by category
    categories = {}
    for e in entries:
        cat = e["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total": len(entries),
        "categories": categories,
        "recent": entries[-10:] if entries else [],
    }


def generate_kernel_modules() -> Dict[str, Any]:
    """Generate kernel module statistics."""
    kernel_dir = REPO_ROOT / "kernel"
    modules = []
    
    if kernel_dir.exists():
        for py_file in sorted(kernel_dir.rglob("*.py")):
            if py_file.name == "__init__.py":
                continue
            rel_path = py_file.relative_to(REPO_ROOT)
            line_count = count_lines(py_file)
            modules.append({
                "path": str(rel_path),
                "lines": line_count,
            })
    
    total_lines = sum(m["lines"] for m in modules)
    
    return {
        "total_files": len(modules),
        "total_lines": total_lines,
        "modules": sorted(modules, key=lambda x: x["lines"], reverse=True)[:50],
    }


def generate_merkle_state() -> Dict[str, Any]:
    """Generate Merkle state from evidence manager if available."""
    try:
        # Try to import and use the evidence manager
        import sys
        sys.path.insert(0, str(REPO_ROOT))
        from toolkit.oe.evidence_manager import EvidenceManager
        
        em = EvidenceManager(str(REPO_ROOT))
        omega_root = em.compute_omega_root()
        
        return {
            "merkle_root": omega_root,
            "file_count": len(em.file_list),
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }
    except:
        # Fallback: compute simple hash of key files
        key_files = [
            "STATE.md",
            "MEMORY.md",
            "SOP_AI_HANDSHAKE.md",
        ]
        
        hasher = hashlib.sha256()
        for fname in key_files:
            fpath = REPO_ROOT / fname
            if fpath.exists():
                hasher.update(fpath.read_bytes())
        
        return {
            "merkle_root": hasher.hexdigest(),
            "file_count": len(key_files),
            "computed_at": datetime.now(timezone.utc).isoformat(),
            "method": "fallback_hash",
        }


def generate_youtuber_audit_stats() -> Dict[str, Any]:
    """Generate YouTuber audit statistics."""
    audits_dir = REPO_ROOT / "case_studies" / "youtuber_audits" / "tech"
    channels = []
    
    if audits_dir.exists():
        for py_file in sorted(audits_dir.glob("*.py")):
            if py_file.name == "__init__.py":
                continue
            
            line_count = count_lines(py_file)
            # Estimate entry count (rough heuristic: ~15 lines per entry)
            estimated_entries = max(1, line_count // 15)
            
            channels.append({
                "name": py_file.stem.replace("_", " ").title(),
                "file": py_file.name,
                "lines": line_count,
                "estimated_entries": estimated_entries,
            })
    
    return {
        "total_channels": len(channels),
        "total_entries": sum(c["estimated_entries"] for c in channels),
        "channels": channels,
    }


def generate_all():
    """Generate all data files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    commit = get_git_commit()
    
    # Generate individual files
    files = {
        "domain_status.json": generate_domain_status(),
        "case_study_index.json": generate_case_study_index(),
        "kernel_modules.json": generate_kernel_modules(),
        "merkle_state.json": generate_merkle_state(),
        "youtuber_audit_stats.json": generate_youtuber_audit_stats(),
    }
    
    for filename, data in files.items():
        data["generated"] = timestamp
        data["commit"] = commit
        data["version"] = "1.0"
        
        output_path = OUTPUT_DIR / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated: {output_path}")
    
    # Generate combined status.json
    status = {
        "version": "1.0",
        "generated": timestamp,
        "commit": commit,
        "domains": files["domain_status.json"]["total"],
        "domains_deepened": files["domain_status.json"]["deepened"],
        "case_studies": files["case_study_index.json"]["total"],
        "kernel_files": files["kernel_modules.json"]["total_files"],
        "kernel_lines": files["kernel_modules.json"]["total_lines"],
        "merkle_root": files["merkle_state.json"]["merkle_root"],
        "youtuber_channels": files["youtuber_audit_stats.json"]["total_channels"],
    }
    
    status_path = OUTPUT_DIR / "status.json"
    with open(status_path, 'w') as f:
        json.dump(status, f, indent=2)
    print(f"Generated: {status_path}")
    
    print("\nAll data files generated successfully!")


if __name__ == "__main__":
    generate_all()
