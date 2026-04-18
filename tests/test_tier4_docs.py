"""
tests/test_tier4_docs.py — Tier 4 documentation validation tests.

Validates existence, structure, and content of the three Tier 4 documentation
files: GLOSSARY.md, AGENT_CAPABILITIES_MATRIX.md, CROSS_REPO_INSTRUCTIONS.md.

Falsifies if: any of the three Tier 4 documentation files is absent, lacks
YAML frontmatter, or fails its minimum content requirements.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

GLOSSARY = REPO_ROOT / "GLOSSARY.md"
CAPABILITIES = REPO_ROOT / "AGENT_CAPABILITIES_MATRIX.md"
CROSS_REPO = REPO_ROOT / "CROSS_REPO_INSTRUCTIONS.md"


def test_glossary_exists() -> None:
    """
    GLOSSARY.md must exist at the repository root.

    Falsifies if: the file is absent or cannot be opened.
    """
    assert GLOSSARY.exists(), f"GLOSSARY.md not found at {GLOSSARY}"


def test_glossary_has_frontmatter() -> None:
    """
    GLOSSARY.md must begin with YAML frontmatter (starts with '---').

    Falsifies if: the file does not start with the string '---'.
    """
    content = GLOSSARY.read_text(encoding="utf-8")
    assert content.startswith("---"), "GLOSSARY.md does not start with YAML frontmatter '---'"


def test_glossary_has_minimum_entries() -> None:
    """
    GLOSSARY.md must contain at least 40 table rows (non-header pipe-separated lines).

    Falsifies if: fewer than 40 lines starting with '|' and containing a
    non-empty first column are found after stripping the header separator row.
    """
    content = GLOSSARY.read_text(encoding="utf-8")
    table_rows = [
        line for line in content.splitlines()
        if line.startswith("|")
        and not line.startswith("|---")
        and not line.strip() == "|"
    ]
    # Exclude the header row (Term | Engineering Definition | ...)
    data_rows = [r for r in table_rows if "Engineering Definition" not in r]
    assert len(data_rows) >= 40, (
        f"GLOSSARY.md has only {len(data_rows)} data rows; expected >= 40"
    )


def test_glossary_has_all_required_terms() -> None:
    """
    GLOSSARY.md must contain all required architectural terms.

    Falsifies if: any of the required terms is absent from the file content.
    """
    content = GLOSSARY.read_text(encoding="utf-8")
    required_terms = [
        "ProofObject",
        "Yeshua Standard",
        "Steward",
        "Accuser",
        "Fraction",
        "LOGOS",
        "ESCHATON",
        "Bar Exam",
        "Recursive Wipe",
    ]
    missing = [term for term in required_terms if term not in content]
    assert not missing, f"GLOSSARY.md is missing required terms: {missing}"


def test_capabilities_matrix_exists() -> None:
    """
    AGENT_CAPABILITIES_MATRIX.md must exist at the repository root.

    Falsifies if: the file is absent or cannot be opened.
    """
    assert CAPABILITIES.exists(), (
        f"AGENT_CAPABILITIES_MATRIX.md not found at {CAPABILITIES}"
    )


def test_capabilities_matrix_has_minimum_agents() -> None:
    """
    AGENT_CAPABILITIES_MATRIX.md must list at least 10 agents in the main table.

    Falsifies if: fewer than 10 table data rows are found in the file.
    """
    content = CAPABILITIES.read_text(encoding="utf-8")
    table_rows = [
        line for line in content.splitlines()
        if line.startswith("|")
        and not line.startswith("|---")
        and "Agent" not in line
        and line.strip() != "|"
    ]
    assert len(table_rows) >= 10, (
        f"AGENT_CAPABILITIES_MATRIX.md has only {len(table_rows)} agent rows; expected >= 10"
    )


def test_capabilities_matrix_has_required_agents() -> None:
    """
    AGENT_CAPABILITIES_MATRIX.md must reference all required agent names.

    Falsifies if: any of the required agent names is absent from the file content.
    """
    content = CAPABILITIES.read_text(encoding="utf-8")
    required_agents = ["Copilot", "Claude", "Devin", "Kimi", "Gemini"]
    missing = [agent for agent in required_agents if agent not in content]
    assert not missing, (
        f"AGENT_CAPABILITIES_MATRIX.md is missing required agents: {missing}"
    )


def test_cross_repo_instructions_exists() -> None:
    """
    CROSS_REPO_INSTRUCTIONS.md must exist at the repository root.

    Falsifies if: the file is absent or cannot be opened.
    """
    assert CROSS_REPO.exists(), (
        f"CROSS_REPO_INSTRUCTIONS.md not found at {CROSS_REPO}"
    )


def test_cross_repo_references_all_repos() -> None:
    """
    CROSS_REPO_INSTRUCTIONS.md must reference all three repositories by name.

    Falsifies if: any of the three repository names is absent from the file content.
    """
    content = CROSS_REPO.read_text(encoding="utf-8")
    required_repos = [
        "orthogonal-engineering",
        "sigma-lora-covenant",
        "truthsystems-mod",
    ]
    missing = [repo for repo in required_repos if repo not in content]
    assert not missing, (
        f"CROSS_REPO_INSTRUCTIONS.md is missing repository references: {missing}"
    )


def test_cross_repo_has_gap4_section() -> None:
    """
    CROSS_REPO_INSTRUCTIONS.md must contain a GAP-4 history section.

    Falsifies if: the string 'GAP-4' is absent from the file content.
    """
    content = CROSS_REPO.read_text(encoding="utf-8")
    assert "GAP-4" in content, (
        "CROSS_REPO_INSTRUCTIONS.md does not contain the required 'GAP-4' section"
    )


def test_all_tier4_docs_have_frontmatter() -> None:
    """
    All three Tier 4 documentation files must begin with YAML frontmatter ('---').

    Falsifies if: any of the three files does not start with the string '---'.
    """
    for path in (GLOSSARY, CAPABILITIES, CROSS_REPO):
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---"), (
            f"{path.name} does not start with YAML frontmatter '---'"
        )


def test_all_tier4_docs_have_register_technical() -> None:
    """
    All three Tier 4 documentation files must contain 'register: technical' in their frontmatter.

    Falsifies if: any of the three files does not contain the string 'register: technical'.
    """
    for path in (GLOSSARY, CAPABILITIES, CROSS_REPO):
        content = path.read_text(encoding="utf-8")
        assert "register: technical" in content, (
            f"{path.name} does not contain 'register: technical' in its YAML frontmatter"
        )
