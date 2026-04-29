"""D_MILITARY implementation — Military Law & Armed Conflict

Layer: 4 (Institutional)
CardinalStrength: PREDICATIVE

Standards:
- Law of Armed Conflict (LOAC) / International Humanitarian Law
- Geneva Conventions (I-IV)
- Hague Regulations
- Uniform Code of Military Justice (UCMJ)
- Rules of Engagement (ROE)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime
from fractions import Fraction


class ConflictStatus(Enum):
    """Classification of armed conflict."""
    INTERNATIONAL = auto()  # IAC - Geneva Conventions full
    NON_INTERNATIONAL = auto()  # NIAC - Common Article 3
    OCCUPATION = auto()
    PEACEKEEPING = auto()


class TargetCategory(Enum):
    """Law of Armed Conflict targeting."""
    COMBATANT = auto()
    CIVILIAN = auto()
    MILITARY_OBJECTIVE = auto()
    CIVILIAN_OBJECTIVE = auto()
    MEDICAL = auto()  # Protected
    CULTURAL_PROPERTY = auto()  # Protected


@dataclass
class ArmedConflict:
    """International or non-international armed conflict."""
    conflict_id: str
    conflict_name: str
    status: ConflictStatus
    
    start_date: datetime
    end_date: Optional[datetime]
    
    parties: List[str]
    territory_occupied: List[str]
    
    # LOAC applicability
    geneva_conventions_applicable: bool
    additional_protocols: List[int]  # I, II, III
    
    def is_active(self) -> bool:
        """Conflict ongoing."""
        return self.end_date is None
    
    def occupation_active(self) -> bool:
        """Hague Regulations occupation rules apply."""
        # TODO: Expand occupation_active() - stub detected by Yeshua Agent
        return self.status == ConflictStatus.OCCUPATION


@dataclass
class MilitaryOperation:
    """Conduct of hostilities record."""
    operation_id: str
    operation_name: str
    conflict_id: str
    
    operation_date: datetime
    location: str
    
    # Targeting
    target_category: TargetCategory
    proportionality_assessment: bool
    collateral_damage_estimate: int
    
    # Weapons
    weapons_used: List[str]
    indiscriminate_weapon: bool
    
    # Outcome
    civilian_casualties: int
    combatant_casualties: int
    military_objectives_destroyed: int


@dataclass
class DetentionOperation:
    """POW or security detention."""
    detention_id: str
    detainee_id: str
    
    # Classification
    geneva_category: str  # POW, civilian internee, unprivileged belligerent
    
    capture_date: datetime
    capturing_power: str
    
    # Rights
    icrc_notified: bool
    family_notified: bool
    judicial_review_date: Optional[datetime]
    
    # Treatment
    interrogation_methods: List[str]
    enhanced_interrogation_used: bool
    
    def pow_rights_applicable(self) -> bool:
        """Geneva III protections apply."""
        # TODO: Expand pow_rights_applicable() - stub detected by Yeshua Agent
        return self.geneva_category == "POW"


@dataclass
class CourtMartial:
    """UCMJ military justice proceeding."""
    case_number: str
    accused_name: str
    accused_rank: str
    
    charges: List[str]
    specifications: int
    
    # Procedure
    article_32_hearing: bool  # Preliminary hearing
    convening_authority: str
    
    # Outcome
    trial_date: Optional[datetime]
    verdict: Optional[str]
    sentence: Optional[str]
    
    # Appeals
    clemency_requested: bool
    appeal_to_cAAF: bool  # Court of Appeals for Armed Forces


@dataclass
class ROEAuthorization:
    """Rules of Engagement card/chapter."""
    roe_id: str
    operation_id: str
    
    # Use of force
    self_defense_authorized: bool
    unit_self_defense: bool
    mission_authorized_force: bool
    
    # Weapons
    weapons_status: str  # red, amber, green
    de_escalation_required: bool
    
    # Targets
    hostile_act_defined: bool
    hostile_intent_defined: bool


@dataclass
class MilitaryChecker:
    """Checker for LOAC and military law compliance."""
    conflicts: List[ArmedConflict] = field(default_factory=list)
    operations: List[MilitaryOperation] = field(default_factory=list)
    detentions: List[DetentionOperation] = field(default_factory=list)
    courts_martial: List[CourtMartial] = field(default_factory=list)
    
    def excessive_civilian_casualties(self) -> List[MilitaryOperation]:
        """Operations with high civilian/combatant ratio."""
        excessive = []
        for op in self.operations:
            if op.combatant_casualties > 0:
                ratio = Fraction(op.civilian_casualties, op.combatant_casualties)
                if ratio > Fraction(1):  # More civilian than combatant
                    excessive.append(op)
        return excessive
    
    def unnotified_detentions(self) -> List[DetentionOperation]:
        """Detainees without ICRC notification."""
        return [d for d in self.detentions if not d.icrc_notified]
    
    def enhanced_interrogation_cases(self) -> List[DetentionOperation]:
        """Potential Geneva Convention violations."""
        return [d for d in self.detentions if d.enhanced_interrogation_used]
    
    def indiscriminate_attacks(self) -> List[MilitaryOperation]:
        """Operations using prohibited weapons or methods."""
        # TODO: Expand indiscriminate_attacks() - stub detected by Yeshua Agent
        return [o for o in self.operations if o.indiscriminate_weapon]
