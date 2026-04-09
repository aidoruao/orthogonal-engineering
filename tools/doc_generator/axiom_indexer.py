"""Axiom Indexer — cross-reference axioms with domains and SAL types.

Maps axioms to their usage across the codebase and detects gaps.
"""

import ast
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from pathlib import Path


@dataclass
class AxiomEntry:
    """Entry for a single axiom module."""
    name: str
    file_path: str
    defined_types: List[str] = field(default_factory=list)
    used_by_domains: List[str] = field(default_factory=list)
    referenced_in: List[str] = field(default_factory=list)
    theorem_count: int = 0
    proof_count: int = 0


class AxiomIndexer:
    """Index and cross-reference axiom modules."""
    
    def __init__(self, axioms_path: str = "axioms", sal_path: str = "src/sal"):
        self.axioms_path = Path(axioms_path)
        self.sal_path = Path(sal_path)
        self.entries: Dict[str, AxiomEntry] = {}
        self._type_registry: Dict[str, str] = {}  # type_name -> axiom file
    
    def index_axioms(self) -> Dict[str, AxiomEntry]:
        """Index all axiom modules."""
        if not self.axioms_path.exists():
            return self.entries
        
        for axiom_file in sorted(self.axioms_path.glob("*.py")):
            entry = self._analyze_axiom_file(axiom_file)
            self.entries[entry.name] = entry
        
        # Cross-reference with SAL
        self._cross_reference_sal()
        
        return self.entries
    
    def _analyze_axiom_file(self, path: Path) -> AxiomEntry:
        """Analyze a single axiom file."""
        content = path.read_text()
        
        entry = AxiomEntry(
            name=path.stem,
            file_path=str(path),
        )
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Count class definitions (types)
                if isinstance(node, ast.ClassDef):
                    entry.defined_types.append(node.name)
                    self._type_registry[node.name] = path.stem
                
                # Count theorem functions
                if isinstance(node, ast.FunctionDef):
                    if "theorem" in node.name.lower():
                        entry.theorem_count += 1
                    if node.name.startswith("prove_") or "proof" in node.name.lower():
                        entry.proof_count += 1
        
        except SyntaxError:
            pass
        
        return entry
    
    def _cross_reference_sal(self) -> None:
        """Find which SAL modules reference which axioms."""
        if not self.sal_path.exists():
            return
        
        for sal_file in self.sal_path.rglob("*.py"):
            content = sal_file.read_text()
            
            for axiom_name, entry in self.entries.items():
                # Check if this SAL file imports from this axiom
                if f"from axioms.{axiom_name}" in content or f"import axioms.{axiom_name}" in content:
                    if str(sal_file) not in entry.referenced_in:
                        entry.referenced_in.append(str(sal_file))
    
    def find_axiom_for_type(self, type_name: str) -> Optional[str]:
        """Find which axiom module defines a type."""
        return self._type_registry.get(type_name)
    
    def find_unreferenced_axioms(self) -> List[str]:
        """Find axioms not referenced anywhere in SAL."""
        if not self.entries:
            self.index_axioms()
        
        unreferenced = []
        for name, entry in self.entries.items():
            if not entry.referenced_in:
                unreferenced.append(name)
        
        return unreferenced
    
    def generate_index(self) -> Dict:
        """Generate complete axiom index."""
        if not self.entries:
            self.index_axioms()
        
        return {
            "total_axioms": len(self.entries),
            "total_defined_types": len(self._type_registry),
            "unreferenced_axioms": self.find_unreferenced_axioms(),
            "axioms": {
                name: {
                    "file": entry.file_path,
                    "defined_types": entry.defined_types,
                    "theorem_count": entry.theorem_count,
                    "proof_count": entry.proof_count,
                    "referenced_in": entry.referenced_in,
                }
                for name, entry in self.entries.items()
            },
            "type_registry": self._type_registry,
        }
    
    def generate_markdown(self) -> str:
        """Generate markdown documentation."""
        if not self.entries:
            self.index_axioms()
        
        lines = [
            "# Axiom Cross-Reference Index",
            "",
            f"**Total Axiom Modules:** {len(self.entries)}",
            f"**Total Defined Types:** {len(self._type_registry)}",
            "",
        ]
        
        # Unreferenced axioms warning
        unref = self.find_unreferenced_axioms()
        if unref:
            lines.append("## ⚠️ Unreferenced Axioms")
            lines.append("")
            for name in unref:
                lines.append(f"- `{name}`")
            lines.append("")
        
        # Axiom details
        lines.append("## Axiom Modules")
        lines.append("")
        
        for name, entry in sorted(self.entries.items()):
            lines.append(f"### {name}")
            lines.append(f"- **File:** `{entry.file_path}`")
            lines.append(f"- **Types:** {', '.join(entry.defined_types) or 'None'}")
            lines.append(f"- **Theorems:** {entry.theorem_count}")
            lines.append(f"- **Proofs:** {entry.proof_count}")
            
            if entry.referenced_in:
                lines.append("- **Referenced in:**")
                for ref in entry.referenced_in[:5]:  # Limit to 5
                    lines.append(f"  - `{ref}`")
            
            lines.append("")
        
        return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    indexer = AxiomIndexer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(indexer.generate_index(), indent=2))
    else:
        print(indexer.generate_markdown())
