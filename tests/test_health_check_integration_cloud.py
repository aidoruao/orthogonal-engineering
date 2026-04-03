import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from health_check_integration import HealthCheckIntegration


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_registry() -> dict:
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
                "health": {
                    "last_query": None,
                    "response_time_ms": None,
                    "success_rate": None,
                    "last_health_check": None,
                    "last_artifact_timestamp": None,
                    "max_report_age_hours": 36,
                    "overall_status": "pending",
                },
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
