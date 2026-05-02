from agent_env.agents import MANAGED_MARKER_TOML
from agent_env.agents.codex import CodexAdapter


def test_user_targets_codex_config(kb_root):
    adapter = CodexAdapter()
    targets = adapter.user_targets(kb_root)
    assert any("config.toml" in str(t.dest) for t in targets)


def test_project_targets_agents_md_has_catalogue(kb_root, project_root):
    adapter = CodexAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    agents_md = next(t for t in targets if t.dest.name == "AGENTS.md")
    catalogue = str((kb_root / "agent_cli_file" / "catalogue.md").resolve())
    assert catalogue in (agents_md.content or "")


def test_is_managed_toml(tmp_path):
    adapter = CodexAdapter()
    f = tmp_path / "config.toml"
    f.write_text(f'{MANAGED_MARKER_TOML}\napproval_policy = "never"\n', encoding="utf-8")
    assert adapter.is_managed(f) is True
