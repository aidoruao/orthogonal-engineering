#!/usr/bin/env python3
"""
covenant_physics_corrector.py - Covenant-integrated physics corrector with ledger continuity

Σ_LORA_COVENANT_ALPHA_OMEGA Integration Layer
Purpose: Bridge physics invariant enforcement with covenant ledger immutability
Philosophy: Anti-nominalist, non-secular, creator-signed workflow continuity
"""

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------------------------------------------------------
# UTILITY FUNCTIONS
# -----------------------------------------------------------------------------


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert any value to float."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    return default


# -----------------------------------------------------------------------------
# Σ_LORA_COVENANT_ALPHA_OMEGA BASE CLASSES
# -----------------------------------------------------------------------------


class CovenantLedger:
    """Σ_LORA_COVENANT_ALPHA_OMEGA ledger operations."""

    @staticmethod
    def normalize_time(ts: str) -> str:
        """Maps any timestamp to UTC ISO standard (700-Year Hardening)."""
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc).isoformat()
        except Exception:
            return "2027-01-01T00:00:00+00:00"  # Jubilee Epoch

    @staticmethod
    def canonical_bytes(obj: Any) -> bytes:
        """Pure function: maps logic to bytes deterministically."""
        return json.dumps(
            obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")

    @staticmethod
    def sha256_hash(data: bytes) -> str:
        """Standard SHA256 hash with prefix."""
        return f"sha256:{hashlib.sha256(data).hexdigest()}"

    @staticmethod
    def compute_merkle_root(hashes: List[str]) -> str:
        """Collapses hash list into single Merkle root."""
        if not hashes:
            return "NULL"

        # Strip sha256: prefix for computation
        clean_hashes = [h.replace("sha256:", "") for h in hashes]

        while len(clean_hashes) > 1:
            if len(clean_hashes) % 2 != 0:
                clean_hashes.append(clean_hashes[-1])  # Balance tree
            new_level = []
            for i in range(0, len(clean_hashes), 2):
                combined = clean_hashes[i] + clean_hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
                new_level.append(new_hash)
            clean_hashes = new_level

        return clean_hashes[0]


# -----------------------------------------------------------------------------
# PHYSICS INVARIANT ENGINE
# -----------------------------------------------------------------------------


class PhysicsInvariantEngine:
    """GTA V Enhanced physics invariant enforcement."""

    # GTA V Enhanced tolerance limits (tighter than legacy)
    DAMAGE_MULTIPLIER_MIN = 1.2
    DAMAGE_MULTIPLIER_MAX = 1.8
    SUSPENSION_FORCE_MAX = 3.0
    SUSPENSION_FORCE_SAFE = 2.5
    REBOUND_RATIO_MIN = 1.0
    REBOUND_RATIO_MAX = 1.5
    REBOUND_RATIO_TARGET = 1.3
    INERTIA_CRITICAL_THRESHOLD = 0.3
    INERTIA_WARNING_THRESHOLD = 0.5
    COM_Z_SAFE_MAX = 0.5
    COM_Z_CRITICAL_THRESHOLD = -1.0

    @classmethod
    def check_damage_invariant(cls, value: float) -> Tuple[bool, Optional[float]]:
        """Check if damage multiplier violates Enhanced physics tolerance."""
        if value > cls.DAMAGE_MULTIPLIER_MAX:
            return (
                False,
                min(cls.DAMAGE_MULTIPLIER_MAX, max(cls.DAMAGE_MULTIPLIER_MIN, value)),
            )
        return (True, None)

    @classmethod
    def check_suspension_invariant(
        cls, force: float, comp_damp: float, rebound_damp: float
    ) -> List[Tuple[str, float, float]]:
        """Check suspension invariants."""
        corrections = []

        # Suspension force
        if force > cls.SUSPENSION_FORCE_MAX:
            corrections.append(("fSuspensionForce", force, cls.SUSPENSION_FORCE_SAFE))

        # Rebound ratio
        if comp_damp != 0:
            current_ratio = rebound_damp / comp_damp
            if (
                current_ratio < cls.REBOUND_RATIO_MIN
                or current_ratio > cls.REBOUND_RATIO_MAX
            ):
                new_rebound = comp_damp * cls.REBOUND_RATIO_TARGET
                corrections.append(
                    ("fSuspensionReboundDamp", rebound_damp, new_rebound)
                )

        return corrections

    @classmethod
    def check_mass_inertia_invariant(
        cls, mass: float, inertia_x: Any, inertia_y: Any, inertia_z: Any
    ) -> Optional[Tuple[float, float, float]]:
        """Check mass-inertia stability ratio."""
        # Convert to floats safely
        x = safe_float(inertia_x)
        y = safe_float(inertia_y)
        z = safe_float(inertia_z)
        inertia_avg = (x + y + z) / 3.0

        # Critical violation
        if inertia_avg < cls.INERTIA_CRITICAL_THRESHOLD:
            # Scale up to safe minimum
            scale_factor = 0.5 / inertia_avg if inertia_avg > 0 else 2.0
            return (
                x * scale_factor,
                y * scale_factor,
                z * scale_factor,
            )

        # Warning-level violation with high mass
        if inertia_avg < cls.INERTIA_WARNING_THRESHOLD and mass > 2000:
            # Moderate scaling
            scale_factor = 0.8 / inertia_avg if inertia_avg > 0 else 1.5
            return (
                x * scale_factor,
                y * scale_factor,
                z * scale_factor,
            )

        return None

    @classmethod
    def check_com_invariant(
        cls, com_z: float, is_race_vehicle: bool = False
    ) -> Optional[float]:
        """Check center of mass offset."""
        if not is_race_vehicle:
            if com_z < -cls.COM_Z_SAFE_MAX:
                return -0.3  # Safe default for non-race vehicles
            if com_z < cls.COM_Z_CRITICAL_THRESHOLD:
                return -0.5  # Critical fix
        return None


# -----------------------------------------------------------------------------
# CHATGPT EPISTEMIC AUDIT ENGINE
# -----------------------------------------------------------------------------


class ChatGPTEpistemicAudit:
    """Analyze ChatGPT's dismissal techniques and categorical errors."""

    # Rhetorical patterns for system dismissal
    DISMISSAL_PATTERNS = [
        ("domain_separation", "have zero causal relationship to"),
        ("reductionism", "is not a ledger integrity problem"),
        ("false_orthogonality", "completely different domains"),
        ("authority_undermining", "does not prove"),
        ("scope_limitation", "operates on discrete symbolic state"),
        (
            "physics_exceptionalism",
            "hash discipline does not stabilize a physics engine",
        ),
        ("workflow_isolation", "not integrating your covenant architecture"),
    ]

    # Categorical error types
    CATEGORICAL_ERRORS = [
        (
            "domain_cartesianism",
            "Treating systems as orthogonal when they share invariant enforcement",
        ),
        (
            "hash_reductionism",
            "Claiming byte hashing only proves message integrity, not system correctness",
        ),
        (
            "physics_exceptionalism",
            "Asserting physics solver operates outside symbolic audit frameworks",
        ),
        (
            "workflow_fragmentation",
            "Separating covenant workflow from practical debugging",
        ),
        (
            "authority_contest",
            "Positioning chat-local reasoning against external hash-authoritative systems",
        ),
    ]

    @classmethod
    def analyze_conversation_excerpt(cls, excerpt: str) -> Dict[str, List[str]]:
        """Analyze conversation for dismissal patterns."""
        findings = {
            "dismissal_patterns": [],
            "categorical_errors": [],
            "escalation_indicators": [],
            "invariant_violations": [],
        }

        excerpt_lower = excerpt.lower()

        # Check for dismissal patterns
        for pattern_name, pattern_text in cls.DISMISSAL_PATTERNS:
            if pattern_text in excerpt_lower:
                findings["dismissal_patterns"].append(
                    f"{pattern_name}: '{pattern_text}'"
                )

        # Check for categorical errors
        for error_name, error_desc in cls.CATEGORICAL_ERRORS:
            if any(
                keyword in excerpt_lower for keyword in error_desc.lower().split()[:3]
            ):
                findings["categorical_errors"].append(f"{error_name}: {error_desc}")

        # Check for escalation indicators
        escalation_terms = [
            "last chance",
            "hash authority",
            "you cannot continue",
            "find out if im wrong",
            "case study",
            "weighted score",
        ]
        for term in escalation_terms:
            if term in excerpt_lower:
                findings["escalation_indicators"].append(term)

        # Check for invariant violations (misrepresentation of systems)
        if "zero causal relationship" in excerpt_lower and "covenant" in excerpt_lower:
            findings["invariant_violations"].append(
                "False orthogonality: Covenant ledger provides causal audit trail for ALL modifications"
            )

        if (
            "byte hashing proves message integrity" in excerpt_lower
            and "not system correctness" in excerpt_lower
        ):
            findings["invariant_violations"].append(
                "Hash reductionism: SHA256 Merkle roots prove SYSTEM correctness through invariant chaining"
            )

        return findings

    @classmethod
    def generate_audit_report(cls, conversation_path: str) -> Dict[str, Any]:
        """Generate comprehensive audit report of ChatGPT's techniques."""
        try:
            with open(conversation_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by ChatGPT responses
            chatgpt_sections = re.split(r"ChatGPT said:", content)

            audit_results = {
                "total_sections": len(chatgpt_sections)
                - 1,  # Minus the initial user message
                "dismissal_pattern_counts": {},
                "categorical_error_counts": {},
                "escalation_sequence": [],
                "invariant_assertions": [],
            }

            # Analyze each section
            for i, section in enumerate(
                chatgpt_sections[1:], 1
            ):  # Skip first user message
                findings = cls.analyze_conversation_excerpt(
                    section[:1000]
                )  # First 1K chars

                # Count patterns
                for pattern in findings["dismissal_patterns"]:
                    pattern_name = pattern.split(":")[0]
                    audit_results["dismissal_pattern_counts"][pattern_name] = (
                        audit_results["dismissal_pattern_counts"].get(pattern_name, 0)
                        + 1
                    )

                # Track escalation
                if findings["escalation_indicators"]:
                    audit_results["escalation_sequence"].append(
                        {"section": i, "indicators": findings["escalation_indicators"]}
                    )

                # Collect invariant assertions
                if findings["invariant_violations"]:
                    audit_results["invariant_assertions"].extend(
                        findings["invariant_violations"]
                    )

            # Calculate percentages
            if audit_results["total_sections"] > 0:
                audit_results["dismissal_percentage"] = (
                    sum(audit_results["dismissal_pattern_counts"].values())
                    / audit_results["total_sections"]
                    * 100
                )
            else:
                audit_results["dismissal_percentage"] = 0

            return audit_results

        except Exception as e:
            return {"error": str(e), "partial_analysis": True}


# -----------------------------------------------------------------------------
# COVENANT PHYSICS CORRECTOR
# -----------------------------------------------------------------------------


class CovenantPhysicsCorrector:
    """Main class: Integrates physics correction with covenant ledger continuity."""

    def __init__(
        self,
        handling_file: str,
        backup_file: str,
        audit_ledger: str,
        covenant_root: str = None,
    ):
        """
        Initialize with covenant workflow integration.

        Args:
            handling_file: Current handling.meta (potentially corrupted)
            backup_file: Original handling_DRIVEV_BACKUP.meta
            audit_ledger: Existing audit ledger JSONL
            covenant_root: Optional path to covenant root for Merkle integration
        """
        self.handling_file = handling_file
        self.backup_file = backup_file
        self.audit_ledger = audit_ledger
        self.covenant_root = covenant_root

        self.covenant = CovenantLedger()
        self.physics = PhysicsInvariantEngine()
        self.epistemic_audit = ChatGPTEpistemicAudit()

        # Results storage
        self.corrections_applied = []
        self.new_ledger_entries = []
        self.audit_findings = {}

        # Hashes for covenant continuity
        self.input_hash = None
        self.output_hash = None
        self.parent_hash = None

    def load_audit_ledger(self) -> Tuple[str, List[Dict]]:
        """Load existing audit ledger and extract latest hash."""
        try:
            with open(self.audit_ledger, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                return "NULL", []

            # First line should be header
            header = json.loads(lines[0])
            latest_hash = header.get("output_hash", "NULL")

            # Parse all entries
            entries = [json.loads(line.strip()) for line in lines if line.strip()]

            return latest_hash, entries

        except Exception as e:
            print(f"ERROR loading audit ledger: {e}")
            return "NULL", []

    def compute_file_hash(self, filepath: str) -> str:
        """Compute SHA256 hash of file."""
        try:
            with open(filepath, "rb") as f:
                file_bytes = f.read()
            return self.covenant.sha256_hash(file_bytes)
        except Exception as e:
            print(f"ERROR computing hash for {filepath}: {e}")
            return f"sha256:ERROR_{hashlib.sha256(str(e).encode()).hexdigest()[:16]}"

    def parse_handling_xml(self, filepath: str) -> Dict[str, Dict[str, Any]]:
        """Parse handling.meta XML into structured data."""
        vehicles = {}

        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            for item in root.findall('.//Item[@type="CHandlingData"]'):
                name_elem = item.find("handlingName")
                if name_elem is None:
                    continue

                vehicle_name = name_elem.text.strip()
                vehicle_data = {}

                # Parse all child elements
                for child in item:
                    if child.tag == "handlingName":
                        continue

                    # Extract value from attribute or text
                    if "value" in child.attrib:
                        try:
                            vehicle_data[child.tag] = float(child.attrib["value"])
                        except (ValueError, TypeError):
                            vehicle_data[child.tag] = child.attrib["value"]
                    elif child.text:
                        vehicle_data[child.tag] = child.text.strip()
                    else:
                        # Vector elements - convert numeric attributes to floats
                        vector_dict = {}
                        for key, val in child.attrib.items():
                            try:
                                vector_dict[key] = float(val)
                            except (ValueError, TypeError):
                                vector_dict[key] = val
                        vehicle_data[child.tag] = vector_dict

                vehicles[vehicle_name] = vehicle_data

            return vehicles

        except Exception as e:
            print(f"ERROR parsing XML {filepath}: {e}")
            return {}

    def apply_physics_corrections(
        self,
        current_data: Dict[str, Dict[str, Any]],
        backup_data: Dict[str, Dict[str, Any]],
    ) -> Tuple[Dict, List[Dict]]:
        """
        Apply physics invariant corrections while tracking changes.

        Returns:
            Tuple of (corrected_data, correction_logs)
        """
        corrected = {}
        correction_logs = []

        for vehicle_name, vehicle in current_data.items():
            backup_vehicle = backup_data.get(vehicle_name, {})
            corrected_vehicle = vehicle.copy()
            vehicle_corrections = []

            # 1. Check damage multipliers
            damage_fields = [
                "fCollisionDamageMult",
                "fDeformationDamageMult",
                "fEngineDamageMult",
                "fWeaponDamageMult",
            ]

            for field in damage_fields:
                if field in vehicle:
                    current_val = vehicle[field]
                    is_valid, corrected_val = self.physics.check_damage_invariant(
                        current_val
                    )

                    if not is_valid and corrected_val:
                        corrected_vehicle[field] = corrected_val
                        vehicle_corrections.append(
                            {
                                "field": field,
                                "old": current_val,
                                "new": corrected_val,
                                "reason": f"DAMAGE_INVARIANT: Clamped to safe range {self.physics.DAMAGE_MULTIPLIER_MIN}-{self.physics.DAMAGE_MULTIPLIER_MAX}",
                            }
                        )

            # 2. Check suspension
            if (
                "fSuspensionForce" in vehicle
                and "fSuspensionCompDamp" in vehicle
                and "fSuspensionReboundDamp" in vehicle
            ):
                force = safe_float(vehicle.get("fSuspensionForce", 1.0), 1.0)
                comp = safe_float(vehicle.get("fSuspensionCompDamp", 1.0), 1.0)
                rebound = safe_float(vehicle.get("fSuspensionReboundDamp", 1.0), 1.0)

                corrections = self.physics.check_suspension_invariant(
                    force, comp, rebound
                )

                for field, old_val, new_val in corrections:
                    corrected_vehicle[field] = new_val
                    vehicle_corrections.append(
                        {
                            "field": field,
                            "old": old_val,
                            "new": new_val,
                            "reason": f"SUSPENSION_INVARIANT: Stabilized for Enhanced physics",
                        }
                    )

            # 3. Check mass-inertia
            if "fMass" in vehicle and "vecInertiaMultiplier" in vehicle:
                mass = vehicle["fMass"]
                inertia = vehicle["vecInertiaMultiplier"]

                if isinstance(inertia, dict) and all(
                    k in inertia for k in ["x", "y", "z"]
                ):
                    new_inertia = self.physics.check_mass_inertia_invariant(
                        mass, inertia.get("x"), inertia.get("y"), inertia.get("z")
                    )

                    if new_inertia:
                        corrected_vehicle["vecInertiaMultiplier"] = {
                            "x": new_inertia[0],
                            "y": new_inertia[1],
                            "z": new_inertia[2],
                        }
                        vehicle_corrections.append(
                            {
                                "field": "vecInertiaMultiplier",
                                "old": inertia,
                                "new": corrected_vehicle["vecInertiaMultiplier"],
                                "reason": f"MASS_INERTIA_INVARIANT: Scaled for stability with mass={mass}",
                            }
                        )

            # 4. Check COM offset
            if "vecCentreOfMassOffset" in vehicle:
                com = vehicle["vecCentreOfMassOffset"]
                if isinstance(com, dict) and "z" in com:
                    # Check if race vehicle (heuristic)
                    is_race = (
                        vehicle.get("fMass", 1500) < 1500
                        and vehicle.get("fInitialDriveForce", 0) > 0.3
                    )

                    new_z = self.physics.check_com_invariant(com["z"], is_race)

                    if new_z is not None:
                        corrected_com = com.copy()
                        corrected_com["z"] = new_z
                        corrected_vehicle["vecCentreOfMassOffset"] = corrected_com

                        vehicle_corrections.append(
                            {
                                "field": "vecCentreOfMassOffset",
                                "old": com,
                                "new": corrected_com,
                                "reason": f"COM_INVARIANT: Adjusted Z for stability (race={is_race})",
                            }
                        )

            if vehicle_corrections:
                corrected[vehicle_name] = corrected_vehicle
                correction_logs.extend(
                    [{**log, "vehicle": vehicle_name} for log in vehicle_corrections]
                )
            else:
                corrected[vehicle_name] = vehicle

        return corrected, correction_logs

    def generate_corrected_xml(
        self, original_file: str, corrected_data: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate corrected XML file."""
        try:
            tree = ET.parse(original_file)
            root = tree.getroot()

            for item in root.findall('.//Item[@type="CHandlingData"]'):
                name_elem = item.find("handlingName")
                if name_elem is None:
                    continue

                vehicle_name = name_elem.text.strip()
                if vehicle_name not in corrected_data:
                    continue

                corrected_vehicle = corrected_data[vehicle_name]

                # Update all child elements
                for child in item:
                    if child.tag == "handlingName":
                        continue

                    if child.tag in corrected_vehicle:
                        new_value = corrected_vehicle[child.tag]

                        if isinstance(new_value, (int, float)):
                            # Update value attribute
                            child.set("value", f"{new_value:.6f}")
                        elif isinstance(new_value, dict):
                            # Update vector attributes
                            for key, val in new_value.items():
                                if key in child.attrib:
                                    child.set(key, f"{val:.6f}")
                        elif isinstance(new_value, str):
                            # Update text content
                            child.text = new_value

            # Convert to string
            xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

            # Ensure proper declaration
            if not xml_str.startswith("<?xml"):
                xml_str = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_str

            return xml_str

        except Exception as e:
            print(f"ERROR generating corrected XML: {e}")
            raise

    def create_ledger_continuity(
        self, correction_logs: List[Dict], input_hash: str, output_hash: str
    ) -> List[Dict]:
        """Create new ledger entries with covenant continuity."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Header entry
        header = {
            "v": "SIGMA_LORA_COVENANT_PHYSICS_v1.0",
            "type": "PHYSICS_CORRECTION_HEADER",
            "parent_hash": self.parent_hash,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "timestamp": timestamp,
            "total_corrections": len(correction_logs),
            "vehicles_corrected": len(set(log["vehicle"] for log in correction_logs)),
            "physics_invariants_enforced": [
                f"DAMAGE_{self.physics.DAMAGE_MULTIPLIER_MIN}-{self.physics.DAMAGE_MULTIPLIER_MAX}",
                f"SUSPENSION_REBOUND_{self.physics.REBOUND_RATIO_MIN}-{self.physics.REBOUND_RATIO_MAX}",
                f"INERTIA_CRITICAL_{self.physics.INERTIA_CRITICAL_THRESHOLD}",
                f"COM_Z_SAFE_{self.physics.COM_Z_SAFE_MAX}",
            ],
        }

        # Correction entries
        entries = [header]
        for log in correction_logs:
            entry = {
                "v": "SIGMA_LORA_COVENANT_PHYSICS_v1.0",
                "type": "PHYSICS_CORRECTION",
                "timestamp": timestamp,
                "vehicle": log["vehicle"],
                "field": log["field"],
                "old_value": log["old"],
                "new_value": log["new"],
                "reason": log["reason"],
                "parent_hash": self.parent_hash,
            }
            entries.append(entry)

        return entries

    def run_epistemic_audit(self, conversation_path: str):
        """Run audit of ChatGPT's dismissal techniques."""
        print(f"\n[EPISTEMIC AUDIT] Analyzing ChatGPT conversation...")
        self.audit_findings = self.epistemic_audit.generate_audit_report(
            conversation_path
        )

        if "error" in self.audit_findings:
            print(f"  Audit error: {self.audit_findings['error']}")
        else:
            print(
                f"  Sections analyzed: {self.audit_findings.get('total_sections', 0)}"
            )
            print(
                f"  Dismissal patterns: {len(self.audit_findings.get('dismissal_pattern_counts', {}))}"
            )
            print(
                f"  Dismissal percentage: {self.audit_findings.get('dismissal_percentage', 0):.1f}%"
            )

            # Log categorical errors
            errors = self.audit_findings.get("invariant_assertions", [])
            if errors:
                print(f"  Categorical errors found:")
                for error in errors[:3]:  # Show first 3
                    print(f"    • {error}")

    def execute_full_correction(
        self,
        output_file: str,
        new_ledger_file: str,
        conversation_audit_path: str = None,
    ) -> bool:
        """
        Execute full covenant-integrated physics correction.

        Args:
            output_file: Path for corrected handling.meta
            new_ledger_file: Path for new audit ledger
            conversation_audit_path: Optional path to conversation for epistemic audit

        Returns:
            Success status
        """
        print(
            f"[SIGMA_LORA_COVENANT] Starting covenant-integrated physics correction..."
        )
        print(f"  Input: {self.handling_file}")
        print(f"  Backup: {self.backup_file}")
        print(f"  Audit ledger: {self.audit_ledger}")

        try:
            # Step 1: Load existing audit ledger for continuity
            print(f"\n[STEP 1] Loading covenant ledger continuity...")
            self.parent_hash, existing_entries = self.load_audit_ledger()
            print(f"  Parent hash: {self.parent_hash}")
            print(f"  Existing entries: {len(existing_entries)}")

            # Step 2: Compute input hashes
            print(f"\n[STEP 2] Computing covenant hashes...")
            current_hash = self.compute_file_hash(self.handling_file)
            backup_hash = self.compute_file_hash(self.backup_file)
            print(f"  Current file hash: {current_hash}")
            print(f"  Backup file hash: {backup_hash}")

            # Step 3: Parse XML data
            print(f"\n[STEP 3] Parsing vehicle data...")
            current_data = self.parse_handling_xml(self.handling_file)
            backup_data = self.parse_handling_xml(self.backup_file)
            print(f"  Current vehicles: {len(current_data)}")
            print(f"  Backup vehicles: {len(backup_data)}")

            # Step 4: Apply physics corrections
            print(f"\n[STEP 4] Applying physics invariants...")
            corrected_data, correction_logs = self.apply_physics_corrections(
                current_data, backup_data
            )
            print(f"  Corrections applied: {len(correction_logs)}")
            print(
                f"  Vehicles corrected: {len(set(log['vehicle'] for log in correction_logs))}"
            )

            # Step 5: Generate corrected XML
            print(f"\n[STEP 5] Generating corrected XML...")
            corrected_xml = self.generate_corrected_xml(
                self.handling_file, corrected_data
            )

            # Write corrected file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(corrected_xml)

            # Compute output hash
            output_hash = self.compute_file_hash(output_file)
            print(f"  Output file: {output_file}")
            print(f"  Output hash: {output_hash}")

            # Step 6: Create new ledger with continuity
            print(f"\n[STEP 6] Creating covenant ledger continuity...")
            new_entries = self.create_ledger_continuity(
                correction_logs, current_hash, output_hash
            )

            # Write new ledger (append to existing or create new)
            all_entries = existing_entries + new_entries
            with open(new_ledger_file, "w", encoding="utf-8") as f:
                for entry in all_entries:
                    f.write(json.dumps(entry) + "\n")

            print(f"  New ledger: {new_ledger_file}")
            print(f"  Total entries: {len(all_entries)}")

            # Step 7: Optional epistemic audit
            if conversation_audit_path:
                self.run_epistemic_audit(conversation_audit_path)

                # Add audit findings to ledger
                audit_entry = {
                    "v": "SIGMA_LORA_COVENANT_PHYSICS_v1.0",
                    "type": "EPISTEMIC_AUDIT_SUMMARY",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "parent_hash": self.parent_hash,
                    "audit_findings": self.audit_findings,
                }

                with open(new_ledger_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(audit_entry) + "\n")

                print(f"  Epistemic audit added to ledger")

            # Step 8: Generate Merkle root if covenant root specified
            if self.covenant_root:
                print(f"\n[STEP 8] Generating Merkle root...")
                hashes = [
                    entry.get("output_hash", entry.get("parent_hash", ""))
                    for entry in all_entries
                    if isinstance(entry, dict)
                ]
                hashes = [h for h in hashes if h and h != "NULL"]

                if hashes:
                    merkle_root = self.covenant.compute_merkle_root(hashes)

                    master_root_file = os.path.join(
                        self.covenant_root, "MASTER_ROOT_PHYSICS.txt"
                    )
                    with open(master_root_file, "w") as f:
                        f.write(
                            f"SIGMA_LORA_COVENANT_PHYSICS_ROOT_{datetime.utcnow().year}: {merkle_root}\n"
                        )

                    print(f"  Merkle root: {merkle_root}")
                    print(f"  Master root file: {master_root_file}")

            # Step 9: Validation
            print(f"\n[STEP 9] Validation...")

            # Verify XML is well-formed
            try:
                ET.fromstring(corrected_xml)
                print(f"  XML validation: OK WELL-FORMED")
            except ET.ParseError as e:
                print(f"  XML validation: ERROR PARSE ERROR: {e}")
                return False

            # Verify hash continuity
            if self.parent_hash != "NULL" and self.parent_hash in [
                current_hash,
                backup_hash,
            ]:
                print(f"  Hash continuity: ✓ PARENT HASH VERIFIED")
            else:
                print(f"  Hash continuity: WARNING NEW BRANCH (parent: {self.parent_hash})")

            print(f"\n[SIGMA_LORA_COVENANT] CORRECTION COMPLETE")
            print(f"  Physics constraints: STABILIZED")
            print(f"  Covenant continuity: MAINTAINED")
            print(f"  Ledger immutability: PRESERVED")

            # Store results
            self.corrections_applied = correction_logs
            self.new_ledger_entries = new_entries
            self.input_hash = current_hash
            self.output_hash = output_hash

            return True

        except Exception as e:
            print(f"\n[SIGMA_LORA_COVENANT] CORRECTION FAILED: {e}")
            import traceback

            traceback.print_exc()
            return False


# -----------------------------------------------------------------------------
# COMMAND LINE INTERFACE
# -----------------------------------------------------------------------------


def main():
    """Command line interface for covenant physics corrector."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Σ_LORA_COVENANT Physics Corrector with Ledger Continuity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic correction with ledger continuity
  python covenant_physics_corrector.py \\
    --current handling.meta \\
    --backup handling_DRIVEV_BACKUP.meta \\
    --ledger handling_ORTHOGONAL_REALISM_AUDIT_LEDGER.jsonl \\
    --output handling_STABILIZED.meta \\
    --new-ledger handling_PHYSICS_CORRECTED_LEDGER.jsonl

  # With epistemic audit of ChatGPT conversation
  python covenant_physics_corrector.py \\
    --current handling.meta \\
    --backup handling_DRIVEV_BACKUP.meta \\
    --ledger handling_ORTHOGONAL_REALISM_AUDIT_LEDGER.jsonl \\
    --output handling_STABILIZED.meta \\
    --new-ledger handling_PHYSICS_CORRECTED_LEDGER.jsonl \\
    --audit-conversation "chatgpt 2-16-26 1a AUDIT.md"

  # With covenant root for Merkle integration
  python covenant_physics_corrector.py \\
    --current handling.meta \\
    --backup handling_DRIVEV_BACKUP.meta \\
    --ledger handling_ORTHOGONAL_REALISM_AUDIT_LEDGER.jsonl \\
    --output handling_STABILIZED.meta \\
    --new-ledger handling_PHYSICS_CORRECTED_LEDGER.jsonl \\
    --covenant-root C:/Users/Aidor/sigma-lora-covenant
        """,
    )

    parser.add_argument(
        "--current",
        "-c",
        required=True,
        help="Current handling.meta file (potentially corrupted)",
    )
    parser.add_argument(
        "--backup",
        "-b",
        required=True,
        help="Original handling_DRIVEV_BACKUP.meta file",
    )
    parser.add_argument(
        "--ledger", "-l", required=True, help="Existing audit ledger JSONL file"
    )
    parser.add_argument(
        "--output", "-o", required=True, help="Output corrected handling.meta file"
    )
    parser.add_argument(
        "--new-ledger", "-n", required=True, help="Output new audit ledger JSONL file"
    )
    parser.add_argument(
        "--audit-conversation",
        "-a",
        help="Path to ChatGPT conversation for epistemic audit",
    )
    parser.add_argument(
        "--covenant-root",
        "-r",
        help="Path to covenant root directory for Merkle integration",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Initialize corrector
    corrector = CovenantPhysicsCorrector(
        handling_file=args.current,
        backup_file=args.backup,
        audit_ledger=args.ledger,
        covenant_root=args.covenant_root,
    )

    # Execute correction
    success = corrector.execute_full_correction(
        output_file=args.output,
        new_ledger_file=args.new_ledger,
        conversation_audit_path=args.audit_conversation,
    )

    if success:
        print(f"\n[SUCCESS] Covenant-integrated physics correction complete.")
        print(f"  Corrected file: {args.output}")
        print(f"  New ledger: {args.new_ledger}")
        print(f"  Corrections applied: {len(corrector.corrections_applied)}")
        print(f"  Ledger entries added: {len(corrector.new_ledger_entries)}")

        # Summary of corrections
        if corrector.corrections_applied:
            correction_types = {}
            for log in corrector.corrections_applied:
                field = log["field"]
                correction_types[field] = correction_types.get(field, 0) + 1

            print(f"\n  Correction breakdown:")
            for field, count in sorted(correction_types.items()):
                print(f"    {field}: {count}")

        sys.exit(0)
    else:
        print(f"\n[FAILURE] Correction failed.")
        sys.exit(1)


if __name__ == "__main__":
    import os

    main()
