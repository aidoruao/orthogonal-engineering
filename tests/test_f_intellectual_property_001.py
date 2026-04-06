"""Falsification tests for D_INTELLECTUAL_PROPERTY"""
from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_intellectual_property import (
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
    check_patent_novelty_requirement,
    check_copyright_originality_required,
    check_trademark_uniqueness,
    check_fair_use_four_factors,
)


def test_patent_novelty_requirement():
    """Patent requires novelty (no prior art)."""
    result = check_patent_novelty_requirement()
    assert result is True


def test_copyright_originality():
    """Copyright requires originality."""
    result = check_copyright_originality_required()
    assert result is True


def test_trademark_uniqueness():
    """Trademark requires distinctiveness."""
    result = check_trademark_uniqueness()
    assert result is True


def test_fair_use_factors():
    """Fair use determined by four factors."""
    result = check_fair_use_four_factors()
    assert result is True


def test_patent_novelty_check():
    """Novel invention passes novelty check."""
    analyzer = PatentAnalyzer()
    
    invention = Invention(
        invention_id="I001",
        title="Novel Widget",
        inventor="Alice",
        filing_date=datetime(2024, 1, 1),
        claims=[PatentClaim(1, PatentClaimType.APPARATUS, "A novel device", ["A", "B"])],
        prior_art_references=[],
    )
    
    result = analyzer.check_novelty(invention)
    assert result["novel"] is True


def test_patent_non_novelty_check():
    """Invention with prior art fails novelty check."""
    analyzer = PatentAnalyzer()
    
    invention = Invention(
        invention_id="I002",
        title="Known Widget",
        inventor="Bob",
        filing_date=datetime(2024, 1, 1),
        claims=[PatentClaim(1, PatentClaimType.APPARATUS, "A device", ["A"])],
        prior_art_references=[
            {"reference": "Smith 2020", "date": datetime(2020, 1, 1), "similarity_score": 0.9},
        ],
    )
    
    result = analyzer.check_novelty(invention)
    assert result["novel"] is False


def test_copyright_substantial_similarity():
    """Copyright infringement requires substantial similarity."""
    analyzer = CopyrightAnalyzer()
    
    work1 = CreativeWork(
        work_id="W001",
        title="Original",
        creator="Author A",
        creation_date=datetime(2020, 1, 1),
        content_type="literary",
        content="The quick brown fox jumps over the lazy dog",
    )
    
    work2 = CreativeWork(
        work_id="W002",
        title="Copy",
        creator="Author B",
        creation_date=datetime(2021, 1, 1),
        content_type="literary",
        content="The quick brown fox jumps over the lazy dog",
    )
    
    result = analyzer.check_substantial_similarity(work1, work2)
    assert result["substantially_similar"] is True


def test_trademark_distinctiveness():
    """Distinctive marks are protectable, generic are not."""
    distinctive = Trademark(
        mark_id="T001",
        mark_text="Kodak",
        owner="Corp A",
        strength=TrademarkStrength.FANCIFUL,
        goods_services_class="Cameras",
        filing_date=datetime(2020, 1, 1),
        registration_date=datetime(2021, 1, 1),
    )
    
    generic = Trademark(
        mark_id="T002",
        mark_text="Camera",
        owner="Corp B",
        strength=TrademarkStrength.GENERIC,
        goods_services_class="Cameras",
        filing_date=datetime(2020, 1, 1),
    )
    
    assert distinctive.is_registered() is True
    assert generic.is_registered() is False


def test_fair_use_criticism():
    """Criticism with small portion is fair use."""
    work = CreativeWork(
        work_id="W003",
        title="Famous Book",
        creator="Famous Author",
        creation_date=datetime(2000, 1, 1),
        content_type="literary",
    )
    
    analysis = FairUseAnalysis(
        purpose=FairUsePurpose.CRITICISM,
        work=work,
        portion_used=Fraction(1, 10),
        market_substitution=False,
    )
    
    result = analysis.analyze_four_factors()
    assert result["likely_fair_use"] is True


def test_not_fair_use():
    """Commercial copying with market harm is not fair use."""
    work = CreativeWork(
        work_id="W004",
        title="Famous Book",
        creator="Famous Author",
        creation_date=datetime(2000, 1, 1),
        content_type="literary",
    )
    
    analysis = FairUseAnalysis(
        purpose=FairUsePurpose.TEACHING,
        work=work,
        portion_used=Fraction(9, 10),  # Large portion
        market_substitution=True,  # Harms market
        work_published=False,  # Unpublished
    )
    
    result = analysis.analyze_four_factors()
    assert result["likely_fair_use"] is False


def test_patent_term_expiration():
    """Patent expires after 20 years."""
    old_patent = Invention(
        invention_id="I003",
        title="Old Invention",
        inventor="Inventor",
        filing_date=datetime(1995, 1, 1),
        patent_number="US1234567",
    )
    
    assert old_patent.is_expired() is True
    
    new_patent = Invention(
        invention_id="I004",
        title="New Invention",
        inventor="Inventor",
        filing_date=datetime(2020, 1, 1),
        patent_number="US7654321",
    )
    
    assert new_patent.is_expired() is False


if __name__ == "__main__":
    test_patent_novelty_requirement()
    test_copyright_originality()
    test_trademark_uniqueness()
    test_fair_use_factors()
    test_patent_novelty_check()
    test_patent_non_novelty_check()
    test_copyright_substantial_similarity()
    test_trademark_distinctiveness()
    test_fair_use_criticism()
    test_not_fair_use()
    test_patent_term_expiration()
    print("All D_INTELLECTUAL_PROPERTY tests: PASS")
