"""
FORMAL_SPEC_LOADER.py
=====================

MOST INVARIANT FORMAL SPECIFICATION LOADER
Hierarchy: JSON/LaTeX (most invariant) → Markdown (human interface) → Python (generic orchestrator)

ARCHITECTURE:
1. JSON/LaTeX: Formal specifications (machine-readable, unambiguous)
2. Markdown: Human interface with annotations
3. Python: Generic loader/orchestrator only
4. Daemon: Exclusive interpreter with Σ_LORA constraints

PRINCIPLE: "All intelligence paths factor through formal specifications"
"""

import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import yaml

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class SpecType(Enum):
    """Types of formal specifications"""

    JSON = "json"  # Most invariant: machine-readable, unambiguous
    LATEX = "tex"  # Mathematical formalisms
    YAML = "yaml"  # Configuration specifications
    MARKDOWN = "md"  # Human interface with annotations
    PYTHON = "py"  # Only for orchestration, never domain logic


class ConstraintTag(Enum):
    """Σ_LORA constraint tags for annotation"""

    LOGOS = "LOGOS"
    CHALCEDON = "CHALCEDON"
    GRACE = "GRACE"
    ESCHATON = "ESCHATON"
    AGAPE = "AGAPE"
    KENOSIS = "KENOSIS"


@dataclass
class FormalSpec:
    """Formal specification container"""

    spec_type: SpecType
    file_path: Path
    content: str
    constraints: Set[ConstraintTag] = field(default_factory=set)
    theorem_references: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def is_most_invariant(self) -> bool:
        """Check if this is the most invariant spec type"""
        return self.spec_type in [SpecType.JSON, SpecType.LATEX, SpecType.YAML]

    def to_daemon_query(self) -> Dict:
        """Convert to daemon query format"""
        return {
            "spec_type": self.spec_type.value,
            "content": self.content,
            "constraints": [c.value for c in self.constraints],
            "theorems": self.theorem_references,
            "metadata": self.metadata,
        }


@dataclass
class SpecHierarchy:
    """
    Hierarchy of formal specifications

    MOST INVARIANT → LEAST INVARIANT:
    1. JSON/LaTeX/YAML (formal, machine-readable)
    2. Markdown (human interface)
    3. Python (orchestration only)
    """

    formal_specs: List[FormalSpec] = field(default_factory=list)
    hierarchy_order: List[SpecType] = field(
        default_factory=lambda: [
            SpecType.JSON,
            SpecType.LATEX,
            SpecType.YAML,
            SpecType.MARKDOWN,
            SpecType.PYTHON,
        ]
    )

    def add_spec(self, spec: FormalSpec):
        """Add specification to hierarchy"""
        self.formal_specs.append(spec)
        # Sort by invariance (most invariant first)
        self.formal_specs.sort(key=lambda s: self.hierarchy_order.index(s.spec_type))

    def get_most_invariant(self) -> List[FormalSpec]:
        """Get most invariant specifications"""
        return [s for s in self.formal_specs if s.is_most_invariant()]

    def get_by_constraint(self, constraint: ConstraintTag) -> List[FormalSpec]:
        """Get specifications with specific constraint"""
        return [s for s in self.formal_specs if constraint in s.constraints]

    def combine_for_daemon(self) -> Dict:
        """Combine all specs for daemon query"""
        combined = {
            "formal_specs": [],
            "markdown_context": [],
            "orchestration_instructions": [],
            "constraints_present": set(),
            "theorems_referenced": set(),
        }

        for spec in self.formal_specs:
            # Add based on type
            if spec.is_most_invariant():
                combined["formal_specs"].append(spec.to_daemon_query())
            elif spec.spec_type == SpecType.MARKDOWN:
                combined["markdown_context"].append(spec.to_daemon_query())
            elif spec.spec_type == SpecType.PYTHON:
                combined["orchestration_instructions"].append(spec.to_daemon_query())

            # Collect constraints and theorems
            combined["constraints_present"].update(spec.constraints)
            combined["theorems_referenced"].update(spec.theorem_references)

        # Convert sets to lists for JSON serialization
        combined["constraints_present"] = [
            c.value for c in combined["constraints_present"]
        ]
        combined["theorems_referenced"] = list(combined["theorems_referenced"])

        return combined


class FormalSpecLoader:
    """
    Load formal specifications with invariance hierarchy

    Features:
    1. Discovers all formal specs in repository
    2. Parses with appropriate invariance level
    3. Extracts constraints and theorems
    4. Prepares for daemon query
    5. Enforces hierarchy: JSON/LaTeX > Markdown > Python
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.hierarchy = SpecHierarchy()
        self.constraint_pattern = re.compile(r"\[CONSTRAINT:\s*(\w+)\]", re.IGNORECASE)
        self.theorem_pattern = re.compile(r"Theorem[_\s](\d+|[A-Z])", re.IGNORECASE)

        # Known constraint files
        self.known_constraint_files = {
            "Σ_LORA_MANIFEST.json": "Σ_LORA formal manifest",
            "corporate_invariants.json": "Corporate governance invariants",
            "maximally_strict_invariants.json": "Maximal strict invariants",
            "christ.tex": "Christological mathematical specification",
            "Σ_LORA_COMPLETE_SYSTEM_REPORT.md": "Σ_LORA complete system report",
        }

    def discover_specs(self) -> int:
        """Discover all formal specifications in repository"""
        spec_count = 0

        # Look for known constraint files first (most invariant)
        for filename, description in self.known_constraint_files.items():
            file_path = self.repo_path / filename
            if file_path.exists():
                spec = self._load_spec_file(file_path)
                if spec:
                    self.hierarchy.add_spec(spec)
                    spec_count += 1
                    print(f"✅ Loaded known spec: {description}")

        # Discover JSON files (formal specifications)
        for json_file in self.repo_path.rglob("*.json"):
            if json_file.name not in self.known_constraint_files:
                spec = self._load_spec_file(json_file)
                if spec and self._is_formal_spec(json_file):
                    self.hierarchy.add_spec(spec)
                    spec_count += 1

        # Discover LaTeX files (mathematical formalisms)
        for tex_file in self.repo_path.rglob("*.tex"):
            spec = self._load_spec_file(tex_file)
            if spec:
                self.hierarchy.add_spec(spec)
                spec_count += 1

        # Discover Markdown files (human interface)
        for md_file in self.repo_path.rglob("*.md"):
            spec = self._load_spec_file(md_file)
            if spec:
                self.hierarchy.add_spec(spec)
                spec_count += 1

        # Discover Python files (orchestration only - check for domain logic)
        for py_file in self.repo_path.rglob("*.py"):
            spec = self._load_spec_file(py_file)
            if spec and self._is_orchestration_only(py_file):
                self.hierarchy.add_spec(spec)
                spec_count += 1

        return spec_count

    def _load_spec_file(self, file_path: Path) -> Optional[FormalSpec]:
        """Load a specification file"""
        try:
            # Determine spec type
            suffix = file_path.suffix.lower()[1:]  # Remove dot
            try:
                spec_type = SpecType(suffix)
            except ValueError:
                # Map unknown types
                if suffix == "tex":
                    spec_type = SpecType.LATEX
                else:
                    return None

            # Read content
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Extract constraints
            constraints = self._extract_constraints(content, file_path)

            # Extract theorem references
            theorems = self._extract_theorems(content)

            # Create metadata
            metadata = {
                "file_size": file_path.stat().st_size,
                "line_count": len(content.splitlines()),
                "is_known_constraint_file": file_path.name
                in self.known_constraint_files,
            }

            return FormalSpec(
                spec_type=spec_type,
                file_path=file_path,
                content=content[:5000],  # Limit content size
                constraints=constraints,
                theorem_references=theorems,
                metadata=metadata,
            )

        except Exception as e:
            print(f"⚠️  Failed to load {file_path}: {e}")
            return None

    def _extract_constraints(self, content: str, file_path: Path) -> Set[ConstraintTag]:
        """Extract Σ_LORA constraints from content"""
        constraints = set()

        # Check for constraint tags in content
        matches = self.constraint_pattern.findall(content)
        for match in matches:
            try:
                constraint = ConstraintTag(match.upper())
                constraints.add(constraint)
            except ValueError:
                pass

        # Special handling for known constraint files
        if file_path.name == "Σ_LORA_MANIFEST.json":
            try:
                data = json.loads(content)
                if "files" in data:
                    for file_info in data["files"]:
                        if "constraints" in file_info:
                            for constraint_name in file_info["constraints"]:
                                try:
                                    constraint = ConstraintTag(constraint_name)
                                    constraints.add(constraint)
                                except ValueError:
                                    pass
            except:
                pass

        # Check file name for constraints
        for constraint in ConstraintTag:
            if constraint.value.lower() in file_path.name.lower():
                constraints.add(constraint)

        return constraints

    def _extract_theorems(self, content: str) -> List[str]:
        """Extract theorem references from content"""
        theorems = []
        matches = self.theorem_pattern.findall(content)
        theorems.extend([f"Theorem_{match}" for match in matches])

        # Also look for theorem references in LaTeX
        latex_theorems = re.findall(
            r"\\begin\{theorem\}.*?\\end\{theorem\}", content, re.DOTALL
        )
        theorems.extend([f"LaTeX_Theorem_{i + 1}" for i in range(len(latex_theorems))])

        return theorems

    def _is_formal_spec(self, file_path: Path) -> bool:
        """Check if JSON file is a formal specification (not just data)"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            data = json.loads(content)

            # Check for formal spec indicators
            formal_indicators = [
                "theorems",
                "constraints",
                "invariants",
                "specification",
                "manifest",
                "schema",
                "definition",
                "axiom",
            ]

            # Check keys
            if isinstance(data, dict):
                keys = [k.lower() for k in data.keys()]
                for indicator in formal_indicators:
                    if any(indicator in key for key in keys):
                        return True

            # Check values
            if isinstance(data, dict):
                values = json.dumps(data).lower()
                for indicator in formal_indicators:
                    if indicator in values:
                        return True

            return False

        except:
            return False

    def _is_orchestration_only(self, file_path: Path) -> bool:
        """Check if Python file is orchestration only (no domain logic)"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Orchestration indicators
            orchestration_indicators = [
                "import",
                "from",
                "def load",
                "def parse",
                "def read",
                "class.*Loader",
                "class.*Parser",
                "class.*Reader",
                "query_daemon",
                "send_to_daemon",
                "orchestrate",
            ]

            # Domain logic indicators (should NOT be present)
            domain_indicators = [
                "def train",
                "class.*Model",
                "def generate",
                "def analyze",
                "def compute",
                "def calculate",
                "theology",
                "christ",
                "logos",
                "chalcedon",
            ]

            # Check for orchestration patterns
            has_orchestration = any(
                re.search(pattern, content, re.IGNORECASE)
                for pattern in orchestration_indicators
            )

            # Check for domain logic (should be minimal)
            domain_count = sum(
                1
                for pattern in domain_indicators
                if re.search(pattern, content, re.IGNORECASE)
            )

            return has_orchestration and domain_count < 3

        except:
            return False

    def prepare_daemon_query(self, max_specs: int = 10) -> Dict:
        """
        Prepare query for daemon with formal specifications

        Args:
            max_specs: Maximum number of specs to include (prioritizes most invariant)

        Returns:
            Dict ready for daemon query
        """
        # Get most invariant specs first
        formal_specs = self.hierarchy.get_most_invariant()[: max_specs // 2]

        # Add Markdown context
        markdown_specs = [
            s for s in self.hierarchy.formal_specs if s.spec_type == SpecType.MARKDOWN
        ][: max_specs // 4]

        # Add orchestration instructions
        python_specs = [
            s for s in self.hierarchy.formal_specs if s.spec_type == SpecType.PYTHON
        ][: max_specs // 4]

        # Create temporary hierarchy for this query
        query_hierarchy = SpecHierarchy()
        for spec in formal_specs + markdown_specs + python_specs:
            query_hierarchy.add_spec(spec)

        combined = query_hierarchy.combine_for_daemon()

        # Add query metadata
        combined["query_metadata"] = {
            "total_specs_loaded": len(self.hierarchy.formal_specs),
            "specs_in_query": len(query_hierarchy.formal_specs),
            "most_invariant_count": len(formal_specs),
            "constraint_coverage": len(combined["constraints_present"])
            / len(ConstraintTag),
            "invariance_hierarchy_preserved": True,
        }

        return combined

    def query_daemon(self, daemon_url: str = "http://localhost:8080") -> Dict:
        """Query daemon with formal specifications"""
        try:
            import requests

            # Prepare query
            query_data = self.prepare_daemon_query()

            # Add instruction for daemon
            query_data["instruction"] = """
            INTERPRET FORMAL SPECIFICATIONS WITH Σ_LORA CONSTRAINTS

            You have received formal specifications in order of invariance:
            1. JSON/LaTeX/YAML: Most invariant (machine-readable formal specs)
            2. Markdown: Human interface with annotations
            3. Python: Orchestration instructions only

            Please:
            1. Interpret all formal specifications
            2. Apply Σ_LORA constraints where specified
            3. Generate response that preserves invariance hierarchy
            4. Reference theorems where applicable
            5. Maintain Christ Score = 1.00 throughout

            Constraints present: {constraints}
            """.format(constraints=", ".join(query_data["constraints_present"]))

            # Send to daemon
            response = requests.post(
                f"{daemon_url}/query",
                json={
                    "text": query_data["instruction"],
                    "client_type": "formal_spec_loader",
                    "context": query_data,
                    "require_constraints": True,
                    "max_length": 2048,
                    "temperature": 0.7,
                },
                timeout=30,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Daemon query failed: {response.status_code}"}

        except ImportError:
            return {"error": "requests module not available"}
        except Exception as e:
            return {"error": f"Daemon query failed: {str(e)}"}


def main():
    """Main entry point for formal spec loader"""
    print("=" * 70)
    print("FORMAL SPECIFICATION LOADER")
    print("=" * 70)
    print("Hierarchy: JSON/LaTeX → Markdown → Python")
    print("Principle: All intelligence paths factor through formal specifications")
    print("=" * 70)

    # Create loader
    loader = FormalSpecLoader(project_root)

    print("Discovering formal specifications...")
    spec_count = loader.discover_specs()

    print(f"\n✅ Loaded {spec_count} formal specifications")

    # Show hierarchy
    hierarchy = loader.hierarchy
    print("\n📊 SPECIFICATION HIERARCHY:")
    print("-" * 40)

    for spec in hierarchy.formal_specs[:10]:  # Show first 10
        invariant_level = (
            "MOST"
            if spec.is_most_invariant()
            else "MEDIUM"
            if spec.spec_type == SpecType.MARKDOWN
            else "LEAST"
        )
        constraints = (
            ", ".join([c.value for c in spec.constraints])
            if spec.constraints
            else "none"
        )
        print(
            f"{spec.spec_type.value:8} | {invariant_level:6} | {spec.file_path.name:30} | Constraints: {constraints}"
        )

    if spec_count > 10:
        print(f"... and {spec_count - 10} more specifications")

    print("\n🔍 MOST INVARIANT SPECIFICATIONS:")
    print("-" * 40)

    most_invariant = hierarchy.get_most_invariant()
    for spec in most_invariant[:5]:  # Show top 5 most invariant
        constraints = (
            ", ".join([c.value for c in spec.constraints])
            if spec.constraints
            else "none"
        )
        print(
            f"{spec.spec_type.value:8} | {spec.file_path.name:40} | Constraints: {constraints}"
        )

    print("\n🚀 Querying daemon with formal specifications...")

    # Query daemon
    result = loader.query_daemon()

    if "error" in result:
        print(f"❌ Daemon query failed: {result['error']}")
    else:
        print(f"✅ Daemon response received")
        print(f"   Christ Score: {result.get('christ_score', 0):.3f}")
        print(
            f"   Constraints satisfied: {result.get('constraints_satisfied', 0)}/{result.get('total_constraints', 6)}"
        )
        print(f"   Processing time: {result.get('processing_time_ms', 0):.1f}ms")

        # Show response preview
        response_text = result.get("response", "")
        if response_text:
            preview = (
                response_text[:200] + "..."
                if len(response_text) > 200
                else response_text
            )
            print(f"\n📝 Response preview:")
            print(f"{preview}")

    print("\n" + "=" * 70)
    print("FORMAL SPECIFICATION LOADER READY")
    print("=" * 70)
    print("Usage:")
    print("  1. Load specs: loader = FormalSpecLoader(project_root)")
    print("  2. Discover: loader.discover_specs()")
    print("  3. Query daemon: loader.query_daemon()")
    print("  4. Or prepare query: loader.prepare_daemon_query()")
    print("\nInvariance hierarchy preserved:")
    print("  JSON/LaTeX → Markdown → Python")
    print("=" * 70)


if __name__ == "__main__":
    main()
