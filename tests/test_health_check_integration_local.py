import json
from pathlib import Path

from health_check_integration import HealthCheckIntegration


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_local_multi_scope_warden_uses_monitored_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_json(
        tmp_path / ".ai_registry.json",
        {
            "base_ai": {
                "model": "llama3.1:70b",
                "api_endpoint": "http://localhost:11434",
                "version": "1.0.0",
            },
            "wardens": {
                "cherub_unit": {
                    "folder_path": ".",
                    "model_name": "mistral:7b",
                    "api_key": "local_ollama",
                    "status": "active",
                    "metadata": {
                        "file_count": 3,
                        "monitored_paths": ["documentation", "scripts", "evidence"],
                    },
                    "health": {
                        "last_query": None,
                        "response_time_ms": None,
                        "success_rate": None,
                        "last_health_check": None,
                    },
                }
            },
            "dynamic_wardens": {"unclassified_folders": [], "temporary_wardens": {}},
            "health_checks": {"interval_seconds": 300, "failure_threshold": 3},
            "dynamic_warden_policy": {"max_lifetime_hours": 24},
            "backup": {},
            "error_handling": {},
            "system_metrics": {},
        },
    )

    for relative_path in ("documentation/doc.md", "scripts/job.py", "evidence/note.txt"):
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("ok", encoding="utf-8")

    results = HealthCheckIntegration(str(tmp_path / ".ai_registry.json")).run_health_checks()
    cherub_health = results["wardens"]["cherub_unit"]

    assert cherub_health["status"] == "healthy"
    assert cherub_health["checks"]["folder_exists"] is True
    assert cherub_health["checks"]["folder_readable"] is True
    assert cherub_health["checks"]["file_count"] == 3
    assert cherub_health["checks"]["file_count_match"] is True
    assert len(cherub_health["checks"]["path_checks"]) == 3
