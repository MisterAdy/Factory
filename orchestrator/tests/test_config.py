from orchestrator.config import Settings, load_settings


def test_load_settings_uses_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("ORCH_ORCHESTRATOR__PROJECT_ROOT", str(tmp_path))
    settings = load_settings()
    assert isinstance(settings, Settings)
    assert settings.orchestrator.project_root == tmp_path
