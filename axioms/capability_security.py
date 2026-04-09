"""Capability Security — Object-capability model, authority attenuation.

Formalizes the principle of least authority (POLA) and capability
confinement. No ambient authority. All access mediated by capabilities.

Mathematical foundation: Dennis & Van Horn, "Programming Semantics
for Multiprogrammed Computations" (1966)
Biblical: Matthew 25:21 — "Well done, good and faithful servant!
You have been faithful with a few things; I will put you in charge
of many things."
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Set, Optional, FrozenSet
from fractions import Fraction
from enum import Enum, auto

from axioms.logic import ProofObject


class Permission(Enum):
    """Standard capability permissions."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELEGATE = "delegate"
    REVOKE = "revoke"


@dataclass(frozen=True)
class Capability:
    """An unforgeable capability token.
    
    A capability grants a set of permissions over a target resource.
    Capabilities can be attenuated (weakened) but never strengthened.
    """
    target: str           # Resource identifier
    permissions: FrozenSet[Permission]
    attenuations: Tuple[str, ...]  # History of attenuations applied
    delegator: str        # Who delegated this capability
    
    def has_permission(self, perm: Permission) -> bool:
        """Check if capability has a specific permission."""
        return perm in self.permissions
    
    def __hash__(self) -> int:
        return hash((self.target, self.permissions, self.attenuations, self.delegator))


@dataclass
class CapabilitySpace:
    """The capability space for a process or system.
    
    Maps process IDs to their held capabilities.
    """
    capabilities: Dict[str, List[Capability]] = field(default_factory=dict)
    
    def add_capability(self, process_id: str, cap: Capability) -> None:
        """Add a capability to a process's capability set."""
        if process_id not in self.capabilities:
            self.capabilities[process_id] = []
        self.capabilities[process_id].append(cap)
    
    def get_capabilities(self, process_id: str) -> List[Capability]:
        """Get all capabilities held by a process."""
        return self.capabilities.get(process_id, [])
    
    def can_access(self, process_id: str, target: str, perm: Permission) -> bool:
        """Check if a process can access a target with given permission."""
        caps = self.get_capabilities(process_id)
        return any(
            cap.target == target and cap.has_permission(perm)
            for cap in caps
        )


def check_no_ambient_authority(space: CapabilitySpace,
                               process_id: str,
                               requested_target: str,
                               requested_perm: Permission) -> Tuple[bool, ProofObject]:
    """Check that a process cannot access without holding appropriate capability.
    
    This is the core of capability security: no ambient authority.
    A process can only access a resource if it holds a capability for it.
    
    Args:
        space: The capability space
        process_id: Process requesting access
        requested_target: Resource being accessed
        requested_perm: Permission being requested
    
    Returns:
        (has_authority, proof)
    """
    caps = space.get_capabilities(process_id)
    
    has_cap = any(
        cap.target == requested_target and cap.has_permission(requested_perm)
        for cap in caps
    )
    
    proof = ProofObject(
        rule="NoAmbientAuthority",
        premises=[
            f"process={process_id}",
            f"target={requested_target}",
            f"permission={requested_perm.value}",
            f"held_capabilities={len(caps)}"
        ],
        conclusion=f"has_authority={has_cap}"
    )
    
    return has_cap, proof


def attenuate(cap: Capability,
              remove_permissions: FrozenSet[Permission]) -> Tuple[Capability, ProofObject]:
    """Create a new capability with reduced permissions.
    
    Attenuation is monotonic: permissions can only be removed, never added.
    This is the basis of authority attenuation (giving someone less power).
    
    Args:
        cap: Original capability
        remove_permissions: Permissions to remove
    
    Returns:
        (attenuated_cap, proof)
    """
    # New permissions = original minus removed
    new_perms = cap.permissions - remove_permissions
    
    # Record this attenuation
    attenuation_record = f"removed:{','.join(p.value for p in remove_permissions)}"
    new_attenuations = cap.attenuations + (attenuation_record,)
    
    new_cap = Capability(
        target=cap.target,
        permissions=frozenset(new_perms),
        attenuations=new_attenuations,
        delegator=cap.delegator
    )
    
    orig_perms_str = "{" + ",".join(p.value for p in cap.permissions) + "}"
    removed_str = "{" + ",".join(p.value for p in remove_permissions) + "}"
    new_perms_str = "{" + ",".join(p.value for p in new_perms) + "}"
    proof = ProofObject(
        rule="Attenuate",
        premises=[
            f"original_perms={orig_perms_str}",
            f"removed={removed_str}",
            f"new_perms={new_perms_str}"
        ],
        conclusion="attenuation applied (monotonic weakening)"
    )
    
    return new_cap, proof


def check_confinement(cap: Capability,
                     allowed_delegatees: FrozenSet[str]) -> Tuple[bool, ProofObject]:
    """Check if a capability respects confinement constraints.
    
    Confinement means the capability cannot be delegated outside
    a specified set of entities.
    
    Args:
        cap: Capability to check
        allowed_delegatees: Set of processes that can receive delegation
    
    Returns:
        (confined, proof)
    """
    # Check if capability has delegation permission
    if not cap.has_permission(Permission.DELEGATE):
        # Cannot be delegated, so trivially confined
        return True, ProofObject(
            rule="Confinement",
            premises=["capability has no DELEGATE permission"],
            conclusion="confined (cannot be delegated)"
        )
    
    # If delegable, check if delegator is in allowed set
    # (In a real system, we'd track delegation chains)
    delegator_allowed = cap.delegator in allowed_delegatees
    
    proof = ProofObject(
        rule="Confinement",
        premises=[
            f"delegator={cap.delegator}",
            f"allowed={allowed_delegatees}",
            f"delegator_allowed={delegator_allowed}"
        ],
        conclusion=f"confined={delegator_allowed}"
    )
    
    return delegator_allowed, proof


def check_least_authority(process_caps: List[Capability],
                         required_caps: List[Capability]) -> Tuple[bool, ProofObject]:
    """Check if a process holds no more capabilities than required (POLA).
    
    Principle of Least Authority: a process should only have the
    minimum capabilities needed to perform its function.
    
    Args:
        process_caps: Capabilities actually held
        required_caps: Capabilities needed for function
    
    Returns:
        (has_least_authority, proof)
        Note: Returns False if process has MORE than required
    """
    # Check if all required are present
    required_targets = {cap.target for cap in required_caps}
    process_targets = {cap.target for cap in process_caps}
    
    has_all_required = required_targets <= process_targets
    
    # Check if process has extra capabilities
    extra = process_targets - required_targets
    has_extra = len(extra) > 0
    
    # POLA: has all required AND no extras
    pola = has_all_required and not has_extra
    
    proof = ProofObject(
        rule="LeastAuthority",
        premises=[
            f"held={len(process_caps)}",
            f"required={len(required_caps)}",
            f"has_all_required={has_all_required}",
            f"extra_capabilities={extra}"
        ],
        conclusion=f"pola={pola}"
    )
    
    return pola, proof


def check_revocation(cap: Capability,
                    revocation_list: List[str]) -> Tuple[bool, ProofObject]:
    """Check if a capability has been revoked.
    
    Revocation is checked by target ID - if the target is in the
    revocation list, the capability is invalid.
    
    Args:
        cap: Capability to check
        revocation_list: List of revoked target IDs
    
    Returns:
        (is_revoked, proof)
    """
    is_revoked = cap.target in revocation_list
    
    proof = ProofObject(
        rule="Revocation",
        premises=[
            f"cap_target={cap.target}",
            f"revocation_list={revocation_list}"
        ],
        conclusion=f"is_revoked={is_revoked}"
    )
    
    return is_revoked, proof


@dataclass
class DelegationChain:
    """A chain of capability delegations."""
    capabilities: List[Capability] = field(default_factory=list)
    
    def is_valid(self) -> Tuple[bool, ProofObject]:
        """Check if delegation chain is valid.
        
        A valid chain:
        1. Each capability must have DELEGATE permission
        2. Target must be consistent (all for same resource)
        3. Permissions must monotonically decrease
        """
        if not self.capabilities:
            return True, ProofObject(
                rule="DelegationChain",
                premises=["empty chain"],
                conclusion="valid (empty)"
            )
        
        # Check 1: All must have DELEGATE permission (except last)
        for i, cap in enumerate(self.capabilities[:-1]):
            if not cap.has_permission(Permission.DELEGATE):
                return False, ProofObject(
                    rule="DelegationChain",
                    premises=[f"cap[{i}] lacks DELEGATE"],
                    conclusion="invalid (cannot delegate)"
                )
        
        # Check 2: Consistent target
        first_target = self.capabilities[0].target
        for cap in self.capabilities[1:]:
            if cap.target != first_target:
                return False, ProofObject(
                    rule="DelegationChain",
                    premises=["inconsistent targets"],
                    conclusion="invalid (target mismatch)"
                )
        
        # Check 3: Monotonically decreasing permissions
        prev_perms = self.capabilities[0].permissions
        for cap in self.capabilities[1:]:
            if not (cap.permissions <= prev_perms):
                return False, ProofObject(
                    rule="DelegationChain",
                    premises=["permissions not monotonically decreasing"],
                    conclusion="invalid (attenuation violated)"
                )
            prev_perms = cap.permissions
        
        return True, ProofObject(
            rule="DelegationChain",
            premises=[
                f"length={len(self.capabilities)}",
                f"target={first_target}"
            ],
            conclusion="valid"
        )


def check_compartmentalization(spaces: List[CapabilitySpace],
                               isolated_targets: Set[str]) -> Tuple[bool, ProofObject]:
    """Check if isolated targets are truly isolated (no cross-process access).
    
    Compartmentalization ensures sensitive resources are only accessible
    within their designated compartments.
    
    Args:
        spaces: List of capability spaces (one per compartment)
        isolated_targets: Set of targets that should be isolated
    
    Returns:
        (is_isolated, proof)
    """
    violations = []
    
    for space in spaces:
        for process_id, caps in space.capabilities.items():
            for cap in caps:
                if cap.target in isolated_targets:
                    # This process has access to an isolated target
                    # Check if this is allowed based on compartment policy
                    # (For now, we flag all cross-access as violation)
                    pass  # Would need compartment boundaries to check
    
    # Simplified: assume isolated means no other space has access
    all_targets_accessible = set()
    for space in spaces:
        for caps in space.capabilities.values():
            for cap in caps:
                all_targets_accessible.add(cap.target)
    
    isolation_violations = isolated_targets & all_targets_accessible
    # This is a placeholder - real implementation would check per-compartment
    
    is_isolated = len(isolation_violations) == 0
    
    proof = ProofObject(
        rule="Compartmentalization",
        premises=[
            f"compartments={len(spaces)}",
            f"isolated_targets={len(isolated_targets)}",
            f"violations={len(isolation_violations)}"
        ],
        conclusion=f"is_isolated={is_isolated}"
    )
    
    return is_isolated, proof
