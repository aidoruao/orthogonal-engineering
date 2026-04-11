#!/usr/bin/env python3
"""
Tech YouTuber Audits Subpackage

Contains audit entries for technology-focused YouTube channels.
"""

from .linus_tech_tips import (
    LTT_AUDITS,
    get_ltt_audits,
    get_ltt_stats,
    ComplaintAudit,
    AuditStatus,
)

from .gamers_nexus import (
    GN_AUDITS,
    get_gn_audits,
    get_gn_stats,
)

from .mental_outlaw import (
    MO_AUDITS,
    get_mo_audits,
    get_mo_stats,
)

from .the_hated_one import (
    THO_AUDITS,
    get_tho_audits,
    get_tho_stats,
)

__all__ = [
    # Linus Tech Tips
    "LTT_AUDITS",
    "get_ltt_audits",
    "get_ltt_stats",
    # Gamers Nexus
    "GN_AUDITS",
    "get_gn_audits",
    "get_gn_stats",
    # Mental Outlaw
    "MO_AUDITS",
    "get_mo_audits",
    "get_mo_stats",
    # The Hated One
    "THO_AUDITS",
    "get_tho_audits",
    "get_tho_stats",
    # Shared
    "ComplaintAudit",
    "AuditStatus",
]
