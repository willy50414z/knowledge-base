import pytest
from click.testing import CliRunner

from agent_env.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_init_project_claude_non_interactive(runner, kb_root, project_root, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)

    result = runner.invoke(main, [
        "init",
        "--path", str(project_root),
        "--project",
        "--agents", "claude",
        "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert result.exit_code == 0, result.output
    assert not (project_root / ".claude" / "CLAUDE.md").exists()
    assert (project_root / ".claude" / "settings.local.json").exists()
    assert (project_root / ".ai" / "catalogue.md").exists()
    assert (project_root / ".ai" / "sync.sh").exists()
    assert (project_root / ".ai" / "sync.bat").exists()


def test_init_project_creates_ai_scaffold(runner, kb_root, project_root, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)

    runner.invoke(main, [
        "init", "--path", str(project_root),
        "--project", "--agents", "claude", "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert (project_root / ".ai" / "skills" / ".gitkeep").exists()
    assert (project_root / ".ai" / "rules" / ".gitkeep").exists()


def test_init_skips_existing_sync_script(runner, kb_root, project_root, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)
    (project_root / ".ai").mkdir(parents=True)
    existing = project_root / ".ai" / "sync.sh"
    existing.write_text("# custom sync", encoding="utf-8")

    runner.invoke(main, [
        "init", "--path", str(project_root),
        "--project", "--agents", "claude", "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert "# custom sync" in existing.read_text(encoding="utf-8")


def test_init_syncs_claude_skills(runner, kb_root, project_root, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)

    # create a fake skill directly under skills/
    skill_dir = kb_root / "agent_cli_file" / "skills" / "my-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# My Skill\n", encoding="utf-8")

    claude_skills_dst = tmp_path / "claude_skills"
    monkeypatch.setattr("agent_env.cli.Path.home", lambda: tmp_path)

    result = runner.invoke(main, [
        "init",
        "--path", str(project_root),
        "--project",
        "--agents", "claude",
        "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert result.exit_code == 0, result.output
    assert "synced skill: my-skill" in result.output


def test_user_init_does_not_modify_claude_md(runner, kb_root, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)
    monkeypatch.setattr("agent_env.cli.Path.home", lambda: tmp_path)

    # pre-existing CLAUDE.md at user level
    claude_md = tmp_path / ".claude" / "CLAUDE.md"
    claude_md.parent.mkdir(parents=True)
    claude_md.write_text("# My CLAUDE.md", encoding="utf-8")

    runner.invoke(main, [
        "init", "--user", "--agents", "claude", "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert claude_md.read_text(encoding="utf-8") == "# My CLAUDE.md"


def test_user_init_syncs_rules_to_claude(runner, kb_root, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)
    monkeypatch.setattr("agent_env.cli.Path.home", lambda: tmp_path)

    rules_src = kb_root / "agent_cli_file" / "rules"
    rules_src.mkdir(parents=True, exist_ok=True)
    (rules_src / "my-rule.md").write_text("# My Rule", encoding="utf-8")

    result = runner.invoke(main, [
        "init", "--user", "--agents", "claude", "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".claude" / "rules" / "my-rule.md").exists()
    assert "synced rule: my-rule.md" in result.output


def test_config_list(runner, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    result = runner.invoke(main, ["config", "list"])
    assert result.exit_code == 0
    assert "repo_url" in result.output


def test_config_set_get(runner, monkeypatch, tmp_path):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    runner.invoke(main, ["config", "set", "default_branch", "develop"])
    result = runner.invoke(main, ["config", "get", "default_branch"])
    assert result.exit_code == 0
    assert "develop" in result.output
