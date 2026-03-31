"""
pcfe_kernel/tests/test_department_registry.py

Tests for Department dataclass and DepartmentRegistry.
"""

import pytest

from pcfe_kernel.department import Department, DepartmentRegistry
from pcfe_kernel.departments import D_BIO, D_CHEM, D_FDACS, D_SENSE, D_TRAIN, build_default_registry


# ---------------------------------------------------------------------------
# Department construction
# ---------------------------------------------------------------------------

class TestDepartmentConstruction:
    def test_all_builtin_departments_instantiate(self):
        for dept in (D_BIO, D_CHEM, D_FDACS, D_SENSE, D_TRAIN):
            assert isinstance(dept, Department)

    def test_department_ids_unique(self):
        depts = [D_BIO, D_CHEM, D_FDACS, D_SENSE, D_TRAIN]
        ids = [d.id for d in depts]
        assert len(ids) == len(set(ids)), "Department IDs must be unique"

    def test_department_roles_valid(self):
        valid_roles = {"state_input", "action_constraint", "rule_filter"}
        for dept in (D_BIO, D_CHEM, D_FDACS, D_SENSE, D_TRAIN):
            assert dept.kernel_role in valid_roles

    def test_invalid_kernel_role_raises(self):
        with pytest.raises(ValueError, match="kernel_role"):
            Department(
                id="D_test",
                name="Test",
                ontology={},
                constraint_keys=[],
                kernel_role="invalid_role",
                falsification_ids=[],
            )

    def test_department_is_frozen(self):
        with pytest.raises((AttributeError, TypeError)):
            D_BIO.id = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Kernel-role injection points
# ---------------------------------------------------------------------------

class TestDepartmentInjection:
    def test_d_bio_is_state_input(self):
        assert D_BIO.kernel_role == "state_input"

    def test_d_chem_is_action_constraint(self):
        assert D_CHEM.kernel_role == "action_constraint"

    def test_d_fdacs_is_rule_filter(self):
        assert D_FDACS.kernel_role == "rule_filter"

    def test_d_sense_is_state_input(self):
        assert D_SENSE.kernel_role == "state_input"

    def test_d_train_is_state_input(self):
        assert D_TRAIN.kernel_role == "state_input"

    def test_d_bio_manifest_entries_non_empty(self):
        entries = D_BIO.manifest_entries()
        assert len(entries) > 0
        assert all(isinstance(e, str) for e in entries)

    def test_d_chem_manifest_entries_empty(self):
        # action_constraint departments return no manifest entries
        assert D_CHEM.manifest_entries() == []

    def test_d_fdacs_rule_keys_non_empty(self):
        keys = D_FDACS.rule_keys()
        assert len(keys) > 0

    def test_d_bio_rule_keys_empty(self):
        # state_input departments return no rule keys
        assert D_BIO.rule_keys() == []


# ---------------------------------------------------------------------------
# Action allowlist
# ---------------------------------------------------------------------------

class TestActionAllowlist:
    def test_d_chem_blocks_prohibited_action(self):
        assert not D_CHEM.is_action_allowed("apply:unregistered_pesticide")

    def test_d_chem_allows_unlisted_action(self):
        assert D_CHEM.is_action_allowed("inspect:premises")

    def test_non_action_constraint_dept_allows_everything(self):
        assert D_BIO.is_action_allowed("apply:unregistered_pesticide")
        assert D_FDACS.is_action_allowed("apply:banned_organochlorine")


# ---------------------------------------------------------------------------
# DepartmentRegistry
# ---------------------------------------------------------------------------

class TestDepartmentRegistry:
    def test_build_default_registry_has_five_departments(self):
        registry = build_default_registry()
        assert len(registry.all()) == 5

    def test_registry_get_by_id(self):
        registry = build_default_registry()
        dept = registry.get("D_bio")
        assert dept.id == "D_bio"

    def test_registry_get_missing_raises(self):
        registry = build_default_registry()
        with pytest.raises(KeyError):
            registry.get("D_nonexistent")

    def test_registry_duplicate_register_raises(self):
        registry = DepartmentRegistry()
        registry.register(D_BIO)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(D_BIO)

    def test_registry_by_role_state_input(self):
        registry = build_default_registry()
        state_depts = registry.by_role("state_input")
        ids = {d.id for d in state_depts}
        assert ids == {"D_bio", "D_sense", "D_train"}

    def test_registry_by_role_action_constraint(self):
        registry = build_default_registry()
        action_depts = registry.by_role("action_constraint")
        assert len(action_depts) == 1
        assert action_depts[0].id == "D_chem"

    def test_registry_by_role_rule_filter(self):
        registry = build_default_registry()
        rule_depts = registry.by_role("rule_filter")
        assert len(rule_depts) == 1
        assert rule_depts[0].id == "D_fdacs"

    def test_registry_all_manifest_entries_non_empty(self):
        registry = build_default_registry()
        entries = registry.all_manifest_entries()
        assert len(entries) > 0

    def test_registry_is_action_allowed_blocks_prohibited(self):
        registry = build_default_registry()
        assert not registry.is_action_allowed("apply:unregistered_pesticide")

    def test_registry_is_action_allowed_permits_valid(self):
        registry = build_default_registry()
        assert registry.is_action_allowed("inspect:premises")

    def test_registry_empty_allows_any_action(self):
        registry = DepartmentRegistry()
        assert registry.is_action_allowed("apply:banned_organochlorine")
