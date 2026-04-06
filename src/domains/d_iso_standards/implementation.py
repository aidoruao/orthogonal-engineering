"""D_ISO_STANDARDS implementation — International Standards"""

from dataclasses import dataclass
from typing import Dict, Optional
import hashlib
from datetime import datetime


@dataclass
class ISOStandard:
    """An ISO standard with version pinning."""
    standard_id: str
    name: str
    version: str
    content_hash: str
    release_date: datetime
    required_sections: list = None  # Required sections for compliance
    
    def __post_init__(self):
        if self.required_sections is None:
            self.required_sections = []
    
    def verify_integrity(self, content: bytes) -> bool:
        """Verify content matches pinned hash."""
        current_hash = hashlib.sha256(content).hexdigest()
        return current_hash == self.content_hash
    
    def check_section_compliance(self, implementation: bytes) -> dict:
        """Check if implementation contains required sections."""
        content_str = implementation.decode('utf-8', errors='ignore').lower()
        results = {}
        for section in self.required_sections:
            results[section] = section.lower() in content_str
        return results


class ISOStandardsRegistry:
    """Registry of pinned ISO standards."""
    
    def __init__(self):
        self.standards: Dict[str, ISOStandard] = {}
    
    def pin_standard(
        self,
        standard_id: str,
        name: str,
        version: str,
        content: bytes,
        release_date: datetime,
        required_sections: list = None,
    ) -> ISOStandard:
        """Pin a standard version with SHA-256 hash."""
        standard = ISOStandard(
            standard_id=standard_id,
            name=name,
            version=version,
            content_hash=hashlib.sha256(content).hexdigest(),
            release_date=release_date,
            required_sections=required_sections or [],
        )
        self.standards[standard_id] = standard
        return standard
    
    def check_compliance(self, standard_id: str, implementation: bytes) -> dict:
        """Check if implementation complies with pinned standard.
        
        Returns a compliance report with:
        - compliant: bool (overall compliance status)
        - integrity_check: bool (hash verification)
        - sections_present: dict (which required sections are found)
        - missing_sections: list (sections not found)
        """
        if standard_id not in self.standards:
            return {
                "compliant": False,
                "integrity_check": False,
                "sections_present": {},
                "missing_sections": ["Standard not found"],
            }
        
        standard = self.standards[standard_id]
        
        # Check integrity (content hash match)
        integrity_pass = standard.verify_integrity(implementation)
        
        # Check required sections
        section_results = standard.check_section_compliance(implementation)
        missing = [s for s, found in section_results.items() if not found]
        
        # Compliant if integrity passes and all required sections present
        is_compliant = integrity_pass and len(missing) == 0
        
        return {
            "compliant": is_compliant,
            "integrity_check": integrity_pass,
            "sections_present": section_results,
            "missing_sections": missing,
        }
