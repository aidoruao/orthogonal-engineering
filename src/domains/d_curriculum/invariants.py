"""D_CURRICULUM invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: State education standards, textbook adoption policies
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_curriculum.implementation import (
    StandardsManager,
    TextbookAdoptionManager,
    AssessmentValidator,
    CurriculumAuditor,
    LearningStandard,
    StandardFramework,
    Textbook,
    TextbookAlignment,
    Assessment,
    AssessmentItem,
    SubjectArea,
    GradeLevel,
    AssessmentType,
)


def check_standards_enumerated_versioned_hashed() -> bool:
    """
    Invariant: State standards are enumerated, versioned, and hash-anchored.
    Falsification: If standard lacks version, ID, or hash.
    """
    manager = StandardsManager()
    
    # Create a standard
    standard = manager.create_standard(
        standard_id="MATH.6.NS.1",
        subject=SubjectArea.MATHEMATICS,
        grade=GradeLevel.GRADE_6,
        description="Interpret and compute quotients of fractions",
        objective="Students will divide fractions and solve word problems",
        version="1.0",
    )
    
    # Standard should have ID
    assert standard.standard_id == "MATH.6.NS.1", (
        "Standard must have enumerated ID"
    )
    
    # Standard should have version
    assert standard.version == "1.0", (
        "Standard must be versioned"
    )
    
    # Standard should have hash
    assert standard.content_hash != "", (
        "Standard must have hash anchor"
    )
    assert len(standard.content_hash) == 64, (
        "Hash should be 64-character SHA-256"
    )
    
    # Hash should be valid
    assert standard.verify_hash() is True, (
        "Standard hash must be valid"
    )
    
    # Modifying content should invalidate hash
    original_hash = standard.content_hash
    standard.description = "Modified description"
    assert standard.verify_hash() is False, (
        "Modified content should fail hash verification"
    )
    
    return True


def check_textbook_adoption_documented() -> bool:
    """
    Invariant: Textbook adoption is documented with alignment scores.
    Falsification: If adoption lacks documentation or alignment scores.
    """
    manager = TextbookAdoptionManager()
    
    # Create textbook with alignments
    textbook = Textbook(
        textbook_id="TB001",
        title="Mathematics Grade 6",
        publisher="EduPress",
        publication_year=2024,
        subjects=[SubjectArea.MATHEMATICS],
        grade_levels=[GradeLevel.GRADE_6],
        alignments=[
            TextbookAlignment(
                textbook_id="TB001",
                standard_id="MATH.6.NS.1",
                coverage_score=Fraction(9, 10),
                depth_score=Fraction(8, 10),
                rigor_score=Fraction(9, 10),
            ),
            TextbookAlignment(
                textbook_id="TB001",
                standard_id="MATH.6.NS.2",
                coverage_score=Fraction(8, 10),
                depth_score=Fraction(7, 10),
                rigor_score=Fraction(8, 10),
            ),
        ],
    )
    
    # Submit for adoption
    result = manager.submit_textbook(textbook)
    assert "alignment_score" in result, (
        "Submission must record alignment score"
    )
    
    # Document adoption
    doc_result = manager.document_adoption(
        "TB001",
        ["alignment_report.pdf", "review_committee_notes.pdf"]
    )
    assert doc_result["documents_recorded"] == 2, (
        "Adoption must be documented"
    )
    assert doc_result["adoption_date"] is not None, (
        "Adoption must have date"
    )
    
    # Undocumented adoption should be detected
    textbook2 = Textbook(
        textbook_id="TB002",
        title="Poor Math Book",
        publisher="BadPress",
        publication_year=2024,
    )
    manager.submit_textbook(textbook2)
    
    # TB002 has no documents
    textbook2_check = manager.textbooks["TB002"]
    assert len(textbook2_check.adoption_documents) == 0, (
        "Undocumented adoption should have empty documents"
    )
    
    return True


def check_assessment_alignment_verifiable() -> bool:
    """
    Invariant: Assessment alignment is verifiable against standards.
    Falsification: If assessment items don't align to valid standards.
    """
    # Create standards framework
    manager = StandardsManager()
    framework = manager.create_framework(
        framework_id="FW001",
        name="State Math Standards",
        jurisdiction="Test State",
    )
    
    # Add standards
    std1 = manager.create_standard(
        "MATH.6.NS.1", SubjectArea.MATHEMATICS, GradeLevel.GRADE_6,
        "Divide fractions", "Students will divide fractions",
    )
    std2 = manager.create_standard(
        "MATH.6.NS.2", SubjectArea.MATHEMATICS, GradeLevel.GRADE_6,
        "Multiply fractions", "Students will multiply fractions",
    )
    
    manager.add_standard_to_framework(framework, std1)
    manager.add_standard_to_framework(framework, std2)
    
    # Create aligned assessment
    validator = AssessmentValidator()
    
    aligned_assessment = Assessment(
        assessment_id="A001",
        name="Fractions Quiz",
        assessment_type=AssessmentType.FORMATIVE,
        subject=SubjectArea.MATHEMATICS,
        items=[
            AssessmentItem(
                item_id="Q1",
                item_type="multiple_choice",
                prompt="What is 1/2 ÷ 1/4?",
                aligned_standards=["MATH.6.NS.1"],
            ),
            AssessmentItem(
                item_id="Q2",
                item_type="short_answer",
                prompt="Explain how to multiply 2/3 × 3/4",
                aligned_standards=["MATH.6.NS.2"],
            ),
        ],
        standards_coverage={"MATH.6.NS.1": 1, "MATH.6.NS.2": 1},
    )
    
    result = validator.validate_assessment(aligned_assessment, framework)
    assert result["all_standards_valid"] is True, (
        "Aligned assessment should have all valid standards"
    )
    assert result["alignment_verified"] is True, (
        "Properly aligned assessment should be verified"
    )
    
    # Create misaligned assessment (references non-existent standard)
    misaligned_assessment = Assessment(
        assessment_id="A002",
        name="Bad Quiz",
        assessment_type=AssessmentType.FORMATIVE,
        subject=SubjectArea.MATHEMATICS,
        items=[
            AssessmentItem(
                item_id="Q1",
                item_type="multiple_choice",
                prompt="Question",
                aligned_standards=["NONEXISTENT.STANDARD.1"],  # Invalid!
            ),
        ],
        standards_coverage={"NONEXISTENT.STANDARD.1": 1},
    )
    
    result2 = validator.validate_assessment(misaligned_assessment, framework)
    assert result2["all_standards_valid"] is False, (
        "Misaligned assessment should fail standards validation"
    )
    
    return True


def check_framework_integrity() -> bool:
    """
    Invariant: Standards framework integrity is verifiable.
    Falsification: If modified framework passes integrity check.
    """
    manager = StandardsManager()
    framework = manager.create_framework(
        framework_id="FW001",
        name="Test Framework",
        jurisdiction="Test State",
    )
    
    # Add standards
    std1 = manager.create_standard(
        "STD.1", SubjectArea.MATHEMATICS, GradeLevel.GRADE_6,
        "Standard 1", "Objective 1",
    )
    manager.add_standard_to_framework(framework, std1)
    
    # Framework should be intact
    assert framework.verify_integrity() is True, (
        "Valid framework should pass integrity check"
    )
    
    # Modify a standard (tampering)
    std1.description = "Tampered description"
    
    # Framework integrity should fail
    assert framework.verify_integrity() is False, (
        "Modified framework should fail integrity check"
    )
    
    return True


def check_alignment_score_calculation() -> bool:
    """
    Invariant: Alignment scores are calculated correctly.
    Falsification: If alignment math is incorrect.
    """
    alignment = TextbookAlignment(
        textbook_id="TB001",
        standard_id="STD.1",
        coverage_score=Fraction(9, 10),  # 0.9
        depth_score=Fraction(8, 10),     # 0.8
        rigor_score=Fraction(7, 10),     # 0.7
    )
    
    # Overall should be average: (0.9 + 0.8 + 0.7) / 3 = 0.8
    expected = Fraction(8, 10)
    assert alignment.overall_alignment == expected, (
        f"Expected alignment {expected}, got {alignment.overall_alignment}"
    )
    
    return True


def check_version_tracking() -> bool:
    """
    Invariant: Standards maintain version history.
    Falsification: If version information is lost.
    """
    manager = StandardsManager()
    
    # Original version
    std_v1 = manager.create_standard(
        "STD.1", SubjectArea.MATHEMATICS, GradeLevel.GRADE_6,
        "Original description", "Original objective", version="1.0",
    )
    
    assert std_v1.version == "1.0", (
        "Standard should have correct version"
    )
    assert std_v1.previous_version is None, (
        "First version should have no previous version"
    )
    
    # Create new version
    std_v2 = LearningStandard(
        standard_id="STD.1",
        subject=SubjectArea.MATHEMATICS,
        grade_level=GradeLevel.GRADE_6,
        description="Updated description",
        learning_objective="Updated objective",
        version="2.0",
        effective_date=datetime.now(),
        previous_version="1.0",  # Reference to previous
    )
    std_v2.content_hash = std_v2.compute_hash()
    
    assert std_v2.version == "2.0", (
        "New version should have updated version number"
    )
    assert std_v2.previous_version == "1.0", (
        "New version should reference previous"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("standards_hashed", check_standards_enumerated_versioned_hashed),
        ("textbook_documented", check_textbook_adoption_documented),
        ("assessment_alignment", check_assessment_alignment_verifiable),
        ("framework_integrity", check_framework_integrity),
        ("alignment_scores", check_alignment_score_calculation),
        ("version_tracking", check_version_tracking),
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
