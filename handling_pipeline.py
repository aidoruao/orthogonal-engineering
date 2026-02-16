"""
Handling pipeline for GTA handling.meta files.

This module provides parsing and clamp engine for CHandlingData entries with:
- Detection of handlingName and numeric parameter attributes
- Phase 1 clamps: collision:1.2-1.8, engine:1.0-2.5, deformation:0.5-2.0
- Phase 2 conservative clamps: suspension:0.5-3.0, traction:0.5-2.5, braking:0.5-3.0, com:-1.0..1.0
- Dry-run and apply modes
- JSONL audit outputs

Author: Orthogonal Engineering
Date: 2026-02-16
Version: 1.0.0
"""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backup import backup_before_write
from logger import PipelineLogger


# Phase 1 clamp ranges
PHASE1_CLAMPS = {
    'fCollisionDamageMult': (1.2, 1.8),
    'fEngineDamageMult': (1.0, 2.5),
    'fDeformationDamageMult': (0.5, 2.0),
}

# Phase 2 conservative clamp ranges
PHASE2_CLAMPS = {
    'fSuspensionForce': (0.5, 3.0),
    'fSuspensionCompDamp': (0.5, 3.0),
    'fSuspensionReboundDamp': (0.5, 3.0),
    'fSuspensionUpperLimit': (0.5, 3.0),
    'fSuspensionLowerLimit': (0.5, 3.0),
    'fSuspensionRaise': (0.5, 3.0),
    'fSuspensionBiasFront': (0.5, 3.0),
    'fSuspensionBiasRear': (0.5, 3.0),
    'fTractionCurveMax': (0.5, 2.5),
    'fTractionCurveMin': (0.5, 2.5),
    'fTractionCurveLateral': (0.5, 2.5),
    'fTractionSpringDeltaMax': (0.5, 2.5),
    'fTractionBiasFront': (0.5, 2.5),
    'fTractionBiasRear': (0.5, 2.5),
    'fBrakeForce': (0.5, 3.0),
    'fBrakeBiasFront': (0.5, 3.0),
    'fBrakeBiasRear': (0.5, 3.0),
    'vecCentreOfMassOffsetX': (-1.0, 1.0),
    'vecCentreOfMassOffsetY': (-1.0, 1.0),
    'vecCentreOfMassOffsetZ': (-1.0, 1.0),
}


class HandlingEntry:
    """Represents a single CHandlingData entry."""
    
    def __init__(self, element: ET.Element):
        """
        Initialize from XML element.
        
        Args:
            element: XML element for CHandlingData entry
        """
        self.element = element
        self.name = element.get('handlingName', 'UNKNOWN')
        self.corrections = []
    
    def get_numeric_value(self, attr_name: str) -> Optional[float]:
        """Get numeric value for an attribute."""
        value = self.element.get(attr_name)
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            return None
    
    def set_value(self, attr_name: str, value: float) -> None:
        """Set numeric value for an attribute."""
        self.element.set(attr_name, f"{value:.6f}")
    
    def apply_clamp(self, attr_name: str, min_val: float, max_val: float, phase: str) -> bool:
        """
        Apply clamp to an attribute if it exists.
        
        Args:
            attr_name: Attribute name
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            phase: Phase name for logging
            
        Returns:
            True if value was clamped, False otherwise
        """
        current = self.get_numeric_value(attr_name)
        if current is None:
            return False
        
        clamped = False
        original = current
        
        if current < min_val:
            current = min_val
            clamped = True
        elif current > max_val:
            current = max_val
            clamped = True
        
        if clamped:
            self.set_value(attr_name, current)
            self.corrections.append({
                'attribute': attr_name,
                'original': original,
                'clamped': current,
                'range': [min_val, max_val],
                'phase': phase
            })
        
        return clamped
    
    def apply_phase1_clamps(self) -> int:
        """Apply Phase 1 clamps. Returns number of corrections."""
        count = 0
        for attr_name, (min_val, max_val) in PHASE1_CLAMPS.items():
            if self.apply_clamp(attr_name, min_val, max_val, 'phase1'):
                count += 1
        return count
    
    def apply_phase2_clamps(self) -> int:
        """Apply Phase 2 conservative clamps. Returns number of corrections."""
        count = 0
        for attr_name, (min_val, max_val) in PHASE2_CLAMPS.items():
            if self.apply_clamp(attr_name, min_val, max_val, 'phase2'):
                count += 1
        return count


class HandlingParser:
    """Parser and clamp engine for handling.meta files."""
    
    def __init__(self, input_path: Path):
        """
        Initialize parser.
        
        Args:
            input_path: Path to handling.meta file
        """
        self.input_path = input_path
        self.tree = None
        self.root = None
        self.entries: List[HandlingEntry] = []
        
    def parse(self) -> bool:
        """
        Parse handling.meta file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.tree = ET.parse(self.input_path)
            self.root = self.tree.getroot()
            
            # Find all CHandlingData entries
            for item in self.root.findall('.//Item[@type="CHandlingData"]'):
                entry = HandlingEntry(item)
                self.entries.append(entry)
            
            return True
        except Exception as e:
            print(f"Error parsing {self.input_path}: {e}")
            return False
    
    def apply_clamps(self, phase1: bool = True, phase2: bool = False) -> Dict:
        """
        Apply clamps to all entries.
        
        Args:
            phase1: Apply Phase 1 clamps
            phase2: Apply Phase 2 clamps
            
        Returns:
            Summary dictionary with corrections
        """
        summary = {
            'total_entries': len(self.entries),
            'total_corrections': 0,
            'phase1_corrections': 0,
            'phase2_corrections': 0,
            'entries': []
        }
        
        for entry in self.entries:
            phase1_count = 0
            phase2_count = 0
            
            if phase1:
                phase1_count = entry.apply_phase1_clamps()
            
            if phase2:
                phase2_count = entry.apply_phase2_clamps()
            
            total_count = phase1_count + phase2_count
            
            if total_count > 0:
                summary['entries'].append({
                    'name': entry.name,
                    'corrections': entry.corrections
                })
                summary['phase1_corrections'] += phase1_count
                summary['phase2_corrections'] += phase2_count
                summary['total_corrections'] += total_count
        
        return summary
    
    def write_output(self, output_path: Path, backup: bool = True) -> bool:
        """
        Write corrected handling.meta file.
        
        Args:
            output_path: Path to output file
            backup: Create backup before writing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup if file exists
            if backup and output_path.exists():
                backup_before_write(output_path)
            
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write XML
            self.tree.write(
                output_path,
                encoding='utf-8',
                xml_declaration=True
            )
            
            return True
        except Exception as e:
            print(f"Error writing {output_path}: {e}")
            return False


def process_handling_file(
    input_path: Path,
    output_dir: Path,
    dry_run: bool = True,
    phase1: bool = True,
    phase2: bool = False,
    logger: Optional[PipelineLogger] = None
) -> Dict:
    """
    Process a handling.meta file with clamping.
    
    Args:
        input_path: Path to input handling.meta
        output_dir: Directory for output files
        dry_run: If True, don't write files
        phase1: Apply Phase 1 clamps
        phase2: Apply Phase 2 clamps
        logger: Optional logger for audit trail
        
    Returns:
        Processing summary dictionary
    """
    if logger:
        logger.log_start('process_handling', {'input': str(input_path), 'dry_run': dry_run})
    
    # Parse file
    parser = HandlingParser(input_path)
    if not parser.parse():
        if logger:
            logger.log_error('process_handling', 'Failed to parse file')
        return {'success': False, 'error': 'Parse failed'}
    
    # Apply clamps
    summary = parser.apply_clamps(phase1=phase1, phase2=phase2)
    summary['input_file'] = str(input_path)
    summary['dry_run'] = dry_run
    
    # Write outputs if not dry-run
    if not dry_run:
        # Write corrected_handling.meta
        corrected_path = output_dir / 'corrected_handling.meta'
        if parser.write_output(corrected_path):
            summary['corrected_output'] = str(corrected_path)
        
        # Write extended version (both Phase 1 and Phase 2)
        if phase1 and not phase2:
            extended_parser = HandlingParser(input_path)
            extended_parser.parse()
            extended_parser.apply_clamps(phase1=True, phase2=True)
            extended_path = output_dir / 'extended_corrected_handling.meta'
            if extended_parser.write_output(extended_path, backup=False):
                summary['extended_output'] = str(extended_path)
        
        # Write JSONL audit
        audit_path = output_dir / 'handling_corrections.jsonl'
        with open(audit_path, 'w') as f:
            f.write(json.dumps(summary) + '\n')
        summary['audit_output'] = str(audit_path)
    
    if logger:
        logger.log_complete('process_handling', summary)
    
    summary['success'] = True
    return summary
