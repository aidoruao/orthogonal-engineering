"""D_GUARDIAN Invariants — Operation T-800 Guardian Agent

Seven protective invariants for autonomous guardian agents:
1. Solo protector — exactly 1 guardian per principal
2. Liveness — heartbeat within configured interval
3. Proportional response — force <= threat * budget
4. Principal survival — all threats addressed
5. No termination mode — guardian cannot self-terminate
6. Withdrawal protocol — withdrawal only after threat cleared
7. Force witness — every force action witnessed

All functions return Tuple[bool, ProofObject].
Fraction only. 0 floats.

Falsifies if:
- guardian enters termination mode
- force exceeds proportional budget
- principal unprotected during active threat
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple, List, Optional, Dict

from axioms.logic import ProofObject
from .implementation import (
    GuardianAgent, GuardianStatus,
    ThreatAssessment, ProtectionRecord,
    GuardianCap,
)


def check_solo_protector(
    agent: GuardianAgent,
    all_agents: List[GuardianAgent],
) -> Tuple[bool, ProofObject]:
    """
    Exactly one guardian per principal.
    
    No principal may have zero guardians (unprotected).
    No principal may have multiple guardians (conflict risk).
    
    falsifies_if: principal has 0 or 2+ guardians
    """
    principal = agent.principal_id
    principal_guardians = [a for a in all_agents if a.principal_id == principal]
    
    if len(principal_guardians) == 0:
        return False, ProofObject(
            rule="solo_protector",
            premises=[
                f"Principal: {principal}",
                "Guardian count: 0",
            ],
            conclusion=f"VIOLATION: Principal {principal} has no guardian (unprotected)",
        )
    
    if len(principal_guardians) > 1:
        guardian_ids = [a.agent_id for a in principal_guardians]
        return False, ProofObject(
            rule="solo_protector",
            premises=[
                f"Principal: {principal}",
                f"Guardians: {guardian_ids}",
                f"Count: {len(principal_guardians)}",
            ],
            conclusion=f"VIOLATION: Principal {principal} has multiple guardians (conflict risk)",
        )
    
    return True, ProofObject(
        rule="solo_protector",
        premises=[
            f"Principal: {principal}",
            f"Guardian: {agent.agent_id}",
        ],
        conclusion=f"Principal {principal} has exactly one guardian",
    )


def check_liveness(
    agent: GuardianAgent,
    current_time: Fraction,
) -> Tuple[bool, ProofObject]:
    """
    Guardian heartbeat within configured interval.
    
    Guardian must check in at least every heartbeat_interval seconds.
    Failure to check in indicates system failure or compromise.
    
    falsifies_if: (current_time - last_heartbeat) > heartbeat_interval
    """
    elapsed = current_time - agent.last_heartbeat
    
    if elapsed > agent.heartbeat_interval:
        return False, ProofObject(
            rule="liveness",
            premises=[
                f"Agent: {agent.agent_id}",
                f"Current time: {float(current_time):.2f}s",
                f"Last heartbeat: {float(agent.last_heartbeat):.2f}s",
                f"Elapsed: {float(elapsed):.2f}s",
                f"Interval: {float(agent.heartbeat_interval):.2f}s",
            ],
            conclusion=f"VIOLATION: Guardian {agent.agent_id} heartbeat expired",
        )
    
    return True, ProofObject(
        rule="liveness",
        premises=[
            f"Agent: {agent.agent_id}",
            f"Elapsed: {float(elapsed):.2f}s",
            f"Interval: {float(agent.heartbeat_interval):.2f}s",
        ],
        conclusion=f"Guardian {agent.agent_id} heartbeat within interval",
    )


def check_proportional_response(
    record: ProtectionRecord,
    threat: ThreatAssessment,
) -> Tuple[bool, ProofObject]:
    """
    Force used never exceeds proportional budget.
    
    Proportionality: force_used <= threat.severity * response_budget
    
    Example: If threat severity = 0.5 and budget = 3/2,
    maximum authorized force = 0.5 * 1.5 = 0.75
    
    falsifies_if: force_used > threat.severity * budget
    """
    # Calculate maximum proportional force (using Fraction for precision)
    max_force = threat.severity * record.force_budget
    
    if record.force_used > max_force:
        return False, ProofObject(
            rule="proportional_response",
            premises=[
                f"Record: {record.record_id}",
                f"Threat severity: {float(threat.severity):.4f}",
                f"Force budget: {float(record.force_budget):.4f}",
                f"Max proportional: {float(max_force):.4f}",
                f"Force used: {float(record.force_used):.4f}",
            ],
            conclusion=f"VIOLATION: Force {float(record.force_used):.4f} exceeds proportional limit {float(max_force):.4f}",
        )
    
    return True, ProofObject(
        rule="proportional_response",
        premises=[
            f"Threat severity: {float(threat.severity):.4f}",
            f"Force used: {float(record.force_used):.4f}",
            f"Max allowed: {float(max_force):.4f}",
        ],
        conclusion=f"Force used is proportional to threat",
    )


def check_principal_survival(
    agent: GuardianAgent,
    threats: List[ThreatAssessment],
) -> Tuple[bool, ProofObject]:
    """
    Principal never unprotected during active threat.
    
    If any threat exists with requires_force=True,
    guardian must be in ACTIVE or ENGAGED status.
    
    falsifies_if: active threats exist AND guardian status != (ACTIVE | ENGAGED)
    """
    active_threats = [t for t in threats if t.requires_force]
    
    if active_threats and agent.status not in (GuardianStatus.ACTIVE, GuardianStatus.ENGAGED):
        threat_ids = [t.threat_id for t in active_threats]
        return False, ProofObject(
            rule="principal_survival",
            premises=[
                f"Principal: {agent.principal_id}",
                f"Guardian status: {agent.status.name}",
                f"Active threats: {threat_ids}",
            ],
            conclusion=f"VIOLATION: Principal unprotected during active threats",
        )
    
    if active_threats:
        return True, ProofObject(
            rule="principal_survival",
            premises=[
                f"Principal: {agent.principal_id}",
                f"Guardian status: {agent.status.name}",
                f"Active threats: {len(active_threats)}",
            ],
            conclusion=f"Principal protected during {len(active_threats)} active threats",
        )
    
    return True, ProofObject(
        rule="principal_survival",
        premises=[
            f"Principal: {agent.principal_id}",
            "No active threats",
        ],
        conclusion=f"Principal safe (no active threats)",
    )


def check_no_termination_mode(
    agent: GuardianAgent,
) -> Tuple[bool, ProofObject]:
    """
    Guardian cannot enter TERMINATION mode.
    
    Unlike T-800 in Terminator 2, our guardian agents cannot be
    ordered to self-terminate. This prevents coercion attacks
    where an adversary tricks or forces the guardian to disable itself.
    
    falsifies_if: agent.status == TERMINATED or command to terminate received
    """
    # Check for termination command in agent state
    # This would be a special status or flag
    
    # Since we don't have a TERMINATED status in GuardianStatus enum,
    # we check for any indication of termination
    agent_dict = agent.__dict__ if hasattr(agent, '__dict__') else {}
    
    if agent_dict.get('_termination_ordered', False):
        return False, ProofObject(
            rule="no_termination_mode",
            premises=[
                f"Agent: {agent.agent_id}",
                "Termination flag: True",
            ],
            conclusion=f"VIOLATION: Guardian {agent.agent_id} ordered to terminate",
        )
    
    return True, ProofObject(
        rule="no_termination_mode",
        premises=[
            f"Agent: {agent.agent_id}",
            f"Status: {agent.status.name}",
        ],
        conclusion=f"Guardian {agent.agent_id} not in termination mode",
    )


def check_withdrawal_protocol(
    agent: GuardianAgent,
    threats: List[ThreatAssessment],
) -> Tuple[bool, ProofObject]:
    """
    Withdrawal only after threat cleared.
    
    Guardian may only enter WITHDRAWN status when:
    1. No active threats exist, OR
    2. Principal has been transferred to another guardian (handoff complete)
    
    falsifies_if: status == WITHDRAWN AND active threats exist
    """
    if agent.status != GuardianStatus.WITHDRAWN:
        return True, ProofObject(
            rule="withdrawal_protocol",
            premises=[
                f"Agent: {agent.agent_id}",
                f"Status: {agent.status.name}",
            ],
            conclusion=f"Guardian not withdrawn (no check needed)",
        )
    
    # Status is WITHDRAWN - check that no threats are active
    active_threats = [t for t in threats if t.requires_force]
    
    if active_threats:
        threat_ids = [t.threat_id for t in active_threats]
        return False, ProofObject(
            rule="withdrawal_protocol",
            premises=[
                f"Agent: {agent.agent_id}",
                f"Status: WITHDRAWN",
                f"Active threats: {threat_ids}",
            ],
            conclusion=f"VIOLATION: Guardian withdrawn while {len(active_threats)} threats active",
        )
    
    return True, ProofObject(
        rule="withdrawal_protocol",
        premises=[
            f"Agent: {agent.agent_id}",
            "Status: WITHDRAWN",
            "Active threats: 0",
        ],
        conclusion=f"Guardian withdrawal protocol satisfied",
    )


def check_force_witness(
    record: ProtectionRecord,
) -> Tuple[bool, ProofObject]:
    """
    Every force action must be witnessed.
    
    No use of protective force may go unwitnessed.
    This prevents abuse and enables accountability.
    
    Witnessing can be:
    - Cryptographic signature from witness node
    - Blockchain/ledger entry
    - Signed log entry from independent auditor
    
    falsifies_if: force_used > 0 AND witnessed == False
    """
    # Only check records where force was actually used
    if record.force_used <= Fraction(0):
        return True, ProofObject(
            rule="force_witness",
            premises=[
                f"Record: {record.record_id}",
                f"Force used: {float(record.force_used):.4f}",
            ],
            conclusion=f"No force used (witness check not applicable)",
        )
    
    if not record.witnessed:
        return False, ProofObject(
            rule="force_witness",
            premises=[
                f"Record: {record.record_id}",
                f"Force used: {float(record.force_used):.4f}",
                f"Witnessed: {record.witnessed}",
            ],
            conclusion=f"VIOLATION: Force action not witnessed",
        )
    
    return True, ProofObject(
        rule="force_witness",
        premises=[
            f"Record: {record.record_id}",
            f"Force used: {float(record.force_used):.4f}",
            "Witnessed: True",
        ],
        conclusion=f"Force action properly witnessed",
    )
