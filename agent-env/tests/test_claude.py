from agent_env.agents import MANAGED_MARKER_MD
from agent_env.agents.claude import ClaudeAdapter


def test_user_targets_only_settings(kb_root):
    adapter = ClaudeAdapter()
    targets = adapter.user_targets(kb_root)
    dests = [t.dest for t in targets]
    assert any("settings.local.json" in str(d) for d in dests)
    assert not any("CLAUDE.md" in str(d) for d in dests)


def test_project_targets_no_claude_md(kb_root, project_root):
    adapter = ClaudeAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    dests = [t.dest for t in targets]
    assert not any("CLAUDE.md" in str(d) for d in dests)


def test_project_targets_includes_settings(kb_root, project_root):
    adapter = ClaudeAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    dests = [t.dest for t in targets]
    assert any("settings.local.json" in str(d) for d in dests)


def test_is_managed_detects_marker(tmp_path):
    adapter = ClaudeAdapter()
    f = tmp_path / "CLAUDE.md"
    f.write_text(f"{MANAGED_MARKER_MD}\nsome content", encoding="utf-8")
    assert adapter.is_managed(f) is True


def test_is_managed_false_without_marker(tmp_path):
    adapter = ClaudeAdapter()
    f = tmp_path / "CLAUDE.md"
    f.write_text("# My CLAUDE.md\nno marker here", encoding="utf-8")
    assert adapter.is_managed(f) is False
