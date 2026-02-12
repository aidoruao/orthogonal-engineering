"""
DEMONSTRATION: Using Atomic Repository Structural Maps
Purpose: Show how to use the generated structural maps for AI analysis
Author: Atomic Investigation System
Date: 2026-01-25
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_structural_map(json_path: str) -> Dict[str, Any]:
    """Load and validate the structural map."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def analyze_repository_structure(structural_map: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze repository structure for AI context."""

    analysis = {
        "summary": {},
        "key_components": {},
        "enforcement_layers": {},
        "recommendations": [],
    }

    # Extract summary statistics
    metadata = structural_map["repository_metadata"]
    analysis["summary"] = {
        "total_files": metadata["total_files"],
        "total_size": metadata["total_size_human"],
        "framework": metadata["framework"],
        "version": metadata["version"],
        "primary_purpose": metadata["primary_purpose"],
    }

    # Analyze directory structure
    dir_structure = structural_map["directory_structure"]
    analysis["key_components"] = {
        "automation_scripts": dir_structure.get("automation", {}).get("file_count", 0),
        "toolkit_modules": dir_structure.get("toolkit", {}).get("file_count", 0),
        "documentation_files": dir_structure.get("documentation", {}).get(
            "file_count", 0
        ),
        "analysis_tools": dir_structure.get("analysis", {}).get("file_count", 0),
        "log_files": dir_structure.get("logs", {}).get("file_count", 0),
    }

    # Extract enforcement layers
    enforcement = structural_map["enforcement_layers"]
    analysis["enforcement_layers"] = {
        layer: {"path": data["path"], "size_kb": data["size_bytes"] / 1024}
        for layer, data in enforcement.items()
    }

    # Generate AI recommendations
    total_files = metadata["total_files"]

    if total_files > 5000:
        analysis["recommendations"].append(
            "Repository has 5,000+ files - consider using the structural map "
            "for context-aware AI assistance to navigate complexity"
        )

    if dir_structure.get("logs", {}).get("file_count", 0) > 1000:
        analysis["recommendations"].append(
            "Extensive logging detected - AI can help analyze log patterns "
            "and identify boundary violation trends"
        )

    # Check for autofix system
    if "autofix_engine" in enforcement:
        analysis["recommendations"].append(
            "Autofix system detected - AI can suggest boundary fixes "
            "using the autofix_engine patterns"
        )

    return analysis


def generate_ai_context(structural_map: Dict[str, Any]) -> str:
    """Generate AI context from structural map."""

    context_parts = []

    # Repository overview
    metadata = structural_map["repository_metadata"]
    context_parts.append(f"# ORTHOGONAL ENGINEERING REPOSITORY CONTEXT")
    context_parts.append(f"**Repository:** {metadata['name']}")
    context_parts.append(f"**Purpose:** {metadata['primary_purpose']}")
    context_parts.append(
        f"**Framework:** {metadata['framework']} {metadata['version']}"
    )
    context_parts.append(
        f"**Size:** {metadata['total_files']} files, {metadata['total_size_human']}"
    )
    context_parts.append("")

    # Key directories
    context_parts.append("## KEY DIRECTORIES")
    dirs = structural_map["directory_structure"]
    for dir_name, info in dirs.items():
        if info.get("exists"):
            context_parts.append(f"- `{dir_name}/`: {info.get('file_count', 0)} files")
    context_parts.append("")

    # Enforcement layers
    context_parts.append("## ENFORCEMENT LAYERS")
    layers = structural_map["enforcement_layers"]
    for layer_name, layer_info in layers.items():
        context_parts.append(
            f"- **{layer_name}**: `{layer_info['path']}` ({layer_info['size_bytes']} bytes)"
        )
    context_parts.append("")

    # Script categories
    context_parts.append("## SCRIPT CATEGORIES")
    scripts = structural_map.get("scripts", [])
    script_categories = {}
    for script in scripts[:20]:  # First 20 as examples
        if script.endswith(".py"):
            if "automation" in script:
                script_categories.setdefault("automation", []).append(script)
            elif "toolkit" in script:
                script_categories.setdefault("toolkit", []).append(script)
            elif "analysis" in script:
                script_categories.setdefault("analysis", []).append(script)

    for category, files in script_categories.items():
        context_parts.append(f"### {category.upper()}")
        for file in files[:5]:  # First 5 files per category
            context_parts.append(f"- `{file}`")
        if len(files) > 5:
            context_parts.append(f"  ... and {len(files) - 5} more")
        context_parts.append("")

    # Verification protocols
    context_parts.append("## VERIFICATION PROTOCOLS")
    protocols = structural_map.get("verification_protocols", {})
    for protocol_name, protocol_info in protocols.items():
        context_parts.append(f"### {protocol_name.replace('_', ' ').title()}")
        if isinstance(protocol_info, dict):
            for key, value in protocol_info.items():
                if isinstance(value, list):
                    context_parts.append(f"- **{key}**: {', '.join(value[:3])}")
                    if len(value) > 3:
                        context_parts.append(f"  ... and {len(value) - 3} more items")
                else:
                    context_parts.append(f"- **{key}**: {value}")
        context_parts.append("")

    return "\n".join(context_parts)


def demonstrate_usage():
    """Demonstrate practical usage of structural maps."""

    print("=" * 70)
    print("DEMONSTRATION: Atomic Repository Structural Map Usage")
    print("=" * 70)

    # Load the structural map
    json_path = "repository_structural_map_full.json"
    yaml_path = "repository_structural_map_full.yaml"

    print(f"\n📁 Loading structural map from: {json_path}")

    try:
        # Load JSON version
        structural_map = load_structural_map(json_path)
        print("✅ Structural map loaded successfully")

        # Analyze the structure
        print("\n🔍 Analyzing repository structure...")
        analysis = analyze_repository_structure(structural_map)

        # Display summary
        print("\n📊 REPOSITORY SUMMARY:")
        print(f"   Total files: {analysis['summary']['total_files']}")
        print(f"   Total size: {analysis['summary']['total_size']}")
        print(f"   Framework: {analysis['summary']['framework']}")
        print(f"   Version: {analysis['summary']['version']}")

        # Display key components
        print("\n🏗️ KEY COMPONENTS:")
        for component, count in analysis["key_components"].items():
            print(f"   {component.replace('_', ' ').title()}: {count} files")

        # Display enforcement layers
        print("\n🛡️ ENFORCEMENT LAYERS:")
        for layer, info in analysis["enforcement_layers"].items():
            print(f"   {layer}: {info['path']} ({info['size_kb']:.1f} KB)")

        # Display recommendations
        print("\n💡 AI RECOMMENDATIONS:")
        for i, recommendation in enumerate(analysis["recommendations"], 1):
            print(f"   {i}. {recommendation}")

        # Generate AI context
        print("\n🤖 GENERATED AI CONTEXT (excerpt):")
        ai_context = generate_ai_context(structural_map)
        lines = ai_context.split("\n")[:30]  # First 30 lines
        for line in lines:
            print(f"   {line}")
        if len(ai_context.split("\n")) > 30:
            print(f"   ... and {len(ai_context.split('\n')) - 30} more lines")

        # Demonstrate practical queries
        print("\n🔎 PRACTICAL QUERIES ENABLED:")
        print("   1. 'What automation scripts are available for boundary enforcement?'")
        print("   2. 'How do I use the autofix system for code violations?'")
        print("   3. 'What are the verification protocols for this repository?'")
        print("   4. 'Show me the enforcement layer architecture'")
        print(
            "   5. 'What analysis tools are available for epistemic drift detection?'"
        )

        # Show file counts by type
        print("\n📈 FILE TYPE DISTRIBUTION:")
        scripts = structural_map.get("scripts", [])
        markdowns = structural_map.get("markdowns", [])
        configs = structural_map.get("configs", [])

        print(f"   Scripts (.py/.js/.bat/.ps1): {len(scripts)}")
        print(f"   Documentation (.md): {len(markdowns)}")
        print(f"   Configuration files: {len(configs)}")

        # Calculate enforcement layer coverage
        print("\n🔄 ENFORCEMENT COVERAGE:")
        required_layers = [
            "html_blueprint",
            "rule_interpretation",
            "python_enforcement",
            "ide_integration",
            "autofix_engine",
        ]

        present_layers = structural_map.get("enforcement_layers", {}).keys()
        coverage = sum(1 for layer in required_layers if layer in present_layers)
        print(f"   Required layers: {len(required_layers)}")
        print(f"   Present layers: {coverage}")
        print(f"   Coverage: {(coverage / len(required_layers)) * 100:.0f}%")

        print("\n" + "=" * 70)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("ATOMIC STRUCTURAL MAP USAGE DEMONSTRATION")
    print("=" * 70)
    print("\nThis script demonstrates how to use the atomic repository")
    print("structural maps for AI-assisted development and analysis.")
    print("\nKey capabilities demonstrated:")
    print("1. Repository structure analysis")
    print("2. AI context generation")
    print("3. Enforcement layer verification")
    print("4. Practical query enablement")
    print("5. Coverage assessment")

    try:
        return demonstrate_usage()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demonstration interrupted by user")
        return 0


if __name__ == "__main__":
    sys.exit(main())
