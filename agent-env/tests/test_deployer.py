from pathlib import Path

from agent_env.agents import MANAGED_MARKER_MD, DeployTarget
from agent_env.deployer import ConflictAction, create_ai_scaffold, deploy_target


def _target(dest: Path, content: str, marker: str = MANAGED_MARKER_MD) -> DeployTarget:
    return DeployTarget(dest=dest, template=None, content=content, managed_marker=marker)


def test_deploy_creates_new_file(tmp_path):
    dest = tmp_path / "subdir" / "file.md"
    deploy_target(_target(dest, "hello"), conflict=ConflictAction.OVERWRITE)
    assert dest.read_text(encoding="utf-8") == "hello"


def test_deploy_creates_parent_dirs(tmp_path):
    dest = tmp_path / "a" / "b" / "c" / "file.md"
    deploy_target(_target(dest, "x"), conflict=ConflictAction.OVERWRITE)
    assert dest.exists()


def test_deploy_skips_existing_unmanaged(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("original", encoding="utf-8")
    result = deploy_target(_target(dest, "new"), conflict=ConflictAction.SKIP)
    assert dest.read_text(encoding="utf-8") == "original"
    assert result == "skipped"


def test_deploy_overwrites_managed_file(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text(f"{MANAGED_MARKER_MD}\nold content", encoding="utf-8")
    deploy_target(
        _target(dest, f"{MANAGED_MARKER_MD}\nnew content"), conflict=ConflictAction.OVERWRITE
    )
    assert "new content" in dest.read_text(encoding="utf-8")


def test_deploy_copies_from_template(tmp_path, kb_root):
    template = kb_root / "agent_cli_file" / "agent_config" / ".claude" / "settings.local.json"
    dest = tmp_path / "settings.local.json"
    marker = '"_managed_by": "agent-env"'
    t = DeployTarget(dest=dest, template=template, content=None, managed_marker=marker)
    deploy_target(t, conflict=ConflictAction.OVERWRITE)
    assert dest.exists()
    assert '"_managed_by": "agent-env"' in dest.read_text(encoding="utf-8")


def test_deploy_template_injects_marker(tmp_path, kb_root):
    template = kb_root / "agent_cli_file" / "agent_config" / ".claude" / "settings.local.json"
    dest = tmp_path / "settings.local.json"
    marker = '"_managed_by": "agent-env"'
    t = DeployTarget(dest=dest, template=template, content=None, managed_marker=marker)
    deploy_target(t, conflict=ConflictAction.OVERWRITE)
    assert '"_managed_by": "agent-env"' in dest.read_text(encoding="utf-8")


def test_create_ai_scaffold_generates_sync_scripts(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    create_ai_scaffold(project)
    assert (project / ".ai" / "sync.sh").exists()
    assert (project / ".ai" / "sync.bat").exists()


def test_create_ai_scaffold_sync_sh_not_overwritten(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / ".ai").mkdir()
    existing = project / ".ai" / "sync.sh"
    existing.write_text("# custom script", encoding="utf-8")
    create_ai_scaffold(project)
    assert existing.read_text(encoding="utf-8") == "# custom script"


def test_create_ai_scaffold_sync_sh_contains_project_root_cd(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    create_ai_scaffold(project)
    content = (project / ".ai" / "sync.sh").read_text(encoding="utf-8")
    assert 'cd "$(dirname "$0")/.."' in content
    assert ".claude/rules/" in content
    assert ".codex/rules/" in content
