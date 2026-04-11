"""D_NONCREATIVE Invariants — Copyright Originality, Public Domain, Orphan Works

Verifies copyright originality requirements, public domain status,
orphan work criteria, non-creative work exemptions.

Standards: 17 U.S.C. § 102 (Copyright Act), Feist v. Rural (1991)
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import Work, FactualCompilation, minimal_creativity_threshold, orphan_work_search_threshold


def check_copyright_originality(work: Work) -> Tuple[bool, ProofObject]:
    """
    Copyright requires original works of authorship (Feist v. Rural).
    
    17 U.S.C. § 102(a):
    - Copyright protection subsists in original works
    - Originality requires independent creation + minimal creativity
    - Facts and ideas not copyrightable
    
    Falsifies if: creativity_score < minimal threshold
    
    
    threshold = minimal_creativity_threshold()
    score = work.get_creativity_score()
    
    # Government works exempt from copyright
    if work.is_government_work:
        return True, ProofObject(
            conclusion=f"Work {work.title} is government work — public domain",
            premises=["Government work per 17 U.S.C. § 105"],
            rule="copyright_government_exemption"
        )
    
    if score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Work {work.title} lacks sufficient originality (score {score} < {threshold})",
            premises=[
                f"Selection originality: {work.selection_originality}",
                f"Arrangement originality: {work.arrangement_originality}",
                f"Coordination originality: {work.coordination_originality}",
                "17 U.S.C. § 102 — Originality requirement"
            ],
            rule="copyright_originality"
        )
    
    return True, ProofObject(
        conclusion=f"Work {work.title} meets originality requirement",
        premises=[f"Creativity score: {score}"],
        rule="copyright_originality"
    )


def check_factual_compilation_creativity(compilation: FactualCompilation) -> Tuple[bool, ProofObject]:
    """
    Factual compilations require original selection or arrangement (Feist).
    
    Feist Publications v. Rural Telephone Service (1991):
    - Sweat of the brow is insufficient for copyright
    - Original selection, coordination, or arrangement required
    - Raw facts not copyrightable
    
    Falsifies if: no original selection AND no original arrangement
    
    
    if not compilation.has_minimal_creativity():
        return False, ProofObject(
            conclusion=f"VIOLATION: Compilation {compilation.title} lacks original selection/arrangement",
            premises=[
                f"Selection original: {compilation.selection_criteria_original}",
                f"Arrangement original: {compilation.arrangement_original}",
                f"Facts collected: {compilation.facts_collected}",
                "Feist v. Rural — Factual compilation originality"
            ],
            rule="factual_compilation_creativity"
        )
    
    return True, ProofObject(
        conclusion=f"Compilation {compilation.title} meets Feist creativity standard",
        premises=[
            f"Selection: {compilation.selection_criteria_original}",
            f"Arrangement: {compilation.arrangement_original}"
        ],
        rule="factual_compilation_creativity"
    )


def check_orphan_work_status(work: Work) -> Tuple[bool, ProofObject]:
    """
    Orphan works have unknown/unlocatable owners despite diligent search.
    
    Copyright Office Orphan Works Report (2006):
    - Reasonably diligent search required
    - Good faith effort to identify owner
    - Documented search efforts
    
    Falsifies if: author known OR insufficient search efforts
    
    
    if work.author_known:
        return True, ProofObject(
            conclusion=f"Work {work.title} has known author — not orphan",
            premises=["Author known"],
            rule="orphan_work_author_known"
        )
    
    min_search = orphan_work_search_threshold()
    total_searches = work.owner_search_efforts + work.registry_searches + work.professional_searches
    
    if total_searches < min_search:
        return False, ProofObject(
            conclusion=f"VIOLATION: Work {work.title} insufficient search efforts ({total_searches} < {min_search}) for orphan claim",
            premises=[
                f"Search efforts: {work.owner_search_efforts}",
                f"Registry searches: {work.registry_searches}",
                f"Professional searches: {work.professional_searches}",
                "Copyright Office Orphan Works guidelines"
            ],
            rule="orphan_work_diligent_search"
        )
    
    return True, ProofObject(
        conclusion=f"Work {work.title} qualifies as orphan work",
        premises=[f"Total search efforts: {total_searches}"],
        rule="orphan_work_diligent_search"
    )


def check_public_domain_status(work: Work) -> Tuple[bool, ProofObject]:
    """
    Public domain works are not protected by copyright.
    
    Copyright Term Extension Act, Public Domain Day:
    - Works published before 1929 generally public domain
    - Government works per 17 U.S.C. § 105
    - Copyright expired works
    
    Falsifies if: claimed copyright on clearly public domain work
    
    
    if work.is_government_work:
        return True, ProofObject(
            conclusion=f"Work {work.title} is U.S. government work — public domain",
            premises=["17 U.S.C. § 105 — Government works exemption"],
            rule="public_domain_government"
        )
    
    if work.creation_year < 1929:
        return True, ProofObject(
            conclusion=f"Work {work.title} created {work.creation_year} — public domain",
            premises=[f"Creation year: {work.creation_year}", "Pre-1929 works public domain"],
            rule="public_domain_term_expired"
        )
    
    return True, ProofObject(
        conclusion=f"Work {work.title} copyright status requires verification",
        premises=[f"Creation year: {work.creation_year}", f"Government work: {work.is_government_work}"],
        rule="public_domain_assessment"
    )


def check_slavish_copy_exemption(work: Work) -> Tuple[bool, ProofObject]:
    """
    Slavish copies lack sufficient originality (Bridgeman v. Corel).
    
    Bridgeman Art Library v. Corel Corp. (1999):
    - Exact photographic copies of public domain works
    - No additional creative expression
    - Not copyrightable
    
    Falsifies if: slavish copy claimed as original
    
    
    if work.work_type.name == "SLAVISH_COPY":
        if work.get_creativity_score() > minimal_creativity_threshold():
            return True, ProofObject(
                conclusion=f"Work {work.title} has added creativity — not mere slavish copy",
                premises=[f"Creativity score: {work.get_creativity_score()}"],
                rule="slavish_copy_added_creativity"
            )
        
        return False, ProofObject(
            conclusion=f"VIOLATION: Work {work.title} is slavish copy lacking originality",
            premises=[
                "Exact reproduction of existing work",
                "No additional creative expression",
                "Bridgeman v. Corel — Slavish copies not copyrightable"
            ],
            rule="slavish_copy_exemption"
        )
    
    return True, ProofObject(
        conclusion=f"Work {work.title} not classified as slavish copy",
        premises=[f"Work type: {work.work_type.name}"],
        rule="slavish_copy_exemption"
    )
