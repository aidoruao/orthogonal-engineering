"""D_DIPLOMATIC implementation — Diplomatic Law.

All arithmetic uses Fraction. No floats.
All dataclasses are frozen=True.

Standards:
- Vienna Convention on Diplomatic Relations (VCDR, 1961)
- Vienna Convention on Consular Relations (VCCR, 1963)
- Diplomatic Relations Act (22 U.S.C. §254a et seq.)
- Convention on Special Missions (1969)
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class DiplomaticAgent:
    """A diplomatic agent with accreditation and immunity status (VCDR Art. 1, 14, 29).

    Fields:
        agent_id: Unique identifier for the diplomatic agent.
        accredited: Whether the agent is formally accredited by the receiving state.
        recognized_by_receiving_state: Whether the receiving state recognizes the agent.
        persona_non_grata: Whether the receiving state has declared the agent PNG.
        recall_completed: Whether the sending state has recalled the agent post-PNG.
        rank: e.g. "ambassador", "counselor", "attache"
    """

    agent_id: str
    accredited: bool
    recognized_by_receiving_state: bool
    persona_non_grata: bool
    recall_completed: bool
    rank: str


@dataclass(frozen=True)
class DiplomaticMission:
    """Mission premises and archive integrity (VCDR Art. 22).

    Fields:
        mission_id: Unique identifier.
        premises_inviolable: Whether premises are protected under VCDR Art. 22.
        receiving_state_entered_without_consent: Whether receiving state breached inviolability.
        archives_secured: Whether archives/documents are protected (VCDR Art. 24).
        protection_duty_met: Whether receiving state has fulfilled its protection duty.
    """

    mission_id: str
    premises_inviolable: bool
    receiving_state_entered_without_consent: bool
    archives_secured: bool
    protection_duty_met: bool


@dataclass(frozen=True)
class ImmunityWaiver:
    """Waiver of diplomatic immunity (VCDR Art. 32).

    Fields:
        waiver_id: Unique identifier.
        explicit: Whether waiver is express (not implied).
        by_sending_state: Whether waiver was granted by the sending state (required).
        scope: e.g. "criminal", "civil", "full"
    """

    waiver_id: str
    explicit: bool
    by_sending_state: bool
    scope: str


@dataclass(frozen=True)
class ConsularOfficer:
    """Consular officer with functional immunity scope (VCCR Art. 43).

    Fields:
        officer_id: Unique identifier.
        official_act: Whether the act in question is an official consular function.
        grave_crime_charged: Whether officer is charged with a grave crime.
        notification_sent_within_hours: Hours until notification sent to consular post.
        max_notification_hours: Maximum hours allowed under VCCR Art. 36(1)(b).
    """

    officer_id: str
    official_act: bool
    grave_crime_charged: bool
    notification_sent_within_hours: Fraction
    max_notification_hours: Fraction


@dataclass(frozen=True)
class SpecialMission:
    """Special mission with temporary immunity (Convention on Special Missions, 1969).

    Fields:
        mission_id: Unique identifier.
        mutual_consent: Whether receiving state gave consent.
        mission_active: Whether the mission is still in its active period.
        official_acts_only: Whether immunity is confined to official acts.
    """

    mission_id: str
    mutual_consent: bool
    mission_active: bool
    official_acts_only: bool
