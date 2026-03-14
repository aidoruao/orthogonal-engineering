#!/usr/bin/env python3
"""
Tests for GLOBAL_SYSTEMIC_REPAIR_SCHEMA.yaml

Validates the schema structure, coverage, and integrity of systemic repair specifications.

Authority: Systems Architecture Layer
Standard: Yeshua
"""

import sys
from pathlib import Path
import yaml
import hashlib

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def schema():
    """Load the Global Systemic Repair Schema."""
    schema_path = Path(__file__).parent.parent / "GLOBAL_SYSTEMIC_REPAIR_SCHEMA.yaml"
    with open(schema_path) as f:
        return yaml.safe_load(f)


def test_schema_file_exists():
    """Test that the schema file exists."""
    schema_path = Path(__file__).parent.parent / "GLOBAL_SYSTEMIC_REPAIR_SCHEMA.yaml"
    assert schema_path.exists(), "GLOBAL_SYSTEMIC_REPAIR_SCHEMA.yaml not found"


def test_schema_metadata(schema):
    """Test schema metadata is correct."""
    assert schema["schema_name"] == "GLOBAL_SYSTEMIC_REPAIR_SCHEMA"
    assert schema["schema_version"] == "1.0.0"
    assert schema["authority"] == "Systems Architecture Layer"
    assert schema["standard"] == "Yeshua"


def test_schema_principles_defined(schema):
    """Test that all core principles are defined."""
    assert "principles" in schema
    principles = schema["principles"]
    
    required_principles = [
        "glass_box",
        "determinism",
        "idempotency",
        "cryptographic_traceability",
        "yeshua_standard"
    ]
    
    for principle in required_principles:
        assert principle in principles, f"Missing principle: {principle}"
        assert "description" in principles[principle]


def test_hashing_configuration(schema):
    """Test hashing configuration is defined."""
    assert "hashing" in schema
    hashing = schema["hashing"]
    
    assert hashing["algorithm"] == "sha256"
    assert hashing["structure"] == "merkle_chain"
    assert "scope" in hashing


def test_record_structure_defined(schema):
    """Test that record structure is properly defined."""
    assert "record_structure" in schema
    structure = schema["record_structure"]
    
    required_fields = ["id", "domain", "problem", "root_cause", "impact", 
                      "remediation_spec", "verification", "hash"]
    
    for field in required_fields:
        assert field in structure, f"Missing field: {field}"


def test_systemic_issues_exist(schema):
    """Test that systemic issues are enumerated."""
    assert "systemic_issues" in schema
    issues = schema["systemic_issues"]
    
    assert isinstance(issues, list)
    assert len(issues) >= 100, f"Expected at least 100 issues, found {len(issues)}"


def test_issue_structure_compliance(schema):
    """Test that all issues follow the defined structure."""
    issues = schema["systemic_issues"]
    
    required_fields = ["id", "domain", "problem", "root_cause", "impact", 
                      "remediation_spec", "verification"]
    
    for issue in issues:
        for field in required_fields:
            assert field in issue, f"Issue {issue.get('id', 'UNKNOWN')} missing field: {field}"
        
        # Check remediation_spec structure
        assert "deterministic_actions" in issue["remediation_spec"]
        assert isinstance(issue["remediation_spec"]["deterministic_actions"], list)
        
        # Check verification structure
        assert "automated_tests" in issue["verification"]
        assert isinstance(issue["verification"]["automated_tests"], list)


def test_domain_coverage(schema):
    """Test that all expected domains are covered."""
    issues = schema["systemic_issues"]
    
    expected_domains = [
        "software_engineering",
        "ai_systems",
        "cybersecurity",
        "healthcare",
        "finance",
        "infrastructure",
        "environment",
        "education",
        "media",
        "supply_chain",
        "legal",
        "governance"
    ]
    
    actual_domains = set(issue["domain"] for issue in issues)
    
    for domain in expected_domains:
        assert domain in actual_domains, f"Missing domain: {domain}"


def test_id_uniqueness(schema):
    """Test that all issue IDs are unique."""
    issues = schema["systemic_issues"]
    ids = [issue["id"] for issue in issues]
    
    assert len(ids) == len(set(ids)), "Duplicate issue IDs found"


def test_id_format(schema):
    """Test that issue IDs follow the expected format."""
    issues = schema["systemic_issues"]
    
    for issue in issues:
        issue_id = issue["id"]
        # Format should be DOMAIN-NUMBER
        assert "-" in issue_id, f"Invalid ID format: {issue_id}"
        
        parts = issue_id.split("-")
        assert len(parts) == 2, f"Invalid ID format: {issue_id}"
        assert parts[1].isdigit(), f"Invalid ID format: {issue_id}"


def test_domain_consistency(schema):
    """Test that domain in ID matches domain field."""
    issues = schema["systemic_issues"]
    
    domain_prefixes = {
        "software_engineering": "SE",
        "ai_systems": "AI",
        "cybersecurity": "CY",
        "healthcare": "HC",
        "finance": "FI",
        "infrastructure": "INF",
        "environment": "ENV",
        "education": "EDU",
        "media": "MED",
        "supply_chain": "SC",
        "legal": "LEG",
        "governance": "GOV"
    }
    
    for issue in issues:
        domain = issue["domain"]
        issue_id = issue["id"]
        
        expected_prefix = domain_prefixes.get(domain)
        if expected_prefix:
            assert issue_id.startswith(expected_prefix), \
                f"ID {issue_id} doesn't match domain {domain}"


def test_remediation_determinism(schema):
    """Test that remediation actions are deterministic."""
    issues = schema["systemic_issues"]
    
    for issue in issues:
        actions = issue["remediation_spec"]["deterministic_actions"]
        assert len(actions) > 0, f"No remediation actions for {issue['id']}"
        
        for action in actions:
            assert isinstance(action, str)
            assert len(action) > 0


def test_verification_completeness(schema):
    """Test that all issues have verification tests."""
    issues = schema["systemic_issues"]
    
    for issue in issues:
        tests = issue["verification"]["automated_tests"]
        assert len(tests) > 0, f"No verification tests for {issue['id']}"


def test_implementation_targets(schema):
    """Test that implementation targets are defined."""
    assert "implementation_targets" in schema
    targets = schema["implementation_targets"]
    
    assert "modules" in targets
    assert "tests" in targets
    assert "dashboards" in targets
    assert "pipelines" in targets
    
    assert len(targets["modules"]) > 0
    assert len(targets["tests"]) > 0


def test_integration_requirements(schema):
    """Test that integration requirements are defined."""
    assert "integration_requirements" in schema
    integration = schema["integration_requirements"]
    
    assert "upstream_schemas" in integration
    assert "downstream_systems" in integration
    assert "compatibility" in integration


def test_metadata_accuracy(schema):
    """Test that metadata matches actual content."""
    assert "metadata" in schema
    metadata = schema["metadata"]
    
    actual_count = len(schema["systemic_issues"])
    assert metadata["total_issues"] == actual_count, \
        f"Metadata says {metadata['total_issues']}, but found {actual_count}"
    
    # Count actual domains
    actual_domains = set(issue["domain"] for issue in schema["systemic_issues"])
    assert metadata["domains_covered"] == len(actual_domains)


def test_domain_distribution(schema):
    """Test that issues are evenly distributed across domains."""
    issues = schema["systemic_issues"]
    metadata = schema["metadata"]
    
    # Count issues per domain
    domain_counts = {}
    for issue in issues:
        domain = issue["domain"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    # Check against metadata
    coverage_dist = metadata["coverage_distribution"]
    for domain, count in coverage_dist.items():
        actual_count = domain_counts.get(domain, 0)
        assert actual_count == count, \
            f"Domain {domain}: metadata says {count}, but found {actual_count}"


def test_yeshua_standard_defined(schema):
    """Test that Yeshua standard is properly defined."""
    principles = schema["principles"]
    yeshua = principles["yeshua_standard"]
    
    assert "description" in yeshua
    assert "requirement" in yeshua
    assert "verification" in yeshua
    
    # Should reference META-001
    assert "META-001" in yeshua["verification"]


def test_glass_box_principle(schema):
    """Test that glass_box principle is enforced."""
    principles = schema["principles"]
    glass_box = principles["glass_box"]
    
    assert "No hidden operations" in glass_box["requirement"]
    assert "Complete audit trail" in glass_box["verification"]


def test_determinism_principle(schema):
    """Test that determinism is guaranteed."""
    principles = schema["principles"]
    determinism = principles["determinism"]
    
    assert "No random" in determinism["requirement"]
    assert "reproducibility" in determinism["verification"]


def test_idempotency_principle(schema):
    """Test that idempotency is guaranteed."""
    principles = schema["principles"]
    idempotency = principles["idempotency"]
    
    assert "no additional side effects" in idempotency["description"]
    assert "re-execute" in idempotency["requirement"]


def test_signoff_block(schema):
    """Test that signoff block is present and complete."""
    assert "signoff" in schema
    signoff = schema["signoff"]
    
    assert "architect" in signoff
    assert "repository" in signoff
    assert "standard" in signoff
    assert "statement" in signoff
    assert "verification" in signoff
    
    assert signoff["standard"] == "Yeshua"
    assert signoff["repository"] == "aidoruao/orthogonal-engineering"


def test_no_placeholders(schema):
    """Test that there are no placeholder values."""
    import json
    schema_str = json.dumps(schema)
    
    # Common placeholder strings
    placeholders = [
        "TODO",
        "FIXME",
        "PLACEHOLDER",
        "TBD",
        "NOT IMPLEMENTED",
        "COMING SOON"
    ]
    
    for placeholder in placeholders:
        assert placeholder not in schema_str, \
            f"Found placeholder: {placeholder}"


def test_concrete_remediation_actions(schema):
    """Test that all remediation actions are concrete and actionable."""
    issues = schema["systemic_issues"]
    
    # Vague action indicators
    vague_terms = ["consider", "think about", "maybe", "possibly"]
    
    for issue in issues:
        actions = issue["remediation_spec"]["deterministic_actions"]
        for action in actions:
            action_lower = action.lower()
            for vague_term in vague_terms:
                assert vague_term not in action_lower, \
                    f"Vague action in {issue['id']}: {action}"


def test_yaml_structure_valid():
    """Test that the YAML structure is valid and loadable."""
    schema_path = Path(__file__).parent.parent / "GLOBAL_SYSTEMIC_REPAIR_SCHEMA.yaml"
    
    try:
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        assert schema is not None
    except yaml.YAMLError as e:
        pytest.fail(f"YAML parsing error: {e}")


def test_schema_loadable_without_errors():
    """Test that schema loads without any errors."""
    schema_path = Path(__file__).parent.parent / "GLOBAL_SYSTEMIC_REPAIR_SCHEMA.yaml"
    
    with open(schema_path) as f:
        content = f.read()
    
    # Should not raise any exceptions
    schema = yaml.safe_load(content)
    assert isinstance(schema, dict)


def test_purpose_field(schema):
    """Test that purpose field is defined."""
    assert "purpose" in schema
    purpose = schema["purpose"]
    
    assert isinstance(purpose, list)
    assert len(purpose) >= 4


def test_description_field(schema):
    """Test that description field is present."""
    assert "description" in schema
    assert isinstance(schema["description"], str)
    assert len(schema["description"]) > 50


def test_success_criteria_defined(schema):
    """Test that all issues have success criteria."""
    issues = schema["systemic_issues"]
    
    for issue in issues:
        remediation = issue["remediation_spec"]
        assert "success_criteria" in remediation, \
            f"No success criteria for {issue['id']}"
        
        criteria = remediation["success_criteria"]
        assert isinstance(criteria, list)
        assert len(criteria) > 0


def test_prerequisites_defined(schema):
    """Test that prerequisites are defined where needed."""
    issues = schema["systemic_issues"]
    
    for issue in issues:
        remediation = issue["remediation_spec"]
        # Prerequisites are optional but if present should be a list
        if "prerequisites" in remediation:
            assert isinstance(remediation["prerequisites"], list)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
