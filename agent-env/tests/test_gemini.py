from agent_env.agents import MANAGED_MARKER_MD
from agent_env.agents.gemini import GeminiAdapter


def test_user_targets_gemini_settings(kb_root):
    adapter = GeminiAdapter()
    targets = adapter.user_targets(kb_root)
    assert any("settings.json" in str(t.dest) and ".gemini" in str(t.dest) for t in targets)


def test_project_targets_gemini_md_has_catalogue(kb_root, project_root):
    adapter = GeminiAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    gemini_md = next(t for t in targets if t.dest.name == "GEMINI.md")
    catalogue = str((kb_root / "agent_cli_file" / "catalogue.md").resolve())
    assert catalogue in (gemini_md.content or "")
    assert MANAGED_MARKER_MD in (gemini_md.content or "")


def test_project_targets_gemini_settings(kb_root, project_root):
    adapter = GeminiAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    assert any(".gemini" in str(t.dest) and "settings.json" in str(t.dest) for t in targets)
