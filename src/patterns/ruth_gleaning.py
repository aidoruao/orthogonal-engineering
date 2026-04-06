"""Ruth Gleaning Pattern

Biblical basis: Ruth 2 — Ruth gleans in Boaz's field. The law (Leviticus 19:9-10,
Deuteronomy 24:19) requires leaving the edges of fields and fallen grain for
the poor and foreigner. This is not charity — it's justice, codified in law.

Application: All code is permissively licensed. Others may glean from this
work. The "edges" — helper utilities, patterns, tools — are left accessible.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path
from enum import Enum, auto


class LicenseType(Enum):
    """License types supported."""
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    BSD_3 = "BSD-3-Clause"
    GPL_3 = "GPL-3.0"
    PROPRIETARY = "Proprietary"


@dataclass
class LicensedFile:
    """A file with its license."""
    filepath: Path
    license: LicenseType
    copyright_holder: str
    gleanable: bool  # Whether this file is meant to be reused by others


class RuthGleaning:
    """
    Implements the Ruth gleaning pattern.
    
    All code should be permissively licensed where possible.
    Helper utilities, patterns, and tools should be marked as
    "gleanable" — reusable by others.
    
    Attributes:
        files: List of tracked files
        preferred_license: Default license for new files
    """
    
    def __init__(self, preferred_license: LicenseType = LicenseType.MIT):
        self.files: List[LicensedFile] = []
        self.preferred_license = preferred_license
    
    def add_file(
        self,
        filepath: Path,
        license: LicenseType,
        copyright_holder: str,
        gleanable: bool = True,
    ) -> LicensedFile:
        """Add a file with its license."""
        file_info = LicensedFile(
            filepath=Path(filepath),
            license=license,
            copyright_holder=copyright_holder,
            gleanable=gleanable,
        )
        self.files.append(file_info)
        return file_info
    
    def get_gleanable_files(self) -> List[LicensedFile]:
        """Get all files marked as gleanable."""
        return [f for f in self.files if f.gleanable]
    
    def get_by_license(self, license: LicenseType) -> List[LicensedFile]:
        """Get all files with a specific license."""
        return [f for f in self.files if f.license == license]
    
    def check_license_compliance(self) -> Dict[str, Any]:
        """
        Check license compliance.
        
        Returns:
            Dict with compliance summary
        """
        proprietary = [f for f in self.files if f.license == LicenseType.PROPRIETARY]
        permissive = [f for f in self.files if f.license != LicenseType.PROPRIETARY]
        gleanable = self.get_gleanable_files()
        
        return {
            "total_files": len(self.files),
            "proprietary_count": len(proprietary),
            "permissive_count": len(permissive),
            "gleanable_count": len(gleanable),
            "gleaning_percentage": (
                len(gleanable) / len(self.files) * 100 if self.files else 0
            ),
            "proprietary_files": [str(f.filepath) for f in proprietary],
        }
    
    def verify_gleanability(self, filepath: Path) -> bool:
        """Verify if a specific file is gleanable."""
        file_info = next((f for f in self.files if f.filepath == filepath), None)
        if file_info is None:
            return False
        return file_info.gleanable and file_info.license != LicenseType.PROPRIETARY
