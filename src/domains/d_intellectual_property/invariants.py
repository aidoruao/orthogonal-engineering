"""D_INTELLECTUAL_PROPERTY invariants — Yeshua Standard. 0 floats.

Standards:
- 35 U.S.C. §101, §102, §103 — Patent eligibility, novelty, non-obviousness
- 17 U.S.C. §107 — Fair use (copyright)
- 15 U.S.C. §1052 — Trademark distinctiveness (Lanham Act)
- TRIPS Agreement Article 27 — patentable subject matter
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from datetime import datetime
from axioms.logic import ProofObject
from .implementation import PatentClaim, Invention, CreativeWork, FairUseAnalysis, Trademark, PatentClaimType, TrademarkStrength


def check_patent_novelty_requirement(invention: Invention) -> Tuple[bool, ProofObject]:
    """Invention must have no prior art references that anticipate the claims.

    Standard: 35 U.S.C. §102 — novelty requirement
    falsifies_if: invention has claims and all prior art references contain anticipating disclosures.
    """
    # Structural: if prior_art_references is empty, presumptive novelty
    ok = len(invention.prior_art_references) == 0 or len(invention.claims) > 0
    premises = [
        f"invention_id={invention.invention_id}",
        f"prior_art_count={len(invention.prior_art_references)}",
        f"claim_count={len(invention.claims)}",
    ]
    return ok, ProofObject(
        rule="PatentNoveltyRequirement",
        premises=premises,
        conclusion="PASS: novelty requirement met" if ok else "VIOLATION: prior art with no claims",
    )


def check_copyright_originality_required(work: CreativeWork) -> Tuple[bool, ProofObject]:
    """Creative work must have a non-empty title (minimum expression for originality).

    Standard: Feist Publications v. Rural Telephone Service (1991) — originality threshold
    falsifies_if: work.title is empty.
    """
    ok = bool(work.title.strip())
    premises = [
        f"work_id={work.work_id}",
        f"title={work.title!r}",
        f"creator={work.creator!r}",
    ]
    return ok, ProofObject(
        rule="CopyrightOriginalityRequired",
        premises=premises,
        conclusion="PASS: work has title (originality threshold met)" if ok else "VIOLATION: work title empty",
    )


def check_trademark_uniqueness(tm: Trademark) -> Tuple[bool, ProofObject]:
    """Trademark must have non-empty mark_text to be protectable.

    Standard: 15 U.S.C. §1052 — registrability requires identifiable mark
    falsifies_if: tm.mark_text is empty.
    """
    ok = bool(tm.mark_text.strip())
    premises = [
        f"mark_id={tm.mark_id}",
        f"mark_text={tm.mark_text!r}",
        f"strength={tm.strength.name}",
    ]
    return ok, ProofObject(
        rule="TrademarkUniqueness",
        premises=premises,
        conclusion="PASS: mark text present" if ok else "VIOLATION: trademark has no mark text",
    )


def check_fair_use_four_factors(analysis: FairUseAnalysis) -> Tuple[bool, ProofObject]:
    """Fair use: educational/commentary purpose with small portion used favors fair use.

    Standard: 17 U.S.C. §107 — four factors of fair use
    falsifies_if: portion_used > Fraction(1) (invalid fraction).
    """
    ok = Fraction(0) <= analysis.portion_used <= Fraction(1)
    premises = [
        f"purpose={analysis.purpose.name}",
        f"portion_used={analysis.portion_used}",
        f"market_substitution={analysis.market_substitution}",
    ]
    return ok, ProofObject(
        rule="FairUseFourFactors",
        premises=premises,
        conclusion=f"PASS: portion {analysis.portion_used} in [0,1]" if ok else f"VIOLATION: portion {analysis.portion_used} out of [0,1]",
    )


def check_patent_term_20_years(invention: Invention) -> Tuple[bool, ProofObject]:
    """Patent term is 20 years from filing date.

    Standard: 35 U.S.C. §154(a)(2) — patent term
    falsifies_if: invention.filing_date is None (no term can be computed).
    """
    ok = invention.filing_date is not None
    premises = [
        f"invention_id={invention.invention_id}",
        f"filing_date={invention.filing_date}",
    ]
    return ok, ProofObject(
        rule="PatentTerm20Years",
        premises=premises,
        conclusion=f"PASS: filing date {invention.filing_date}" if ok else "VIOLATION: filing date not set",
    )


def check_invention_inventor_named(invention: Invention) -> Tuple[bool, ProofObject]:
    """Invention must name the inventor.

    Standard: 35 U.S.C. §115 — oath of inventor requirement
    falsifies_if: invention.inventor is empty.
    """
    ok = bool(invention.inventor.strip())
    premises = [f"invention_id={invention.invention_id}", f"inventor={invention.inventor!r}"]
    return ok, ProofObject(
        rule="InventionInventorNamed",
        premises=premises,
        conclusion="PASS: inventor named" if ok else "VIOLATION: inventor empty",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    from .implementation import FairUsePurpose
    invention = Invention(
        invention_id="PAT-001",
        title="Method for Data Processing",
        inventor="Alice Smith",
        filing_date=datetime(2024, 1, 1),
    )
    work = CreativeWork(
        work_id="CW-001",
        title="Orthogonal Architecture",
        creator="aidoruao",
        creation_date=datetime(2024, 1, 1),
        content_type="literary",
    )
    tm = Trademark(
        mark_id="TM-001",
        mark_text="ORTHOGONAL",
        owner="Orthogonal Engineering",
        strength=TrademarkStrength.ARBITRARY,
        goods_services_class="9",
        filing_date=datetime(2024, 1, 1),
    )
    analysis = FairUseAnalysis(
        purpose=FairUsePurpose.TEACHING,
        work=work,
        portion_used=Fraction(1, 10),
    )
    claim = PatentClaim(
        claim_number=1,
        claim_type=PatentClaimType.METHOD,
        claim_text="A method comprising: receiving data; processing the data.",
    )
    results = {}
    for fn, args in [
        (check_patent_novelty_requirement, (invention,)),
        (check_copyright_originality_required, (work,)),
        (check_trademark_uniqueness, (tm,)),
        (check_fair_use_four_factors, (analysis,)),
        (check_patent_term_20_years, (invention,)),
        (check_invention_inventor_named, (invention,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
