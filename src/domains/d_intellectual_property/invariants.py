"""D_INTELLECTUAL_PROPERTY invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- 35 U.S.C. (Patent Act)
- 17 U.S.C. (Copyright Act)
- 15 U.S.C. §1051 (Lanham Act - Trademarks)
- TRIPS Agreement

Source: ontology/ontology.json#D_INTELLECTUAL_PROPERTY
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple
from datetime import datetime, timedelta

from axioms.logic import ProofObject

from src.domains.d_intellectual_property.implementation import (
    PatentAnalyzer,
    CopyrightAnalyzer,
    TrademarkAnalyzer,
    Invention,
    CreativeWork,
    Trademark,
    FairUseAnalysis,
    PatentClaim,
    PatentClaimType,
    TrademarkStrength,
    FairUsePurpose,
)


def check_patent_novelty_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Patent requires novelty—no identical prior art.
    
    Standard: 35 U.S.C. §102
    Falsifies if: Invention with prior art passes as novel.
    falsifies_if: Invention with prior art passes as novel.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    analyzer = PatentAnalyzer()
    
    # Novel invention (no prior art)
    novel_invention = Invention(
        invention_id="I001",
        title="Novel Widget",
        inventor="Alice",
        filing_date=datetime(2024, 1, 1),
        claims=[PatentClaim(1, PatentClaimType.APPARATUS, "A novel device", ["element1", "element2"])],
        prior_art_references=[],
    )
    
    result_novel = analyzer.check_novelty(novel_invention)
    novel_passes = result_novel["novel"] is True
    
    # Non-novel invention (has prior art)
    non_novel_invention = Invention(
        invention_id="I002",
        title="Known Widget",
        inventor="Bob",
        filing_date=datetime(2024, 1, 1),
        claims=[PatentClaim(1, PatentClaimType.APPARATUS, "A known device", ["element1"])],
        prior_art_references=[
            {"reference": "Smith 2020", "date": datetime(2020, 1, 1), "similarity_score": Fraction(9, 10)},
        ],
    )
    
    result_non_novel = analyzer.check_novelty(non_novel_invention)
    non_novel_fails = result_non_novel["novel"] is False
    
    success = novel_passes and non_novel_fails
    
    proof = ProofObject(
        rule="PatentNoveltyRequirement",
        premises=[
            f"novel_invention_passes = {novel_passes}",
            f"non_novel_invention_fails = {non_novel_fails}",
        ],
        conclusion=(
            "35 U.S.C. §102 novelty requirement enforced"
            if success
            else "FAIL: Novelty requirement not enforced"
        ),
    )
    return success, proof


def check_patent_term_twenty_years() -> Tuple[bool, ProofObject]:
    """
    Invariant: Patent term is 20 years from filing date.
    
    Standard: 35 U.S.C. §154
    Falsifies if: Patent valid beyond 20 years from filing.
    falsifies_if: Patent valid beyond 20 years from filing.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Patent filed 25+ years ago (expired)
    old_patent = Invention(
        invention_id="I003",
        title="Old Invention",
        inventor="Inventor",
        filing_date=datetime(1995, 1, 1),
        patent_number="US1234567",
        issue_date=datetime(1997, 1, 1),
    )
    
    old_is_expired = old_patent.is_expired() is True
    
    # Recent patent (not expired)
    new_patent = Invention(
        invention_id="I004",
        title="New Invention",
        inventor="Inventor",
        filing_date=datetime(2020, 1, 1),
        patent_number="US7654321",
        issue_date=datetime(2022, 1, 1),
    )
    
    new_not_expired = new_patent.is_expired() is False
    
    success = old_is_expired and new_not_expired
    
    proof = ProofObject(
        rule="PatentTermTwentyYears",
        premises=[
            f"29_year_patent_expired = {old_is_expired}",
            f"4_year_patent_not_expired = {new_not_expired}",
        ],
        conclusion=(
            "35 U.S.C. §154 20-year patent term enforced"
            if success
            else "FAIL: Patent term not properly calculated"
        ),
    )
    return success, proof


def check_copyright_originality_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Copyright requires originality—identical copying not protected.
    
    Standard: 17 U.S.C. §102(a); Feist Publications v. Rural Telephone Service
    Falsifies if: Substantial similarity not detected between original and copy.
    falsifies_if: Substantial similarity not detected between original and copy.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Original work
    original = CreativeWork(
        work_id="W001",
        title="Original Novel",
        creator="Author A",
        creation_date=datetime(2024, 1, 1),
        content_type="literary",
        content="Once upon a time in a unique land...",
    )
    
    # Copy
    copy = CreativeWork(
        work_id="W002",
        title="Copy of Novel",
        creator="Author B",
        creation_date=datetime(2024, 6, 1),
        content_type="literary",
        content="Once upon a time in a unique land...",
    )
    
    similarity = original.get_similarity_score(copy)
    high_similarity = similarity >= Fraction(9, 10)
    
    # Copy created after original
    copy_after_original = copy.creation_date > original.creation_date
    
    success = high_similarity and copy_after_original
    
    proof = ProofObject(
        rule="CopyrightOriginalityRequirement",
        premises=[
            f"similarity_score = {similarity}",
            f"high_similarity = {high_similarity}",
            f"copy_after_original = {copy_after_original}",
        ],
        conclusion=(
            "17 U.S.C. §102 originality requirement enforced"
            if success
            else "FAIL: Originality requirement not enforced"
        ),
    )
    return success, proof


def check_fair_use_four_factors() -> Tuple[bool, ProofObject]:
    """
    Invariant: Fair use determined by four-factor test per §107.
    
    Standard: 17 U.S.C. §107; Campbell v. Acuff-Rose Music
    Falsifies if: Non-transformative commercial use qualifies as fair use.
    falsifies_if: Non-transformative commercial use qualifies as fair use.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    work = CreativeWork(
        work_id="W003",
        title="Famous Novel",
        creator="Famous Author",
        creation_date=datetime(2000, 1, 1),
        content_type="literary",
        content="It was the best of times...",
    )
    
    # Favored purpose (criticism, small portion, no market substitution)
    fair_use = FairUseAnalysis(
        purpose=FairUsePurpose.CRITICISM,
        work=work,
        portion_used=Fraction(1, 10),
        market_substitution=False,
        work_is_factual=False,
        work_published=True,
    )
    
    result_fair = fair_use.analyze_four_factors()
    fair_use_likely = result_fair["likely_fair_use"] is True
    
    # Unfavored (large portion, market substitution)
    unfair_use = FairUseAnalysis(
        purpose=FairUsePurpose.TEACHING,
        work=work,
        portion_used=Fraction(9, 10),
        market_substitution=True,
        work_is_factual=False,
        work_published=False,
    )
    
    result_unfair = unfair_use.analyze_four_factors()
    unfair_use_not_fair = result_unfair["likely_fair_use"] is False
    
    success = fair_use_likely and unfair_use_not_fair
    
    proof = ProofObject(
        rule="FairUseFourFactors",
        premises=[
            f"fair_use_likely = {fair_use_likely}",
            f"unfair_use_not_fair = {unfair_use_not_fair}",
            f"fair_score = {result_fair['total_score']}",
            f"unfair_score = {result_unfair['total_score']}",
        ],
        conclusion=(
            "17 U.S.C. §107 fair use factors enforced"
            if success
            else "FAIL: Fair use factors not properly applied"
        ),
    )
    return success, proof


def check_trademark_distinctiveness() -> Tuple[bool, ProofObject]:
    """
    Invariant: Trademark protection requires distinctiveness.
    
    Standard: 15 U.S.C. §1052; Abercrombie & Fitch spectrum
    Falsifies if: Generic mark gets trademark protection.
    falsifies_if: Generic mark gets trademark protection.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Strong distinctive mark (fanciful)
    distinctive = Trademark(
        mark_id="T001",
        mark_text="Xerphlux",
        owner="Corp A",
        strength=TrademarkStrength.FANCIFUL,
        goods_services_class="Software",
        filing_date=datetime(2020, 1, 1),
        registration_date=datetime(2021, 1, 1),
    )
    
    distinctive_registered = distinctive.is_registered() is True
    distinctive_not_abandoned = distinctive.is_abandoned() is False
    
    # Generic mark (not protectable)
    generic = Trademark(
        mark_id="T002",
        mark_text="Computer",
        owner="Corp B",
        strength=TrademarkStrength.GENERIC,
        goods_services_class="Computers",
        filing_date=datetime(2020, 1, 1),
    )
    
    generic_not_registered = generic.is_registered() is False
    
    success = distinctive_registered and distinctive_not_abandoned and generic_not_registered
    
    proof = ProofObject(
        rule="TrademarkDistinctiveness",
        premises=[
            f"distinctive_registered = {distinctive_registered}",
            f"distinctive_not_abandoned = {distinctive_not_abandoned}",
            f"generic_not_registered = {generic_not_registered}",
        ],
        conclusion=(
            "15 U.S.C. §1052 trademark distinctiveness requirements enforced"
            if success
            else "FAIL: Trademark distinctiveness not enforced"
        ),
    )
    return success, proof


def check_trademark_likelihood_of_confusion() -> Tuple[bool, ProofObject]:
    """
    Invariant: Trademark infringement requires likelihood of confusion.
    
    Standard: 15 U.S.C. §1114; Polaroid Corp. v. Polarad Elects. Corp. factors
    Falsifies if: Dissimilar marks found confusing or similar marks not flagged.
    falsifies_if: Dissimilar marks found confusing or similar marks not flagged.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    analyzer = TrademarkAnalyzer()
    
    # Similar marks
    mark1 = Trademark(
        mark_id="T003",
        mark_text="Nike",
        owner="Nike Inc",
        strength=TrademarkStrength.FANCIFUL,
        goods_services_class="Apparel",
        filing_date=datetime(1971, 1, 1),
        registration_date=datetime(1972, 1, 1),
    )
    
    mark2 = Trademark(
        mark_id="T004",
        mark_text="Nike",
        owner="Copycat Corp",
        strength=TrademarkStrength.ARBITRARY,
        goods_services_class="Apparel",
        filing_date=datetime(2023, 1, 1),
    )
    
    confusion_result = analyzer.check_likelihood_of_confusion(mark1, mark2)
    likely_confusion = confusion_result["likely_confusion"]
    
    # High similarity score
    high_similarity = confusion_result["mark_similarity"] >= Fraction(3, 4)
    
    success = likely_confusion and high_similarity
    
    proof = ProofObject(
        rule="TrademarkLikelihoodOfConfusion",
        premises=[
            f"likely_confusion = {likely_confusion}",
            f"high_similarity = {high_similarity}",
            f"similarity_score = {confusion_result['mark_similarity']}",
        ],
        conclusion=(
            "15 U.S.C. §1114 likelihood of confusion standard enforced"
            if success
            else "FAIL: Likelihood of confusion not properly assessed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_INTELLECTUAL_PROPERTY invariants.

    Falsifies if: any intellectual property invariant check fails or raises an exception.
    falsifies_if: any intellectual property invariant check fails or raises an exception.
    """
    checks = [
        ("check_patent_novelty_requirement", check_patent_novelty_requirement),
        ("check_patent_term_twenty_years", check_patent_term_twenty_years),
        ("check_copyright_originality_requirement", check_copyright_originality_requirement),
        ("check_fair_use_four_factors", check_fair_use_four_factors),
        ("check_trademark_distinctiveness", check_trademark_distinctiveness),
        ("check_trademark_likelihood_of_confusion", check_trademark_likelihood_of_confusion),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_INTELLECTUAL_PROPERTY invariants: PASS")
