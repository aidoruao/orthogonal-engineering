"""D_POLICE_PROCEDURE implementation — Police Procedure

Implements police procedures including body camera requirements,
use of force reporting, and complaint processing.

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE
Source: Department policies, POST standards, DOJ consent decrees

Biblical: Romans 13:4 — "For the one in authority is God's servant for your
good... They hold no terror for those who do right, but for those who do wrong."
Also: Micah 6:8 — "Act justly, love mercy, walk humbly."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction


class EncounterType(Enum):
    """Types of police-citizen encounters."""
    TRAFFIC_STOP = auto()
    FIELD_INTERVIEW = auto()
    ARREST = auto()
    SEARCH = auto()
    WARRANT_SERVICE = auto()
    DOMESTIC_CALL = auto()
    DISTURBANCE = auto()
    PROACTIVE_PATROL = auto()


class ForceLevel(Enum):
    """Levels of force used."""
    NONE = auto()
    PRESENCE = auto()        # Officer presence
    VERBAL = auto()          # Verbal commands
    SOFT_HAND = auto()       # Soft empty-hand control
    HARD_HAND = auto()       # Hard empty-hand control
    LESS_LETHAL = auto()     # OC spray, baton, TASER
    LETHAL = auto()          # Deadly force


class ComplaintType(Enum):
    """Types of citizen complaints."""
    EXCESSIVE_FORCE = auto()
    FALSE_ARREST = auto()
    DISCRIMINATION = auto()
    UNPROFESSIONAL_CONDUCT = auto()
    FAILURE_TO_RESPOND = auto()
    PROPERTY_DAMAGE = auto()
    OTHER = auto()


class ComplaintStatus(Enum):
    """Status of complaint investigation."""
    RECEIVED = auto()
    UNDER_REVIEW = auto()
    INVESTIGATING = auto()
    AWAITING_EVIDENCE = auto()
    SUBSTANTIATED = auto()
    UNSUBSTANTIATED = auto()
    EXONERATED = auto()
    UNFOUNDED = auto()


@dataclass
class BodyCamera:
    """A police body-worn camera."""
    camera_id: str
    officer_id: str
    serial_number: str
    
    # Status
    activated: bool = False
    recording: bool = False
    battery_level: Fraction = Fraction(100)
    storage_available: bool = True
    
    # Audit trail
    last_activation: Optional[datetime] = None
    last_deactivation: Optional[datetime] = None
    recordings_count: int = 0


@dataclass
class CitizenEncounter:
    """A police-citizen encounter."""
    encounter_id: str
    officer_id: str
    officer_camera_id: Optional[str]
    
    encounter_type: EncounterType
    start_time: datetime
    location: str
    
    # Body camera
    camera_activated: bool = False
    camera_recording_start: Optional[datetime] = None
    camera_recording_end: Optional[datetime] = None
    
    # Outcome
    end_time: Optional[datetime] = None
    outcome: Optional[str] = None
    
    def check_camera_compliance(self) -> Dict:
        """Check if body camera was properly activated."""
        if self.encounter_type in [EncounterType.TRAFFIC_STOP, 
                                    EncounterType.ARREST,
                                    EncounterType.SEARCH,
                                    EncounterType.WARRANT_SERVICE]:
            # Camera required
            return {
                "encounter_id": self.encounter_id,
                "camera_required": True,
                "camera_activated": self.camera_activated,
                "compliant": self.camera_activated,
            }
        else:
            # Camera recommended but not strictly required
            return {
                "encounter_id": self.encounter_id,
                "camera_required": False,
                "camera_activated": self.camera_activated,
                "compliant": True,  # Not required
            }


@dataclass
class UseOfForceIncident:
    """A use of force incident."""
    incident_id: str
    encounter_id: str
    officer_id: str
    
    # Incident details
    force_level: ForceLevel
    force_type: str  # specific type used
    timestamp: datetime
    
    # Subject
    subject_injured: bool = False
    subject_injury_type: Optional[str] = None
    medical_aid_provided: bool = False
    
    # Reporting
    report_filed: bool = False
    report_timestamp: Optional[datetime] = None
    supervisor_notified: bool = False
    supervisor_notification_time: Optional[datetime] = None


@dataclass
class CitizenComplaint:
    """A citizen complaint against an officer."""
    complaint_id: str
    complainant_name: str
    complaint_date: datetime
    
    # Allegations
    complaint_type: ComplaintType
    officer_id: str
    incident_date: datetime
    incident_location: str
    description: str
    
    # Process
    status: ComplaintStatus = ComplaintStatus.RECEIVED
    assigned_investigator: Optional[str] = None
    
    # Timeline
    investigation_start_date: Optional[datetime] = None
    investigation_complete_date: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    
    # Documentation
    evidence_collected: List[str] = field(default_factory=list)
    witness_statements: List[str] = field(default_factory=list)
    
    # Outcome
    finding: Optional[str] = None
    discipline_recommended: Optional[str] = None


class BodyCameraManager:
    """Manager for body camera compliance."""
    
    REQUIRED_ENCOUNTER_TYPES = [
        EncounterType.TRAFFIC_STOP,
        EncounterType.ARREST,
        EncounterType.SEARCH,
        EncounterType.WARRANT_SERVICE,
    ]
    
    def check_camera_status(self, camera: BodyCamera) -> Dict:
        """Check if camera is operational."""
        return {
            "camera_id": camera.camera_id,
            "operational": (
                camera.battery_level >= Fraction(20) and
                camera.storage_available
            ),
            "battery_ok": camera.battery_level >= Fraction(20),
            "storage_ok": camera.storage_available,
        }
    
    def activate_camera(self, camera: BodyCamera) -> Dict:
        """Activate body camera for recording."""
        if camera.battery_level < Fraction(10):
            return {"error": "Battery too low", "activated": False}
        
        if not camera.storage_available:
            return {"error": "Storage full", "activated": False}
        
        camera.activated = True
        camera.recording = True
        camera.last_activation = datetime.now()
        camera.recordings_count += 1
        
        return {
            "camera_id": camera.camera_id,
            "activated": True,
            "timestamp": camera.last_activation,
        }
    
    def audit_encounter(self, encounter: CitizenEncounter) -> Dict:
        """Audit encounter for body camera compliance."""
        return encounter.check_camera_compliance()


class UseOfForceReporter:
    """Manager for use of force reporting."""
    
    REPORTING_DEADLINE_HOURS = 24
    SUPERVISOR_NOTIFICATION_MINUTES = 30
    
    def file_report(self, incident: UseOfForceIncident) -> Dict:
        """File use of force report."""
        incident.report_filed = True
        incident.report_timestamp = datetime.now()
        
        return {
            "incident_id": incident.incident_id,
            "report_filed": True,
            "timestamp": incident.report_timestamp,
        }
    
    def notify_supervisor(self, incident: UseOfForceIncident) -> Dict:
        """Record supervisor notification."""
        incident.supervisor_notified = True
        incident.supervisor_notification_time = datetime.now()
        
        return {
            "incident_id": incident.incident_id,
            "supervisor_notified": True,
            "timestamp": incident.supervisor_notification_time,
        }
    
    def check_reporting_compliance(self, incident: UseOfForceIncident) -> Dict:
        """
        Check if reporting requirements were met.
        
        Invariant: Use of force report filed within 24 hours.
        """
        # Check report filing deadline
        if not incident.report_filed:
            hours_elapsed = (datetime.now() - incident.timestamp).total_seconds() / 3600
            return {
                "incident_id": incident.incident_id,
                "report_filed": False,
                "compliant": False,
                "hours_elapsed": hours_elapsed,
                "deadline_hours": self.REPORTING_DEADLINE_HOURS,
                "deadline_missed": hours_elapsed > self.REPORTING_DEADLINE_HOURS,
            }
        
        # Calculate reporting time
        report_time = incident.report_timestamp
        incident_time = incident.timestamp
        hours_to_report = (report_time - incident_time).total_seconds() / 3600
        
        return {
            "incident_id": incident.incident_id,
            "report_filed": True,
            "hours_to_report": hours_to_report,
            "deadline_hours": self.REPORTING_DEADLINE_HOURS,
            "compliant": hours_to_report <= self.REPORTING_DEADLINE_HOURS,
        }
    
    def check_supervisor_notification(self, incident: UseOfForceIncident) -> Dict:
        """Check if supervisor was notified promptly."""
        if not incident.supervisor_notified:
            return {
                "incident_id": incident.incident_id,
                "supervisor_notified": False,
                "compliant": False,
            }
        
        minutes_to_notify = (
            incident.supervisor_notification_time - incident.timestamp
        ).total_seconds() / 60
        
        return {
            "incident_id": incident.incident_id,
            "supervisor_notified": True,
            "minutes_to_notify": minutes_to_notify,
            "deadline_minutes": self.SUPERVISOR_NOTIFICATION_MINUTES,
            "compliant": minutes_to_notify <= self.SUPERVISOR_NOTIFICATION_MINUTES,
        }


class ComplaintProcessor:
    """Processor for citizen complaints."""
    
    # Investigation timelines
    INVESTIGATION_START_DAYS = 7
    INVESTIGATION_COMPLETE_DAYS = 90
    
    def receive_complaint(self, complaint: CitizenComplaint) -> Dict:
        """Receive and log a new complaint."""
        complaint.status = ComplaintStatus.RECEIVED
        
        return {
            "complaint_id": complaint.complaint_id,
            "received": True,
            "timestamp": complaint.complaint_date,
        }
    
    def assign_investigator(self, complaint: CitizenComplaint,
                            investigator_id: str) -> Dict:
        """Assign investigator to complaint."""
        complaint.assigned_investigator = investigator_id
        complaint.status = ComplaintStatus.INVESTIGATING
        complaint.investigation_start_date = datetime.now()
        
        return {
            "complaint_id": complaint.complaint_id,
            "investigator": investigator_id,
            "status": complaint.status.name,
        }
    
    def document_evidence(self, complaint: CitizenComplaint,
                          evidence: List[str]) -> Dict:
        """Document evidence for complaint."""
        complaint.evidence_collected.extend(evidence)
        
        return {
            "complaint_id": complaint.complaint_id,
            "evidence_count": len(complaint.evidence_collected),
        }
    
    def complete_investigation(self, complaint: CitizenComplaint,
                               finding: str) -> Dict:
        """Complete investigation with finding."""
        complaint.investigation_complete_date = datetime.now()
        complaint.finding = finding
        complaint.decision_date = datetime.now()
        
        # Map finding to status
        finding_to_status = {
            "substantiated": ComplaintStatus.SUBSTANTIATED,
            "unsubstantiated": ComplaintStatus.UNSUBSTANTIATED,
            "exonerated": ComplaintStatus.EXONERATED,
            "unfounded": ComplaintStatus.UNFOUNDED,
        }
        complaint.status = finding_to_status.get(finding.lower(), 
                                                  ComplaintStatus.UNDER_REVIEW)
        
        return {
            "complaint_id": complaint.complaint_id,
            "status": complaint.status.name,
            "finding": finding,
        }
    
    def check_process_compliance(self, complaint: CitizenComplaint) -> Dict:
        """
        Check if complaint process was followed.
        
        Invariant: Complaint process is deterministic and documented.
        """
        checks = {
            "received": complaint.status != ComplaintStatus.RECEIVED,
            "assigned_investigator": complaint.assigned_investigator is not None,
            "investigation_started": complaint.investigation_start_date is not None,
            "evidence_collected": len(complaint.evidence_collected) > 0,
            "completed_or_pending": (
                complaint.status in [
                    ComplaintStatus.SUBSTANTIATED,
                    ComplaintStatus.UNSUBSTANTIATED,
                    ComplaintStatus.EXONERATED,
                    ComplaintStatus.UNFOUNDED,
                ] or complaint.status in [
                    ComplaintStatus.RECEIVED,
                    ComplaintStatus.UNDER_REVIEW,
                    ComplaintStatus.INVESTIGATING,
                ]
            ),
        }
        
        # For completed complaints, check timeline
        timeline_compliant = True
        if complaint.investigation_complete_date:
            days_to_complete = (
                complaint.investigation_complete_date - complaint.complaint_date
            ).days
            timeline_compliant = days_to_complete <= self.INVESTIGATION_COMPLETE_DAYS
            checks["timeline_met"] = timeline_compliant
        
        all_compliant = all(checks.values())
        
        return {
            "complaint_id": complaint.complaint_id,
            "checks": checks,
            "all_compliant": all_compliant,
            "status": complaint.status.name,
        }


class PoliceProcedureAuditor:
    """Comprehensive auditor for police procedures."""
    
    def __init__(self):
        self.camera_manager = BodyCameraManager()
        self.force_reporter = UseOfForceReporter()
        self.complaint_processor = ComplaintProcessor()
    
    def audit_body_camera(self, encounter: CitizenEncounter) -> Dict:
        """Audit body camera compliance for an encounter."""
        return self.camera_manager.audit_encounter(encounter)
    
    def audit_use_of_force(self, incident: UseOfForceIncident) -> Dict:
        """Audit use of force reporting compliance."""
        report_compliance = self.force_reporter.check_reporting_compliance(incident)
        supervisor_compliance = self.force_reporter.check_supervisor_notification(incident)
        
        return {
            "incident_id": incident.incident_id,
            "report_compliant": report_compliance["compliant"],
            "supervisor_notification_compliant": supervisor_compliance["compliant"],
            "fully_compliant": (
                report_compliance["compliant"] and 
                supervisor_compliance["compliant"]
            ),
        }
    
    def audit_complaint(self, complaint: CitizenComplaint) -> Dict:
        """Audit complaint process compliance."""
        return self.complaint_processor.check_process_compliance(complaint)


# Convenience functions
def check_camera_activation(encounter: CitizenEncounter) -> Dict:
    """Quick check of body camera activation."""
    return encounter.check_camera_compliance()


def check_force_report_timeliness(incident: UseOfForceIncident) -> Dict:
    """Quick check of use of force reporting timeliness."""
    reporter = UseOfForceReporter()
    return reporter.check_reporting_compliance(incident)


def check_complaint_documentation(complaint: CitizenComplaint) -> Dict:
    """Quick check of complaint documentation."""
    processor = ComplaintProcessor()
    return processor.check_process_compliance(complaint)
