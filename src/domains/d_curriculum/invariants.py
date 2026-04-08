"""D_CURRICULUM invariant checks — Curriculum Standards."""

from datetime import datetime
from fractions import Fraction
from src.domains.d_curriculum.implementation import (
    CurriculumStandard,
    Textbook,
    Assessment,
    AlignmentStatus,
    CurriculumComplianceChecker,
    SubjectArea,
    GradeLevel,
)


def check_standards_versioned() -> bool:
    """Invariant: State standards are enumerated, versioned, and hash-anchored."""
    checker = CurriculumComplianceChecker()
    
    standard = CurriculumStandard(
        standard_id="MATH-7-001",
        subject=SubjectArea.MATHEMATICS,
        grade_level=GradeLevel.GRADE_7,
        description="Solve linear equations",
        version="2024.1",
    )
    
    result = checker.verify_standard_format(standard)
    assert result["valid"] is True, "Standard should have valid format"
    assert result["has_version"] is True, "Standard must be versioned"
    assert result["has_id"] is True, "Standard must have ID"
    
    return True


def check_textbook_alignment_scored() -> bool:
    """Invariant: Textbook adoption is documented with alignment scores."""
    checker = CurriculumComplianceChecker()
    
    # Create aligned textbook
    aligned_textbook = Textbook(
        isbn="978-0-123456-78-9",
        title="Mathematics Grade 7",
        subject=SubjectArea.MATHEMATICS,
        alignment_score=Fraction(85, 100),
        alignment_status=AlignmentStatus.ALIGNED,
    )
    
    result = checker.check_textbook_adoption(aligned_textbook)
    assert result["alignment_documented"] is True, "Alignment must be documented"
    assert result["score"] >= 0.8, "Alignment score should be at least 80%"
    
    # Non-aligned should fail
    non_aligned = Textbook(
        isbn="978-0-987654-32-1",
        title="Unaligned Math",
        subject=SubjectArea.MATHEMATICS,
        alignment_score=Fraction(50, 100),
        alignment_status=AlignmentStatus.NOT_ALIGNED,
    )
    
    result2 = checker.check_textbook_adoption(non_aligned)
    assert result2["approved"] is False, "Non-aligned textbook should not be approved"
    
    return True


def check_assessment_verifiable() -> bool:
    """Invariant: Assessment alignment is verifiable against standards."""
    checker = CurriculumComplianceChecker()
    
    assessment = Assessment(
        assessment_id="TEST-001",
        subject=SubjectArea.MATHEMATICS,
        grade_level=GradeLevel.GRADE_7,
        aligned_standards=["MATH-7-001", "MATH-7-002"],
    )
    
    result = checker.verify_assessment_alignment(assessment)
    assert result["verifiable"] is True, "Assessment alignment must be verifiable"
    assert len(result["aligned_standards"]) > 0, "Must align to at least one standard"
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks."""
    results = {}
    
    checks = [
        ("standards_versioned", check_standards_versioned),
        ("textbook_alignment", check_textbook_alignment_scored),
        ("assessment_verifiable", check_assessment_verifiable),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results
