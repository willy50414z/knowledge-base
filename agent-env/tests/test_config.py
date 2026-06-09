from agent_env.config import AppConfig, load_config, save_config, set_config_value


def test_load_config_returns_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    cfg = load_config()
    assert cfg.repo_url == "https://github.com/willy50414z/knowledge-base.git"
    assert cfg.default_branch == "main"
    assert cfg.schema_version == 1


def test_save_and_reload_config(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", path)
    cfg = load_config()
    cfg.repo_url = "https://github.com/other/repo.git"
    save_config(cfg)
    reloaded = load_config()
    assert reloaded.repo_url == "https://github.com/other/repo.git"


def test_set_config_value(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", path)
    set_config_value("default_branch", "develop")
    cfg = load_config()
    assert cfg.default_branch == "develop"


def test_kb_path_resolves_home(monkeypatch):
    cfg = AppConfig(
        repo_url="x", knowledge_base_path="~/.agent-env/knowledge-base",
        anthropics_skills_url="https://github.com/anthropics/skills.git",
        anthropics_skills_path="~/.agent-env/anthropics-skills",
        default_branch="main", last_updated=None,
        last_deployed_agents=[], schema_version=1,
    )
    assert cfg.kb_path.is_absolute()
    assert "~" not in str(cfg.kb_path)
