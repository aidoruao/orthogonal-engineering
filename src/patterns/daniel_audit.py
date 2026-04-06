"""Daniel Audit Pattern

Biblical basis: Daniel 6 — Daniel's integrity under Persian audit. When
the king's commissioners audited the satraps, they found no corruption
or negligence in Daniel. The only way to trap him was to make his faith illegal.

Application: The system must survive external review. All invariants,
proofs, and claims must be verifiable by an external party with no
prior knowledge of the system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum, auto


class AuditFinding(Enum):
    """Types of findings from an audit."""
    CLEAN = auto()        # No issues found
    MINOR = auto()        # Minor issues, non-blocking
    MAJOR = auto()        # Major issues, requires attention
    CRITICAL = auto()     # Critical issues, system integrity at risk


@dataclass
class AuditReport:
    """Report from an audit."""
    auditor_id: str
    audit_date: datetime
    scope: List[str]  # What was audited
    findings: List[Dict[str, Any]]
    overall_status: AuditFinding
    recommendations: List[str]


class DanielAudit:
    """
    Implements the Daniel audit pattern.
    
    The system must be able to survive external review. All claims,
    invariants, and proofs must be verifiable by external auditors.
    
    Attributes:
        audit_history: History of past audits
        required_evidence: Types of evidence required for claims
    """
    
    def __init__(self):
        self.audit_history: List[AuditReport] = []
        self.required_evidence = [
            "proof_object",
            "falsification_test",
            "source_reference",
            "timestamp",
        ]
    
    def conduct_audit(
        self,
        auditor_id: str,
        scope: List[str],
        evidence: Dict[str, Any],
    ) -> AuditReport:
        """
        Conduct an audit of the specified scope.
        
        Args:
            auditor_id: Identifier for the auditor
            scope: What is being audited
            evidence: Evidence to evaluate
        
        Returns:
            AuditReport with findings
        """
        findings = []
        
        # Check for required evidence types
        for req in self.required_evidence:
            if req not in evidence:
                findings.append({
                    "type": "missing_evidence",
                    "severity": "major",
                    "description": f"Missing required evidence: {req}",
                })
        
        # Check for falsification tests
        if "falsification_test" in evidence:
            test_result = evidence["falsification_test"]
            if not test_result.get("exists", False):
                findings.append({
                    "type": "no_falsification",
                    "severity": "critical",
                    "description": "Claim has no falsification test",
                })
        
        # Determine overall status
        if any(f["severity"] == "critical" for f in findings):
            status = AuditFinding.CRITICAL
        elif any(f["severity"] == "major" for f in findings):
            status = AuditFinding.MAJOR
        elif findings:
            status = AuditFinding.MINOR
        else:
            status = AuditFinding.CLEAN
        
        report = AuditReport(
            auditor_id=auditor_id,
            audit_date=datetime.now(),
            scope=scope,
            findings=findings,
            overall_status=status,
            recommendations=[
                "Add missing evidence types",
                "Ensure all claims have falsification tests",
            ] if findings else ["No action required"],
        )
        
        self.audit_history.append(report)
        return report
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get summary of all audits."""
        if not self.audit_history:
            return {"total_audits": 0}
        
        findings_count = {
            "clean": sum(1 for a in self.audit_history if a.overall_status == AuditFinding.CLEAN),
            "minor": sum(1 for a in self.audit_history if a.overall_status == AuditFinding.MINOR),
            "major": sum(1 for a in self.audit_history if a.overall_status == AuditFinding.MAJOR),
            "critical": sum(1 for a in self.audit_history if a.overall_status == AuditFinding.CRITICAL),
        }
        
        return {
            "total_audits": len(self.audit_history),
            "findings_count": findings_count,
            "clean_percentage": findings_count["clean"] / len(self.audit_history) * 100,
        }
    
    def is_survivable(self) -> bool:
        """
        Check if the system can survive external audit.
        
        Returns:
            True if no critical findings in any audit
        """
        return not any(
            a.overall_status == AuditFinding.CRITICAL
            for a in self.audit_history
        )
