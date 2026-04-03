import json
from pathlib import Path

from health_check_integration import HealthCheckIntegration


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _base_registry(wardens: dict, autonomy_policy: dict = None) -> dict:
    reg = {
        "base_ai": {
            "model": "llama3.1:70b",
            "api_endpoint": "http://localhost:11434",
            "version": "1.0.0",
        },
        "wardens": wardens,
        "dynamic_wardens": {"unclassified_folders": [], "temporary_wardens": {}},
        "health_checks": {"interval_seconds": 300, "failure_threshold": 3},
        "dynamic_warden_policy": {"max_lifetime_hours": 24},
        "backup": {},
        "error_handling": {},
        "system_metrics": {},
    }
    if autonomy_policy:
        reg["autonomy_policy"] = autonomy_policy
    return reg


def test_local_multi_scope_warden_uses_monitored_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_json(
        tmp_path / ".ai_registry.json",
        _base_registry(
            wardens={
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
            }
        ),
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


# ------------------------------------------------------------------ #
# A-1: file count self-healing                                        #
# ------------------------------------------------------------------ #

def _single_warden_registry(
    file_count: int, actual_files: int, autonomy_policy: dict = None
) -> dict:
    warden = {
        "my_warden": {
            "folder_path": "watched",
            "model_name": "llama3.2:3b",
            "api_key": "local_ollama",
            "status": "active",
            "metadata": {"file_count": file_count},
            "health": {"last_query": None, "response_time_ms": None, "success_rate": None},
        }
    }
    return _base_registry(wardens=warden, autonomy_policy=autonomy_policy)


def test_file_count_mismatch_produces_warning_in_dry_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reg = _single_warden_registry(file_count=5, actual_files=7)
    _write_json(tmp_path / ".ai_registry.json", reg)
    watched = tmp_path / "watched"
    watched.mkdir()
    for i in range(7):
        (watched / f"f{i}.txt").write_text("x", encoding="utf-8")

    results = HealthCheckIntegration(str(tmp_path / ".ai_registry.json")).run_health_checks()
    warden_health = results["wardens"]["my_warden"]

    # No autonomy_policy → default dry_run → no self-heal, still a warning
    assert warden_health["status"] == "warning"
    assert any("File count mismatch" in i for i in warden_health["issues"])
    assert warden_health["checks"]["file_count_match"] is False


def test_file_count_self_healing_in_execute_mode(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    autonomy = {
        "global_mode": "dry_run",
        "action_policies": {
            "update_file_count": {
                "mode": "execute",
                "requires_approval": False,
                "max_delta_pct": 20,
                "evidence_required": True,
                "audit_log": True,
            }
        },
        "guardrails": {
            "no_credential_commits": True,
            "no_warden_file_creation": True,
            "registry_backup_before_write": True,
            "max_writes_per_run": 5,
        },
    }
    reg = _single_warden_registry(file_count=5, actual_files=6, autonomy_policy=autonomy)
    _write_json(tmp_path / ".ai_registry.json", reg)
    watched = tmp_path / "watched"
    watched.mkdir()
    for i in range(6):
        (watched / f"f{i}.txt").write_text("x", encoding="utf-8")

    hci = HealthCheckIntegration(str(tmp_path / ".ai_registry.json"))
    results = hci.run_health_checks()
    warden_health = results["wardens"]["my_warden"]

    # Self-healing should have resolved the mismatch
    assert warden_health["status"] == "healthy"
    assert warden_health["checks"]["file_count_match"] is True
    assert warden_health["checks"].get("self_healed") is True

    # Registry should be persisted with the corrected count
    updated = json.loads((tmp_path / ".ai_registry.json").read_text())
    assert updated["wardens"]["my_warden"]["metadata"]["file_count"] == 6

    # file_count_history should have an entry
    history = updated["wardens"]["my_warden"]["health"]["file_count_history"]
    assert len(history) >= 1
    assert history[-1]["action_taken"] == "execute"
    assert history[-1]["actual"] == 6

    # A backup should have been created
    backups = list((tmp_path / ".ai_registry_backups").glob("registry_*.json"))
    assert len(backups) >= 1


def test_file_count_dry_run_writes_proposal(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reg = _single_warden_registry(file_count=10, actual_files=12)
    _write_json(tmp_path / ".ai_registry.json", reg)
    watched = tmp_path / "watched"
    watched.mkdir()
    for i in range(12):
        (watched / f"f{i}.txt").write_text("x", encoding="utf-8")

    HealthCheckIntegration(str(tmp_path / ".ai_registry.json")).run_health_checks()

    proposals_dir = tmp_path / "logs" / "health_checks" / "proposals"
    proposal_files = list(proposals_dir.glob("REM-*-my_warden-filecount.json"))
    assert len(proposal_files) == 1
    proposal = json.loads(proposal_files[0].read_text())
    assert proposal["action_type"] == "update_file_count"
    assert proposal["mode"] == "dry_run"
    assert proposal["evidence"]["actual_file_count"] == 12
    assert proposal["evidence"]["stored_file_count"] == 10
    assert proposal["falsifiability_note"] != ""


def test_file_count_self_heal_blocked_by_delta_pct_guard(tmp_path, monkeypatch):
    """Self-healing must be skipped when delta exceeds max_delta_pct."""
    monkeypatch.chdir(tmp_path)
    autonomy = {
        "global_mode": "dry_run",
        "action_policies": {
            "update_file_count": {
                "mode": "execute",
                "max_delta_pct": 5,  # tight limit
                "audit_log": True,
            }
        },
        "guardrails": {"registry_backup_before_write": True, "max_writes_per_run": 5},
    }
    # stored=5, actual=10 → 100 % delta → exceeds 5 % limit
    reg = _single_warden_registry(file_count=5, actual_files=10, autonomy_policy=autonomy)
    _write_json(tmp_path / ".ai_registry.json", reg)
    watched = tmp_path / "watched"
    watched.mkdir()
    for i in range(10):
        (watched / f"f{i}.txt").write_text("x", encoding="utf-8")

    results = HealthCheckIntegration(str(tmp_path / ".ai_registry.json")).run_health_checks()
    warden_health = results["wardens"]["my_warden"]

    # Delta exceeds guard → no self-heal, stays warning
    assert warden_health["status"] == "warning"
    assert warden_health["checks"].get("self_healed") is not True


# ------------------------------------------------------------------ #
# A-6: credential resolver                                            #
# ------------------------------------------------------------------ #

def test_credential_resolver_local_ollama(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reg = _single_warden_registry(file_count=0, actual_files=0)
    _write_json(tmp_path / ".ai_registry.json", reg)
    (tmp_path / "watched").mkdir()

    results = HealthCheckIntegration(str(tmp_path / ".ai_registry.json")).run_health_checks()
    assert results["wardens"]["my_warden"]["checks"]["credential_source"] == "none"


def test_credential_resolver_structured_field(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    reg = _base_registry(
        wardens={
            "ext_warden": {
                "folder_path": "watched",
                "model_name": "gpt-4o",
                "api_key": "env_var_fallback",
                "credential_resolver": {"source": "github_secret", "ref": "MY_API_KEY"},
                "status": "active",
                "metadata": {"file_count": None},
                "health": {},
            }
        }
    )
    _write_json(tmp_path / ".ai_registry.json", reg)
    (tmp_path / "watched").mkdir()

    results = HealthCheckIntegration(str(tmp_path / ".ai_registry.json")).run_health_checks()
    assert (
        results["wardens"]["ext_warden"]["checks"]["credential_source"]
        == "github_secret:MY_API_KEY"
    )

