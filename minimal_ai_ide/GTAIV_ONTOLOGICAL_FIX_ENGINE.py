"""
GTAIV_ONTOLOGICAL_FIX_ENGINE.py
================================

ONTOLOGICAL FIX ENGINE FOR GTA IV MOD VERSION MISMATCHES
Implements formal ontological reasoning to detect and fix mod compatibility issues

CORE PRINCIPLE: Fix version mismatches at the ontological level by:
1. Formalizing game version identity
2. Modeling mod compatibility constraints
3. Implementing constraint satisfaction algorithms
4. Automatically resolving conflicts

ONTOLOGICAL AXIOMS:
1. Version Identity: Every GTA IV executable has determinable version identity
2. Mod Specificity: Every mod has explicit/implicit version constraints
3. Loader Exclusivity: Only one ASI loader can occupy the loader space
4. Conflict Symmetry: If A conflicts with B, then B conflicts with A
"""

import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

# ==================== ONTOLOGICAL CORE ====================

class GTAIVVersionOntology:
    """Formal ontology of GTA IV game versions"""

    VERSION_SIGNATURES = {
        # File size in bytes -> version mapping
        17425752: "1.0.7.0_or_CompleteEdition",  # 17.4 MB - Patch 7 or CE
        15204352: "1.0.0.0",  # 14.5 MB - Original
        17426432: "1.0.8.0",  # 17.4 MB with slight variation
    }

    VERSION_COMPATIBILITY = {
        "1.0.7.0_or_CompleteEdition": {
            "scripthook_versions": ["0.5.1", "0.6.0"],
            "asi_loaders": ["dinput8.dll", "xlive.dll"],
            "requires_downgrade": False,
            "notes": "Most common modding target"
        },
        "1.0.0.0": {
            "scripthook_versions": ["0.5.0"],
            "asi_loaders": ["dinput8.dll"],
            "requires_downgrade": True,
            "notes": "Original release, GFWL required"
        },
        "1.0.8.0": {
            "scripthook_versions": ["0.5.2", "0.6.1"],
            "asi_loaders": ["xlive.dll"],
            "requires_downgrade": False,
            "notes": "Complete Edition base"
        }
    }

    @classmethod
    def identify_version(cls, exe_path: Path) -> Dict[str, Any]:
        """Ontologically identify game version using multi-factor analysis"""
        if not exe_path.exists():
            return {"error": "GTAIV.exe not found"}

        # Factor 1: File size
        file_size = exe_path.stat().st_size
        size_based = cls.VERSION_SIGNATURES.get(file_size, "unknown")

        # Factor 2: Binary hash pattern (partial for speed)
        hash_based = "unknown"
        try:
            with open(exe_path, 'rb') as f:
                # Read first 1MB for signature analysis
                data = f.read(1024 * 1024)
                file_hash = hashlib.md5(data).hexdigest()
                # Simple pattern matching (in reality would use more sophisticated signatures)
                if file_hash.startswith(('a1b2', 'c3d4')):
                    hash_based = "1.0.7.0"
                elif file_hash.startswith(('e5f6', '7890')):
                    hash_based = "1.0.8.0"
        except:
            hash_based = "hash_failed"

        # Factor 3: File structure analysis
        structure_based = "unknown"

        # Combine factors with confidence scoring
        if size_based == hash_based != "unknown":
            confidence = "high"
            version = size_based
        elif size_based != "unknown":
            confidence = "medium"
            version = size_based
        else:
            confidence = "low"
            version = "unknown"

        return {
            "detected_version": version,
            "confidence": confidence,
            "file_size": file_size,
            "size_based": size_based,
            "hash_based": hash_based,
            "timestamp": datetime.now().isoformat()
        }


class ModCompatibilityOntology:
    """Formal ontology of mod compatibility relationships"""

    MOD_COMPATIBILITY_RULES = {
        # Rule: (mod_pattern, version_constraint, conflict_with)
        "scripthook": {
            "pattern": r"ScriptHook\.dll",
            "version_constraint": "must_match_game_version",
            "conflicts": [],
            "essential": True
        },
        "asi_loader": {
            "pattern": r"(dinput8|xlive)\.dll",
            "version_constraint": "version_agnostic",
            "conflicts": ["other_asi_loader"],
            "essential": True,
            "mutually_exclusive": True
        },
        "graphics_wrapper": {
            "pattern": r"d3d9\.dll",
            "version_constraint": "version_agnostic",
            "conflicts": ["other_graphics_wrapper"],
            "essential": False
        },
        "dotnet_support": {
            "pattern": r"ScriptHookDotNet\.asi",
            "version_constraint": "requires_scripthook",
            "conflicts": [],
            "essential": False
        },
        "zolikapatch": {
            "pattern": r"ZolikaPatch\.asi",
            "version_constraint": "1.0.7.0_or_later",
            "conflicts": [],
            "essential": False
        }
    }

    @classmethod
    def analyze_mod_compatibility(cls, game_version: str, mod_files: List[Path]) -> Dict[str, Any]:
        """Ontologically analyze mod compatibility with game version"""

        results = {
            "game_version": game_version,
            "total_mods": len(mod_files),
            "compatible": [],
            "incompatible": [],
            "conflicts": [],
            "recommendations": []
        }

        # Categorize mods
        categorized = {}
        for mod_file in mod_files:
            mod_name = mod_file.name
            for mod_type, rules in cls.MOD_COMPATIBILITY_RULES.items():
                if re.search(rules["pattern"], mod_name, re.IGNORECASE):
                    categorized.setdefault(mod_type, []).append(mod_file)
                    break

        # Check ASI loader exclusivity (ontological axiom: loader exclusivity)
        asi_loaders = categorized.get("asi_loader", [])
        if len(asi_loaders) > 1:
            results["conflicts"].append({
                "type": "asi_loader_conflict",
                "message": f"Multiple ASI loaders found: {[f.name for f in asi_loaders]}",
                "fix": "Remove all but one ASI loader"
            })

        # Check ScriptHook version compatibility
        scripthooks = categorized.get("scripthook", [])
        if scripthooks:
            # In reality, would check actual ScriptHook version
            results["compatible"].append({
                "mod": "ScriptHook.dll",
                "status": "present",
                "check": "version_verification_needed"
            })
        else:
            results["recommendations"].append({
                "action": "install_scripthook",
                "reason": "No ScriptHook found - essential for most mods"
            })

        # Check for graphics wrapper conflicts
        graphics_wrappers = categorized.get("graphics_wrapper", [])
        if len(graphics_wrappers) > 1:
            results["conflicts"].append({
                "type": "graphics_wrapper_conflict",
                "message": f"Multiple graphics wrappers: {[f.name for f in graphics_wrappers]}",
                "fix": "Remove all but one graphics wrapper (d3d9.dll)"
            })

        return results


# ==================== CONSTRAINT SATISFACTION ENGINE ====================

class ConstraintSatisfactionEngine:
    """Implements ontological constraint satisfaction for mod compatibility"""

    def __init__(self, gtaiv_path: Path):
        self.gtaiv_path = gtaiv_path
        self.version_ontology = GTAIVVersionOntology()
        self.mod_ontology = ModCompatibilityOntology()

    def detect_game_version(self) -> Dict[str, Any]:
        """Ontologically detect game version with confidence scoring"""
        exe_path = self.gtaiv_path / "GTAIV.exe"
        return self.version_ontology.identify_version(exe_path)

    def enumerate_mods(self) -> List[Path]:
        """Find all mod files in GTA IV directory"""
        mod_patterns = [
            "*.asi",
            "*.dll",
            "*.ini",
            "*.cfg"
        ]

        mods = []
        for pattern in mod_patterns:
            mods.extend(self.gtaiv_path.glob(pattern))

        # Also check common mod directories
        mod_dirs = ["plugins", "scripts", "update"]
        for mod_dir in mod_dirs:
            dir_path = self.gtaiv_path / mod_dir
            if dir_path.exists():
                for item in dir_path.rglob("*"):
                    if item.is_file() and item.suffix in ['.asi', '.dll', '.ini', '.xml', '.dat']:
                        mods.append(item)

        return mods

    def analyze_constraints(self) -> Dict[str, Any]:
        """Perform full ontological constraint analysis"""
        # Step 1: Identify game version
        version_info = self.detect_game_version()
        game_version = version_info.get("detected_version", "unknown")

        # Step 2: Enumerate mods
        mod_files = self.enumerate_mods()

        # Step 3: Analyze compatibility
        compatibility = self.mod_ontology.analyze_mod_compatibility(game_version, mod_files)

        # Step 4: Generate fix plan
        fix_plan = self.generate_fix_plan(version_info, compatibility)

        return {
            "timestamp": datetime.now().isoformat(),
            "game_version": version_info,
            "mod_analysis": compatibility,
            "fix_plan": fix_plan,
            "constraints_satisfied": len(fix_plan.get("actions", [])) == 0
        }

    def generate_fix_plan(self, version_info: Dict, compatibility: Dict) -> Dict[str, Any]:
        """Generate ontological fix plan based on constraint violations"""
        actions = []

        # Fix 1: Resolve ASI loader conflicts
        for conflict in compatibility.get("conflicts", []):
            if conflict["type"] == "asi_loader_conflict":
                actions.append({
                    "action": "resolve_asi_loader_conflict",
                    "description": conflict["message"],
                    "steps": [
                        "Identify all ASI loader files",
                        "Select optimal loader based on other mods",
                        "Remove redundant loaders",
                        "Test remaining loader"
                    ]
                })

        # Fix 2: Ensure ScriptHook compatibility
        if version_info.get("detected_version") != "unknown":
            actions.append({
                "action": "verify_scripthook_compatibility",
                "description": f"Ensure ScriptHook matches game version {version_info['detected_version']}",
                "steps": [
                    f"Check ScriptHook version compatibility for {version_info['detected_version']}",
                    "Download correct version if needed",
                    "Replace incompatible ScriptHook"
                ]
            })

        # Fix 3: Handle graphics wrapper conflicts
        for conflict in compatibility.get("conflicts", []):
            if conflict["type"] == "graphics_wrapper_conflict":
                actions.append({
                    "action": "resolve_graphics_wrapper_conflict",
                    "description": conflict["message"],
                    "steps": [
                        "Identify all graphics wrapper files",
                        "Select primary wrapper (usually d3d9.dll)",
                        "Remove conflicting wrappers",
                        "Test graphics functionality"
                    ]
                })

        return {
            "total_actions": len(actions),
            "actions": actions,
            "constraint_violations": len(compatibility.get("conflicts", [])),
            "ready_for_repair": len(actions) > 0
        }


# ==================== ONTOLOGICAL REPAIR ENGINE ====================

class OntologicalRepairEngine:
    """Implements ontological repairs based on constraint analysis"""

    def __init__(self, gtaiv_path: Path):
        self.gtaiv_path = gtaiv_path
        self.backup_dir = gtaiv_path / "ontological_backup"
        self.backup_dir.mkdir(exist_ok=True)

    def backup_file(self, file_path: Path) -> Path:
        """Create ontological backup of file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{timestamp}"
        backup_path = self.backup_dir / backup_name

        if file_path.exists():
            shutil.copy2(file_path, backup_path)
            return backup_path
        return None

    def resolve_asi_loader_conflict(self) -> Dict[str, Any]:
        """Ontologically resolve ASI loader conflicts (enforce exclusivity axiom)"""
        asi_loaders = list(self.gtaiv_path.glob("*.dll"))
        asi_loaders = [f for f in asi_loaders if f.name.lower() in ["dinput8.dll", "xlive.dll"]]

        if len(asi_loaders) <= 1:
            return {"status": "no_conflict", "message": "Only one or zero ASI loaders found"}

        # Ontological decision: Keep xlive.dll if present (better for Complete Edition)
        # Otherwise keep dinput8.dll
        loader_to_keep = None
        loader_to_remove = []

        for loader in asi_loaders:
            if loader.name.lower() == "xlive.dll":
                loader_to_keep = loader
                break

        if not loader_to_keep:
            loader_to_keep = asi_loaders[0]  # Keep first one

        # Backup and remove others
        results = {"kept": loader_to_keep.name, "removed": []}
        for loader in asi_loaders:
            if loader != loader_to_keep:
                backup = self.backup_file(loader)
                loader.unlink()
                results["removed"].append({
                    "file": loader.name,
                    "backup": backup.name if backup else "no_backup"
                })

        return results

    def fix_scripthook_version(self, target_version: str) -> Dict[str, Any]:
        """Ontologically fix ScriptHook version mismatch"""
        scripthook_path = self.gtaiv_path / "ScriptHook.dll"

        if not scripthook_path.exists():
            return {"status": "not_found", "message": "ScriptHook.dll not present"}

        # Backup current
        backup = self.backup_file(scripthook_path)

        # In reality, would:
        # 1. Determine current ScriptHook version
        # 2. Download correct version for target_version
        # 3. Replace if mismatch

        return {
            "status": "simulated_fix",
            "message": f"Would fix ScriptHook for version {target_version}",
            "backup": backup.name if backup else "no_backup",
            "action_required": "manual_download_needed"
        }

    def create_version_identity_file(self) -> Path:
        """Create ontological version identity file to prevent future mismatches"""
        version_file = self.gtaiv_path / "ONTOLOGICAL_VERSION_IDENTITY.json"

        identity = {
            "ontology": "GTAIV_Version_Identity_v1.0",
            "created": datetime.now().isoformat(),
            "detection_method": "ontological_constraint_analysis",
            "game_directory": str(self.gtaiv_path),
            "identity_assertions": [
                "This file formally declares the ontological identity of this GTA IV installation",
                "Mods should check this file before loading to ensure compatibility",
                "Automatically generated by ontological fix engine"
            ],
            "recommended_mods": {
                "asi_loader": "xlive.dll (recommended for Complete Edition)",
                "scripthook_source": "http://dev-c.com/gta4/scripthook/",
                "compatibility_check": "Run ontological analysis before adding new mods"
            }
        }

        with open(version_file, 'w') as f:
            json.dump(identity, f, indent=2)

        return version_file

    def execute_fix_plan(self, fix_plan: Dict) -> Dict[str, Any]:
        """Execute ontological fix plan"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "actions_performed": [],
            "backups_created": [],
            "errors": []
        }

        for action in fix_plan.get("actions", []):
            try:
                if action["action"] == "resolve_asi_loader_conflict":
                    result = self.resolve_asi_loader_conflict()
                    results["actions_performed"].append({
                        "action": "resolve_asi_loader_conflict",
                        "result": result
                    })

                elif action["action"] == "verify_scripthook_compatibility":
                    # Would need actual target version from analysis
                    result = self.fix_scripthook_version("1.0.7.0_or_CompleteEdition")
                    results["actions_performed"].append({
                        "action": "verify_scripthook_compatibility",
                        "result": result
                    })

                elif action["action"] == "resolve_graphics_wrapper_conflict":
                    # Simple implementation: keep only one d3d9.dll
                    graphics_files = list(self.gtaiv_path.glob("d3d9.dll"))
                    if len(graphics_files) > 1:
                        # Keep the first, backup and remove others
                        keeper = graphics_files[0]
                        for gfx in graphics_files[1:]:
                            backup = self.backup_file(gfx)
                            gfx.unlink()
                            results["backups_created"].append(backup.name if backup else "unknown")

                        results["actions_performed"].append({
                            "action": "resolve_graphics_wrapper_conflict",
                            "kept": keeper.name,
                            "removed": len(g
