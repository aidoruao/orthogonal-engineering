"""Domain Summarizer — auto-generate domain documentation.

Analyzes domain implementations and generates:
- Status summaries
- Invariant documentation
- Cross-domain relationship maps
"""

import ast
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from fractions import Fraction


@dataclass
class DomainSummary:
    """Summary of a domain's state."""
    name: str
    domain_id: str
    line_count: int
    invariant_count: int
    test_count: int
    status: str
    key_invariants: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


class DomainSummarizer:
    """Generate documentation summaries from domain code."""
    
    def __init__(self, domains_path: str = "src/domains"):
        self.domains_path = Path(domains_path)
        self.summaries: Dict[str, DomainSummary] = {}
    
    def analyze_domain(self, domain_dir: Path) -> Optional[DomainSummary]:
        """Analyze a single domain directory."""
        if not domain_dir.is_dir():
            return None
        
        name = domain_dir.name
        
        # Read invariants.py
        inv_path = domain_dir / "invariants.py"
        line_count = 0
        invariant_count = 0
        key_invariants = []
        
        if inv_path.exists():
            content = inv_path.read_text()
            line_count = len(content.splitlines())
            
            # Count def check_* functions
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith("check_"):
                            invariant_count += 1
                            key_invariants.append(node.name)
            except SyntaxError:
                pass
        
        # Count tests
        test_dir = domain_dir / "tests"
        test_count = 0
        if test_dir.exists():
            test_count = len(list(test_dir.glob("test_*.py")))
        
        # Determine status
        if line_count >= 100:
            status = "deep"
        elif line_count >= 50:
            status = "developing"
        elif line_count > 0:
            status = "stub"
        else:
            status = "empty"
        
        return DomainSummary(
            name=name,
            domain_id=name.upper(),
            line_count=line_count,
            invariant_count=invariant_count,
            test_count=test_count,
            status=status,
            key_invariants=key_invariants[:5],  # Top 5
        )
    
    def analyze_all(self) -> Dict[str, DomainSummary]:
        """Analyze all domains."""
        for domain_dir in sorted(self.domains_path.iterdir()):
            if domain_dir.name.startswith("d_"):
                summary = self.analyze_domain(domain_dir)
                if summary:
                    self.summaries[summary.name] = summary
        
        return self.summaries
    
    def generate_markdown(self) -> str:
        """Generate markdown documentation."""
        if not self.summaries:
            self.analyze_all()
        
        lines = [
            "# Auto-Generated Domain Documentation",
            "",
            f"**Generated:** {self._timestamp()}",
            f"**Total Domains:** {len(self.summaries)}",
            "",
            "## Summary Statistics",
            "",
        ]
        
        # Statistics
        deep = sum(1 for s in self.summaries.values() if s.status == "deep")
        developing = sum(1 for s in self.summaries.values() if s.status == "developing")
        stubs = sum(1 for s in self.summaries.values() if s.status == "stub")
        empty = sum(1 for s in self.summaries.values() if s.status == "empty")
        
        lines.extend([
            f"| Status | Count |",
            f"|--------|-------|",
            f"| Deep (100+ lines) | {deep} |",
            f"| Developing (50-99 lines) | {developing} |",
            f"| Stub (<50 lines) | {stubs} |",
            f"| Empty | {empty} |",
            "",
            "## Domain Details",
            "",
        ])
        
        # Individual domains
        for name, summary in sorted(self.summaries.items()):
            lines.append(f"### {name}")
            lines.append(f"- **Status:** {summary.status}")
            lines.append(f"- **Lines:** {summary.line_count}")
            lines.append(f"- **Invariants:** {summary.invariant_count}")
            lines.append(f"- **Tests:** {summary.test_count}")
            
            if summary.key_invariants:
                lines.append("- **Key Invariants:**")
                for inv in summary.key_invariants:
                    lines.append(f"  - `{inv}()`")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_json(self) -> Dict[str, Any]:
        """Generate JSON representation."""
        if not self.summaries:
            self.analyze_all()
        
        return {
            "generated": self._timestamp(),
            "total_domains": len(self.summaries),
            "domains": {
                name: {
                    "domain_id": s.domain_id,
                    "line_count": s.line_count,
                    "invariant_count": s.invariant_count,
                    "test_count": s.test_count,
                    "status": s.status,
                    "key_invariants": s.key_invariants,
                }
                for name, s in self.summaries.items()
            }
        }
    
    def _timestamp(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    import sys
    
    summarizer = DomainSummarizer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(summarizer.generate_json(), indent=2))
    else:
        print(summarizer.generate_markdown())
