"""Drift Detector — detect when documentation diverges from code.

Compares:
- Domain count in ontology vs actual domains
- Axiom count in omega.md vs actual axioms
- Case study count in index vs actual case studies
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path


@dataclass
class DriftReport:
    """Report of detected drift."""
    category: str
    documented: int
    actual: int
    drift: int
    severity: str  # "low", "medium", "high"
    suggestions: List[str]


class DriftDetector:
    """Detect divergence between documentation and code reality."""
    
    def __init__(self, repo_root: str = "."):
        self.root = Path(repo_root)
        self.reports: List[DriftReport] = []
    
    def check_domain_count(self) -> Optional[DriftReport]:
        """Check if domain count matches documentation."""
        # Count actual domains
        domains_dir = self.root / "src" / "domains"
        actual = len([d for d in domains_dir.iterdir() if d.name.startswith("d_")]) if domains_dir.exists() else 0
        
        # Check DOMAIN_INVARIANT_STATUS.md
        status_file = self.root / "DOMAIN_INVARIANT_STATUS.md"
        documented = 0
        
        if status_file.exists():
            content = status_file.read_text()
            # Look for "Total domains | N"
            for line in content.splitlines():
                if "Total domains" in line and "|" in line:
                    try:
                        documented = int(line.split("|")[2].strip().split()[0])
                    except (ValueError, IndexError):
                        pass
        
        drift = actual - documented
        
        if drift != 0:
            return DriftReport(
                category="Domain Count",
                documented=documented,
                actual=actual,
                drift=drift,
                severity="high" if abs(drift) > 10 else "medium",
                suggestions=[
                    f"Update DOMAIN_INVARIANT_STATUS.md to reflect {actual} domains",
                    "Run: python tools/doc_generator/domain_summarizer.py",
                ]
            )
        
        return None
    
    def check_axiom_count(self) -> Optional[DriftReport]:
        """Check if axiom count matches eschaton/omega.md."""
        axioms_dir = self.root / "axioms"
        actual = len(list(axioms_dir.glob("*.py"))) if axioms_dir.exists() else 0
        
        # Check omega.md
        omega_file = self.root / "eschaton" / "omega.md"
        documented = 0
        
        if omega_file.exists():
            content = omega_file.read_text()
            # Look for axiom count mentions
            for line in content.splitlines():
                if "axiom" in line.lower() and any(c.isdigit() for c in line):
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        documented = int(numbers[0])
                        break
        
        drift = actual - documented
        
        if drift != 0:
            return DriftReport(
                category="Axiom Count",
                documented=documented,
                actual=actual,
                drift=drift,
                severity="high" if abs(drift) > 5 else "medium",
                suggestions=[
                    f"Update eschaton/omega.md: {actual} axioms (was {documented})",
                    "Regenerate axiom index with: python tools/doc_generator/axiom_indexer.py",
                ]
            )
        
        return None
    
    def check_case_studies(self) -> Optional[DriftReport]:
        """Check case study count."""
        case_studies_dir = self.root / "case_studies"
        
        # Count category directories
        if case_studies_dir.exists():
            categories = [d for d in case_studies_dir.iterdir() if d.is_dir() and d.name.startswith("category_")]
            actual = sum(len(list(c.iterdir())) for c in categories)
        else:
            actual = 0
        
        # Check index
        index_file = case_studies_dir / "CASE_STUDY_INDEX.json" if case_studies_dir.exists() else None
        documented = 0
        
        if index_file and index_file.exists():
            try:
                data = json.loads(index_file.read_text())
                documented = data.get("metadata", {}).get("total_target", 0)
            except (json.JSONDecodeError, KeyError):
                pass
        
        drift = actual - documented
        
        if drift != 0:
            return DriftReport(
                category="Case Studies",
                documented=documented,
                actual=actual,
                drift=drift,
                severity="low" if abs(drift) < 50 else "medium",
                suggestions=[
                    f"Update CASE_STUDY_INDEX.json with {actual} case studies",
                    f"Progress: {actual}/{documented} ({100*actual//documented if documented else 0}%)",
                ]
            )
        
        return None
    
    def run_all_checks(self) -> List[DriftReport]:
        """Run all drift detection checks."""
        checks = [
            self.check_domain_count(),
            self.check_axiom_count(),
            self.check_case_studies(),
        ]
        
        self.reports = [r for r in checks if r is not None]
        return self.reports
    
    def generate_report(self) -> str:
        """Generate drift detection report."""
        if not self.reports:
            self.run_all_checks()
        
        if not self.reports:
            return "# Drift Detection Report\n\n✅ No drift detected. Documentation matches code.\n"
        
        lines = [
            "# Drift Detection Report",
            "",
            f"**Issues Found:** {len(self.reports)}",
            "",
        ]
        
        for report in self.reports:
            lines.append(f"## {report.category}")
            lines.append(f"- **Severity:** {report.severity.upper()}")
            lines.append(f"- **Documented:** {report.documented}")
            lines.append(f"- **Actual:** {report.actual}")
            lines.append(f"- **Drift:** {'+' if report.drift > 0 else ''}{report.drift}")
            lines.append("")
            lines.append("**Suggestions:**")
            for suggestion in report.suggestions:
                lines.append(f"- {suggestion}")
            lines.append("")
        
        return "\n".join(lines)


if __name__ == "__main__":
    detector = DriftDetector()
    print(detector.generate_report())
