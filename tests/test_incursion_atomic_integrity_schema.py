import pathlib
import yaml


def load_schema():
    schema_path = pathlib.Path(__file__).resolve().parent.parent / "INCURSION_ATOMIC_INTEGRITY_SCHEMA.yaml"
    with schema_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_top_level_metadata():
    schema = load_schema()
    assert schema["schema_version"] == "5.0.0"
    assert schema["authority"] == "EXTERNAL_IMMUTABLE"
    assert schema["hash_algorithm"] == "SHA-256"


def test_covenant_principles_defined():
    schema = load_schema()
    principles = schema["covenant_principles"]
    assert set(principles.keys()) == {"LOGOS", "CHALCEDON", "GRACE", "KENOSIS", "AGAPE"}
    assert principles["LOGOS"]["rule"].startswith("Truth-Only")
    assert "output_must_be_verifiable_against_artifacts" in principles["LOGOS"]["constraints"]
    assert principles["AGAPE"]["rule"].startswith("Infrastructure exists solely to serve users")


def test_operational_modes():
    schema = load_schema()
    modes = schema["operational_modes"]
    assert "FORENSIC" in modes and "POPPERIAN" in modes
    assert "hash_verification" in modes["FORENSIC"]["allowed"]
    assert "emotion_labeling" in modes["FORENSIC"]["prohibited"]
    assert "hypothesis_testing" in modes["POPPERIAN"]["allowed"]
    assert "interpretive_analysis" in modes["POPPERIAN"]["prohibited"]


def test_engineering_invariants_and_anti_nominalism():
    schema = load_schema()
    invariants = schema["engineering_invariants"]
    assert "ATOMIC" in invariants and "DETERMINISTIC" in invariants
    assert "PreStateHash" in invariants["ATOMIC"]["rule"]
    clauses = schema["anti_nominalism_clauses"]
    assert len(clauses) == 5
    assert clauses["clause_001"].startswith("No label without hashed referent")


def test_core_modules_present():
    schema = load_schema()
    modules = schema["modules"]
    expected = {
        "MissionManager",
        "InventoryUI",
        "AIController",
        "WeaponSystem",
        "MapManager",
        "AudioVisual",
        "EnginePerf",
        "CoOpNetwork",
    }
    assert expected.issubset(set(modules.keys()))

    mission = modules["MissionManager"]
    assert mission["invariants"][0].startswith("MissionStateHash = SHA256")
    assert "ObjectiveList" in mission["fields"]

    weapon = modules["WeaponSystem"]
    assert "TransitionHash" in weapon["fields"]
    assert any("ActiveAnimationLock" in field for field in weapon["fields"])
    assert any("ActiveAnimationLock" in inv or "TransitionHash" in inv for inv in weapon["invariants"])

    coop = modules["CoOpNetwork"]
    assert "SessionID" in coop["fields"]
    assert "PeerLatencies" in coop["fields"]
    assert coop["fields"]["PeerLatencies"]["type"] == "map<UUID,float>"
