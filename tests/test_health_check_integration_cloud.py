import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from health_check_integration import HealthCheckIntegration


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_registry(extra_health: dict = None) -> dict:
    health = {
        "last_query": None,
        "response_time_ms": None,
        "success_rate": None,
        "last_health_check": None,
        "last_artifact_timestamp": None,
        "max_report_age_hours": 36,
        "overall_status": "pending",
        "report_age_history": [],
        "suggested_max_report_age_hours": None,
        "threshold_sample_size": 0,
        "threshold_confidence": None,
    }
    if extra_health:
        health.update(extra_health)
    return {
        "base_ai": {
            "model": "llama3.1:70b",
            "api_endpoint": "http://localhost:11434",
            "version": "1.0.0",
        },
        "wardens": {
            "gemini_warden": {
                "folder_path": "**",
                "model_name": "gemini-2.5-flash",
                "api_key": "github_secret:GEMINI_API_KEY",
                "status": "active",
                "runtime": "github_actions",
                "workflow_path": ".github/workflows/shiro-daily-scan.yml",
                "metadata": {
                    "artifact_report_path": "logs/health_checks/cloud_wardens/gemini_warden_status.json"
                },
                "health": health,
            }
        },
        "dynamic_wardens": {"unclassified_folders": [], "temporary_wardens": {}},
        "health_checks": {"interval_seconds": 300, "failure_threshold": 3},
        "dynamic_warden_policy": {"max_lifetime_hours": 24},
        "backup": {},
        "error_handling": {},
        "system_metrics": {"last_registry_update": datetime.now(timezone.utc).isoformat()},
    }


def _prepare_workspace(tmp_path: Path, registry: dict) -> Path:
    registry_path = tmp_path / ".ai_registry.json"
    _write_json(registry_path, registry)
    workflow_path = tmp_path / ".github" / "workflows" / "shiro-daily-scan.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text("name: test\n", encoding="utf-8")
    return registry_path


def test_cloud_warden_health_is_healthy_with_fresh_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry = _build_registry()
    registry_path = _prepare_workspace(tmp_path, registry)

    fresh_timestamp = datetime.now(timezone.utc).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {
            "status": "healthy",
            "timestamp": fresh_timestamp,
            "findings": [],
            "issues": [],
            "recommendations": [],
        },
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    gemini_health = results["wardens"]["gemini_warden"]

    assert gemini_health["status"] == "healthy"
    assert gemini_health["checks"]["workflow_exists"] is True
    assert gemini_health["checks"]["report_exists"] is True
    assert gemini_health["checks"]["report_fresh"] is True


def test_cloud_warden_health_warns_when_report_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    gemini_health = results["wardens"]["gemini_warden"]

    assert gemini_health["status"] == "warning"
    assert gemini_health["checks"]["workflow_exists"] is True
    assert gemini_health["checks"]["report_exists"] is False
    assert any("Cloud report not found" in issue for issue in gemini_health["issues"])


def test_cloud_warden_health_warns_when_report_is_stale(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    stale_timestamp = (datetime.now(timezone.utc) - timedelta(hours=72)).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {
            "status": "healthy",
            "timestamp": stale_timestamp,
            "findings": [],
            "issues": [],
            "recommendations": [],
        },
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    gemini_health = results["wardens"]["gemini_warden"]

    assert gemini_health["status"] == "warning"
    assert gemini_health["checks"]["report_exists"] is True
    assert gemini_health["checks"]["report_fresh"] is False
    assert any("Cloud report is stale" in issue for issue in gemini_health["issues"])


# ------------------------------------------------------------------ #
# A-2: report_age_history ring buffer + shadow threshold             #
# ------------------------------------------------------------------ #

def test_report_age_history_appended_on_fresh_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    fresh_ts = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    HealthCheckIntegration(str(registry_path)).run_health_checks()

    updated = json.loads(registry_path.read_text())
    history = updated["wardens"]["gemini_warden"]["health"]["report_age_history"]
    assert len(history) == 1
    assert 1.9 <= history[0] <= 2.1  # approximately 2 hours


def test_report_age_history_ring_buffer_respects_max_size(tmp_path, monkeypatch):
    """Seeding 35 entries should be trimmed to REPORT_AGE_HISTORY_MAX_SIZE=30."""
    monkeypatch.chdir(tmp_path)
    seed = [float(i) for i in range(35)]
    registry = _build_registry(extra_health={"report_age_history": seed, "threshold_sample_size": 35})
    registry_path = _prepare_workspace(tmp_path, registry)

    fresh_ts = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    HealthCheckIntegration(str(registry_path)).run_health_checks()

    updated = json.loads(registry_path.read_text())
    history = updated["wardens"]["gemini_warden"]["health"]["report_age_history"]
    assert len(history) == 30  # capped at REPORT_AGE_HISTORY_MAX_SIZE


def test_suggested_threshold_computed_when_enough_samples(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Pre-seed 7 observations so the next run (8th) triggers computation
    seed = [24.0, 23.5, 24.1, 23.8, 24.3, 23.9, 24.2]
    registry = _build_registry(extra_health={"report_age_history": seed, "threshold_sample_size": 7})
    registry_path = _prepare_workspace(tmp_path, registry)

    fresh_ts = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    HealthCheckIntegration(str(registry_path)).run_health_checks()

    updated = json.loads(registry_path.read_text())
    health_block = updated["wardens"]["gemini_warden"]["health"]
    suggested = health_block["suggested_max_report_age_hours"]
    assert suggested is not None
    # mean ~24.0, stddev ~0.27 → mean + 1.5*stddev ≈ 24.4; must be > 24
    assert suggested > 24.0
    assert health_block["threshold_sample_size"] == 8
    assert health_block["threshold_confidence"] is not None


def test_suggested_threshold_null_below_min_sample_size(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    fresh_ts = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    HealthCheckIntegration(str(registry_path)).run_health_checks()

    updated = json.loads(registry_path.read_text())
    health_block = updated["wardens"]["gemini_warden"]["health"]
    # Only 1 observation → below min_sample_size of 7
    assert health_block["suggested_max_report_age_hours"] is None


# ------------------------------------------------------------------ #
# A-6: credential_source in cloud warden checks                      #
# ------------------------------------------------------------------ #

def test_cloud_warden_credential_source_recorded(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    fresh_ts = datetime.now(timezone.utc).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    cred = results["wardens"]["gemini_warden"]["checks"]["credential_source"]
    assert cred == "github_secret:GEMINI_API_KEY"



# ------------------------------------------------------------------ #
# A-7: Moral Anchor                                                   #
# ------------------------------------------------------------------ #

def test_moral_anchor_detects_no_violations_on_clean_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    fresh_ts = datetime.now(timezone.utc).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    assert results["moral_anchor_violations"] == []


def test_moral_anchor_detects_deception_in_proposal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    # Write a proposal lacking evidence and falsifiability_note
    _write_json(
        tmp_path / "logs" / "health_checks" / "proposals" / "REM-bad.json",
        {
            "proposal_id": "REM-bad",
            "action_type": "update_file_count",
            "mode": "dry_run",
            "status": "pending",
            # Missing: evidence, falsifiability_note
        },
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    assert any("deception" in v for v in results["moral_anchor_violations"])


def test_moral_anchor_freezes_autonomy_on_violation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    _write_json(
        tmp_path / "logs" / "health_checks" / "proposals" / "REM-no-evidence.json",
        {"proposal_id": "REM-no-evidence", "mode": "dry_run", "status": "pending"},
    )

    hci = HealthCheckIntegration(str(registry_path))
    results = hci.run_health_checks()
    assert len(results["moral_anchor_violations"]) > 0
    updated = json.loads(registry_path.read_text())
    assert updated["autonomy_policy"]["global_mode"] == "frozen"
    assert updated["autonomy_policy"]["moral_anchor"]["frozen"] is True


# ------------------------------------------------------------------ #
# A-8: Drift Detection                                                #
# ------------------------------------------------------------------ #

def test_drift_report_zero_for_fresh_cloud_warden(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    fresh_ts = datetime.now(timezone.utc).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    drift = results["drift_report"]["drift_per_warden"].get("gemini_warden", 0.0)
    # Fresh warden with only 1 history entry — drift requires ≥3 entries
    assert drift == 0.0


def test_drift_report_contains_all_wardens(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    assert "gemini_warden" in results["drift_report"]["drift_per_warden"]
    assert "evaluated_at" in results["drift_report"]
    assert "warning_threshold" in results["drift_report"]
    assert "critical_threshold" in results["drift_report"]


# ------------------------------------------------------------------ #
# A-10: Structural Integrity Warden                                   #
# ------------------------------------------------------------------ #

def test_structural_integrity_reports_missing_section(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry = _build_registry()
    # Remove health_checks to trigger violation
    del registry["health_checks"]
    registry_path = _prepare_workspace(tmp_path, registry)

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    integrity = results["integrity_report"]
    assert any("health_checks" in v for v in integrity["violations"])


def test_structural_integrity_healthy_on_complete_registry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Build a registry that includes autonomy_policy so no violations
    registry = _build_registry()
    registry["autonomy_policy"] = {
        "schema_version": "1.0",
        "global_mode": "dry_run",
        "guardrails": {"no_credential_commits": True},
        "moral_anchor": {},
        "drift_detection": {},
        "approval_workflow": {},
        "objective_function": {},
    }
    registry_path = _prepare_workspace(tmp_path, registry)

    fresh_ts = datetime.now(timezone.utc).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    assert results["integrity_report"]["status"] == "healthy"
    assert results["integrity_report"]["violations"] == []


# ------------------------------------------------------------------ #
# A-11: Epistemic Conflict Detector                                   #
# ------------------------------------------------------------------ #

def test_epistemic_conflict_detects_overlapping_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry = _build_registry()
    # Add a second warden monitoring the same path as gemini_warden (**) — but both non-catch-all
    registry["wardens"]["local_warden"] = {
        "folder_path": "monitored_dir",
        "model_name": "llama3.2:3b",
        "api_key": "local_ollama",
        "status": "active",
        "metadata": {"file_count": 0, "monitored_paths": ["monitored_dir"]},
        "health": {},
    }
    registry["wardens"]["local_warden2"] = {
        "folder_path": "monitored_dir",
        "model_name": "llama3.2:3b",
        "api_key": "local_ollama",
        "status": "active",
        "metadata": {"file_count": 0},
        "health": {},
    }
    registry_path = _prepare_workspace(tmp_path, registry)
    (tmp_path / "monitored_dir").mkdir()

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    conflicts = results["conflict_report"]["conflicts"]
    assert any(c["type"] == "overlapping_monitored_path" for c in conflicts)


def test_epistemic_conflict_clean_on_single_warden(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    assert results["conflict_report"]["status"] == "healthy"
    assert results["conflict_report"]["conflict_count"] == 0


# ------------------------------------------------------------------ #
# A-12/A-13/A-14/A-17: Intelligence Metrics                          #
# ------------------------------------------------------------------ #

def test_intelligence_metrics_present_in_results(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    fresh_ts = datetime.now(timezone.utc).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    im = results["intelligence_metrics"]

    assert "entropy_bits" in im
    assert "consistency_ratio" in im
    assert "convergence_score" in im
    assert "convergence_reached" in im
    assert "objective_score" in im
    assert "evaluated_at" in im
    assert im["entropy_bits"] >= 0.0
    assert 0.0 <= im["objective_score"] <= 1.0
    assert 0.0 <= im["convergence_score"] <= 1.0


def test_entropy_is_zero_when_all_wardens_same_status(tmp_path, monkeypatch):
    """All wardens healthy → only one state → entropy = 0."""
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    results = HealthCheckIntegration(str(registry_path)).run_health_checks()
    im = results["intelligence_metrics"]
    # Only one warden and report is missing → status="warning"; still only one state
    assert im["entropy_bits"] == 0.0


def test_intelligence_metrics_persisted_to_registry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry_path = _prepare_workspace(tmp_path, _build_registry())

    HealthCheckIntegration(str(registry_path)).run_health_checks()

    updated = json.loads(registry_path.read_text())
    sm = updated["system_metrics"]
    assert "entropy_bits" in sm
    assert "consistency_ratio" in sm
    assert "convergence_score" in sm
    assert "objective_score" in sm


# ------------------------------------------------------------------ #
# A-14: Convergence + Equilibrium Conditions                          #
# ------------------------------------------------------------------ #

def test_equilibrium_conditions_written_to_objective_function(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registry = _build_registry()
    registry["autonomy_policy"] = {
        "schema_version": "1.0",
        "global_mode": "dry_run",
        "guardrails": {},
        "moral_anchor": {},
        "drift_detection": {},
        "approval_workflow": {},
        "objective_function": {"equilibrium_conditions": {}, "convergence_reached": False},
    }
    registry_path = _prepare_workspace(tmp_path, registry)

    fresh_ts = datetime.now(timezone.utc).isoformat()
    _write_json(
        tmp_path / "logs" / "health_checks" / "cloud_wardens" / "gemini_warden_status.json",
        {"status": "healthy", "timestamp": fresh_ts, "findings": [], "issues": [], "recommendations": []},
    )

    HealthCheckIntegration(str(registry_path)).run_health_checks()

    updated = json.loads(registry_path.read_text())
    eq = updated["autonomy_policy"]["objective_function"]["equilibrium_conditions"]
    assert "all_invariants_satisfied" in eq
    assert "all_claims_verifiable" in eq
    assert "no_unnecessary_proposals" in eq
    assert "no_drift_detected" in eq
